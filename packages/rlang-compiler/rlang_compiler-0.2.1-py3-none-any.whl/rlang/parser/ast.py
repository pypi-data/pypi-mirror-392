"""Abstract Syntax Tree definitions for RLang.

Defines the complete AST structure for representing RLang source code.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Node(ABC):
    """Base class for all AST nodes with position tracking."""

    start_line: int = 0
    start_col: int = 0
    end_line: int = 0
    end_col: int = 0

    def __post_init__(self):
        """Post-initialization hook for subclasses."""
        pass


@dataclass
class TypeExpr(Node, ABC):
    """Base class for type expressions."""

    pass


@dataclass
class SimpleType(TypeExpr):
    """Simple type reference (e.g., Int, String, Bool)."""

    name: str = ""


@dataclass
class GenericType(TypeExpr):
    """Generic type with type arguments (e.g., List<Int>, Map<String, Int>)."""

    name: str = ""
    type_args: list[TypeExpr] = None

    def __post_init__(self):
        """Initialize type_args to empty list if None."""
        if self.type_args is None:
            self.type_args = []


@dataclass
class TopLevelDecl(Node, ABC):
    """Abstract base class for top-level declarations."""

    pass


@dataclass
class TypeAlias(TopLevelDecl):
    """Type alias declaration: type Name = TypeExpr;"""

    name: str = ""
    target: TypeExpr = None


@dataclass
class Param(Node):
    """Function parameter with optional type annotation."""

    name: str = ""
    type: Optional[TypeExpr] = None


@dataclass
class FunctionDecl(TopLevelDecl):
    """Function declaration: fn Name(params?) -> TypeExpr?;"""

    name: str = ""
    params: list[Param] = None
    return_type: Optional[TypeExpr] = None
    body: list[Statement] = None  # For now, empty list for declarative style

    def __post_init__(self):
        """Initialize params and body to empty lists if None."""
        if self.params is None:
            self.params = []
        if self.body is None:
            self.body = []


@dataclass
class PipelineStep(Node):
    """A single step in a pipeline."""

    name: str = ""
    args: list[Expr] = None  # Optional arguments to the step
    expr: Optional["Expr"] = None  # Optional expression (e.g., IfExpr) for v0.2+

    def __post_init__(self):
        """Initialize args to empty list if None."""
        if self.args is None:
            self.args = []


@dataclass
class PipelineDecl(TopLevelDecl):
    """Pipeline declaration: pipeline Name(TypeExpr?) -> TypeExpr? { steps }"""

    name: str = ""
    input_type: Optional[TypeExpr] = None
    output_type: Optional[TypeExpr] = None
    steps: list[PipelineStep] = None

    def __post_init__(self):
        """Initialize steps to empty list if None."""
        if self.steps is None:
            self.steps = []


@dataclass
class Statement(Node, ABC):
    """Base class for statements."""

    pass


@dataclass
class ExprStmt(Statement):
    """Expression statement."""

    expr: Expr = None


@dataclass
class Expr(Node, ABC):
    """Base class for expressions."""

    pass


@dataclass
class Identifier(Expr):
    """Identifier expression (variable reference)."""

    name: str = ""


@dataclass
class Literal(Expr):
    """Literal value (number, string, boolean, null)."""

    value: object = None


@dataclass
class BinaryOp(Expr):
    """Binary operator expression."""

    op: str = ""
    left: Expr = None
    right: Expr = None


@dataclass
class Call(Expr):
    """Function call expression."""

    func: Expr = None  # Typically an Identifier
    args: list[Expr] = None

    def __post_init__(self):
        """Initialize args to empty list if None."""
        if self.args is None:
            self.args = []


@dataclass
class AttributeRef(Expr):
    """Attribute access expression (e.g., obj.attr)."""

    obj: Expr = None
    attr: str = ""


@dataclass
class IfExpr(Expr):
    """If/else conditional expression with pipeline-style step bodies."""

    condition: Expr = None
    then_steps: List["PipelineStep"] = None
    else_steps: Optional[List["PipelineStep"]] = None

    def __post_init__(self):
        """Initialize steps to empty list if None."""
        if self.then_steps is None:
            object.__setattr__(self, "then_steps", [])
        if self.else_steps is None:
            object.__setattr__(self, "else_steps", None)


@dataclass
class Module(Node):
    """Top-level module containing declarations."""

    decls: list[TopLevelDecl] = None

    def __post_init__(self):
        """Initialize decls to empty list if None."""
        if self.decls is None:
            self.decls = []


__all__ = [
    "Node",
    "Module",
    "TopLevelDecl",
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
]

