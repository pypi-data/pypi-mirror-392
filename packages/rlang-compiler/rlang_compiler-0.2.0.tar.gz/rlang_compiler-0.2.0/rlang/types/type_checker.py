"""Type checker for RLang semantic analysis.

Validates function signatures, pipeline wiring, and expression types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from rlang.parser import BinaryOp, Call, Expr, FunctionDecl, Identifier, IfExpr, Literal, Module, PipelineDecl, PipelineStep
from rlang.semantic import ResolutionResult, Symbol, SymbolKind, SymbolTable

from .type_system import RType, rtype_from_type_expr


class TypeCheckError(Exception):
    """Exception raised when type checking fails."""

    def __init__(self, message: str, line: Optional[int] = None, col: Optional[int] = None):
        """Initialize type check error with position information.

        Args:
            message: Error message
            line: Optional line number
            col: Optional column number
        """
        self.message = message
        self.line = line
        self.col = col
        if line is not None and col is not None:
            super().__init__(f"TypeCheckError(line {line}, col {col}): {message}")
        else:
            super().__init__(f"TypeCheckError: {message}")

    def __str__(self) -> str:
        """String representation of the error."""
        if self.line is not None and self.col is not None:
            return f"TypeCheckError(line {self.line}, col {self.col}): {self.message}"
        return f"TypeCheckError: {self.message}"


@dataclass
class TypeCheckResult:
    """Result of type checking.

    Attributes:
        module: The type-checked module AST
        symbols: Symbol table with resolved symbols
        expr_types: Mapping from expression node IDs to inferred types
    """

    module: Module
    symbols: SymbolTable
    expr_types: Dict[int, RType] = field(default_factory=dict)  # Use id(expr) as key


class TypeChecker:
    """Type checker for RLang modules."""

    def __init__(self, resolution: ResolutionResult):
        """Initialize type checker with resolution result.

        Args:
            resolution: Resolution result containing module and symbol table
        """
        self.module = resolution.module
        self.symbols = resolution.global_table
        self.expr_types: Dict[int, RType] = {}  # Use id(expr) as key since Expr nodes aren't hashable
        self.fn_types: Dict[str, tuple[list[RType], Optional[RType]]] = {}
        self._current_if_input_type: Optional[RType] = None  # Context for __value type inference

    def check(self) -> TypeCheckResult:
        """Perform type checking on the module.

        Returns:
            TypeCheckResult with type-checked module and expression types

        Raises:
            TypeCheckError: If type checking fails
        """
        # Type-check all functions (prepare signatures)
        self._check_functions()

        # Type-check all pipelines
        self._check_pipelines()

        return TypeCheckResult(module=self.module, symbols=self.symbols, expr_types=self.expr_types)

    def _check_functions(self) -> None:
        """Type-check all function declarations."""
        for decl in self.module.decls:
            if isinstance(decl, FunctionDecl):
                symbol = self.symbols.lookup(decl.name)
                if symbol is None or symbol.kind != SymbolKind.FUNCTION:
                    continue  # Should not happen if resolver worked

                # Convert parameter types to RType
                param_rtypes: list[RType] = []
                for param in decl.params:
                    if param.type is not None:
                        param_rtype = rtype_from_type_expr(param.type, self.symbols)
                        param_rtypes.append(param_rtype)

                # Convert return type to RType
                ret_rtype: Optional[RType] = None
                if decl.return_type is not None:
                    ret_rtype = rtype_from_type_expr(decl.return_type, self.symbols)

                # Store function signature
                self.fn_types[decl.name] = (param_rtypes, ret_rtype)

    def _check_pipelines(self) -> None:
        """Type-check all pipeline declarations."""
        for decl in self.module.decls:
            if isinstance(decl, PipelineDecl):
                symbol = self.symbols.lookup(decl.name)
                if symbol is None or symbol.kind != SymbolKind.PIPELINE:
                    continue  # Should not happen if resolver worked

                # Determine pipeline-level input/output RTypes
                pipeline_input_rtype: Optional[RType] = None
                if decl.input_type is not None:
                    pipeline_input_rtype = rtype_from_type_expr(decl.input_type, self.symbols)

                pipeline_output_rtype: Optional[RType] = None
                if decl.output_type is not None:
                    pipeline_output_rtype = rtype_from_type_expr(decl.output_type, self.symbols)

                # Type-check the linear chain of steps
                if not decl.steps:
                    # Empty pipeline - just check input/output compatibility
                    if pipeline_input_rtype is not None or pipeline_output_rtype is not None:
                        raise TypeCheckError(
                            "Empty pipeline cannot have input or output types",
                            decl.start_line,
                            decl.start_col,
                        )
                    continue

                # Check each step
                prev_step_return_rtype: Optional[RType] = None

                for i, step in enumerate(decl.steps):
                    # Check if this is an expression-based step (e.g., IfExpr)
                    if step.expr is not None:
                        if isinstance(step.expr, IfExpr):
                            prev_step_return_rtype = self._check_if_expr_step(
                                step.expr, prev_step_return_rtype, i == 0, pipeline_input_rtype
                            )
                        else:
                            raise TypeCheckError(
                                "Only if-expressions are currently supported as expression steps",
                                step.start_line,
                                step.start_col,
                            )
                    else:
                        # Normal function-based step
                        prev_step_return_rtype = self._check_normal_pipeline_step(
                            step, prev_step_return_rtype, i == 0, pipeline_input_rtype
                        )

                # Check final step return matches pipeline output
                if pipeline_output_rtype is not None:
                    if prev_step_return_rtype is None:
                        raise TypeCheckError(
                            f"Pipeline output type {pipeline_output_rtype} specified but last step has no return type",
                            decl.steps[-1].start_line,
                            decl.steps[-1].start_col,
                        )
                    if not self._rtype_equal(pipeline_output_rtype, prev_step_return_rtype):
                        raise TypeCheckError(
                            f"Pipeline output type {pipeline_output_rtype} does not match last step return type {prev_step_return_rtype}",
                            decl.steps[-1].start_line,
                            decl.steps[-1].start_col,
                        )

    def _check_normal_pipeline_step(
        self,
        step: PipelineStep,
        prev_step_return_rtype: Optional[RType],
        is_first_step: bool,
        pipeline_input_rtype: Optional[RType],
    ) -> Optional[RType]:
        """Check a normal function-based pipeline step.

        Args:
            step: Pipeline step to check
            prev_step_return_rtype: Return type of previous step (None for first step)
            is_first_step: Whether this is the first step in the pipeline
            pipeline_input_rtype: Pipeline input type (None if not specified)

        Returns:
            Return type of this step

        Raises:
            TypeCheckError: If type checking fails
        """
        # Ensure step name resolves to a FUNCTION symbol
        step_symbol = self.symbols.lookup(step.name)
        if step_symbol is None:
            raise TypeCheckError(
                f"Unknown step '{step.name}'",
                step.start_line,
                step.start_col,
            )

        if step_symbol.kind != SymbolKind.FUNCTION:
            raise TypeCheckError(
                f"Step '{step.name}' is not a function",
                step.start_line,
                step.start_col,
            )

        # Get function signature
        param_rtypes, ret_rtype = self._get_function_signature(step.name)

        # Pipeline wiring checks
        # If explicit arguments are provided, they replace implicit ones
        has_explicit_args = len(step.args) > 0

        if is_first_step:
            # First step: pipeline input is implicitly passed as first argument if no explicit args
            if not has_explicit_args:
                if pipeline_input_rtype is not None:
                    if not param_rtypes:
                        raise TypeCheckError(
                            f"Pipeline input type {pipeline_input_rtype} provided but first step '{step.name}' has no parameters",
                            step.start_line,
                            step.start_col,
                        )
                    if not self._rtype_equal(pipeline_input_rtype, param_rtypes[0]):
                        raise TypeCheckError(
                            f"Pipeline input type {pipeline_input_rtype} does not match first step '{step.name}' parameter type {param_rtypes[0]}",
                            step.start_line,
                            step.start_col,
                        )
            else:
                # Explicit args provided: they REPLACE pipeline input completely.
                # Therefore pipeline_input_rtype should NOT be checked here.
                pass
        else:
            # Subsequent step: previous step return is implicitly passed as first argument if no explicit args
            if not has_explicit_args:
                if prev_step_return_rtype is None:
                    raise TypeCheckError(
                        f"Step '{step.name}' cannot follow step with no return type",
                        step.start_line,
                        step.start_col,
                    )
                if not param_rtypes:
                    raise TypeCheckError(
                        f"Step '{step.name}' has no parameters but follows step with return type {prev_step_return_rtype}",
                        step.start_line,
                        step.start_col,
                    )
                if not self._rtype_equal(prev_step_return_rtype, param_rtypes[0]):
                    raise TypeCheckError(
                        f"Step '{step.name}' parameter type {param_rtypes[0]} does not match previous step return type {prev_step_return_rtype}",
                        step.start_line,
                        step.start_col,
                    )
            else:
                # Explicit args provided: check that first explicit arg matches previous step return
                if prev_step_return_rtype is None:
                    raise TypeCheckError(
                        f"Step '{step.name}' cannot follow step with no return type",
                        step.start_line,
                        step.start_col,
                    )
                first_arg_type = self._infer_expr_type(step.args[0])
                if not self._rtype_equal(prev_step_return_rtype, first_arg_type):
                    raise TypeCheckError(
                        f"Step '{step.name}' first argument type {first_arg_type} does not match previous step return type {prev_step_return_rtype}",
                        step.args[0].start_line,
                        step.args[0].start_col,
                    )

        # Check arity:
        # - If no explicit args: allow 0 (implicit first arg will be used)
        # - If explicit args: must provide all parameters explicitly
        if has_explicit_args:
            # With explicit args, must provide all parameters
            if len(step.args) != len(param_rtypes):
                raise TypeCheckError(
                    f"Step '{step.name}' expects {len(param_rtypes)} arguments, got {len(step.args)}",
                    step.start_line,
                    step.start_col,
                )
        else:
            # Without explicit args, implicit first arg counts as one argument
            # So we need at least 1 parameter total, and 0 explicit args is fine
            if len(param_rtypes) == 0:
                raise TypeCheckError(
                    f"Step '{step.name}' has no parameters but no explicit arguments provided",
                    step.start_line,
                    step.start_col,
                )

        # Check explicit argument types (only if explicit args provided)
        if has_explicit_args:
            for arg_idx, (arg_expr, param_rtype) in enumerate(zip(step.args, param_rtypes)):
                arg_rtype = self._infer_expr_type(arg_expr)
                if not self._rtype_equal(arg_rtype, param_rtype):
                    raise TypeCheckError(
                        f"Step '{step.name}' argument {arg_idx + 1}: expected {param_rtype}, got {arg_rtype}",
                        arg_expr.start_line,
                        arg_expr.start_col,
                    )

        return ret_rtype

    def _check_pipeline_steps_fragment(
        self, steps: list[PipelineStep], input_type: RType
    ) -> Optional[RType]:
        """Check a fragment of pipeline steps (e.g., inside an if branch).

        Args:
            steps: List of pipeline steps to check
            input_type: Input type for the fragment

        Returns:
            Output type of the fragment (None if no steps or last step has no return)

        Raises:
            TypeCheckError: If type checking fails
        """
        if not steps:
            return input_type  # Empty fragment: identity

        current_type: Optional[RType] = input_type

        for i, step in enumerate(steps):
            if step.expr is not None:
                # Expression-based step (e.g., nested if)
                if isinstance(step.expr, IfExpr):
                    # For fragments, we always have an input type, so treat as non-first step
                    current_type = self._check_if_expr_step(
                        step.expr, current_type, False, None
                    )
                else:
                    raise TypeCheckError(
                        "Only if-expressions are currently supported as expression steps",
                        step.start_line,
                        step.start_col,
                    )
            else:
                # Normal function-based step - treat as non-first step in fragment
                current_type = self._check_normal_pipeline_step(
                    step, current_type, False, None
                )

        return current_type

    def _check_if_expr_step(
        self,
        if_expr: IfExpr,
        prev_step_return_rtype: Optional[RType],
        is_first_step: bool,
        pipeline_input_rtype: Optional[RType],
    ) -> Optional[RType]:
        """Check an if expression used as a pipeline step.

        Args:
            if_expr: If expression to check
            prev_step_return_rtype: Return type of previous step (None for first step)
            is_first_step: Whether this is the first step in the pipeline
            pipeline_input_rtype: Pipeline input type (None if not specified)

        Returns:
            Output type of the if expression (same for both branches)

        Raises:
            TypeCheckError: If type checking fails
        """
        # Determine input type for the if branches
        if is_first_step:
            input_type = pipeline_input_rtype
        else:
            input_type = prev_step_return_rtype

        if input_type is None:
            raise TypeCheckError(
                "If expression requires an input type from pipeline or previous step",
                if_expr.start_line,
                if_expr.start_col,
            )

        # Store input_type in a context for __value type inference
        # We'll use a temporary attribute to pass this context
        self._current_if_input_type = input_type

        # 1. Type-check the condition
        cond_type = self._infer_expr_type(if_expr.condition)
        
        # Clear the context
        self._current_if_input_type = None
        if not self._is_bool_type(cond_type):
            raise TypeCheckError(
                f"if condition must be Bool, got {cond_type}",
                if_expr.condition.start_line,
                if_expr.condition.start_col,
            )

        # 2. Type-check then branch as a pipeline fragment
        then_type = self._check_pipeline_steps_fragment(if_expr.then_steps, input_type)

        # 3. Type-check else branch (if any)
        if if_expr.else_steps is None:
            # Implicit identity: else branch passes through input unchanged
            else_type = input_type
        else:
            else_type = self._check_pipeline_steps_fragment(if_expr.else_steps, input_type)

        # 4. Enforce same output type
        if then_type is None or else_type is None:
            raise TypeCheckError(
                "if branches must have a return type",
                if_expr.start_line,
                if_expr.start_col,
            )

        if not self._rtype_equal(then_type, else_type):
            raise TypeCheckError(
                f"if branches must have the same output type: then={then_type}, else={else_type}",
                if_expr.start_line,
                if_expr.start_col,
            )

        # 5. Record final type as type of the IfExpr (for completeness)
        self.expr_types[id(if_expr)] = then_type

        return then_type

    def _get_function_signature(self, name: str) -> tuple[list[RType], Optional[RType]]:
        """Get function signature as RTypes.

        Args:
            name: Function name

        Returns:
            Tuple of (parameter types list, return type)

        Raises:
            TypeCheckError: If function is missing or not a FUNCTION symbol
        """
        symbol = self.symbols.lookup(name)
        if symbol is None:
            raise TypeCheckError(f"Function '{name}' not found")

        if symbol.kind != SymbolKind.FUNCTION:
            raise TypeCheckError(f"'{name}' is not a function")

        # Check if we already computed the signature
        if name in self.fn_types:
            return self.fn_types[name]

        # Otherwise, compute it from the AST node
        if not isinstance(symbol.node, FunctionDecl):
            raise TypeCheckError(f"Function '{name}' has invalid AST node")

        fn_decl = symbol.node
        param_rtypes: list[RType] = []
        for param in fn_decl.params:
            if param.type is not None:
                param_rtype = rtype_from_type_expr(param.type, self.symbols)
                param_rtypes.append(param_rtype)

        ret_rtype: Optional[RType] = None
        if fn_decl.return_type is not None:
            ret_rtype = rtype_from_type_expr(fn_decl.return_type, self.symbols)

        signature = (param_rtypes, ret_rtype)
        self.fn_types[name] = signature
        return signature

    def _infer_expr_type(self, expr: Expr) -> RType:
        """Infer the type of an expression.

        Args:
            expr: Expression to infer type for

        Returns:
            Inferred RType

        Raises:
            TypeCheckError: If type inference fails
        """
        # Check cache first (use id() since Expr nodes aren't hashable)
        expr_id = id(expr)
        if expr_id in self.expr_types:
            return self.expr_types[expr_id]

        inferred_type: RType

        if isinstance(expr, Literal):
            # Infer type from literal value
            value = expr.value
            if isinstance(value, int):
                inferred_type = RType("Int")
            elif isinstance(value, float):
                inferred_type = RType("Float")
            elif isinstance(value, str):
                inferred_type = RType("String")
            elif isinstance(value, bool):
                inferred_type = RType("Bool")
            elif value is None:
                inferred_type = RType("Unit")
            else:
                raise TypeCheckError(
                    f"Unsupported literal type: {type(value).__name__}",
                    expr.start_line,
                    expr.start_col,
                )

        elif isinstance(expr, Identifier):
            # Special identifier __value refers to current pipeline value
            if expr.name == "__value":
                # Type-checking __value: infer its type from context
                # If we're in an if condition context, use the stored input type
                if hasattr(self, '_current_if_input_type') and self._current_if_input_type is not None:
                    inferred_type = self._current_if_input_type
                else:
                    # Fallback: assume Int (will be validated in context)
                    inferred_type = RType("Int")
            else:
                # For now, only __value is supported as an identifier in expressions
                raise TypeCheckError(
                    f"Unbound identifier '{expr.name}' in expression. Only '__value' is supported to reference the current pipeline value.",
                    expr.start_line,
                    expr.start_col,
                )

        elif isinstance(expr, Call):
            # Function call: type is the return type of the function
            if not isinstance(expr.func, Identifier):
                raise TypeCheckError(
                    "Function call must have identifier as function",
                    expr.start_line,
                    expr.start_col,
                )

            func_name = expr.func.name
            param_rtypes, ret_rtype = self._get_function_signature(func_name)

            # Check argument count
            if len(expr.args) != len(param_rtypes):
                raise TypeCheckError(
                    f"Function '{func_name}' expects {len(param_rtypes)} arguments, got {len(expr.args)}",
                    expr.start_line,
                    expr.start_col,
                )

            # Check argument types
            for arg_idx, (arg_expr, param_rtype) in enumerate(zip(expr.args, param_rtypes)):
                arg_rtype = self._infer_expr_type(arg_expr)
                if not self._rtype_equal(arg_rtype, param_rtype):
                    raise TypeCheckError(
                        f"Function '{func_name}' argument {arg_idx + 1}: expected {param_rtype}, got {arg_rtype}",
                        arg_expr.start_line,
                        arg_expr.start_col,
                    )

            # Return type must exist
            if ret_rtype is None:
                raise TypeCheckError(
                    f"Function '{func_name}' used as expression has no return type",
                    expr.start_line,
                    expr.start_col,
                )

            inferred_type = ret_rtype

        elif isinstance(expr, BinaryOp):
            # Binary operations: infer types of operands and determine result type
            left_type = self._infer_expr_type(expr.left)
            right_type = self._infer_expr_type(expr.right)

            # Comparison operators return Bool
            if expr.op in (">", "<", ">=", "<=", "==", "!="):
                inferred_type = RType("Bool")
            # Arithmetic operators: promote to Float if either operand is Float
            elif expr.op in ("+", "-", "*", "/"):
                if left_type.name == "Float" or right_type.name == "Float":
                    inferred_type = RType("Float")
                elif left_type.name == "Int" and right_type.name == "Int":
                    inferred_type = RType("Int")
                else:
                    raise TypeCheckError(
                        f"Binary operator '{expr.op}' not supported for types {left_type} and {right_type}",
                        expr.start_line,
                        expr.start_col,
                    )
            else:
                raise TypeCheckError(
                    f"Unknown binary operator: {expr.op}",
                    expr.start_line,
                    expr.start_col,
                )

        elif isinstance(expr, IfExpr):
            # IfExpr is only valid in pipeline bodies, not as a standalone expression
            raise TypeCheckError(
                "IfExpr is only valid in pipeline bodies, not as a standalone expression",
                expr.start_line,
                expr.start_col,
            )

        else:
            raise TypeCheckError(
                f"Expression type inference not implemented for {type(expr).__name__}",
                expr.start_line,
                expr.start_col,
            )

        # Cache and return (use id() since Expr nodes aren't hashable)
        self.expr_types[expr_id] = inferred_type
        return inferred_type

    def _rtype_equal(self, a: RType, b: RType) -> bool:
        """Check if two RTypes are equal.

        Args:
            a: First type
            b: Second type

        Returns:
            True if types are equal, False otherwise
        """
        if a.name != b.name:
            return False
        if len(a.args) != len(b.args):
            return False
        return all(self._rtype_equal(arg_a, arg_b) for arg_a, arg_b in zip(a.args, b.args))

    def _is_bool_type(self, rtype: RType) -> bool:
        """Check if an RType is Bool.

        Args:
            rtype: Type to check

        Returns:
            True if type is Bool, False otherwise
        """
        return rtype.name == "Bool" and len(rtype.args) == 0


def type_check(resolution: ResolutionResult) -> TypeCheckResult:
    """Type-check a resolved module.

    Args:
        resolution: Resolution result containing module and symbol table

    Returns:
        TypeCheckResult with type-checked module and expression types

    Raises:
        TypeCheckError: If type checking fails
    """
    checker = TypeChecker(resolution)
    return checker.check()


__all__ = [
    "TypeCheckError",
    "TypeCheckResult",
    "TypeChecker",
    "type_check",
]

