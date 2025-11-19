"""Canonical program bundle module for RLang compiler.

Primary IR and program bundle building.
"""

from rlang.canonical.builder import build_primary_from_lowering
from rlang.canonical.primary_ir import (
    PrimaryProgramIR,
    build_primary_program_ir,
    choose_entry_pipeline,
)

__all__ = [
    "PrimaryProgramIR",
    "build_primary_program_ir",
    "choose_entry_pipeline",
    "build_primary_from_lowering",
]

