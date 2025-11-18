"""End-to-end compiler emitter for RLang → BoR.

Provides pure, deterministic compilation from RLang source to PrimaryProgramIR and JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from rlang.canonical import PrimaryProgramIR, build_primary_from_lowering
from rlang.lowering import lower_to_ir
from rlang.parser import parse
from rlang.semantic import resolve_module
from rlang.types import type_check


@dataclass(frozen=True)
class CompileResult:
    """Result of end-to-end compilation.

    Attributes:
        program_ir: The complete primary program IR
    """

    program_ir: PrimaryProgramIR

    def to_json(self) -> str:
        """Convert compilation result to canonical JSON string.

        Returns:
            Canonical JSON representation of the program
        """
        return self.program_ir.to_json()


def compile_source_to_ir(
    source: str,
    explicit_entry: Optional[str] = None,
    version: str = "v0",
    language: str = "rlang",
) -> CompileResult:
    """End-to-end compilation from RLang source string to PrimaryProgramIR.

    Runs all compiler phases:
    1. Parse source to AST
    2. Resolve symbols
    3. Type-check
    4. Lower to IR
    5. Build primary program IR

    Args:
        source: RLang source code string
        explicit_entry: Optional explicit entry pipeline name
        version: Program version (default "v0")
        language: Source language (default "rlang")

    Returns:
        CompileResult containing PrimaryProgramIR

    Raises:
        ParseError: If parsing fails
        ResolutionError: If symbol resolution fails
        TypeCheckError: If type checking fails
        LoweringError: If lowering fails
        ValueError: If explicit_entry doesn't exist
    """
    # Phase 1: Parse
    module = parse(source)

    # Phase 2: Resolve
    resolution = resolve_module(module)

    # Phase 3: Type-check
    tc_result = type_check(resolution)

    # Phase 4: Lower to IR
    lowering = lower_to_ir(tc_result)

    # Phase 5: Build primary IR
    program_ir = build_primary_from_lowering(
        lowering,
        explicit_entry=explicit_entry,
        version=version,
        language=language,
    )

    return CompileResult(program_ir=program_ir)


def compile_source_to_json(
    source: str,
    explicit_entry: Optional[str] = None,
    version: str = "v0",
    language: str = "rlang",
) -> str:
    """End-to-end compilation from RLang source string to canonical JSON.

    Convenience function that compiles source and returns JSON directly.

    Args:
        source: RLang source code string
        explicit_entry: Optional explicit entry pipeline name
        version: Program version (default "v0")
        language: Source language (default "rlang")

    Returns:
        Canonical JSON string representation of the compiled program

    Raises:
        ParseError: If parsing fails
        ResolutionError: If symbol resolution fails
        TypeCheckError: If type checking fails
        LoweringError: If lowering fails
        ValueError: If explicit_entry doesn't exist
    """
    result = compile_source_to_ir(
        source=source,
        explicit_entry=explicit_entry,
        version=version,
        language=language,
    )
    return result.to_json()


__all__ = [
    "CompileResult",
    "compile_source_to_ir",
    "compile_source_to_json",
]

