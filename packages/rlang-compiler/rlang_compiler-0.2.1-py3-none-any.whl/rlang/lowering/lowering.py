"""IR lowering from type-checked RLang modules.

Converts type-checked AST into StepTemplateIR and PipelineIR.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from rlang.parser import BinaryOp, Call, Expr, FunctionDecl, Identifier, IfExpr, Literal, Module, PipelineDecl, PipelineStep
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
                pipeline_steps: List[PipelineStepIR | IRIf] = []
                for idx, step in enumerate(decl.steps):
                    # Check if this is an expression-based step (e.g., IfExpr)
                    if step.expr is not None:
                        if isinstance(step.expr, IfExpr):
                            ir_if = self._lower_if_expr_step(step.expr)
                            pipeline_steps.append(ir_if)
                        else:
                            raise LoweringError(
                                f"Unsupported expression type in pipeline step: {type(step.expr).__name__}"
                            )
                    else:
                        # Normal function-based step
                        pipeline_step = self._lower_normal_pipeline_step(step, idx)
                        pipeline_steps.append(pipeline_step)

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

    def _lower_expr(self, expr: Expr) -> IRExpr:
        """Lower an expression AST node to IRExpr.

        Args:
            expr: Expression AST node

        Returns:
            IRExpr node

        Raises:
            LoweringError: If expression type is not supported
        """
        if isinstance(expr, Literal):
            return IRExpr(kind="literal", value=expr.value)

        elif isinstance(expr, Identifier):
            return IRExpr(kind="identifier", name=expr.name)

        elif isinstance(expr, BinaryOp):
            left_ir = self._lower_expr(expr.left)
            right_ir = self._lower_expr(expr.right)
            return IRExpr(kind="binary_op", op=expr.op, left=left_ir, right=right_ir)

        elif isinstance(expr, Call):
            if not isinstance(expr.func, Identifier):
                raise LoweringError("Function call must have identifier as function")
            func_name = expr.func.name
            args_ir = [self._lower_expr(arg) for arg in expr.args]
            return IRExpr(kind="call", func=func_name, args=args_ir)

        else:
            raise LoweringError(f"Unsupported expression type for lowering: {type(expr).__name__}")

    def _lower_pipeline_steps_fragment(
        self, steps: List[PipelineStep], start_index: int
    ) -> Tuple[List[PipelineStepIR], int]:
        """Lower a fragment of pipeline steps (e.g., inside an if branch).

        Args:
            steps: List of pipeline step AST nodes
            start_index: Starting index for step numbering (for reference, not used in fragment)

        Returns:
            Tuple of (list of PipelineStepIR nodes, next_index)
        """
        ir_steps: List[PipelineStepIR] = []
        current_index = start_index

        for step in steps:
            if step.expr is not None:
                # Expression-based steps in fragments (e.g., nested if)
                # For now, we only support nested if expressions
                if isinstance(step.expr, IfExpr):
                    # Lower nested if expression - but we need to return PipelineStepIR, not IRIf
                    # Actually, fragments should return PipelineStepIR only, not IRIf
                    # Nested if expressions will be handled when we support them fully
                    raise LoweringError("Nested if expressions in branches not yet fully supported")
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

        Args:
            if_expr: If expression AST node

        Returns:
            IRIf node

        Raises:
            LoweringError: If lowering fails
        """
        # Lower condition expression
        condition_ir = self._lower_expr(if_expr.condition)

        # Lower then branch steps
        then_steps_ir, _ = self._lower_pipeline_steps_fragment(if_expr.then_steps, 0)

        # Lower else branch steps (if any)
        if if_expr.else_steps is None:
            else_steps_ir: List[PipelineStepIR] = []
        else:
            else_steps_ir, _ = self._lower_pipeline_steps_fragment(if_expr.else_steps, 0)

        return IRIf(
            condition=condition_ir,
            then_steps=then_steps_ir,
            else_steps=else_steps_ir,
        )


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

