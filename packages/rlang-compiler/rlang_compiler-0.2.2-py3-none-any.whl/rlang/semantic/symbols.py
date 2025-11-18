"""Symbol table model for RLang semantic analysis.

Defines symbols, symbol tables, and primitive types for name resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SymbolKind(Enum):
    """Kind of symbol in the symbol table."""

    TYPE = "type"
    FUNCTION = "function"
    PIPELINE = "pipeline"


@dataclass
class Symbol:
    """Represents a symbol in the symbol table.

    Attributes:
        name: Name of the symbol
        kind: Kind of symbol (TYPE, FUNCTION, PIPELINE)
        node: AST node that declared this symbol
        type_expr: For TYPE symbols, the resolved TypeExpr target
        params: For FUNCTION symbols, list of parameter TypeExprs
        return_type: For FUNCTION symbols, the return TypeExpr
        input_type: For PIPELINE symbols, the input TypeExpr
        output_type: For PIPELINE symbols, the output TypeExpr
    """

    name: str
    kind: SymbolKind
    node: object  # AST node that declared this symbol
    type_expr: Optional[object] = None  # For TYPE: target TypeExpr
    params: Optional[list[object]] = None  # For FUNCTION: list of TypeExpr
    return_type: Optional[object] = None  # For FUNCTION: return TypeExpr
    input_type: Optional[object] = None  # For PIPELINE: input TypeExpr
    output_type: Optional[object] = None  # For PIPELINE: output TypeExpr

    def __post_init__(self):
        """Initialize optional fields to empty lists if None."""
        if self.params is None:
            self.params = []


@dataclass
class SymbolTable:
    """Symbol table with parent chain for scoping.

    Attributes:
        parent: Parent symbol table (for nested scopes)
        _symbols: Dictionary mapping names to symbols
    """

    parent: Optional[SymbolTable] = None
    _symbols: dict[str, Symbol] = field(default_factory=dict)

    def define(self, symbol: Symbol) -> None:
        """Define a symbol in this table.

        Args:
            symbol: Symbol to define

        Raises:
            ValueError: If a symbol with the same name already exists
        """
        if symbol.name in self._symbols:
            raise ValueError(f"Symbol '{symbol.name}' already defined in this scope")
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol by name, checking parent chain.

        Args:
            name: Name of symbol to look up

        Returns:
            Symbol if found, None otherwise
        """
        if name in self._symbols:
            return self._symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def __contains__(self, name: str) -> bool:
        """Check if a symbol exists in this table or parent chain.

        Args:
            name: Name of symbol to check

        Returns:
            True if symbol exists, False otherwise
        """
        return self.lookup(name) is not None

    def __getitem__(self, name: str) -> Symbol:
        """Get a symbol by name, raising KeyError if not found.

        Args:
            name: Name of symbol to get

        Returns:
            Symbol

        Raises:
            KeyError: If symbol not found
        """
        symbol = self.lookup(name)
        if symbol is None:
            raise KeyError(f"Symbol '{name}' not found")
        return symbol


# Primitive types that are always available (including built-in generic types like List)
PRIMITIVE_TYPES: set[str] = {
    "Int",
    "Float",
    "String",
    "Bool",
    "Unit",
    "List",  # Built-in generic type
}


def is_primitive_type(name: str) -> bool:
    """Check if a type name is a primitive type.

    Args:
        name: Type name to check

    Returns:
        True if primitive, False otherwise
    """
    return name in PRIMITIVE_TYPES


__all__ = [
    "SymbolKind",
    "Symbol",
    "SymbolTable",
    "PRIMITIVE_TYPES",
    "is_primitive_type",
]

