# Phase 7 — Emission (End-to-End Compiler Function)

## Overview

Implemented pure, end-to-end compiler API that provides a single-call interface from RLang source code to PrimaryProgramIR and canonical JSON. The emitter orchestrates all compiler phases (parse → resolve → type-check → lower → primary IR) in a deterministic, pure function.

## Implementation Details

### Files Created

1. **`rlang/emitter/emitter.py`** (100 lines)
   - `CompileResult` dataclass (frozen): Result container with PrimaryProgramIR
     - Method: `to_json()` returns canonical JSON
   - `compile_source_to_ir()`: End-to-end compilation to PrimaryProgramIR
     - Runs all phases: parse → resolve → type-check → lower → primary IR
     - Supports explicit_entry, version, language parameters
     - Propagates all errors (ParseError, ResolutionError, TypeCheckError, LoweringError, ValueError)
   - `compile_source_to_json()`: Convenience function for direct JSON output
     - Calls `compile_source_to_ir()` and returns JSON string
   - Full `__all__` export list

2. **`rlang/emitter/__init__.py`** (10 lines)
   - Public API exports: All emitter components

3. **`rlang/__init__.py`** (updated)
   - Re-exports compiler functions at top level
   - Preserves existing `__version__` export
   - Adds: `CompileResult`, `compile_source_to_ir`, `compile_source_to_json`

4. **`tests/test_emitter.py`** (200+ lines)
   - Comprehensive end-to-end test suite with 12+ test cases covering:
     - Empty source compilation
     - Simple pipeline compilation
     - Explicit entry override
     - JSON determinism end-to-end
     - Error propagation (parse errors, resolution errors, type check errors)
     - CompileResult.to_json() method
     - Custom version and language
     - Complex program compilation
     - Direct JSON compilation
     - Explicit entry validation

## Key Features

- **Single-call API**: `compile_source_to_json(source)` for complete compilation
- **Pure and deterministic**: No I/O, no hidden state, reproducible output
- **Error propagation**: All phase errors propagate correctly
- **Flexible output**: Returns either PrimaryProgramIR or JSON string
- **Metadata support**: Custom version and language
- **Entry pipeline control**: Explicit entry override support

## Compilation Pipeline

The emitter orchestrates the complete compilation pipeline:

1. **Parse**: `parse(source)` → Module AST
2. **Resolve**: `resolve_module(module)` → ResolutionResult
3. **Type-check**: `type_check(resolution)` → TypeCheckResult
4. **Lower**: `lower_to_ir(tc_result)` → LoweringResult
5. **Primary IR**: `build_primary_from_lowering(lowering)` → PrimaryProgramIR

## API Usage

### Basic Usage
```python
from rlang import compile_source_to_json

source = """
fn step1(x: Int) -> Int;
pipeline main(Int) -> Int {
  step1(42)
}
"""

json_output = compile_source_to_json(source)
```

### With Options
```python
from rlang import compile_source_to_ir

result = compile_source_to_ir(
    source=source,
    explicit_entry="custom_pipeline",
    version="v1.0",
    language="rlang-v2"
)

# Access IR or JSON
ir = result.program_ir
json_str = result.to_json()
```

## Error Handling

All compiler phase errors propagate correctly:
- **ParseError**: Invalid syntax
- **ResolutionError**: Unknown types, duplicate definitions
- **TypeCheckError**: Type mismatches, arity errors
- **LoweringError**: Missing functions, invalid references
- **ValueError**: Invalid explicit_entry

## Integration

- Uses all previous phases (parser, resolver, type checker, lowerer, canonical)
- Top-level API available via `rlang` package
- Follows project invariants (no empty files, deterministic, testable)
- Ready for Phase 8 (CLI integration)

## Testing

All emitter functionality is thoroughly tested:
- ✅ Empty source compilation
- ✅ Simple and complex program compilation
- ✅ Explicit entry override
- ✅ JSON determinism end-to-end
- ✅ Error propagation (all error types)
- ✅ Custom metadata (version, language)
- ✅ JSON consistency

## Next Steps

Phase 7 complete. Ready to proceed to **Phase 8 — CLI Integration**, which will add command-line interface for file I/O and user interaction while keeping the core compiler pure.

