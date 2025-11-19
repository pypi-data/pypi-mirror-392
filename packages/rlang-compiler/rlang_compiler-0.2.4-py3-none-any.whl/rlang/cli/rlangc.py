"""Command-line interface for the RLang compiler.

Provides rlangc CLI tool for compiling RLang source files to canonical JSON.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from rlang.emitter import compile_source_to_json
from rlang.lowering import LoweringError
from rlang.parser import ParseError
from rlang.semantic import ResolutionError
from rlang.types import TypeCheckError


def build_arg_parser() -> argparse.ArgumentParser:
    """Build argument parser for rlangc CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="rlangc",
        description="RLang → BoR compiler: compile RLang source into canonical JSON.",
    )
    parser.add_argument(
        "source",
        help="Path to the RLang source file.",
    )
    parser.add_argument(
        "--entry",
        dest="entry",
        help="Explicit entry pipeline name (overrides automatic selection).",
    )
    parser.add_argument(
        "--version",
        dest="version",
        default="v0",
        help="Program IR version label (default: v0).",
    )
    parser.add_argument(
        "--language",
        dest="language",
        default="rlang",
        help="Language label for the IR (default: rlang).",
    )
    parser.add_argument(
        "--out",
        dest="out",
        help="Output file path for JSON. If omitted, prints to stdout.",
    )
    return parser


def run_compiler(
    source_path: str,
    entry: Optional[str] = None,
    version: str = "v0",
    language: str = "rlang",
    out_path: Optional[str] = None,
    stderr=sys.stderr,
) -> int:
    """Compile a source file and write canonical JSON either to stdout or to `out_path`.

    Args:
        source_path: Path to RLang source file
        entry: Optional explicit entry pipeline name
        version: Program IR version label
        language: Language label for the IR
        out_path: Optional output file path (if None, prints to stdout)
        stderr: Stream for error output (default: sys.stderr)

    Returns:
        0 on success, non-zero on error
    """
    # Read source file
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"Error: cannot read file '{source_path}': {e}", file=sys.stderr)
        return 1

    # Compile source
    try:
        json_output = compile_source_to_json(
            source,
            explicit_entry=entry,
            version=version,
            language=language,
        )
    except (ParseError, ResolutionError, TypeCheckError, LoweringError, ValueError) as e:
        print(f"Compilation failed: {e}", file=sys.stderr)
        return 1

    # Write output
    if out_path is not None:
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(json_output)
        except Exception as e:
            print(f"Error: cannot write output to '{out_path}': {e}", file=sys.stderr)
            return 1
    else:
        print(json_output)

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main entrypoint for rlangc CLI.

    Args:
        argv: Optional command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 on success, non-zero on error)
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    return run_compiler(
        source_path=args.source,
        entry=args.entry,
        version=args.version,
        language=args.language,
        out_path=args.out,
    )


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "build_arg_parser",
    "run_compiler",
    "main",
]

