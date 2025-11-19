"""Primary Program IR model for RLang compiler.

Defines the top-level program IR that wraps all step templates and pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rlang.ir import LoweringIRBundle, PipelineIR, StepTemplateIR
from rlang.utils.canonical_json import canonical_dumps


@dataclass(frozen=True)
class PrimaryProgramIR:
    """Primary Program IR representing a complete RLang program.

    Attributes:
        version: Program version (e.g., "v0")
        language: Source language (e.g., "rlang")
        entry_pipeline: Name of entry pipeline, or None
        step_templates: List of step templates (sorted by id)
        pipelines: List of pipelines (sorted by name)
    """

    version: str
    language: str
    entry_pipeline: str | None
    step_templates: list[StepTemplateIR] = field(default_factory=list)
    pipelines: list[PipelineIR] = field(default_factory=list)

    def to_dict(self) -> dict[str, any]:
        """Convert to plain dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "version": self.version,
            "language": self.language,
            "entry_pipeline": self.entry_pipeline,
            "step_templates": [st.to_dict() for st in self.step_templates],
            "pipelines": [p.to_dict() for p in self.pipelines],
        }

    def to_json(self) -> str:
        """Convert to canonical JSON string.

        Returns:
            Canonical JSON representation
        """
        return canonical_dumps(self.to_dict())


def choose_entry_pipeline(bundle: LoweringIRBundle) -> str | None:
    """Choose a default entry pipeline name.

    Rules:
        - If there is a pipeline named "main", return "main"
        - Else, if bundle.pipelines is non-empty, return the lexicographically smallest name
        - Else, return None

    Args:
        bundle: LoweringIRBundle to choose entry from

    Returns:
        Entry pipeline name, or None if no pipelines
    """
    if not bundle.pipelines:
        return None

    # Check for "main" first
    if "main" in bundle.pipelines:
        return "main"

    # Return lexicographically smallest name
    return min(bundle.pipelines.keys())


def build_primary_program_ir(
    bundle: LoweringIRBundle,
    explicit_entry: str | None = None,
    version: str = "v0",
    language: str = "rlang",
) -> PrimaryProgramIR:
    """Build a PrimaryProgramIR from a LoweringIRBundle.

    Args:
        bundle: LoweringIRBundle to build from
        explicit_entry: Optional explicit entry pipeline name
        version: Program version (default "v0")
        language: Source language (default "rlang")

    Returns:
        PrimaryProgramIR with all templates and pipelines

    Raises:
        ValueError: If explicit_entry is provided but doesn't exist in bundle
    """
    # Determine entry pipeline
    if explicit_entry is not None:
        if explicit_entry not in bundle.pipelines:
            raise ValueError(f"Entry pipeline '{explicit_entry}' not found in bundle")
        entry_pipeline = explicit_entry
    else:
        entry_pipeline = choose_entry_pipeline(bundle)

    # Sort step templates by id for deterministic output
    sorted_templates = sorted(bundle.step_templates.values(), key=lambda t: t.id)

    # Sort pipelines by name for deterministic output
    sorted_pipelines = sorted(bundle.pipelines.values(), key=lambda p: p.name)

    return PrimaryProgramIR(
        version=version,
        language=language,
        entry_pipeline=entry_pipeline,
        step_templates=sorted_templates,
        pipelines=sorted_pipelines,
    )


__all__ = [
    "PrimaryProgramIR",
    "build_primary_program_ir",
    "choose_entry_pipeline",
]

