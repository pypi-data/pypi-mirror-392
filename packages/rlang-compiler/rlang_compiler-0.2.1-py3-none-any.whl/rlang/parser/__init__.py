"""Parser module for RLang compiler.

Public API for parsing RLang source code into ASTs.
"""

from rlang.parser.ast import (
    AttributeRef,
    BinaryOp,
    Call,
    Expr,
    ExprStmt,
    FunctionDecl,
    GenericType,
    Identifier,
    IfExpr,
    Literal,
    Module,
    Param,
    PipelineDecl,
    PipelineStep,
    SimpleType,
    Statement,
    TypeAlias,
    TypeExpr,
)
from rlang.parser.parser import ParseError, Parser, parse

__all__ = [
    # AST nodes
    "Module",
    "TypeAlias",
    "TypeExpr",
    "SimpleType",
    "GenericType",
    "Param",
    "FunctionDecl",
    "PipelineDecl",
    "PipelineStep",
    "Statement",
    "ExprStmt",
    "Expr",
    "Identifier",
    "Literal",
    "BinaryOp",
    "Call",
    "AttributeRef",
    "IfExpr",
    # Parser
    "Parser",
    "ParseError",
    "parse",
]

