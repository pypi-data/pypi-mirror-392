"""IR lowering from type-checked RLang modules.

Converts type-checked AST into StepTemplateIR and PipelineIR.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from rlang.parser import BinaryOp, BooleanAnd, BooleanNot, BooleanOr, Call, Case, Expr, FieldAccess, ForExpr, FunctionDecl, Identifier, IfExpr, ListExpr, ListPattern, Literal, LiteralPattern, MatchExpr, Module, PipelineDecl, PipelineStep, Pattern, RecordExpr, RecordPattern, VarPattern, WildcardPattern
from rlang.semantic import SymbolKind, SymbolTable
from rlang.types import RType, TypeCheckResult
from rlang.types.type_system import rtype_from_type_expr

from rlang.ir.model import (
    IRExpr,
    IRIf,
    LoweringIRBundle,
    PipelineIR,
    PipelineStepIR,
    StepTemplateIR,
    rtype_to_string,
)


class LoweringError(Exception):
    """Exception raised when IR lowering fails."""

    pass


@dataclass
class LoweringResult:
    """Result of IR lowering.

    Attributes:
        module: The original module AST
        ir: LoweringIRBundle containing all step templates and pipelines
    """

    module: Module
    ir: LoweringIRBundle


class Lowerer:
    """Lowers type-checked RLang modules to IR."""

    def __init__(self, tc_result: TypeCheckResult):
        """Initialize lowerer with type check result.

        Args:
            tc_result: Type check result containing module, symbols, and expression types
        """
        self.module = tc_result.module
        self.symbols = tc_result.symbols
        self.expr_types = tc_result.expr_types  # mapping expr_id -> RType
        self._fn_signatures: Dict[str, Tuple[List[RType], Optional[RType]]] = {}
        self._step_templates: Dict[str, StepTemplateIR] = {}
        self._pipelines: Dict[str, PipelineIR] = {}

    def lower(self) -> LoweringResult:
        """Lower the module to IR.

        Returns:
            LoweringResult with module and IR bundle

        Raises:
            LoweringError: If lowering fails
        """
        # Build function signatures
        self._collect_function_signatures()

        # Build step templates
        self._build_step_templates()

        # Lower pipelines
        self._lower_pipelines()

        # Construct bundle
        bundle = LoweringIRBundle(
            step_templates=self._step_templates,
            pipelines=self._pipelines,
        )

        return LoweringResult(module=self.module, ir=bundle)

    def _collect_function_signatures(self) -> None:
        """Collect function signatures as RTypes."""
        for decl in self.module.decls:
            if isinstance(decl, FunctionDecl):
                symbol = self.symbols.lookup(decl.name)
                if symbol is None or symbol.kind != SymbolKind.FUNCTION:
                    continue

                # Convert parameter types to RType
                param_rtypes: List[RType] = []
                for param in decl.params:
                    if param.type is not None:
                        param_rtype = rtype_from_type_expr(param.type, self.symbols)
                        param_rtypes.append(param_rtype)

                # Convert return type to RType
                ret_rtype: Optional[RType] = None
                if decl.return_type is not None:
                    ret_rtype = rtype_from_type_expr(decl.return_type, self.symbols)

                self._fn_signatures[decl.name] = (param_rtypes, ret_rtype)

    def _build_step_templates(self) -> None:
        """Build StepTemplateIR for each function."""
        for name, (param_rtypes, ret_rtype) in self._fn_signatures.items():
            template_id = f"fn:{name}"

            param_types = [rtype_to_string(t) for t in param_rtypes]
            return_type_str = rtype_to_string(ret_rtype) if ret_rtype is not None else None

            # Build rule_repr
            param_str = ", ".join(param_types)
            return_str = return_type_str if return_type_str is not None else "Unit"
            rule_repr = f"fn {name}({param_str}) -> {return_str}"

            template = StepTemplateIR(
                id=template_id,
                name=name,
                fn_name=name,
                param_types=param_types,
                return_type=return_type_str,
                rule_repr=rule_repr,
            )

            self._step_templates[template_id] = template

    def _lower_pipelines(self) -> None:
        """Lower all pipeline declarations to PipelineIR."""
        for decl in self.module.decls:
            if isinstance(decl, PipelineDecl):
                pipeline_id = f"pipeline:{decl.name}"

                # Convert input/output types to strings
                input_type_str: Optional[str] = None
                if decl.input_type is not None:
                    input_rtype = rtype_from_type_expr(decl.input_type, self.symbols)
                    input_type_str = rtype_to_string(input_rtype)

                output_type_str: Optional[str] = None
                if decl.output_type is not None:
                    output_rtype = rtype_from_type_expr(decl.output_type, self.symbols)
                    output_type_str = rtype_to_string(output_rtype)

                # Lower each step
                pipeline_steps: List[PipelineStepIR | IRIf | IRExpr] = []
                step_index = 0  # Running index for PipelineStepIR nodes
                for step in decl.steps:
                    # Check if this is an expression-based step (e.g., IfExpr, ForExpr, MatchExpr, RecordExpr, FieldAccess)
                    if step.expr is not None:
                        if isinstance(step.expr, IfExpr):
                            ir_if = self._lower_if_expr_step(step.expr)
                            pipeline_steps.append(ir_if)
                        elif isinstance(step.expr, ForExpr):
                            # Unroll for loop: expand body steps (end - start) times
                            unrolled_steps, step_index = self._lower_for_expr_step(step.expr, step_index)
                            pipeline_steps.extend(unrolled_steps)
                        elif isinstance(step.expr, MatchExpr):
                            ir_if = self._lower_match_expr_step(step.expr)
                            pipeline_steps.append(ir_if)
                        elif isinstance(step.expr, (RecordExpr, FieldAccess, ListExpr)):
                            # RecordExpr, FieldAccess, and ListExpr are lowered to IRExpr and used directly as steps
                            ir_expr = self._lower_expr(step.expr, pattern_bindings={})
                            pipeline_steps.append(ir_expr)
                        else:
                            raise LoweringError(
                                f"Unsupported expression type in pipeline step: {type(step.expr).__name__}"
                            )
                    else:
                        # Normal function-based step
                        pipeline_step = self._lower_normal_pipeline_step(step, step_index)
                        pipeline_steps.append(pipeline_step)
                        step_index += 1

                # Construct PipelineIR
                pipeline_ir = PipelineIR(
                    id=pipeline_id,
                    name=decl.name,
                    input_type=input_type_str,
                    output_type=output_type_str,
                    steps=pipeline_steps,
                )

                self._pipelines[decl.name] = pipeline_ir

    def _lower_normal_pipeline_step(self, step: PipelineStep, index: int) -> PipelineStepIR:
        """Lower a normal function-based pipeline step to PipelineStepIR.

        Args:
            step: Pipeline step AST node
            index: Step index in pipeline

        Returns:
            PipelineStepIR node

        Raises:
            LoweringError: If lowering fails
        """
        step_name = step.name

        # Look up function signature
        if step_name not in self._fn_signatures:
            raise LoweringError(f"Function '{step_name}' not found for pipeline step")

        param_rtypes, ret_rtype = self._fn_signatures[step_name]
        template_id = f"fn:{step_name}"

        # Determine arg_types from explicit arguments
        arg_types: List[str] = []
        for arg_expr in step.args:
            arg_expr_id = id(arg_expr)
            if arg_expr_id not in self.expr_types:
                raise LoweringError(
                    f"Expression type not found for argument in step '{step_name}'"
                )
            arg_rtype = self.expr_types[arg_expr_id]
            arg_types.append(rtype_to_string(arg_rtype))

        # Determine input_type and output_type for this step
        step_input_type: Optional[str] = None
        if param_rtypes:
            step_input_type = rtype_to_string(param_rtypes[0])

        step_output_type: Optional[str] = None
        if ret_rtype is not None:
            step_output_type = rtype_to_string(ret_rtype)

        return PipelineStepIR(
            index=index,
            name=step_name,
            template_id=template_id,
            arg_types=arg_types,
            input_type=step_input_type,
            output_type=step_output_type,
        )

    def _lower_expr(self, expr: Expr, pattern_bindings: Dict[str, IRExpr] = None) -> IRExpr:
        """Lower an expression AST node to IRExpr.

        Args:
            expr: Expression AST node
            pattern_bindings: Dictionary mapping pattern-bound variable names to their IRExpr values

        Returns:
            IRExpr node

        Raises:
            LoweringError: If expression type is not supported
        """
        if pattern_bindings is None:
            pattern_bindings = {}
        
        if isinstance(expr, Literal):
            return IRExpr(kind="literal", value=expr.value)

        elif isinstance(expr, Identifier):
            # Check if this identifier is a pattern-bound variable
            if expr.name in pattern_bindings:
                return pattern_bindings[expr.name]
            return IRExpr(kind="identifier", name=expr.name)

        elif isinstance(expr, BooleanAnd):
            left_ir = self._lower_expr(expr.left, pattern_bindings=pattern_bindings)
            right_ir = self._lower_expr(expr.right, pattern_bindings=pattern_bindings)
            return IRExpr(kind="boolean_and", left=left_ir, right=right_ir)

        elif isinstance(expr, BooleanOr):
            left_ir = self._lower_expr(expr.left, pattern_bindings=pattern_bindings)
            right_ir = self._lower_expr(expr.right, pattern_bindings=pattern_bindings)
            return IRExpr(kind="boolean_or", left=left_ir, right=right_ir)

        elif isinstance(expr, BooleanNot):
            operand_ir = self._lower_expr(expr.operand, pattern_bindings=pattern_bindings)
            return IRExpr(kind="boolean_not", operand=operand_ir)

        elif isinstance(expr, BinaryOp):
            left_ir = self._lower_expr(expr.left, pattern_bindings=pattern_bindings)
            right_ir = self._lower_expr(expr.right, pattern_bindings=pattern_bindings)
            return IRExpr(kind="binary_op", op=expr.op, left=left_ir, right=right_ir)

        elif isinstance(expr, Call):
            if not isinstance(expr.func, Identifier):
                raise LoweringError("Function call must have identifier as function")
            func_name = expr.func.name
            args_ir = [self._lower_expr(arg, pattern_bindings=pattern_bindings) for arg in expr.args]
            return IRExpr(kind="call", func=func_name, args=args_ir)

        elif isinstance(expr, RecordExpr):
            # Lower record literal: sort fields alphabetically for IR determinism
            lowered_fields: Dict[str, IRExpr] = {}
            for field_name, field_expr in expr.fields.items():
                lowered_fields[field_name] = self._lower_expr(field_expr, pattern_bindings=pattern_bindings)
            # Sort by field name for canonical ordering
            sorted_fields = dict(sorted(lowered_fields.items()))
            return IRExpr(kind="record", fields=sorted_fields)

        elif isinstance(expr, FieldAccess):
            record_ir = self._lower_expr(expr.record, pattern_bindings=pattern_bindings)
            return IRExpr(kind="field_access", record=record_ir, field_name=expr.field)

        elif isinstance(expr, ListExpr):
            # Lower list literal: recursively lower all elements
            elements_ir = [self._lower_expr(elem, pattern_bindings=pattern_bindings) for elem in expr.elements]
            return IRExpr(kind="list", elements=elements_ir)

        else:
            raise LoweringError(f"Unsupported expression type for lowering: {type(expr).__name__}")

    def _lower_pipeline_steps_fragment(
        self, steps: List[PipelineStep], start_index: int, pattern_bindings: Dict[str, IRExpr] = None
    ) -> Tuple[List[PipelineStepIR | IRIf | IRExpr], int]:
        """Lower a fragment of pipeline steps (e.g., inside an if branch).

        Args:
            steps: List of pipeline step AST nodes
            start_index: Starting index for step numbering (for reference, not used in fragment)
            pattern_bindings: Dictionary mapping pattern-bound variable names to their IRExpr values

        Returns:
            Tuple of (list of PipelineStepIR, IRIf, or IRExpr nodes, next_index)
        """
        if pattern_bindings is None:
            pattern_bindings = {}
        
        ir_steps: List[PipelineStepIR | IRIf | IRExpr] = []
        current_index = start_index

        for step in steps:
            if step.expr is not None:
                # Expression-based steps in fragments (e.g., nested if, match, record expressions)
                if isinstance(step.expr, IfExpr):
                    # Lower nested if expression recursively
                    ir_if = self._lower_if_expr_step(step.expr)
                    ir_steps.append(ir_if)
                    # IRIf doesn't have an index, so we don't increment current_index
                elif isinstance(step.expr, MatchExpr):
                    # Lower nested match expression recursively
                    ir_if = self._lower_match_expr_step(step.expr)
                    ir_steps.append(ir_if)
                    # IRIf doesn't have an index, so we don't increment current_index
                elif isinstance(step.expr, (RecordExpr, FieldAccess, ListExpr)):
                    # RecordExpr, FieldAccess, and ListExpr are lowered to IRExpr
                    ir_expr = self._lower_expr(step.expr, pattern_bindings=pattern_bindings)
                    ir_steps.append(ir_expr)
                else:
                    raise LoweringError(
                        f"Unsupported expression type in fragment: {type(step.expr).__name__}"
                    )
            else:
                ir_step = self._lower_normal_pipeline_step(step, current_index)
                ir_steps.append(ir_step)
                current_index += 1

        return ir_steps, current_index

    def _lower_if_expr_step(self, if_expr: IfExpr) -> IRIf:
        """Lower an IfExpr AST node to IRIf.

        Supports nested IF expressions recursively.

        Args:
            if_expr: If expression AST node

        Returns:
            IRIf node

        Raises:
            LoweringError: If lowering fails
        """
        # Lower condition expression (no pattern bindings in IF conditions)
        condition_ir = self._lower_expr(if_expr.condition, pattern_bindings={})

        # Lower then branch steps (recursively handles nested IFs)
        then_steps_ir, _ = self._lower_pipeline_steps_fragment(if_expr.then_steps, 0, pattern_bindings={})

        # Lower else branch steps (if any, recursively handles nested IFs)
        if if_expr.else_steps is None:
            else_steps_ir: List[PipelineStepIR | IRIf] = []
        else:
            else_steps_ir, _ = self._lower_pipeline_steps_fragment(if_expr.else_steps, 0, pattern_bindings={})

        return IRIf(
            condition=condition_ir,
            then_steps=then_steps_ir,
            else_steps=else_steps_ir,
        )

    def _lower_for_expr_step(
        self, for_expr: ForExpr, start_index: int
    ) -> Tuple[List[PipelineStepIR | IRIf | IRExpr], int]:
        """Lower a ForExpr AST node by unrolling it into repeated steps.

        Args:
            for_expr: For expression AST node
            start_index: Starting index for step numbering

        Returns:
            Tuple of (list of unrolled IR steps, next_index)
        """
        # Calculate iteration count
        count = max(0, for_expr.end - for_expr.start)

        # Lower the body steps once (no pattern bindings in for loops)
        body_steps_ir, _ = self._lower_pipeline_steps_fragment(for_expr.body, 0, pattern_bindings={})

        # Unroll: repeat body steps 'count' times
        unrolled_steps: List[PipelineStepIR | IRIf | IRExpr] = []
        current_index = start_index

        for _ in range(count):
            for body_step in body_steps_ir:
                if isinstance(body_step, PipelineStepIR):
                    # Create a new PipelineStepIR with updated index
                    updated_step = PipelineStepIR(
                        index=current_index,
                        name=body_step.name,
                        template_id=body_step.template_id,
                        arg_types=body_step.arg_types,
                        input_type=body_step.input_type,
                        output_type=body_step.output_type,
                    )
                    unrolled_steps.append(updated_step)
                    current_index += 1
                else:
                    # IRIf and IRExpr don't have indices, just append as-is
                    unrolled_steps.append(body_step)

        return unrolled_steps, current_index

    def _lower_match_expr_step(self, match_expr: MatchExpr) -> IRIf:
        """Lower a MatchExpr AST node to nested IRIf.

        Converts match expression into nested if-else chain.

        Args:
            match_expr: Match expression AST node

        Returns:
            IRIf node representing nested if-else chain

        Raises:
            LoweringError: If lowering fails
        """
        # Lower the scrutinee (value expression) - no pattern bindings at this level
        scrutinee_ir = self._lower_expr(match_expr.value, pattern_bindings={})

        # Build nested if-else chain from cases
        if not match_expr.cases:
            raise LoweringError("Match expression must have at least one case")

        # Separate wildcard case from regular cases
        regular_cases = []
        wildcard_case = None
        
        for case in match_expr.cases:
            if isinstance(case.pattern, WildcardPattern):
                if wildcard_case is not None:
                    raise LoweringError("Match expression can only have one wildcard case")
                wildcard_case = case
            else:
                regular_cases.append(case)

        # Start with the final else branch (wildcard or MatchError)
        current_else: List[PipelineStepIR | IRIf | IRExpr] = []
        if wildcard_case is not None:
            # Lower the wildcard case body (no bindings for wildcard)
            current_else, _ = self._lower_pipeline_steps_fragment(wildcard_case.body, 0, pattern_bindings={})
        else:
            # No wildcard case: add MatchError
            match_error = IRExpr(
                kind="call",
                func="raise",
                args=[IRExpr(kind="literal", value="MatchError: no pattern matched")]
            )
            current_else = [match_error]

        # Build nested IRIf chain from regular cases (in reverse order)
        # Process cases in reverse to build nested structure: case1 -> (case2 -> (case3 -> else))
        for i in range(len(regular_cases) - 1, -1, -1):
            case = regular_cases[i]

            # Compute pattern bindings (var_name -> IRExpr)
            pattern_bindings = self._compute_pattern_bindings(case.pattern, scrutinee_ir)

            # Lower pattern condition (with guarded field/index access)
            condition_ir = self._lower_pattern_cond(case.pattern, scrutinee_ir)

            # Lower case body with pattern bindings available
            then_steps, _ = self._lower_pipeline_steps_fragment(case.body, 0, pattern_bindings=pattern_bindings)

            # Create IRIf node
            ir_if = IRIf(
                condition=condition_ir,
                then_steps=then_steps,
                else_steps=current_else,
            )

            # This becomes the else branch for the next case
            current_else = [ir_if]

        # The outermost IRIf is the result
        if len(current_else) == 1 and isinstance(current_else[0], IRIf):
            return current_else[0]
        elif regular_cases:
            # Should have at least one regular case if we got here
            raise LoweringError("Failed to construct match expression IR")
        else:
            # Only wildcard case - return a simple if(true) with the wildcard body
            return IRIf(
                condition=IRExpr(kind="literal", value=True),
                then_steps=current_else,
                else_steps=[],
            )

    def _compute_pattern_bindings(self, pattern: Pattern, scrutinee_ir: IRExpr) -> Dict[str, IRExpr]:
        """Compute variable bindings from a pattern.

        Args:
            pattern: Pattern to extract bindings from
            scrutinee_ir: IRExpr for the value being matched

        Returns:
            Dictionary mapping variable names to their IRExpr values
        """
        bindings: Dict[str, IRExpr] = {}
        
        if isinstance(pattern, VarPattern):
            # Variable pattern binds the entire scrutinee
            bindings[pattern.name] = scrutinee_ir
        
        elif isinstance(pattern, RecordPattern):
            # Record pattern: bind each field variable
            for field_name, field_pattern in pattern.fields.items():
                # Access field
                field_access_ir = IRExpr(
                    kind="field_access",
                    record=scrutinee_ir,
                    field_name=field_name,
                )
                # Recursively compute bindings from subpattern
                sub_bindings = self._compute_pattern_bindings(field_pattern, field_access_ir)
                bindings.update(sub_bindings)
        
        elif isinstance(pattern, ListPattern):
            # List pattern: bind each element variable
            for i, elem_pattern in enumerate(pattern.elements):
                # Access list element
                elem_access_ir = IRExpr(
                    kind="call",
                    func="list_index",
                    args=[scrutinee_ir, IRExpr(kind="literal", value=i)],
                )
                # Recursively compute bindings from subpattern
                sub_bindings = self._compute_pattern_bindings(elem_pattern, elem_access_ir)
                bindings.update(sub_bindings)
        
        # WildcardPattern and LiteralPattern don't create bindings
        return bindings

    def _lower_pattern_cond(self, pattern: Pattern, scrutinee_ir: IRExpr) -> IRExpr:
        """Lower a pattern to a boolean IRExpr condition.

        Args:
            pattern: Pattern to lower
            scrutinee_ir: IRExpr for the value being matched

        Returns:
            IRExpr of kind boolean_* representing the pattern condition

        Raises:
            LoweringError: If pattern type is not supported
        """
        if isinstance(pattern, WildcardPattern):
            # Wildcard always matches - return true
            return IRExpr(kind="literal", value=True)

        elif isinstance(pattern, VarPattern):
            # Variable pattern always matches - return true
            return IRExpr(kind="literal", value=True)

        elif isinstance(pattern, LiteralPattern):
            # Literal pattern: equality check
            literal_ir = IRExpr(kind="literal", value=pattern.value)
            return IRExpr(kind="binary_op", op="==", left=scrutinee_ir, right=literal_ir)

        elif isinstance(pattern, RecordPattern):
            # Record pattern: AND of all field pattern conditions
            # Guard field access: check field exists before accessing
            conditions: List[IRExpr] = []
            
            # Sort fields lexicographically for deterministic ordering
            sorted_fields = sorted(pattern.fields.items())
            
            for field_name, field_pattern in sorted_fields:
                # Guard: check if field exists in record
                # Use a hypothetical "has_field" function to check existence
                # If field doesn't exist, this pattern doesn't match (short-circuit)
                field_exists_check = IRExpr(
                    kind="call",
                    func="has_field",
                    args=[scrutinee_ir, IRExpr(kind="literal", value=field_name)],
                )
                
                # Access field (only if exists)
                field_access_ir = IRExpr(
                    kind="field_access",
                    record=scrutinee_ir,
                    field_name=field_name,
                )
                
                # Recursively lower subpattern
                field_cond = self._lower_pattern_cond(field_pattern, field_access_ir)
                
                # Combine: field_exists AND field_cond
                # This ensures we don't crash on missing fields
                combined_cond = IRExpr(
                    kind="boolean_and",
                    left=field_exists_check,
                    right=field_cond,
                )
                conditions.append(combined_cond)
            
            # Combine all conditions with AND (left-to-right)
            if not conditions:
                # Empty record pattern matches any record
                return IRExpr(kind="literal", value=True)
            
            # Build left-associative AND chain
            result = conditions[0]
            for cond in conditions[1:]:
                result = IRExpr(kind="boolean_and", left=result, right=cond)
            
            return result

        elif isinstance(pattern, ListPattern):
            # List pattern: check length AND all element conditions
            # Length check guards against index out of range
            conditions: List[IRExpr] = []
            
            # Check length first (this guards all subsequent index accesses)
            pattern_len = len(pattern.elements)
            length_check = IRExpr(
                kind="binary_op",
                op="==",
                left=IRExpr(kind="call", func="len", args=[scrutinee_ir]),
                right=IRExpr(kind="literal", value=pattern_len),
            )
            conditions.append(length_check)
            
            # Check each element pattern (only if length matches)
            # Since length_check is first in the AND chain, if it fails,
            # the subsequent index accesses won't be evaluated (short-circuit)
            for i, elem_pattern in enumerate(pattern.elements):
                # Access list element (using index access)
                # Length check above ensures this is safe
                elem_access_ir = IRExpr(
                    kind="call",
                    func="list_index",
                    args=[scrutinee_ir, IRExpr(kind="literal", value=i)],
                )
                
                # Recursively lower element pattern
                elem_cond = self._lower_pattern_cond(elem_pattern, elem_access_ir)
                conditions.append(elem_cond)
            
            # Combine all conditions with AND (left-to-right)
            # Short-circuit evaluation ensures length check protects index accesses
            if not conditions:
                # Empty list pattern matches any empty list
                return IRExpr(kind="literal", value=True)
            
            # Build left-associative AND chain
            result = conditions[0]
            for cond in conditions[1:]:
                result = IRExpr(kind="boolean_and", left=result, right=cond)
            
            return result

        else:
            raise LoweringError(f"Unknown pattern type: {type(pattern).__name__}")


def lower_to_ir(tc_result: TypeCheckResult) -> LoweringResult:
    """Lower a type-checked module to IR.

    Args:
        tc_result: Type check result containing module and type information

    Returns:
        LoweringResult with module and IR bundle

    Raises:
        LoweringError: If lowering fails
    """
    lowerer = Lowerer(tc_result)
    return lowerer.lower()


__all__ = [
    "LoweringError",
    "LoweringResult",
    "Lowerer",
    "lower_to_ir",
]

