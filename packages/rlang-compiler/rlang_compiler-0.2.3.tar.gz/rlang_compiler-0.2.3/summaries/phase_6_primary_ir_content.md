# Phase 6 — Primary IR + Canonical Program Bundle

## Overview

Implemented PrimaryProgramIR and canonical program bundle builder that wraps all step templates and pipelines into a single, deterministic JSON-ready program representation. The primary IR includes entry pipeline selection, metadata, and sorted collections for reproducible output.

## Implementation Details

### Files Created

1. **`rlang/canonical/primary_ir.py`** (110 lines)
   - `PrimaryProgramIR` dataclass (frozen): Top-level program IR
     - Fields: version, language, entry_pipeline, step_templates, pipelines
     - Methods: `to_dict()`, `to_json()` using canonical JSON
   - `choose_entry_pipeline()`: Helper to select default entry pipeline
     - Prefers "main" if present
     - Otherwise selects lexicographically smallest name
     - Returns None if no pipelines
   - `build_primary_program_ir()`: Builder function
     - Supports explicit entry pipeline
     - Sorts templates by id and pipelines by name for determinism
     - Validates explicit entry exists
   - Full `__all__` export list

2. **`rlang/canonical/builder.py`** (30 lines)
   - `build_primary_from_lowering()`: Convenience function
     - Takes LoweringResult and builds PrimaryProgramIR
     - Supports explicit entry, version, and language customization
   - Full `__all__` export list

3. **`rlang/canonical/__init__.py`** (15 lines)
   - Public API exports: All primary IR components

4. **`tests/test_primary_ir.py`** (250+ lines)
   - Comprehensive test suite with 10+ test cases covering:
     - Empty module handling
     - Single pipeline entry selection
     - "main" pipeline preference
     - Lexicographic selection when no "main"
     - Explicit entry respect and validation
     - JSON determinism
     - Sorting verification (templates by id, pipelines by name)
     - Custom version and language
     - JSON round-trip validation

## Key Features

- **PrimaryProgramIR**: Top-level program representation with metadata
- **Entry pipeline selection**: Automatic selection with "main" preference
- **Deterministic sorting**: Templates sorted by id, pipelines by name
- **Explicit entry support**: Allows overriding default entry selection
- **Canonical JSON**: Uses canonical_dumps for stable, reproducible output
- **Metadata support**: Version and language fields for program identification
- **Error handling**: Validates explicit entry exists

## Entry Pipeline Selection

1. **Explicit entry**: If provided, use it (with validation)
2. **"main" preference**: If "main" pipeline exists, use it
3. **Lexicographic fallback**: Otherwise, use lexicographically smallest name
4. **None if empty**: Return None if no pipelines exist

## Deterministic Output

- **Step templates**: Sorted by `id` (e.g., "fn:alpha", "fn:beta", "fn:zeta")
- **Pipelines**: Sorted by `name` (e.g., "alpha", "beta", "zeta")
- **JSON**: Canonical format ensures byte-for-byte identical output across runs

## JSON Structure

```json
{
  "version": "v0",
  "language": "rlang",
  "entry_pipeline": "main",
  "step_templates": [...],
  "pipelines": [...]
}
```

## Integration

- Uses existing lowering infrastructure (`rlang.lowering`)
- Works with IR models from Phase 5
- Follows project invariants (no empty files, deterministic, testable)
- Ready for Phase 7 (Emission - CLI JSON artifacts)

## Testing

All primary IR functionality is thoroughly tested:
- ✅ Empty module handling
- ✅ Entry pipeline selection (main preference, lexicographic fallback)
- ✅ Explicit entry support and validation
- ✅ JSON determinism
- ✅ Sorting verification
- ✅ Custom metadata (version, language)
- ✅ JSON round-trip validation

## Next Steps

Phase 6 complete. Ready to proceed to **Phase 7 — Emission**, which will turn this PrimaryProgramIR into CLI-usable JSON artifacts while keeping the core passes pure.

