# RLang Language Specification

## Overview

RLang is a domain-specific language designed for expressing **deterministic reasoning pipelines**—sequences of computational steps that produce verifiable, reproducible results. Unlike general-purpose languages, RLang enforces determinism at the language level, making it impossible to write non-deterministic programs.

## Syntax

RLang uses a simple, declarative syntax focused on type definitions, function declarations, and pipeline composition.

### Type Definitions

```rlang
type UserId = Int;
type Email = String;
type Price = Float;
type IsActive = Bool;
```

### Function Declarations

Functions are declared with their signatures but not implemented in RLang (implementations come from the runtime function registry):

```rlang
fn increment(x: Int) -> Int;
fn add(x: Int, y: Int) -> Int;
fn formatEmail(name: String, domain: String) -> String;
```

### Pipeline Definitions

Pipelines compose functions into sequential execution chains:

```rlang
pipeline process(Int) -> Int {
  increment -> double
}
```

## Type System

RLang supports five primitive types: `Int`, `Float`, `String`, `Bool`, and `Unit`. Type aliases provide semantic meaning and enable domain modeling. The compiler infers types for pipeline step return types, binary operation result types, and function call argument types.

## Control Flow: if/else (v0.2)

RLang v0.2 introduces **pure, deterministic control flow** via `if/else` expressions inside pipeline bodies. The condition must evaluate to `Bool`, and both `then` and `else` blocks must produce the same output type. If `else` is omitted, it is treated as an implicit identity (pass-through).

## Deterministic Semantics

RLang enforces determinism through: no randomness, no I/O, no time-dependent operations, pure functions, and fixed evaluation order. This ensures bit-for-bit reproducible execution suitable for cryptographic verification.

