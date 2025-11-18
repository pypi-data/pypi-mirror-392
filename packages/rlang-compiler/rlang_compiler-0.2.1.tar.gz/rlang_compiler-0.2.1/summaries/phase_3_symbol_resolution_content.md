# Phase 3 — Symbol Resolution

## Overview

Implemented a complete symbol resolution system for the RLang compiler. The resolver builds a global symbol table containing types, functions, and pipelines, and validates that all referenced types exist (either as primitives or defined aliases).

## Implementation Details

### Files Created

1. **`rlang/semantic/symbols.py`** (140 lines)
   - `SymbolKind` enum: TYPE, FUNCTION, PIPELINE
   - `Symbol` dataclass: Represents a symbol with name, kind, node, and optional metadata
   - `SymbolTable` class: Hierarchical symbol table with parent chain support
     - `define()`: Define a symbol (raises ValueError on duplicate)
     - `lookup()`: Look up symbol in current table and parent chain
     - `__contains__()` and `__getitem__()`: Convenience methods
   - `PRIMITIVE_TYPES`: Set of built-in types (Int, Float, String, Bool, Unit)
   - `is_primitive_type()`: Helper function to check primitive types
   - Full `__all__` export list

2. **`rlang/semantic/resolver.py`** (320 lines)
   - `ResolutionError` exception: Error with position information
   - `ResolutionResult` dataclass: Contains resolved module and global symbol table
   - `Resolver` class: Main resolver implementation
     - `__init__()`: Initialize with module and pre-load primitive types
     - `resolve()`: Main resolution driver with four passes:
       1. Register all type alias names
       2. Resolve type alias targets
       3. Register functions and pipelines
       4. Validate all referenced types
     - Helper methods:
       - `_preload_primitive_types()`: Load primitive type symbols
       - `_register_type_aliases()`: Register type alias declarations
       - `_resolve_type_alias_targets()`: Resolve and validate alias targets
       - `_register_functions_and_pipelines()`: Register function and pipeline declarations
       - `_validate_functions()`: Validate function parameter and return types
       - `_validate_pipelines()`: Validate pipeline input and output types
       - `_ensure_type_exists()`: Ensure type expression references valid type
       - `_resolve_type_expr()`: Resolve and validate type expression
   - `resolve_module()`: Public convenience function
   - Full `__all__` export list

3. **`rlang/semantic/__init__.py`** (20 lines)
   - Public API exports: All symbols and resolver components

4. **`tests/test_resolver.py`** (280+ lines)
   - Comprehensive test suite with 15+ test cases covering:
     - Primitive type pre-loading
     - Type alias registration and resolution
     - Duplicate definition detection
     - Unknown type error detection
     - Function registration and type validation
     - Pipeline registration and type validation
     - Complex module resolution
     - Edge cases (functions/pipelines without types)

## Key Features

- **Four-pass resolution**: Clean separation of concerns
  - Pass 1: Register type aliases
  - Pass 2: Resolve type alias targets
  - Pass 3: Register functions and pipelines
  - Pass 4: Validate all type references
- **Primitive type support**: Built-in types (Int, Float, String, Bool, Unit) always available
- **Type validation**: Ensures all referenced types exist (primitives or aliases)
- **Error handling**: `ResolutionError` with accurate position information
- **Duplicate detection**: Prevents duplicate definitions of same name
- **Deterministic**: Pure, stateless resolver (except for its own symbol table)

## Resolution Process

1. **Pre-load primitives**: All primitive types are added to symbol table at initialization
2. **Register type aliases**: All `type Name = TypeExpr;` declarations are registered
3. **Resolve alias targets**: Type alias targets are validated and resolved
4. **Register functions/pipelines**: Function and pipeline declarations are registered
5. **Validate types**: All type references in functions and pipelines are validated

## Type Validation

- **SimpleType**: Checks if name is primitive or defined type alias
- **GenericType**: Validates base type and recursively validates type arguments
- **Error reporting**: Includes line/column information from AST nodes

## Integration

- Uses existing parser infrastructure (`rlang.parser`)
- Works with AST nodes from Phase 2
- Follows project invariants (no empty files, deterministic, testable)
- Ready for Phase 4 (Type Checking)

## Testing

All resolver functionality is thoroughly tested:
- ✅ Primitive type pre-loading
- ✅ Type alias registration and resolution
- ✅ Duplicate definition detection
- ✅ Unknown type error detection
- ✅ Function type validation
- ✅ Pipeline type validation
- ✅ Complex module resolution
- ✅ Edge cases

## Next Steps

Phase 3 complete. Ready to proceed to **Phase 4 — Type Checking**, which will use the symbol table to perform deeper type analysis and validation.

