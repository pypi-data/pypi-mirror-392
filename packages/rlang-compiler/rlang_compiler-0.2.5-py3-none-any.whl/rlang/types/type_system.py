"""Internal type system for RLang type checking.

Defines the RType model for representing types during type checking.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from rlang.parser import GenericType, RecordType, SimpleType, TypeExpr
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


@dataclass(frozen=True)
class RecordRType(RType):
    """Record type representation.

    Attributes:
        fields: Dictionary mapping field names to their types
    """

    fields: Dict[str, RType] = None

    def __post_init__(self):
        """Initialize fields to empty dict if None."""
        if self.fields is None:
            object.__setattr__(self, "fields", {})

    def __str__(self) -> str:
        """String representation of the record type.

        Returns:
            String like "Record{ id: Int, name: String }"
        """
        if not self.fields:
            return "Record{ }"
        fields_str = ", ".join(f"{k}: {v}" for k, v in self.fields.items())
        return f"Record{{ {fields_str} }}"


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

    if isinstance(type_expr, RecordType):
        # Convert record type: resolve all field types
        field_types: Dict[str, RType] = {}
        for field_name, field_type_expr in type_expr.fields.items():
            field_types[field_name] = rtype_from_type_expr(field_type_expr, symbols)
        return RecordRType(name="Record", fields=field_types)

    raise TypeError(f"Unknown type expression node: {type(type_expr).__name__}")


__all__ = [
    "RType",
    "RecordRType",
    "rtype_from_type_expr",
]

