# Phase 2 — Parsing

## Overview

Implemented a complete recursive-descent parser for RLang that converts token streams into Abstract Syntax Trees (ASTs). The parser handles type aliases, function declarations, and pipeline definitions with full expression parsing support.

## Implementation Details

### Files Created

1. **`rlang/parser/ast.py`** (205 lines)
   - Complete AST node definitions using `@dataclass`
   - Base `Node` class with position tracking (start_line, start_col, end_line, end_col)
   - Type system: `TypeExpr`, `SimpleType`, `GenericType`
   - Top-level declarations: `TypeAlias`, `FunctionDecl`, `PipelineDecl`
   - Expression hierarchy: `Expr`, `Identifier`, `Literal`, `BinaryOp`, `Call`, `AttributeRef`
   - Statement hierarchy: `Statement`, `ExprStmt`
   - Support structures: `Param`, `PipelineStep`
   - `Module` as root AST node
   - Full `__all__` export list

2. **`rlang/parser/parser.py`** (683 lines)
   - `Parser` class: Recursive-descent parser implementation
   - `ParseError` exception with position information
   - `parse()` convenience function
   - Grammar support:
     - **Type aliases**: `type Name = TypeExpr;`
     - **Function declarations**: `fn Name(params?) -> TypeExpr?;`
     - **Pipeline declarations**: `pipeline Name(TypeExpr?) -> TypeExpr? { steps }`
     - **Expressions**: identifiers, literals, binary ops, function calls
     - **Type expressions**: simple types and generics (extensible)
   - Operator precedence: multiplication/division before addition/subtraction
   - Accurate position tracking for all AST nodes

3. **`rlang/parser/__init__.py`** (35 lines)
   - Public API exports: All AST nodes and parser functions

4. **`tests/test_parser.py`** (330+ lines)
   - Comprehensive test suite with 20+ test cases covering:
     - Empty module parsing
     - Type alias parsing (single and multiple)
     - Function declaration parsing (with/without params, with/without return type)
     - Pipeline parsing (simple, with arguments, complex)
     - Expression parsing (literals, binary operations, nested calls)
     - Error handling (missing semicolons, invalid syntax, unclosed braces)
     - Complex module with multiple declarations

## Key Features

- **Recursive-descent parsing**: Clean, maintainable parser structure
- **Position tracking**: Accurate line/column information for error reporting
- **Error handling**: Raises `ParseError` with position information
- **Expression parsing**: Full support for literals, identifiers, binary operations, function calls
- **Type system**: Extensible type expression parsing (supports generics structure)
- **Deterministic**: Pure, stateless parser with no side effects

## Grammar Supported

### Type Aliases
```
type UserId = Int;
type Email = String;
```

### Function Declarations
```
fn add(a: Int, b: Int) -> Int;
fn greet(name: String);
fn getValue() -> Int;
```

### Pipeline Declarations
```
pipeline main(Input) -> Output {
  validate -> transform -> persist
}

pipeline run() {
  load("file.json") -> normalize(42, "x")
}
```

### Expressions
- Literals: `42`, `3.14`, `"hello"`, `true`, `false`, `null`
- Identifiers: `x`, `foo`, `bar`
- Binary operations: `1 + 2`, `3 * 4`, `10 / 2`
- Function calls: `foo(x, y)`, `transform(data)`
- Nested calls: `process(transform(data))`

## Integration

- Uses existing lexer infrastructure (`rlang.lexer`)
- Follows project invariants (no empty files, deterministic, testable)
- AST nodes integrate with canonical JSON utilities (ready for serialization)
- Ready for Phase 3 (Symbol Resolution)

## Testing

All parser functionality is thoroughly tested:
- ✅ Empty module parsing
- ✅ Type alias parsing
- ✅ Function declaration parsing
- ✅ Pipeline parsing (simple and complex)
- ✅ Expression parsing (all forms)
- ✅ Error handling (invalid syntax detection)

## Next Steps

Phase 2 complete. Ready to proceed to **Phase 3 — Symbol Resolution**, which will build symbol tables and resolve references in the AST.

