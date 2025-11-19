"""CLI module for RLang compiler.

Command-line interface for compiling RLang source files.
"""

from rlang.cli.rlangc import build_arg_parser, main, run_compiler

__all__ = [
    "build_arg_parser",
    "run_compiler",
    "main",
]

