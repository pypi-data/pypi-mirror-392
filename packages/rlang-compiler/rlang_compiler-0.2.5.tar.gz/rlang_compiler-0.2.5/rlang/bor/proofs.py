"""RLang execution proof bundle generation.

Produces deterministic, JSON-serializable execution proof bundles that record
step-level traces for RLang program execution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional

from rlang.canonical import PrimaryProgramIR
from rlang.emitter import compile_source_to_ir
from rlang.ir import IRExpr, IRIf, PipelineIR, PipelineStepIR, StepTemplateIR
from rlang.utils.canonical_json import canonical_dumps


@dataclass(frozen=True)
class StepExecutionRecord:
    """Record of a single step execution within a pipeline.

    Attributes:
        index: 0-based index of the step in the pipeline
        step_name: Name of the step (from template)
        template_id: Template ID reference
        input_snapshot: Input value passed to this step
        output_snapshot: Output value produced by this step
    """

    index: int
    step_name: str
    template_id: str
    input_snapshot: Any
    output_snapshot: Any

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "index": self.index,
            "step_name": self.step_name,
            "template_id": self.template_id,
            "input": self.input_snapshot,
            "output": self.output_snapshot,
        }


@dataclass(frozen=True)
class BranchExecutionRecord:
    """Record of a branch execution within a pipeline.

    Attributes:
        index: Index of the IRIf in the top-level pipeline steps list
        path: "then" or "else"
        condition_value: Evaluated condition value (should be bool)
    """

    index: int
    path: str
    condition_value: Any

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "index": self.index,
            "path": self.path,
            "condition_value": self.condition_value,
        }


@dataclass(frozen=True)
class PipelineProofBundle:
    """Complete proof bundle for a pipeline execution.

    Attributes:
        version: Program version
        language: Source language
        entry_pipeline: Name of entry pipeline, or None
        program_ir: The complete PrimaryProgramIR
        input_value: Initial input value
        output_value: Final output value
        steps: Ordered list of step execution records
        branches: Ordered list of branch execution records
    """

    version: str
    language: str
    entry_pipeline: Optional[str]
    program_ir: PrimaryProgramIR
    input_value: Any
    output_value: Any
    steps: List[StepExecutionRecord] = field(default_factory=list)
    branches: List[BranchExecutionRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "version": self.version,
            "language": self.language,
            "entry_pipeline": self.entry_pipeline,
            "program": self.program_ir.to_dict(),
            "input": self.input_value,
            "output": self.output_value,
            "steps": [s.to_dict() for s in self.steps],
            "branches": [b.to_dict() for b in self.branches],
        }

    def to_json(self) -> str:
        """Convert to canonical JSON string.

        Returns:
            Canonical JSON representation
        """
        return canonical_dumps(self.to_dict())


def _find_entry_pipeline(ir: PrimaryProgramIR) -> Optional[PipelineIR]:
    """Find the PipelineIR corresponding to ir.entry_pipeline.

    Args:
        ir: PrimaryProgramIR to search

    Returns:
        PipelineIR if found, None if no entry pipeline or not found
    """
    if ir.entry_pipeline is None:
        return None

    for pipeline in ir.pipelines:
        if pipeline.name == ir.entry_pipeline:
            return pipeline

    return None


def _build_template_map(ir: PrimaryProgramIR) -> Dict[str, StepTemplateIR]:
    """Map template_id -> StepTemplateIR.

    Args:
        ir: PrimaryProgramIR containing step templates

    Returns:
        Dictionary mapping template_id to StepTemplateIR
    """
    return {template.id: template for template in ir.step_templates}




def _eval_irexpr(
    expr: IRExpr,
    fn_registry: Dict[str, Callable[[Any], Any]],
    current_value: Any,
) -> Any:
    """Evaluate an IRExpr to a Python value.

    Args:
        expr: IRExpr to evaluate
        fn_registry: Dictionary mapping function names to implementations
        current_value: Current pipeline value (for potential future use)

    Returns:
        Evaluated Python value

    Raises:
        RuntimeError: If expression type is not supported or evaluation fails
    """
    if expr.kind == "literal":
        return expr.value

    elif expr.kind == "identifier":
        # Special identifier __value refers to current pipeline value
        if expr.name == "__value":
            return current_value
        else:
            raise RuntimeError(
                f"Unsupported identifier in runtime conditions: {expr.name}. Only '__value' is supported to reference the current pipeline value."
            )

    elif expr.kind == "binary_op":
        left_val = _eval_irexpr(expr.left, fn_registry, current_value)
        right_val = _eval_irexpr(expr.right, fn_registry, current_value)

        if expr.op in ("+", "-", "*", "/"):
            # Arithmetic operations
            if expr.op == "+":
                return left_val + right_val
            elif expr.op == "-":
                return left_val - right_val
            elif expr.op == "*":
                return left_val * right_val
            elif expr.op == "/":
                if right_val == 0:
                    raise RuntimeError("Division by zero")
                return left_val / right_val
        elif expr.op in (">", "<", ">=", "<=", "==", "!="):
            # Comparison operations
            if expr.op == ">":
                return left_val > right_val
            elif expr.op == "<":
                return left_val < right_val
            elif expr.op == ">=":
                return left_val >= right_val
            elif expr.op == "<=":
                return left_val <= right_val
            elif expr.op == "==":
                return left_val == right_val
            elif expr.op == "!=":
                return left_val != right_val
        else:
            raise RuntimeError(f"Unknown binary operator: {expr.op}")

    elif expr.kind == "boolean_and":
        # Boolean AND: evaluate both operands left-to-right, return bool result
        left_val = _eval_irexpr(expr.left, fn_registry, current_value)
        right_val = _eval_irexpr(expr.right, fn_registry, current_value)
        return bool(left_val) and bool(right_val)

    elif expr.kind == "boolean_or":
        # Boolean OR: evaluate both operands left-to-right, return bool result
        left_val = _eval_irexpr(expr.left, fn_registry, current_value)
        right_val = _eval_irexpr(expr.right, fn_registry, current_value)
        return bool(left_val) or bool(right_val)

    elif expr.kind == "boolean_not":
        # Boolean NOT: evaluate operand, return negated bool result
        operand_val = _eval_irexpr(expr.operand, fn_registry, current_value)
        return not bool(operand_val)

    elif expr.kind == "call":
        # Evaluate arguments
        arg_values = [_eval_irexpr(arg, fn_registry, current_value) for arg in expr.args]

        # Look up function
        if expr.func not in fn_registry:
            raise RuntimeError(f"Function '{expr.func}' not found in registry")
        fn_impl = fn_registry[expr.func]

        # Call function
        return fn_impl(*arg_values)

    elif expr.kind == "record":
        # Evaluate record literal: evaluate each field expression
        if expr.fields is None:
            return {}
        
        # Evaluate fields and build dict in sorted order (fields are already sorted in IR)
        record_dict = {}
        for field_name, field_expr in expr.fields.items():
            field_value = _eval_irexpr(field_expr, fn_registry, current_value)
            record_dict[field_name] = field_value
        
        # Return dict with fields in alphabetical order (guaranteed by IR sorting)
        return record_dict

    elif expr.kind == "field_access":
        # Evaluate field access: evaluate record expression, then access field
        if expr.record is None or expr.field_name is None:
            raise RuntimeError("Field access expression missing record or field_name")
        
        record_value = _eval_irexpr(expr.record, fn_registry, current_value)
        
        # Defensive checks: record_value should be a dict
        if not isinstance(record_value, dict):
            raise RuntimeError(
                f"Field access failed: expected dict, got {type(record_value).__name__}"
            )
        
        if expr.field_name not in record_value:
            raise RuntimeError(
                f"Field access failed: field '{expr.field_name}' not found in record"
            )
        
        return record_value[expr.field_name]

    elif expr.kind == "list":
        # Evaluate list literal: evaluate all element expressions
        elements = []
        for elem_expr in expr.elements:
            elem_value = _eval_irexpr(elem_expr, fn_registry, current_value)
            elements.append(elem_value)
        # Return Python list preserving element order
        return elements

    else:
        raise RuntimeError(f"Unsupported expression kind for evaluation: {expr.kind}")


def _execute_normal_step(
    step_ir: PipelineStepIR,
    current_value: Any,
    fn_registry: Dict[str, Callable[[Any], Any]],
    template_map: Dict[str, StepTemplateIR],
) -> tuple[Any, StepExecutionRecord]:
    """Execute a normal pipeline step.

    Args:
        step_ir: PipelineStepIR to execute
        current_value: Current pipeline value
        fn_registry: Dictionary mapping function names to implementations
        template_map: Dictionary mapping template_id to StepTemplateIR

    Returns:
        Tuple of (new_value, StepExecutionRecord)

    Raises:
        ValueError: If template is not found
    """
    # Get template
    template_id = step_ir.template_id
    if template_id not in template_map:
        raise ValueError(
            f"Template ID '{template_id}' referenced in pipeline "
            f"but not found in step templates"
        )
    template = template_map[template_id]
    step_name = template.name

    # Resolve function implementation - require all functions to be provided
    if step_name not in fn_registry:
        raise ValueError(
            f"Function '{step_name}' (template_id: '{template_id}') not found in fn_registry. "
            f"All pipeline steps must have corresponding function implementations provided."
        )
    fn_impl = fn_registry[step_name]

    # Execute step
    in_snapshot = current_value
    out_value = fn_impl(current_value)

    # Create execution record
    record = StepExecutionRecord(
        index=step_ir.index,
        step_name=step_name,
        template_id=template_id,
        input_snapshot=in_snapshot,
        output_snapshot=out_value,
    )

    return out_value, record


def _execute_if_step(
    ir_if: IRIf,
    current_value: Any,
    fn_registry: Dict[str, Callable[[Any], Any]],
    template_map: Dict[str, StepTemplateIR],
    if_index: int,
) -> tuple[Any, List[StepExecutionRecord], List[BranchExecutionRecord]]:
    """Execute an IRIf step.

    Supports nested IF expressions recursively.

    Args:
        ir_if: IRIf to execute
        current_value: Current pipeline value
        fn_registry: Dictionary mapping function names to implementations
        template_map: Dictionary mapping template_id to StepTemplateIR
        if_index: Index of the IRIf in the top-level pipeline steps list

    Returns:
        Tuple of (new_value, list of StepExecutionRecord, list of BranchExecutionRecord)
        The branch records list includes this IF's branch record followed by any nested branch records
        in encounter order.

    Raises:
        RuntimeError: If condition does not evaluate to bool
    """
    # Evaluate condition
    cond_val = _eval_irexpr(ir_if.condition, fn_registry, current_value)
    if not isinstance(cond_val, bool):
        raise RuntimeError(
            f"If condition did not evaluate to Bool, got {type(cond_val).__name__}: {cond_val}"
        )

    # Choose branch
    if cond_val:
        branch_steps = ir_if.then_steps
        path = "then"
    else:
        branch_steps = ir_if.else_steps or []
        path = "else"

    # Create branch execution record for this IF (appended first, before nested records)
    branch_record = BranchExecutionRecord(
        index=if_index,
        path=path,
        condition_value=cond_val,
    )

    # Execute branch steps as a fragment (recursively handles nested IFs)
    branch_records: List[StepExecutionRecord] = []
    nested_branch_records: List[BranchExecutionRecord] = []
    current = current_value

    for step_ir in branch_steps:
        if isinstance(step_ir, IRIf):
            # Support nested conditionals recursively
            # Use a placeholder index for nested IFs (they're not in top-level steps list)
            # The actual index doesn't matter for nested IFs since they're tracked by encounter order
            nested_current, nested_step_records, nested_branches = _execute_if_step(
                step_ir, current, fn_registry, template_map, -1  # -1 indicates nested
            )
            branch_records.extend(nested_step_records)
            nested_branch_records.extend(nested_branches)  # Includes nested IF's own branch record
            current = nested_current
        elif isinstance(step_ir, IRExpr):
            # Execute expression step (e.g., RecordExpr, FieldAccess, ListExpr)
            in_snapshot = current
            out_value = _eval_irexpr(step_ir, fn_registry, current)
            template_id = f"expr:{step_ir.kind}"
            rec = StepExecutionRecord(
                index=-1,  # Nested expression step
                step_name="",
                template_id=template_id,
                input_snapshot=in_snapshot,
                output_snapshot=out_value,
            )
            branch_records.append(rec)
            current = out_value
        else:
            current, rec = _execute_normal_step(step_ir, current, fn_registry, template_map)
            branch_records.append(rec)

    # Return: this IF's branch record first, then nested branch records in encounter order
    all_branch_records = [branch_record] + nested_branch_records

    return current, branch_records, all_branch_records


def run_program_with_proof(
    source: str,
    input_value: Any,
    fn_registry: Optional[Dict[str, Callable[[Any], Any]]] = None,
    version: str = "v0",
    language: str = "rlang",
) -> PipelineProofBundle:
    """Compile source, execute entry pipeline, and return proof bundle.

    Compiles the RLang source, executes the entry pipeline over the input value,
    and returns a deterministic proof bundle containing step-level traces.

    Execution is done at the RLang level by following the PipelineIR:
    - All step functions must be provided in fn_registry.
    - Raises ValueError if any required function is missing.

    Args:
        source: RLang source code string
        input_value: Input value to pass to the pipeline
        fn_registry: Optional dictionary mapping function names to implementations
        version: Program version (default "v0")
        language: Source language (default "rlang")

    Returns:
        PipelineProofBundle containing execution trace

    Raises:
        ValueError: If no entry pipeline is found or template is missing
    """
    # 1. Compile to PrimaryProgramIR
    compile_result = compile_source_to_ir(source, version=version, language=language)
    program_ir = compile_result.program_ir

    # 2. Find entry pipeline
    pipeline_ir = _find_entry_pipeline(program_ir)
    if pipeline_ir is None:
        raise ValueError("No entry pipeline found in program.")

    # 3. Build template map
    template_map = _build_template_map(program_ir)

    # 4. Prepare function registry
    registry = fn_registry or {}

    # 5. Execute pipeline sequentially
    current_value = input_value
    records: List[StepExecutionRecord] = []
    branch_records: List[BranchExecutionRecord] = []

    for step_idx, step_ir in enumerate(pipeline_ir.steps):
        if isinstance(step_ir, IRIf):
            # Execute if step (returns list of branch records including nested ones)
            current_value, step_records, branch_records_list = _execute_if_step(
                step_ir, current_value, registry, template_map, step_idx
            )
            records.extend(step_records)
            # Extend branch_records with all branch records (outer IF + nested IFs in encounter order)
            branch_records.extend(branch_records_list)
        elif isinstance(step_ir, IRExpr):
            # Execute expression step (e.g., RecordExpr, FieldAccess, ListExpr)
            # Evaluate expression and create a step record
            in_snapshot = current_value
            out_value = _eval_irexpr(step_ir, registry, current_value)
            
            # Create execution record for expression step
            # Use a synthetic template_id for expression steps
            template_id = f"expr:{step_ir.kind}"
            record = StepExecutionRecord(
                index=step_idx,
                step_name="",  # Empty name for expression steps
                template_id=template_id,
                input_snapshot=in_snapshot,
                output_snapshot=out_value,
            )
            records.append(record)
            current_value = out_value
        else:
            # Execute normal step
            current_value, record = _execute_normal_step(
                step_ir, current_value, registry, template_map
            )
            records.append(record)

    # 6. Build and return proof bundle
    final_output = current_value

    bundle = PipelineProofBundle(
        version=version,
        language=language,
        entry_pipeline=program_ir.entry_pipeline,
        program_ir=program_ir,
        input_value=input_value,
        output_value=final_output,
        steps=records,
        branches=branch_records,
    )

    return bundle


__all__ = [
    "StepExecutionRecord",
    "BranchExecutionRecord",
    "PipelineProofBundle",
    "run_program_with_proof",
]

