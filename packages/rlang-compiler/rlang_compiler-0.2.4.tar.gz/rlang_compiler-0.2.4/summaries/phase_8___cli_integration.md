# Phase 8 — CLI Integration (`rlangc`)

## Overview

Implemented command-line interface for the RLang compiler, providing the `rlangc` tool that compiles RLang source files to canonical JSON. The CLI wraps the pure compiler with file I/O while keeping the core compiler phases completely pure.

## Implementation Details

### Files Created

1. **`rlang/cli/rlangc.py`** (130 lines)
   - `build_arg_parser()`: Argument parser builder for testability
     - Arguments: source, --entry, --version, --language, --out
   - `run_compiler()`: Core compiler function with file I/O
     - Reads source file (UTF-8)
     - Calls `compile_source_to_json()` (pure compiler)
     - Writes output to file or stdout
     - Handles file I/O errors gracefully
     - Returns exit code (0 = success, non-zero = error)
   - `main()`: User-facing entrypoint
     - Parses arguments
     - Calls `run_compiler()`
     - Returns exit code for SystemExit
   - Full `__all__` export list

2. **`rlang/cli/__init__.py`** (10 lines)
   - Public API exports: All CLI components

3. **`pyproject.toml`** (updated)
   - Added `[project.scripts]` section
   - Registered `rlangc = "rlang.cli.rlangc:main"` as console script

4. **`tests/test_cli.py`** (200+ lines)
   - Comprehensive CLI test suite with 10+ test cases covering:
     - Compile to stdout (happy path)
     - Compile with --out to file
     - Explicit entry override via CLI
     - Non-existent file error handling
     - Bad syntax error handling
     - JSON determinism via CLI
     - Custom version and language
     - Direct `run_compiler()` function testing
     - File read/write error handling

## Key Features

- **Pure compiler core**: All file I/O isolated to CLI layer
- **Testable API**: `run_compiler()` function can be tested without subprocess
- **Error handling**: Graceful handling of file I/O errors and compilation errors
- **Flexible output**: Can write to file or stdout
- **CLI options**: Support for explicit entry, version, language customization
- **Console script**: Registered in pyproject.toml for easy installation

## CLI Usage

### Basic Usage
```bash
rlangc program.rlang
```

### With Output File
```bash
rlangc program.rlang --out output.json
```

### With Explicit Entry
```bash
rlangc program.rlang --entry custom_pipeline
```

### With Custom Metadata
```bash
rlangc program.rlang --version v1.0 --language rlang-v2
```

## Error Handling

- **File read errors**: Clear error message with file path
- **File write errors**: Clear error message with output path
- **Compilation errors**: Propagates all compiler phase errors with clear messages
- **Exit codes**: Returns 0 on success, non-zero on any error

## Architecture

- **Separation of concerns**: File I/O only in CLI layer
- **Pure compiler**: Core compiler (`compile_source_to_json`) remains pure
- **Testable**: `run_compiler()` function can be tested directly
- **Standard library only**: Uses only `argparse` and `sys` (no external CLI dependencies)

## Integration

- Uses existing emitter infrastructure (`rlang.emitter`)
- Console script registered in `pyproject.toml`
- Follows project invariants (no empty files, deterministic, testable)
- Ready for production use and BoR runtime integration

## Testing

All CLI functionality is thoroughly tested:
- ✅ Compile to stdout
- ✅ Compile to file
- ✅ Explicit entry override
- ✅ Error handling (file I/O, compilation errors)
- ✅ JSON determinism
- ✅ Custom metadata
- ✅ Direct function testing

## Next Steps

Phase 8 complete. The compiler is now a complete, production-ready tool with:
- Pure library API (`compile_source_to_json`)
- Command-line interface (`rlangc`)
- Full test coverage
- Deterministic, canonical JSON output

Ready for BoR runtime integration and production deployment.

