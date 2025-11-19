"""Emitter module for RLang compiler.

End-to-end compilation from source to IR and JSON.
"""

from rlang.emitter.emitter import CompileResult, compile_source_to_ir, compile_source_to_json

__all__ = [
    "CompileResult",
    "compile_source_to_ir",
    "compile_source_to_json",
]

