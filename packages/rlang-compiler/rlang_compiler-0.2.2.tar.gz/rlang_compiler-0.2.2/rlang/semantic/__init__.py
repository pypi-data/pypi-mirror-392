"""Semantic analysis module for RLang compiler.

Symbol resolution and type checking.
"""

from rlang.semantic.resolver import ResolutionError, ResolutionResult, Resolver, resolve_module
from rlang.semantic.symbols import PRIMITIVE_TYPES, Symbol, SymbolKind, SymbolTable, is_primitive_type

__all__ = [
    # Symbols
    "SymbolKind",
    "Symbol",
    "SymbolTable",
    "PRIMITIVE_TYPES",
    "is_primitive_type",
    # Resolver
    "ResolutionError",
    "ResolutionResult",
    "Resolver",
    "resolve_module",
]

