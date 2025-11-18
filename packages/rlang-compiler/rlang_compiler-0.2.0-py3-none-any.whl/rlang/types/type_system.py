"""Internal type system for RLang type checking.

Defines the RType model for representing types during type checking.
"""

from __future__ import annotations

from dataclasses import dataclass

from rlang.parser import GenericType, SimpleType, TypeExpr
from rlang.semantic import SymbolTable, is_primitive_type


@dataclass(frozen=True)
class RType:
    """Internal representation of a type during type checking.

    Attributes:
        name: Name of the type (e.g., "Int", "String", "List")
        args: Tuple of type arguments for generic types (empty for simple types)
    """

    name: str
    args: tuple[RType, ...] = ()

    def is_primitive(self) -> bool:
        """Check if this type is a primitive type.

        Returns:
            True if primitive, False otherwise
        """
        return is_primitive_type(self.name)

    def __str__(self) -> str:
        """String representation of the type.

        Returns:
            String like "Int" or "List[Int,String]"
        """
        if not self.args:
            return self.name
        args_str = ",".join(str(arg) for arg in self.args)
        return f"{self.name}[{args_str}]"


def rtype_from_type_expr(type_expr: TypeExpr, symbols: SymbolTable) -> RType:
    """Convert a TypeExpr AST node into an internal RType.

    Resolves type aliases by following the chain until a primitive or concrete type is found.

    Args:
        type_expr: Type expression AST node
        symbols: Symbol table for type resolution

    Returns:
        RType representation of the type expression

    Raises:
        TypeError: If type_expr is not a recognized type node
    """
    if isinstance(type_expr, SimpleType):
        # If it's a primitive type, return immediately
        if is_primitive_type(type_expr.name):
            return RType(name=type_expr.name)
        
        # Check if this is a type alias and resolve it
        symbol = symbols.lookup(type_expr.name)
        if symbol is not None and symbol.kind.value == "type" and symbol.type_expr is not None:
            # This is a type alias, resolve it recursively
            return rtype_from_type_expr(symbol.type_expr, symbols)
        # Not a type alias or primitive type, use as-is
        return RType(name=type_expr.name)

    if isinstance(type_expr, GenericType):
        # Recursively convert type arguments
        arg_rtypes = tuple(rtype_from_type_expr(arg, symbols) for arg in type_expr.type_args)
        return RType(name=type_expr.name, args=arg_rtypes)

    raise TypeError(f"Unknown type expression node: {type(type_expr).__name__}")


__all__ = [
    "RType",
    "rtype_from_type_expr",
]

