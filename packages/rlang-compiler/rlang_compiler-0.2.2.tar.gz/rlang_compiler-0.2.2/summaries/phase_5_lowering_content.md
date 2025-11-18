# Phase 5 — Lowering to IR (StepIR + PipelineIR)

## Overview

Implemented complete IR lowering from type-checked RLang modules to StepTemplateIR and PipelineIR representations. The lowering process produces deterministic, canonical JSON-ready IR bundles.

## Implementation Details

### Files Created

1. **`rlang/ir/model.py`** (180 lines)
   - `rtype_to_string()`: Helper to convert RType to canonical string representation
   - `StepTemplateIR` dataclass (frozen): IR for function step templates
     - Fields: id, name, fn_name, param_types, return_type, rule_repr, version
     - Methods: `to_dict()`, `to_json()` using canonical JSON
   - `PipelineStepIR` dataclass (frozen): IR for individual pipeline steps
     - Fields: index, name, template_id, arg_types, input_type, output_type
     - Methods: `to_dict()`, `to_json()` using canonical JSON
   - `PipelineIR` dataclass (frozen): IR for complete pipelines
     - Fields: id, name, input_type, output_type, steps
     - Methods: `to_dict()`, `to_json()` using canonical JSON
   - `LoweringIRBundle` dataclass (frozen): Container for all IR
     - Fields: step_templates (dict), pipelines (dict)
     - Methods: `to_dict()`, `to_json()` using canonical JSON
   - Full `__all__` export list

2. **`rlang/lowering/lowering.py`** (200 lines)
   - `LoweringError` exception: Error for lowering failures
   - `LoweringResult` dataclass: Contains module and IR bundle
   - `Lowerer` class: Main lowering implementation
     - `lower()`: Main driver that builds IR bundle
     - `_collect_function_signatures()`: Collects function signatures as RTypes
     - `_build_step_templates()`: Builds StepTemplateIR for each function
     - `_lower_pipelines()`: Lowers PipelineDecl to PipelineIR
   - `lower_to_ir()`: Public convenience function
   - Full `__all__` export list

3. **`rlang/ir/__init__.py`** (15 lines)
   - Public API exports: All IR model components

4. **`rlang/lowering/__init__.py`** (10 lines)
   - Public API exports: All lowering components

5. **`tests/test_lowering.py`** (200+ lines)
   - Comprehensive test suite with 10+ test cases covering:
     - Empty module lowering
     - Single function lowering
     - Simple pipeline lowering
     - Pipeline with literal arguments
     - Bundle JSON stability and canonicity
     - rtype_to_string helper
     - Step template rule_repr formatting
     - Pipeline steps without explicit args
     - Complex pipeline lowering
     - IR to_dict conversions

## Key Features

- **StepTemplateIR**: Represents function templates with canonical rule_repr
- **PipelineStepIR**: Represents individual pipeline steps with type information
- **PipelineIR**: Represents complete pipelines with step chains
- **LoweringIRBundle**: Container for all IR with canonical JSON support
- **Deterministic JSON**: Uses canonical_dumps for stable, reproducible output
- **Type preservation**: All type information preserved through lowering
- **Error handling**: `LoweringError` for missing functions or invalid references

## Lowering Process

1. **Collect function signatures**: Convert all FunctionDecl to RType signatures
2. **Build step templates**: Create StepTemplateIR for each function with:
   - Template ID: `"fn:{name}"`
   - Parameter and return types as strings
   - Canonical rule_repr: `"fn {name}({params}) -> {return}"`
3. **Lower pipelines**: For each PipelineDecl:
   - Create PipelineIR with pipeline-level input/output types
   - For each step:
     - Look up function signature
     - Extract argument types from expression type mapping
     - Create PipelineStepIR with step-level type information
     - Assign 0-based index

## Type Stringification

- **rtype_to_string()**: Converts RType to canonical string format
  - Simple types: `"Int"`, `"String"`
  - Generic types: `"List[Int]"`, `"Map[String,Int]"`
  - Nested generics: `"List[Map[String,Int]]"`

## JSON Canonicalization

- All IR classes support `to_json()` using `canonical_dumps()`
- Ensures deterministic, reproducible JSON output
- Bundle JSON is stable across multiple calls

## Integration

- Uses existing type checker infrastructure (`rlang.types`)
- Works with AST nodes from Phase 2
- Follows project invariants (no empty files, deterministic, testable)
- Ready for Phase 6 (PrimaryIR + canonical JSON bundle emission)

## Testing

All lowering functionality is thoroughly tested:
- ✅ Empty module lowering
- ✅ Function template creation
- ✅ Pipeline lowering (simple and complex)
- ✅ Pipeline steps with and without explicit arguments
- ✅ JSON stability and canonicity
- ✅ Type stringification
- ✅ IR to_dict conversions

## Next Steps

Phase 5 complete. Ready to proceed to **Phase 6 — PrimaryIR + canonical JSON bundle emission**, which will tie this IR into final BoR-ready artifacts.

