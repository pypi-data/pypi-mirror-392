"""Symbol resolution for RLang semantic analysis.

Builds symbol tables and validates type references.
"""

from __future__ import annotations

from dataclasses import dataclass

from rlang.parser import (
    FunctionDecl,
    GenericType,
    Module,
    Param,
    PipelineDecl,
    PipelineStep,
    RecordType,
    SimpleType,
    TypeAlias,
    TypeExpr,
)

from .symbols import PRIMITIVE_TYPES, Symbol, SymbolKind, SymbolTable, is_primitive_type


class ResolutionError(Exception):
    """Exception raised when symbol resolution fails."""

    def __init__(self, message: str, line: int | None = None, col: int | None = None):
        """Initialize resolution error with position information.

        Args:
            message: Error message
            line: Optional line number
            col: Optional column number
        """
        self.message = message
        self.line = line
        self.col = col
        if line is not None and col is not None:
            super().__init__(f"ResolutionError(line {line}, col {col}): {message}")
        else:
            super().__init__(f"ResolutionError: {message}")

    def __str__(self) -> str:
        """String representation of the error."""
        if self.line is not None and self.col is not None:
            return f"ResolutionError(line {self.line}, col {self.col}): {self.message}"
        return f"ResolutionError: {self.message}"


@dataclass
class ResolutionResult:
    """Result of symbol resolution.

    Attributes:
        module: The resolved module AST
        global_table: Global symbol table with all symbols
    """

    module: Module
    global_table: SymbolTable


class Resolver:
    """Resolves symbols and validates type references in a module."""

    def __init__(self, module: Module):
        """Initialize resolver with a module.

        Args:
            module: Module AST to resolve
        """
        self.module = module
        self.global_table = SymbolTable(parent=None)
        self._preload_primitive_types()

    def _preload_primitive_types(self) -> None:
        """Pre-load primitive type symbols into the global table."""
        for name in PRIMITIVE_TYPES:
            # Create a synthetic SimpleType node for primitives
            synthetic_type = SimpleType(name=name, start_line=0, start_col=0, end_line=0, end_col=0)
            symbol = Symbol(
                name=name,
                kind=SymbolKind.TYPE,
                node=synthetic_type,
                type_expr=synthetic_type,
            )
            self.global_table.define(symbol)

    def resolve(self) -> ResolutionResult:
        """Resolve all symbols in the module.

        Returns:
            ResolutionResult with resolved module and symbol table

        Raises:
            ResolutionError: If resolution fails
        """
        # First pass: register all type alias names
        self._register_type_aliases()

        # Second pass: resolve type alias targets
        self._resolve_type_alias_targets()

        # Third pass: register functions and pipelines
        self._register_functions_and_pipelines()

        # Fourth pass: validate all referenced types in functions and pipelines
        self._validate_functions()
        self._validate_pipelines()

        return ResolutionResult(module=self.module, global_table=self.global_table)

    def _register_type_aliases(self) -> None:
        """Register all type alias names in the symbol table."""
        for decl in self.module.decls:
            if isinstance(decl, TypeAlias):
                symbol = Symbol(
                    name=decl.name,
                    kind=SymbolKind.TYPE,
                    node=decl,
                    type_expr=None,  # Will be resolved in next pass
                )
                try:
                    self.global_table.define(symbol)
                except ValueError as e:
                    raise ResolutionError(
                        f"Duplicate type alias '{decl.name}'",
                        decl.start_line,
                        decl.start_col,
                    ) from e

    def _resolve_type_alias_targets(self) -> None:
        """Resolve type alias targets and validate they exist."""
        for decl in self.module.decls:
            if isinstance(decl, TypeAlias):
                # Look up the symbol we just created
                symbol = self.global_table.lookup(decl.name)
                if symbol is None:
                    continue  # Should not happen, but be safe

                # Resolve the target type expression
                resolved_target = self._resolve_type_expr(decl.target)
                symbol.type_expr = resolved_target

    def _register_functions_and_pipelines(self) -> None:
        """Register all function and pipeline declarations."""
        for decl in self.module.decls:
            if isinstance(decl, FunctionDecl):
                symbol = Symbol(
                    name=decl.name,
                    kind=SymbolKind.FUNCTION,
                    node=decl,
                    params=None,  # Will be populated in validation pass
                    return_type=None,  # Will be populated in validation pass
                )
                try:
                    self.global_table.define(symbol)
                except ValueError as e:
                    raise ResolutionError(
                        f"Duplicate function '{decl.name}'",
                        decl.start_line,
                        decl.start_col,
                    ) from e

            elif isinstance(decl, PipelineDecl):
                symbol = Symbol(
                    name=decl.name,
                    kind=SymbolKind.PIPELINE,
                    node=decl,
                    input_type=None,  # Will be populated in validation pass
                    output_type=None,  # Will be populated in validation pass
                )
                try:
                    self.global_table.define(symbol)
                except ValueError as e:
                    raise ResolutionError(
                        f"Duplicate pipeline '{decl.name}'",
                        decl.start_line,
                        decl.start_col,
                    ) from e

    def _validate_functions(self) -> None:
        """Validate function parameter and return types."""
        for decl in self.module.decls:
            if isinstance(decl, FunctionDecl):
                symbol = self.global_table.lookup(decl.name)
                if symbol is None:
                    continue  # Should not happen

                # Validate parameter types
                param_types: list[TypeExpr] = []
                for param in decl.params:
                    if param.type is not None:
                        self._ensure_type_exists(param.type)
                        param_types.append(param.type)
                    else:
                        # Parameter without type annotation
                        param_types.append(None)  # type: ignore

                symbol.params = param_types

                # Validate return type
                if decl.return_type is not None:
                    self._ensure_type_exists(decl.return_type)
                    symbol.return_type = decl.return_type

    def _validate_pipelines(self) -> None:
        """Validate pipeline input and output types."""
        for decl in self.module.decls:
            if isinstance(decl, PipelineDecl):
                symbol = self.global_table.lookup(decl.name)
                if symbol is None:
                    continue  # Should not happen

                # Validate input type
                if decl.input_type is not None:
                    self._ensure_type_exists(decl.input_type)
                    symbol.input_type = decl.input_type

                # Validate output type
                if decl.output_type is not None:
                    self._ensure_type_exists(decl.output_type)
                    symbol.output_type = decl.output_type

    def _ensure_type_exists(self, type_expr: TypeExpr) -> None:
        """Ensure a type expression references a valid type.

        Args:
            type_expr: Type expression to validate

        Raises:
            ResolutionError: If type does not exist
        """
        if isinstance(type_expr, SimpleType):
            name = type_expr.name

            # Check if it's a primitive
            if is_primitive_type(name):
                return

            # Check if it's a defined type alias
            symbol = self.global_table.lookup(name)
            if symbol is not None and symbol.kind == SymbolKind.TYPE:
                return

            # Type not found
            raise ResolutionError(
                f"Unknown type '{name}'",
                type_expr.start_line,
                type_expr.start_col,
            )

        elif isinstance(type_expr, GenericType):
            # Ensure base type exists
            base_symbol = self.global_table.lookup(type_expr.name)
            if base_symbol is None or base_symbol.kind != SymbolKind.TYPE:
                if not is_primitive_type(type_expr.name):
                    raise ResolutionError(
                        f"Unknown type '{type_expr.name}'",
                        type_expr.start_line,
                        type_expr.start_col,
                    )

            # Recursively validate type arguments
            for type_arg in type_expr.type_args:
                self._ensure_type_exists(type_arg)

        elif isinstance(type_expr, RecordType):
            # Record types: recursively validate all field types
            for field_name, field_type_expr in type_expr.fields.items():
                self._ensure_type_exists(field_type_expr)

    def _resolve_type_expr(self, type_expr: TypeExpr) -> TypeExpr:
        """Resolve a type expression (validate and possibly normalize).

        Args:
            type_expr: Type expression to resolve

        Returns:
            Resolved type expression

        Raises:
            ResolutionError: If type does not exist
        """
        self._ensure_type_exists(type_expr)
        return type_expr


def resolve_module(module: Module) -> ResolutionResult:
    """Resolve symbols in a module.

    Args:
        module: Module AST to resolve

    Returns:
        ResolutionResult with resolved module and symbol table

    Raises:
        ResolutionError: If resolution fails
    """
    resolver = Resolver(module)
    return resolver.resolve()


__all__ = [
    "ResolutionError",
    "ResolutionResult",
    "Resolver",
    "resolve_module",
]

