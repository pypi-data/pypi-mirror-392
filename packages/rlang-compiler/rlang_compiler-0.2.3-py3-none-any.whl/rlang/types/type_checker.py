"""Type checker for RLang semantic analysis.

Validates function signatures, pipeline wiring, and expression types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from rlang.parser import BinaryOp, BooleanAnd, BooleanNot, BooleanOr, Call, Case, Expr, FieldAccess, ForExpr, FunctionDecl, Identifier, IfExpr, ListExpr, ListPattern, Literal, LiteralPattern, MatchExpr, Module, PipelineDecl, PipelineStep, Pattern, RecordExpr, RecordPattern, VarPattern, WildcardPattern
from rlang.semantic import ResolutionResult, Symbol, SymbolKind, SymbolTable

from .type_system import RType, RecordRType, rtype_from_type_expr


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
                    # Set context for __value type inference
                    # For first step, use pipeline input; for others, use previous step return
                    if i == 0:
                        self._current_if_input_type = pipeline_input_rtype
                    else:
                        self._current_if_input_type = prev_step_return_rtype
                    
                    # Check if this is an expression-based step (e.g., IfExpr, ForExpr, MatchExpr, RecordExpr)
                    if step.expr is not None:
                        if isinstance(step.expr, IfExpr):
                            prev_step_return_rtype = self._check_if_expr_step(
                                step.expr, prev_step_return_rtype, i == 0, pipeline_input_rtype
                            )
                        elif isinstance(step.expr, ForExpr):
                            prev_step_return_rtype = self._check_for_expr_step(
                                step.expr, prev_step_return_rtype, i == 0, pipeline_input_rtype
                            )
                        elif isinstance(step.expr, MatchExpr):
                            prev_step_return_rtype = self._check_match_expr_step(
                                step.expr, prev_step_return_rtype, i == 0, pipeline_input_rtype
                            )
                        elif isinstance(step.expr, (RecordExpr, FieldAccess, ListExpr)):
                            # Record literal, field access, or list literal as pipeline step
                            expr_type = self._infer_expr_type(step.expr)
                            prev_step_return_rtype = expr_type
                        else:
                            # Try to infer type for other expression types
                            expr_type = self._infer_expr_type(step.expr)
                            prev_step_return_rtype = expr_type
                    else:
                        # Normal function-based step
                        prev_step_return_rtype = self._check_normal_pipeline_step(
                            step, prev_step_return_rtype, i == 0, pipeline_input_rtype
                        )
                    
                    # Clear context after step
                    self._current_if_input_type = None

                # Check final step return matches pipeline output
                if pipeline_output_rtype is not None:
                    if prev_step_return_rtype is None:
                        raise TypeCheckError(
                            f"Pipeline output type {pipeline_output_rtype} specified but last step has no return type",
                            decl.steps[-1].start_line,
                            decl.steps[-1].start_col,
                        )
                    
                    # Special handling: if last step is a RecordExpr and output is a named record type,
                    # validate field-by-field matching
                    if isinstance(decl.steps[-1].expr, RecordExpr):
                        self._check_record_literal_matches_type(
                            decl.steps[-1].expr, pipeline_output_rtype, decl.steps[-1].start_line, decl.steps[-1].start_col
                        )
                    # For ListExpr, check element type matches
                    elif isinstance(decl.steps[-1].expr, ListExpr):
                        if pipeline_output_rtype.name != "List":
                            raise TypeCheckError(
                                f"Pipeline output type is {pipeline_output_rtype}, but last step returns List",
                                decl.steps[-1].start_line,
                                decl.steps[-1].start_col,
                            )
                        if len(pipeline_output_rtype.args) != 1:
                            raise TypeCheckError(
                                f"Expected List[T] output type, got {pipeline_output_rtype}",
                                decl.steps[-1].start_line,
                                decl.steps[-1].start_col,
                            )
                        if prev_step_return_rtype.name != "List" or len(prev_step_return_rtype.args) != 1:
                            raise TypeCheckError(
                                f"Last step returns {prev_step_return_rtype}, expected List[T]",
                                decl.steps[-1].start_line,
                                decl.steps[-1].start_col,
                            )
                        if not self._rtype_equal(pipeline_output_rtype.args[0], prev_step_return_rtype.args[0]):
                            raise TypeCheckError(
                                f"List element type mismatch: expected {pipeline_output_rtype.args[0]}, got {prev_step_return_rtype.args[0]}",
                                decl.steps[-1].start_line,
                                decl.steps[-1].start_col,
                            )
                    elif not self._rtype_equal(pipeline_output_rtype, prev_step_return_rtype):
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
                # Expression-based step (e.g., nested if, match, record/list expressions)
                if isinstance(step.expr, IfExpr):
                    # For fragments, we always have an input type, so treat as non-first step
                    current_type = self._check_if_expr_step(
                        step.expr, current_type, False, None
                    )
                elif isinstance(step.expr, MatchExpr):
                    # For fragments, we always have an input type, so treat as non-first step
                    current_type = self._check_match_expr_step(
                        step.expr, current_type, False, None
                    )
                elif isinstance(step.expr, (RecordExpr, FieldAccess, ListExpr)):
                    # Record/list/field access expressions: infer type
                    expr_type = self._infer_expr_type(step.expr)
                    current_type = expr_type
                else:
                    raise TypeCheckError(
                        f"Unsupported expression type in fragment: {type(step.expr).__name__}",
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

    def _check_for_expr_step(
        self,
        for_expr: ForExpr,
        prev_step_return_rtype: Optional[RType],
        is_first_step: bool,
        pipeline_input_rtype: Optional[RType],
    ) -> Optional[RType]:
        """Check a for loop expression used as a pipeline step.

        Args:
            for_expr: For expression to check
            prev_step_return_rtype: Return type of previous step (None for first step)
            is_first_step: Whether this is the first step in the pipeline
            pipeline_input_rtype: Pipeline input type (None if not specified)

        Returns:
            Output type of the for loop body (same as body type after N iterations)

        Raises:
            TypeCheckError: If type checking fails
        """
        # Determine input type for the loop body
        if is_first_step:
            input_type = pipeline_input_rtype
        else:
            input_type = prev_step_return_rtype

        if input_type is None:
            raise TypeCheckError(
                "For loop requires an input type from pipeline or previous step",
                for_expr.start_line,
                for_expr.start_col,
            )

        # Validate bounds (optional sanity check)
        if for_expr.start < 0 or for_expr.end < 0:
            raise TypeCheckError(
                f"For loop bounds must be non-negative: start={for_expr.start}, end={for_expr.end}",
                for_expr.start_line,
                for_expr.start_col,
            )

        # Type-check the body as a pipeline fragment
        # Since loops are unrolled, we just typecheck the body once
        # The output type after N iterations is the same as after 1 iteration
        body_type = self._check_pipeline_steps_fragment(for_expr.body, input_type)

        if body_type is None:
            raise TypeCheckError(
                "For loop body must have a return type",
                for_expr.start_line,
                for_expr.start_col,
            )

        # Record final type as type of the ForExpr (for completeness)
        self.expr_types[id(for_expr)] = body_type

        return body_type

    def _check_match_expr_step(
        self,
        match_expr: MatchExpr,
        prev_step_return_rtype: Optional[RType],
        is_first_step: bool,
        pipeline_input_rtype: Optional[RType],
    ) -> Optional[RType]:
        """Check a match expression used as a pipeline step.

        Args:
            match_expr: Match expression to check
            prev_step_return_rtype: Return type of previous step (None for first step)
            is_first_step: Whether this is the first step in the pipeline
            pipeline_input_rtype: Pipeline input type (None if not specified)

        Returns:
            Output type of the match expression (same for all cases)

        Raises:
            TypeCheckError: If type checking fails
        """
        # Determine input type for the match branches
        if is_first_step:
            input_type = pipeline_input_rtype
        else:
            input_type = prev_step_return_rtype

        if input_type is None:
            raise TypeCheckError(
                "Match expression requires an input type from pipeline or previous step",
                match_expr.start_line,
                match_expr.start_col,
            )

        # Store input_type in a context for __value type inference
        self._current_if_input_type = input_type

        # 1. Type-check the scrutinee (value expression)
        value_type = self._infer_expr_type(match_expr.value)
        
        # Clear the context
        self._current_if_input_type = None

        # 2. Validate all patterns and collect bindings
        case_types: list[Optional[RType]] = []
        for case in match_expr.cases:
            # Validate pattern and get bindings
            bindings = self._validate_pattern(case.pattern, value_type)
            
            # Type-check case body with bindings in environment
            # For now, we'll type-check the body steps with the input_type
            # The bindings would be used in a more sophisticated implementation
            case_type = self._check_pipeline_steps_fragment(case.body, input_type)
            case_types.append(case_type)

        # 3. Enforce same output type for all cases
        if not case_types:
            raise TypeCheckError(
                "Match expression must have at least one case",
                match_expr.start_line,
                match_expr.start_col,
            )

        first_case_type = case_types[0]
        for i, case_type in enumerate(case_types[1:], 1):
            if first_case_type is None or case_type is None:
                raise TypeCheckError(
                    "Match cases must have a return type",
                    match_expr.cases[i].start_line,
                    match_expr.cases[i].start_col,
                )
            if not self._rtype_equal(first_case_type, case_type):
                raise TypeCheckError(
                    f"All match cases must return the same type: case 0={first_case_type}, case {i}={case_type}",
                    match_expr.cases[i].start_line,
                    match_expr.cases[i].start_col,
                )

        # 4. Record final type as type of the MatchExpr
        self.expr_types[id(match_expr)] = first_case_type

        return first_case_type

    def _validate_pattern(self, pattern: Pattern, value_type: RType) -> Dict[str, RType]:
        """Validate a pattern against a value type and return variable bindings.

        Args:
            pattern: Pattern to validate
            value_type: Type of the value being matched

        Returns:
            Dictionary mapping variable names to their types (bindings)

        Raises:
            TypeCheckError: If pattern is incompatible with value_type
        """
        bindings: Dict[str, RType] = {}

        if isinstance(pattern, WildcardPattern):
            # Wildcard always matches, no bindings
            return bindings

        elif isinstance(pattern, VarPattern):
            # Variable pattern binds the entire value
            bindings[pattern.name] = value_type
            return bindings

        elif isinstance(pattern, LiteralPattern):
            # Literal pattern must match the literal's type
            literal_type = self._infer_literal_type(pattern.value)
            if not self._rtype_equal(literal_type, value_type):
                raise TypeCheckError(
                    f"Literal pattern type {literal_type} does not match value type {value_type}",
                    pattern.start_line,
                    pattern.start_col,
                )
            return bindings

        elif isinstance(pattern, RecordPattern):
            # Record pattern requires value_type to be a RecordRType
            if not isinstance(value_type, RecordRType):
                raise TypeCheckError(
                    f"Record pattern requires Record type, got {value_type}",
                    pattern.start_line,
                    pattern.start_col,
                )
            
            # Validate each field pattern (iterate in sorted order for determinism)
            # Note: pattern.fields preserves source order, but we validate consistently
            sorted_field_names = sorted(pattern.fields.keys())
            for field_name in sorted_field_names:
                field_pattern = pattern.fields[field_name]
                if field_name not in value_type.fields:
                    # Field absence is allowed (treated as false condition at runtime)
                    # This allows patterns to match records that don't have all fields
                    continue
                field_type = value_type.fields[field_name]
                # Recursively validate subpattern
                sub_bindings = self._validate_pattern(field_pattern, field_type)
                bindings.update(sub_bindings)
            
            return bindings

        elif isinstance(pattern, ListPattern):
            # List pattern requires value_type to be List[T]
            if value_type.name != "List" or len(value_type.args) != 1:
                raise TypeCheckError(
                    f"List pattern requires List type, got {value_type}",
                    pattern.start_line,
                    pattern.start_col,
                )
            
            element_type = value_type.args[0]
            
            # Validate each element pattern
            for elem_pattern in pattern.elements:
                sub_bindings = self._validate_pattern(elem_pattern, element_type)
                bindings.update(sub_bindings)
            
            return bindings

        else:
            raise TypeCheckError(
                f"Unknown pattern type: {type(pattern).__name__}",
                pattern.start_line,
                pattern.start_col,
            )

    def _infer_literal_type(self, value: object) -> RType:
        """Infer the type of a literal value.

        Args:
            value: Literal value (int, str, bool, None)

        Returns:
            RType for the literal
        """
        if isinstance(value, int):
            return RType(name="Int")
        elif isinstance(value, float):
            return RType(name="Float")
        elif isinstance(value, str):
            return RType(name="String")
        elif isinstance(value, bool):
            return RType(name="Bool")
        elif value is None:
            return RType(name="Null")
        else:
            raise TypeCheckError(f"Unknown literal type: {type(value).__name__}")

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

        elif isinstance(expr, BooleanNot):
            # Boolean NOT: operand must be Bool, result is Bool
            operand_type = self._infer_expr_type(expr.operand)
            if not self._is_bool_type(operand_type):
                raise TypeCheckError(
                    f"Boolean NOT operator '!' requires Bool operand, got {operand_type}",
                    expr.operand.start_line,
                    expr.operand.start_col,
                )
            inferred_type = RType("Bool")

        elif isinstance(expr, BooleanAnd):
            # Boolean AND: both operands must be Bool, result is Bool
            left_type = self._infer_expr_type(expr.left)
            right_type = self._infer_expr_type(expr.right)
            
            if not self._is_bool_type(left_type):
                raise TypeCheckError(
                    f"Boolean AND operator '&&' requires Bool operands, got {left_type} on left",
                    expr.left.start_line,
                    expr.left.start_col,
                )
            if not self._is_bool_type(right_type):
                raise TypeCheckError(
                    f"Boolean AND operator '&&' requires Bool operands, got {right_type} on right",
                    expr.right.start_line,
                    expr.right.start_col,
                )
            inferred_type = RType("Bool")

        elif isinstance(expr, BooleanOr):
            # Boolean OR: both operands must be Bool, result is Bool
            left_type = self._infer_expr_type(expr.left)
            right_type = self._infer_expr_type(expr.right)
            
            if not self._is_bool_type(left_type):
                raise TypeCheckError(
                    f"Boolean OR operator '||' requires Bool operands, got {left_type} on left",
                    expr.left.start_line,
                    expr.left.start_col,
                )
            if not self._is_bool_type(right_type):
                raise TypeCheckError(
                    f"Boolean OR operator '||' requires Bool operands, got {right_type} on right",
                    expr.right.start_line,
                    expr.right.start_col,
                )
            inferred_type = RType("Bool")

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

        elif isinstance(expr, RecordExpr):
            # Record literal: typecheck all fields and construct RecordRType
            field_types: Dict[str, RType] = {}
            for field_name, field_expr in expr.fields.items():
                field_type = self._infer_expr_type(field_expr)
                field_types[field_name] = field_type
            inferred_type = RecordRType(name="Record", fields=field_types)

        elif isinstance(expr, FieldAccess):
            # Field access: typecheck record expression, ensure it's a record, return field type
            record_type = self._infer_expr_type(expr.record)
            
            if not isinstance(record_type, RecordRType):
                raise TypeCheckError(
                    f"Attempted field access on non-record type {record_type}",
                    expr.start_line,
                    expr.start_col,
                )
            
            if expr.field not in record_type.fields:
                raise TypeCheckError(
                    f"Unknown field '{expr.field}' in record type {record_type}",
                    expr.start_line,
                    expr.start_col,
                )
            
            inferred_type = record_type.fields[expr.field]

        elif isinstance(expr, ListExpr):
            # List literal: typecheck all elements and infer common element type
            if not expr.elements:
                # Empty list: cannot infer element type, require explicit type annotation
                raise TypeCheckError(
                    "Cannot infer type of empty list literal; explicit type annotation required",
                    expr.start_line,
                    expr.start_col,
                )
            
            # Infer type of first element
            first_elem_type = self._infer_expr_type(expr.elements[0])
            
            # Check that all elements have the same type
            for i, elem in enumerate(expr.elements[1:], start=1):
                elem_type = self._infer_expr_type(elem)
                if not self._rtype_equal(elem_type, first_elem_type):
                    raise TypeCheckError(
                        f"List element {i + 1} has type {elem_type}, expected {first_elem_type}",
                        elem.start_line,
                        elem.start_col,
                    )
            
            # Return List[element_type]
            inferred_type = RType(name="List", args=(first_elem_type,))

        elif isinstance(expr, IfExpr):
            # IfExpr is only valid in pipeline bodies, not as a standalone expression
            raise TypeCheckError(
                "IfExpr is only valid in pipeline bodies, not as a standalone expression",
                expr.start_line,
                expr.start_col,
            )

        elif isinstance(expr, MatchExpr):
            # MatchExpr as standalone expression: type-check similar to IF
            # 1. Type-check scrutinee
            value_type = self._infer_expr_type(expr.value)
            
            # 2. Validate patterns and type-check case bodies
            case_types: list[Optional[RType]] = []
            for case in expr.cases:
                # Validate pattern and get bindings
                bindings = self._validate_pattern(case.pattern, value_type)
                
                # Type-check case body as expression steps
                # For standalone MatchExpr, case bodies operate on the current environment
                # Pattern bindings are available as additional locals
                if not case.body:
                    raise TypeCheckError(
                        "Match case body must have at least one step",
                        case.start_line,
                        case.start_col,
                    )
                
                # Type-check body steps (they operate on current environment, not pipeline input)
                # Since this is a standalone expression, we don't have a pipeline input type
                # The body steps should be expressions that produce values
                # For now, treat as if they're in a fragment with no input type
                case_type = self._check_pipeline_steps_fragment(case.body, None)
                if case_type is None:
                    # If no steps return a value, infer from last step
                    if case.body:
                        # Try to infer type from last step if it's an expression
                        last_step = case.body[-1]
                        if last_step.expr is not None:
                            case_type = self._infer_expr_type(last_step.expr)
                        else:
                            raise TypeCheckError(
                                "Match case body must return a value",
                                case.start_line,
                                case.start_col,
                            )
                case_types.append(case_type)
            
            # 3. Enforce same output type
            if not case_types:
                raise TypeCheckError(
                    "Match expression must have at least one case",
                    expr.start_line,
                    expr.start_col,
                )
            
            first_case_type = case_types[0]
            for i, case_type in enumerate(case_types[1:], 1):
                if first_case_type is None or case_type is None:
                    raise TypeCheckError(
                        "Match cases must have a return type",
                        expr.cases[i].start_line,
                        expr.cases[i].start_col,
                    )
                if not self._rtype_equal(first_case_type, case_type):
                    raise TypeCheckError(
                        f"All match cases must return the same type: case 0={first_case_type}, case {i}={case_type}",
                        expr.cases[i].start_line,
                        expr.cases[i].start_col,
                    )
            
            inferred_type = first_case_type

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
        # Handle RecordRType specially
        if isinstance(a, RecordRType) and isinstance(b, RecordRType):
            # Structural equality: same field names and types
            if set(a.fields.keys()) != set(b.fields.keys()):
                return False
            return all(self._rtype_equal(a.fields[field], b.fields[field]) for field in a.fields.keys())
        
        # If one is RecordRType and the other isn't, they're not equal
        if isinstance(a, RecordRType) or isinstance(b, RecordRType):
            return False
        
        # Standard RType equality
        if a.name != b.name:
            return False
        if len(a.args) != len(b.args):
            return False
        return all(self._rtype_equal(arg_a, arg_b) for arg_a, arg_b in zip(a.args, b.args))

    def _check_record_literal_matches_type(
        self, record_expr: RecordExpr, expected_type: RType, line: int, col: int
    ) -> None:
        """Check that a record literal matches an expected record type.

        Args:
            record_expr: Record literal expression
            expected_type: Expected record type (may be RecordRType or named type alias)
            line: Line number for error reporting
            col: Column number for error reporting

        Raises:
            TypeCheckError: If record literal doesn't match expected type
        """
        # Resolve expected type to RecordRType if it's a type alias
        expected_record_type = expected_type
        if isinstance(expected_type, RType) and not isinstance(expected_type, RecordRType):
            # Check if it's a type alias that resolves to a record
            symbol = self.symbols.lookup(expected_type.name)
            if symbol is not None and symbol.kind == SymbolKind.TYPE and symbol.type_expr is not None:
                resolved = rtype_from_type_expr(symbol.type_expr, self.symbols)
                if isinstance(resolved, RecordRType):
                    expected_record_type = resolved
                else:
                    raise TypeCheckError(
                        f"Expected record type {expected_type}, but got non-record type",
                        line,
                        col,
                    )
            else:
                raise TypeCheckError(
                    f"Expected record type {expected_type}, but got non-record type",
                    line,
                    col,
                )
        
        if not isinstance(expected_record_type, RecordRType):
            raise TypeCheckError(
                f"Expected record type {expected_type}, but got non-record type",
                line,
                col,
            )
        
        # Check all expected fields exist
        for field_name, expected_field_type in expected_record_type.fields.items():
            if field_name not in record_expr.fields:
                raise TypeCheckError(
                    f"Missing field '{field_name}' in record literal",
                    record_expr.start_line,
                    record_expr.start_col,
                )
            
            # Check field type matches
            actual_field_type = self._infer_expr_type(record_expr.fields[field_name])
            if not self._rtype_equal(expected_field_type, actual_field_type):
                raise TypeCheckError(
                    f"Type mismatch in field '{field_name}': expected {expected_field_type}, got {actual_field_type}",
                    record_expr.fields[field_name].start_line,
                    record_expr.fields[field_name].start_col,
                )
        
        # Check no extra fields
        for field_name in record_expr.fields.keys():
            if field_name not in expected_record_type.fields:
                raise TypeCheckError(
                    f"Unexpected field '{field_name}' in record literal",
                    record_expr.fields[field_name].start_line,
                    record_expr.fields[field_name].start_col,
                )

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

