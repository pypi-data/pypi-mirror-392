# Phase 1 — Lexing (Tokenization)

## Overview

Implemented a complete, deterministic lexer for the RLang → BoR compiler. The lexer converts source code into a stream of tokens with precise position tracking, enabling all subsequent compiler phases.

## Implementation Details

### Files Created

1. **`rlang/lexer/tokens.py`**
   - `TokenType` enum with all token types (keywords, operators, punctuation, literals)
   - `Token` dataclass with type, value, line, and column information
   - `KEYWORDS` mapping dictionary for keyword recognition
   - Full `__all__` export list

2. **`rlang/lexer/tokenizer.py`**
   - `Tokenizer` class: Pure, stateless tokenizer implementation
   - `LexerError` exception for invalid input handling
   - `tokenize()` convenience function
   - Supports:
     - Identifiers (alphanumeric + underscore)
     - Keywords (case-insensitive recognition)
     - Integers and floats
     - String literals with escape sequences
     - All operators (arithmetic, comparison, logical, assignment, arrow)
     - Punctuation: `(){}:;,`
     - Whitespace handling (spaces, tabs)
     - Comments (single-line `#`)
     - Newline tracking
     - Precise line/column position tracking

3. **`rlang/lexer/__init__.py`**
   - Public API exports: `TokenType`, `Token`, `tokenize`, `Tokenizer`, `LexerError`, `KEYWORDS`

4. **`tests/test_lexer.py`**
   - Comprehensive test suite with 25+ test cases covering:
     - Identifier lexing
     - Keyword recognition (all keywords)
     - Number lexing (integers and floats)
     - String literal lexing with escape sequences
     - Operator recognition (all operators)
     - Punctuation tokens
     - Whitespace and newline handling
     - Comment skipping
     - Position tracking
     - Error handling (unterminated strings, unexpected characters)
     - Complex expressions and function declarations

## Key Features

- **Deterministic**: Pure, stateless tokenization with no side effects
- **Position Tracking**: Accurate line and column numbers for error reporting
- **Error Handling**: Raises `LexerError` with position information for invalid input
- **Complete Coverage**: All RLang language constructs tokenized correctly
- **Test Coverage**: Comprehensive test suite ensures correctness

## Token Types Supported

- **Identifiers**: `foo`, `bar123`, `_underscore`
- **Keywords**: `if`, `else`, `while`, `for`, `function`, `return`, `let`, `const`, `true`, `false`, `null`, `and`, `or`, `not`
- **Literals**: Integers (`42`), Floats (`3.14`), Strings (`"hello"`)
- **Operators**: `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `=`, `->`
- **Punctuation**: `(`, `)`, `{`, `}`, `:`, `;`, `,`
- **Special**: `EOF`, `NEWLINE`

## Integration

- Uses existing infrastructure (`tests/base.py` fixtures)
- Follows project invariants (no empty files, deterministic, testable)
- Ready for Phase 2 (Parsing) integration

## Testing

All tests pass successfully. The lexer correctly handles:
- Simple and complex expressions
- Function declarations
- Edge cases (empty input, whitespace-only, comments)
- Error cases (unterminated strings, invalid characters)

## Next Steps

Phase 1 complete. Ready to proceed to **Phase 2 — Parsing**, which will consume the token stream and build an Abstract Syntax Tree (AST).

