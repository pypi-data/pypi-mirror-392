# Phase 4 — Type Checking

## Overview

Implemented a complete type checking system for the RLang compiler. The type checker validates function signatures, pipeline wiring, step arguments, and catches type/arity mismatches before IR generation.

## Implementation Details

### Files Created

1. **`rlang/types/type_system.py`** (70 lines)
   - `RType` dataclass (frozen): Internal type representation with `name` and `args` tuple
   - Methods: `is_primitive()`, `__str__()` for string representation
   - `rtype_from_type_expr()`: Converts AST `TypeExpr` nodes to `RType`
   - Supports simple types and generic types with type arguments
   - Full `__all__` export list

2. **`rlang/types/type_checker.py`** (443 lines)
   - `TypeCheckError` exception: Error with position information
   - `TypeCheckResult` dataclass: Contains type-checked module, symbol table, and expression type mappings
   - `TypeChecker` class: Main type checker implementation
     - `check()`: Main driver that type-checks functions and pipelines
     - `_check_functions()`: Type-checks function signatures (prepares for future body checking)
     - `_check_pipelines()`: Type-checks pipeline wiring, step arguments, and arity
     - `_get_function_signature()`: Gets function signature as RTypes
     - `_infer_expr_type()`: Infers types of expressions (literals, identifiers, calls)
     - `_rtype_equal()`: Structural equality comparison for RTypes
   - `type_check()`: Public convenience function
   - Full `__all__` export list

3. **`rlang/types/__init__.py`** (15 lines)
   - Public API exports: All type system and type checker components

4. **`tests/test_type_checker.py`** (200+ lines)
   - Comprehensive test suite with 15+ test cases covering:
     - Empty module type checking
     - Simple function and pipeline wiring (happy path)
     - Pipeline input type mismatch
     - Step-to-step wiring mismatch
     - Pipeline output type mismatch
     - Step argument literal type checking
     - Step argument type mismatch
     - Unbound identifier detection
     - Step arity mismatch
     - Unknown step detection
     - Step not a function error
     - Empty pipeline with types
     - Complex pipeline type checking

## Key Features

- **Internal type model**: `RType` for consistent type representation during checking
- **Pipeline wiring validation**: Ensures input/output types match step signatures
- **Step chaining**: Validates that each step's return type matches next step's first parameter
- **Argument type checking**: Validates literal types and function call argument types
- **Arity checking**: Ensures correct number of arguments for steps and function calls
- **Expression type inference**: Infers types for literals, function calls
- **Implicit arguments**: Pipeline input and previous step outputs are implicitly passed
- **Error reporting**: `TypeCheckError` with accurate position information

## Type Checking Process

1. **Function signature checking**: Converts function parameter and return types to `RType`
2. **Pipeline checking**:
   - Validates pipeline input matches first step's first parameter
   - Validates each step's return type matches next step's first parameter
   - Validates pipeline output matches last step's return type
   - Checks step argument types and arity
   - Ensures steps reference valid functions

## Expression Type Inference

- **Literals**: Infers type from Python value type (int→Int, float→Float, str→String, bool→Bool, None→Unit)
- **Identifiers**: Currently raises error (unbound identifiers not supported yet)
- **Function calls**: Infers return type from function signature, validates argument types

## Pipeline Step Argument Handling

- **First step**: Pipeline input is implicitly passed as first argument
- **Subsequent steps**: Previous step's return value is implicitly passed as first argument
- **Explicit arguments**: Additional arguments beyond the implicit first argument are type-checked

## Integration

- Uses existing resolver infrastructure (`rlang.semantic`)
- Works with AST nodes from Phase 2
- Follows project invariants (no empty files, deterministic, testable)
- Ready for Phase 5 (Lowering to BoR StepIR + PipelineIR)

## Testing

All type checker functionality is thoroughly tested:
- ✅ Empty module type checking
- ✅ Function and pipeline wiring validation
- ✅ Type mismatch detection (input, output, step-to-step)
- ✅ Argument type and arity checking
- ✅ Unbound identifier detection
- ✅ Complex pipeline type checking
- ✅ Error cases

## Next Steps

Phase 4 complete. Ready to proceed to **Phase 5 — Lowering to BoR StepIR + PipelineIR**, which will use the type-checked module to generate intermediate representation.

