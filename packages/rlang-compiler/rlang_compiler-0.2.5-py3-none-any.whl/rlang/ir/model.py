"""Intermediate Representation (IR) models for RLang compiler.

Defines StepTemplateIR, PipelineStepIR, PipelineIR, and LoweringIRBundle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from rlang.types import RType
from rlang.utils.canonical_json import canonical_dumps


def rtype_to_string(rtype: RType) -> str:
    """Convert an RType to a canonical string representation.

    Args:
        rtype: RType to convert

    Returns:
        String representation, e.g., "Int" or "Foo[Int,String]"
    """
    if not rtype.args:
        return rtype.name
    args_str = ",".join(rtype_to_string(arg) for arg in rtype.args)
    return f"{rtype.name}[{args_str}]"


@dataclass(frozen=True)
class StepTemplateIR:
    """IR representation of a function step template.

    Attributes:
        id: Template identifier (e.g., "fn:add")
        name: Function name
        fn_name: Same as name, explicit
        param_types: List of stringified parameter types
        return_type: Stringified return type, or None if no return
        rule_repr: Canonical textual representation
        version: Template version (default "v0")
    """

    id: str
    name: str
    fn_name: str
    param_types: list[str]
    return_type: str | None
    rule_repr: str
    version: str = "v0"

    def to_dict(self) -> dict[str, any]:
        """Convert to plain dictionary.

        Returns:
            Dictionary representation
        """
        return asdict(self)

    def to_json(self) -> str:
        """Convert to canonical JSON string.

        Returns:
            Canonical JSON representation
        """
        return canonical_dumps(self.to_dict())


@dataclass(frozen=True)
class PipelineStepIR:
    """IR representation of a single step in a pipeline.

    Attributes:
        index: 0-based index in the pipeline
        name: Pipeline step name (usually function name)
        template_id: Reference to StepTemplateIR.id
        arg_types: Types of arguments (as stringified RType)
        input_type: Effective input type to this step
        output_type: Step return type
    """

    index: int
    name: str
    template_id: str
    arg_types: list[str]
    input_type: str | None
    output_type: str | None

    def to_dict(self) -> dict[str, any]:
        """Convert to plain dictionary.

        Returns:
            Dictionary representation
        """
        return asdict(self)

    def to_json(self) -> str:
        """Convert to canonical JSON string.

        Returns:
            Canonical JSON representation
        """
        return canonical_dumps(self.to_dict())


@dataclass(frozen=True)
class IRExpr:
    """IR representation of an expression (for conditions, etc.).

    Attributes:
        kind: Expression kind ("binary_op", "literal", "identifier", "call", "boolean_and", "boolean_or", "boolean_not", "record", "field_access", "list")
        op: Operator for binary operations (e.g., ">", "==")
        left: Left operand (IRExpr or value) - for binary_op, boolean_and, boolean_or
        right: Right operand (IRExpr or value) - for binary_op, boolean_and, boolean_or
        operand: Operand (IRExpr) - for boolean_not
        value: Literal value (for literals)
        name: Identifier name (for identifiers)
        func: Function name (for calls)
        args: Function arguments (for calls)
        fields: Record fields (dict[str, IRExpr]) - for record kind
        record: Record expression (IRExpr) - for field_access kind
        field_name: Field name (str) - for field_access kind
        elements: List elements (list[IRExpr]) - for list kind
    """

    kind: str
    op: str | None = None
    left: "IRExpr | None" = None
    right: "IRExpr | None" = None
    operand: "IRExpr | None" = None
    value: object = None
    name: str | None = None
    func: str | None = None
    args: list["IRExpr"] = field(default_factory=list)
    fields: dict[str, "IRExpr"] | None = None
    record: "IRExpr | None" = None
    field_name: str | None = None
    elements: list["IRExpr"] = field(default_factory=list)

    def to_dict(self) -> dict[str, any]:
        """Convert to plain dictionary with sorted keys."""
        result: dict[str, any] = {"kind": self.kind}
        if self.op is not None:
            result["op"] = self.op
        if self.left is not None:
            result["left"] = self.left.to_dict()
        if self.right is not None:
            result["right"] = self.right.to_dict()
        if self.operand is not None:
            result["operand"] = self.operand.to_dict()
        # value can be None (for null literals), so check if it was explicitly set
        # We use a sentinel approach: if kind is "literal", always include value
        if self.kind == "literal":
            result["value"] = self.value
        elif self.value is not None:
            result["value"] = self.value
        if self.name is not None:
            result["name"] = self.name
        if self.func is not None:
            result["func"] = self.func
        if self.args:
            result["args"] = [arg.to_dict() for arg in self.args]
        if self.fields is not None:
            # Sort fields alphabetically for canonical ordering
            sorted_fields = {k: v.to_dict() for k, v in sorted(self.fields.items())}
            result["fields"] = sorted_fields
        if self.record is not None:
            result["record"] = self.record.to_dict()
        if self.field_name is not None:
            result["field_name"] = self.field_name
        if self.elements:
            result["elements"] = [elem.to_dict() for elem in self.elements]
        return result

    def to_json(self) -> str:
        """Convert to canonical JSON string."""
        return canonical_dumps(self.to_dict())


@dataclass(frozen=True)
class IRIf:
    """IR representation of an if/else conditional expression.

    Attributes:
        condition: IR expression for the condition
        then_steps: List of IR steps for the then branch (can contain nested IRIf or IRExpr)
        else_steps: List of IR steps for the else branch (can contain nested IRIf or IRExpr, empty if no else)
    """

    condition: IRExpr
    then_steps: list["PipelineStepIR | IRIf | IRExpr"] = field(default_factory=list)
    else_steps: list["PipelineStepIR | IRIf | IRExpr"] = field(default_factory=list)

    def to_dict(self) -> dict[str, any]:
        """Convert to plain dictionary with sorted keys.
        
        Handles nested IRIf objects recursively.
        """
        return {
            "condition": self.condition.to_dict(),
            "else": [step.to_dict() for step in self.else_steps],
            "kind": "if",
            "then": [step.to_dict() for step in self.then_steps],
        }

    def to_json(self) -> str:
        """Convert to canonical JSON string."""
        return canonical_dumps(self.to_dict())


@dataclass(frozen=True)
class PipelineIR:
    """IR representation of a complete pipeline.

    Attributes:
        id: Pipeline identifier (e.g., "pipeline:main")
        name: Pipeline name
        input_type: Pipeline input type string, or None
        output_type: Pipeline output type string, or None
        steps: List of pipeline steps (PipelineStepIR, IRIf, or IRExpr for expression steps)
    """

    id: str
    name: str
    input_type: str | None
    output_type: str | None
    steps: list[PipelineStepIR | IRIf | IRExpr] = field(default_factory=list)

    def to_dict(self) -> dict[str, any]:
        """Convert to plain dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "name": self.name,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "steps": [step.to_dict() for step in self.steps],
        }

    def to_json(self) -> str:
        """Convert to canonical JSON string.

        Returns:
            Canonical JSON representation
        """
        return canonical_dumps(self.to_dict())


@dataclass(frozen=True)
class LoweringIRBundle:
    """Complete IR bundle containing all step templates and pipelines.

    Attributes:
        step_templates: Dictionary mapping template_id to StepTemplateIR
        pipelines: Dictionary mapping pipeline name to PipelineIR
    """

    step_templates: dict[str, StepTemplateIR]
    pipelines: dict[str, PipelineIR]

    def to_dict(self) -> dict[str, any]:
        """Convert to plain dictionary.

        Returns:
            Dictionary representation with "step_templates" and "pipelines" as lists
        """
        return {
            "step_templates": [template.to_dict() for template in self.step_templates.values()],
            "pipelines": [pipeline.to_dict() for pipeline in self.pipelines.values()],
        }

    def to_json(self) -> str:
        """Convert to canonical JSON string.

        Returns:
            Canonical JSON representation
        """
        return canonical_dumps(self.to_dict())


__all__ = [
    "StepTemplateIR",
    "PipelineStepIR",
    "IRExpr",
    "IRIf",
    "PipelineIR",
    "LoweringIRBundle",
    "rtype_to_string",
]

