# Compiler Architecture

## Overview

The RLang compiler follows a traditional multi-pass compiler architecture, enhanced with proof generation capabilities. The pipeline transforms source code through lexical analysis, parsing, symbol resolution, type checking, IR generation, and canonical JSON emission.

## Compiler Pipeline

### Phase 1: Lexical Analysis (Lexer)

The lexer tokenizes source code into a stream of tokens. It handles comments, various float formats, string literals, and maintains accurate line/column tracking for error reporting.

### Phase 2: Parsing

The parser builds an Abstract Syntax Tree (AST) from tokens using recursive descent parsing. It handles operator precedence, pipeline composition, and explicit arguments.

### Phase 3: Symbol Resolution

The resolver builds a symbol table mapping identifiers to their declarations. All declarations are in global scope with no shadowing allowed.

### Phase 4: Type Checking

The type checker validates type correctness and infers types. It enforces function call argument matching, pipeline composition type matching, and type alias resolution.

### Phase 5: IR Lowering

The lowering phase converts the type-checked AST into an Intermediate Representation (IR). IR is execution-ready, canonical, deterministic, and hashable.

### Phase 6: Primary IR Builder

The primary IR builder creates the final `PrimaryProgramIR` structure, which is then serialized to canonical JSON with sorted keys for deterministic hashing.

## Key Architectural Principles

1. **Separation of Concerns**: Each phase has a single responsibility
2. **Immutability**: AST and IR nodes are immutable dataclasses
3. **Pure Functions**: Compiler phases are pure (no side effects)
4. **Deterministic Output**: Every phase produces deterministic results
5. **Canonical Serialization**: JSON output is always canonical (sorted keys)

