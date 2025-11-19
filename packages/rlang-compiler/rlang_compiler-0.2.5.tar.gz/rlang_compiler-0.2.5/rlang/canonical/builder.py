"""Builder for PrimaryProgramIR from LoweringResult.

Convenience functions to build primary program IR from lowering results.
"""

from __future__ import annotations

from typing import Optional

from rlang.canonical.primary_ir import PrimaryProgramIR, build_primary_program_ir
from rlang.lowering import LoweringResult


def build_primary_from_lowering(
    lowering: LoweringResult,
    explicit_entry: Optional[str] = None,
    version: str = "v0",
    language: str = "rlang",
) -> PrimaryProgramIR:
    """Build a PrimaryProgramIR from a LoweringResult.

    Convenience helper that takes a LoweringResult and builds a PrimaryProgramIR.

    Args:
        lowering: LoweringResult containing IR bundle
        explicit_entry: Optional explicit entry pipeline name
        version: Program version (default "v0")
        language: Source language (default "rlang")

    Returns:
        PrimaryProgramIR with all templates and pipelines

    Raises:
        ValueError: If explicit_entry is provided but doesn't exist
    """
    return build_primary_program_ir(
        bundle=lowering.ir,
        explicit_entry=explicit_entry,
        version=version,
        language=language,
    )


__all__ = [
    "build_primary_from_lowering",
]

