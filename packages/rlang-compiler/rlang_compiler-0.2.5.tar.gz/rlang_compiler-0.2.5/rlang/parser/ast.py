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
class RecordType(TypeExpr):
    """Record type definition: Record { field1: Type1, field2: Type2, ... }."""

    fields: dict[str, TypeExpr] = None

    def __post_init__(self):
        """Initialize fields to empty dict if None."""
        if self.fields is None:
            self.fields = {}


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
class BooleanAnd(Expr):
    """Boolean AND expression (&&)."""

    left: Expr = None
    right: Expr = None


@dataclass
class BooleanOr(Expr):
    """Boolean OR expression (||)."""

    left: Expr = None
    right: Expr = None


@dataclass
class BooleanNot(Expr):
    """Boolean NOT expression (!)."""

    operand: Expr = None


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
class RecordExpr(Expr):
    """Record literal expression: { field1: expr1, field2: expr2, ... }."""

    fields: dict[str, Expr] = None

    def __post_init__(self):
        """Initialize fields to empty dict if None."""
        if self.fields is None:
            self.fields = {}


@dataclass
class FieldAccess(Expr):
    """Field access expression (e.g., obj.field)."""

    record: Expr = None
    field: str = ""


@dataclass
class ListExpr(Expr):
    """List literal expression: [ expr1, expr2, ... ]."""

    elements: list[Expr] = None

    def __post_init__(self):
        """Initialize elements to empty list if None."""
        if self.elements is None:
            self.elements = []


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
class ForExpr(Expr):
    """Bounded for loop expression with pipeline-style step body."""

    var_name: str = ""  # Loop variable name (e.g., "i")
    start: int = 0  # Inclusive start bound (compile-time literal)
    end: int = 0  # Exclusive end bound (compile-time literal)
    body: List["PipelineStep"] = None  # Steps inside the loop body

    def __post_init__(self):
        """Initialize body to empty list if None."""
        if self.body is None:
            object.__setattr__(self, "body", [])


@dataclass
class MatchExpr(Expr):
    """Pattern matching expression."""

    value: Expr = None
    cases: list["Case"] = None

    def __post_init__(self):
        """Initialize cases to empty list if None."""
        if self.cases is None:
            object.__setattr__(self, "cases", [])


@dataclass
class Case(Node):
    """A single case in a match expression."""

    pattern: "Pattern" = None
    body: list[PipelineStep] = None

    def __post_init__(self):
        """Initialize body to empty list if None."""
        if self.body is None:
            object.__setattr__(self, "body", [])


class Pattern(Node):
    """Base class for pattern matching patterns."""

    pass


@dataclass
class WildcardPattern(Pattern):
    """Wildcard pattern (_) that matches anything."""

    pass


@dataclass
class LiteralPattern(Pattern):
    """Literal pattern that matches a specific literal value."""

    value: object = None  # int, string, bool


@dataclass
class VarPattern(Pattern):
    """Variable pattern that binds to a variable name."""

    name: str = ""


@dataclass
class RecordPattern(Pattern):
    """Record pattern that matches record structures."""

    fields: dict[str, Pattern] = None  # preserve source order

    def __post_init__(self):
        """Initialize fields to empty dict if None."""
        if self.fields is None:
            object.__setattr__(self, "fields", {})


@dataclass
class ListPattern(Pattern):
    """List pattern that matches list structures."""

    elements: list[Pattern] = None

    def __post_init__(self):
        """Initialize elements to empty list if None."""
        if self.elements is None:
            object.__setattr__(self, "elements", [])


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
    "RecordType",
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
    "RecordExpr",
    "FieldAccess",
    "AttributeRef",
    "IfExpr",
    "ForExpr",
    "MatchExpr",
    "Case",
    "Pattern",
    "WildcardPattern",
    "LiteralPattern",
    "VarPattern",
    "RecordPattern",
    "ListPattern",
]

