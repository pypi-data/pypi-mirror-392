"""RLang to BoR compiler implementation."""

__version__ = "0.2.5"

from rlang.emitter import CompileResult, compile_source_to_ir, compile_source_to_json

__all__ = [
    "__version__",
    "CompileResult",
    "compile_source_to_ir",
    "compile_source_to_json",
]

