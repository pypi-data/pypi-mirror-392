# The Physics of the RLang Compiler
## The Deterministic Execution & Proof Architecture Specification (v0.2.x → v1.0)

**Version:** 0.2.1  
**Date:** November 2025  
**Status:** Formal Specification

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [The Three Non-Negotiable Invariants](#2-the-three-non-negotiable-invariants-compiler-physics)
3. [Architecture Overview](#3-architecture-overview-birds-eye-structural-diagram)
4. [Language Semantics (Formal)](#4-language-semantics-formal)
5. [IR Specification (The Real Physics Layer)](#5-ir-specification-the-real-physics-layer)
6. [Canonicalization Specification](#6-canonicalization-specification)
7. [Execution Semantics](#7-execution-semantics)
8. [Proof System Architecture](#8-proof-system-architecture)
9. [The Untouchable Core (Frozen Physics)](#9-the-untouchable-core-frozen-physics)
10. [Expandable Surfaces (Safe to Extend)](#10-expandable-surfaces-safe-to-extend)
11. [Rules for Deterministic Expansion](#11-rules-for-deterministic-expansion)
12. [Meta-Architecture for v0.3 → v1.0](#12-meta-architecture-for-v03--v10)
13. [Change Control: Golden Files + Determinism Tests](#13-change-control-golden-files--determinism-tests)
14. [Reference Appendix](#14-reference-appendix)
15. [Appendix: Change Log of Compiler Physics Updates (Auto-Reconstructed)](#15-appendix-change-log-of-compiler-physics-updates-auto-reconstructed)

---

## 1. Purpose and Scope

### 1.1 Why a Deterministic Compiler Exists

RLang is not a general-purpose programming language. It is a **domain-specific language (DSL) for deterministic reasoning pipelines**—computational sequences that must produce **bit-for-bit identical results** across all executions, environments, and time periods.

This determinism is not optional; it is the **fundamental requirement** that enables:

- **Cryptographic Verification**: Proof bundles can be verified without re-execution
- **Trustless Execution**: Results can be independently verified by third parties
- **Reproducible Science**: Computational results remain stable across time
- **Blockchain Integration**: Execution traces can be committed to immutable ledgers

### 1.2 Why RLang is Not a General-Purpose PL

General-purpose languages (Python, JavaScript, Rust) intentionally allow:
- Non-deterministic behavior (random numbers, timestamps, I/O)
- Side effects (mutation, network calls, file operations)
- Environment-dependent execution (platform-specific behavior)

RLang **prohibits** all of these. Every construct must be:
- **Pure**: No side effects, no hidden state
- **Deterministic**: Same input → same output, always
- **Stateless**: No mutable global state
- **Time-independent**: No time-based operations
- **Order-independent**: No unordered collections in IR

### 1.3 Why Determinism + Cryptographic Proofs Define the "Physics Layer"

The "physics layer" of RLang is the set of **invariant rules** that cannot be violated without breaking the fundamental guarantees of the language. These rules are analogous to physical laws:

- **Conservation of Determinism**: Information flow must preserve determinism
- **Canonical Equivalence**: Same semantic structure → same canonical representation
- **Hash Stability**: Same proof bundle → same cryptographic hash
- **Trace Completeness**: Every execution step must be recorded

These invariants are **non-negotiable**. They form the foundation upon which all language features are built.

---

## 2. The Three Non-Negotiable Invariants (Compiler Physics)

### 2.1 Invariant 1: Deterministic Semantics Invariant

**Formal Definition:**

For any RLang program `P` and input value `x`, there exists a unique output value `y` such that:

```
Eval(P, x) = y
```

This must hold **regardless of**:
- Execution environment (OS, hardware, Python version)
- Execution time (today vs. tomorrow)
- Execution order (if multiple valid orders exist, they must be equivalent)
- Random number generators (none allowed)
- External state (none allowed)

**Mathematical Properties:**

- **Functionality**: `∀P, x. ∃!y. Eval(P, x) = y`
- **Idempotency**: `Eval(P, x) = Eval(P, x)` (always)
- **Compositionality**: `Eval(P₁; P₂, x) = Eval(P₂, Eval(P₁, x))`

**Violation Examples:**

❌ **FORBIDDEN**: Using `time.time()` in function registry  
❌ **FORBIDDEN**: Reading from `/dev/urandom`  
❌ **FORBIDDEN**: Non-deterministic iteration order  
❌ **FORBIDDEN**: Floating-point operations that vary by platform

✅ **ALLOWED**: Pure mathematical operations  
✅ **ALLOWED**: Deterministic string operations  
✅ **ALLOWED**: Fixed-order list operations

### 2.2 Invariant 2: Deterministic Proof Shape Invariant

**Formal Definition:**

For any RLang program `P` and input value `x`, there exists a unique execution trace `trace` such that:

```
TRP(P, x) = trace
```

The trace must be:
- **Complete**: Every step execution is recorded
- **Ordered**: Steps appear in execution order
- **Deterministic**: Same execution → same trace
- **Canonical**: Trace structure is stable across serializations

**Trace Structure (TRP v1):**

```python
trace = {
    "steps": [
        {
            "index": int,           # 0-based step index
            "step_name": str,        # Function name
            "template_id": str,     # Template reference
            "input": Any,           # Input snapshot
            "output": Any           # Output snapshot
        },
        ...
    ],
    "branches": [
        {
            "index": int,           # IF step index
            "path": "then" | "else",
            "condition_value": bool
        },
        ...
    ]
}
```

**Hash Invariants:**

```
Hash(canonical(P)) = H_IR          # Program IR hash
Hash(trace) = HRICH                 # Execution trace hash
Hash(H_IR | HRICH) = HMASTER        # Master hash
```

**Violation Examples:**

❌ **FORBIDDEN**: Recording steps in non-deterministic order  
❌ **FORBIDDEN**: Including timestamps in trace  
❌ **FORBIDDEN**: Non-deterministic trace serialization  
❌ **FORBIDDEN**: Omitting steps from trace

✅ **ALLOWED**: Recording all steps in execution order  
✅ **ALLOWED**: Canonical JSON serialization  
✅ **ALLOWED**: Deterministic branch recording

### 2.3 Invariant 3: Single-Source Specification Invariant

**Formal Definition:**

For any RLang program `P`, there exists a unique canonical representation `canonical(P)` such that:

```
canonical(P₁) = canonical(P₂) ⟺ P₁ ≡ P₂
```

Where `≡` denotes semantic equivalence.

**Canonical Representation Rules:**

1. **Key Ordering**: All dictionary keys must be sorted alphabetically
2. **Value Normalization**: Floats normalized, integers preferred where possible
3. **Structure Stability**: Same structure → same JSON string
4. **Encoding Stability**: UTF-8, no BOM, consistent line endings

**Hash Stability:**

```
Hash(canonical(P)) = H_IR
```

This hash must be **stable** across:
- Different compiler versions (if semantics unchanged)
- Different platforms
- Different Python versions
- Different serialization libraries

**Violation Examples:**

❌ **FORBIDDEN**: Non-deterministic key ordering  
❌ **FORBIDDEN**: Platform-dependent float formatting  
❌ **FORBIDDEN**: Non-canonical JSON serialization  
❌ **FORBIDDEN**: Including compiler metadata in canonical form

✅ **ALLOWED**: Alphabetically sorted keys  
✅ **ALLOWED**: Normalized float representation  
✅ **ALLOWED**: Consistent JSON formatting

---

## 3. Architecture Overview (Bird's Eye Structural Diagram)

### 3.1 Compilation Pipeline

```
┌─────────┐
│ Source  │
│  Code   │
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (EXTENSION-SAFE)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │  Lexer   │───▶│  Parser  │───▶│ Resolver │             │
│  │          │    │          │    │          │             │
│  │ PLUGGABLE│    │ PLUGGABLE│    │ PLUGGABLE│             │
│  └──────────┘    └──────────┘    └──────────┘             │
│                                                              │
│                          │                                   │
│                          ▼                                   │
│                  ┌──────────────┐                            │
│                  │ Type Checker │                            │
│                  │              │                            │
│                  │ EXTENSION-   │                            │
│                  │ SAFE         │                            │
│                  └──────────────┘                            │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              MIDDLE-END (SAFE BUT STRICT)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                  ┌──────────────┐                            │
│                  │   Lowering   │                            │
│                  │              │                            │
│                  │ MUST REMAIN  │                            │
│                  │ DETERMINISTIC│                            │
│                  └──────┬───────┘                            │
│                         │                                     │
│                         ▼                                     │
│                  ┌──────────────┐                            │
│                  │      IR      │                            │
│                  │              │                            │
│                  │   PHYSICS   │                            │
│                  │    LAYER    │                            │
│                  └──────┬───────┘                            │
└─────────────────────────┼─────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (VERY SENSITIVE)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │ Canonicalizer│───▶│   Executor   │                      │
│  │              │    │              │                      │
│  │    FIXED     │    │ MUST REMAIN  │                      │
│  │              │    │ DETERMINISTIC│                      │
│  └──────┬───────┘    └──────┬───────┘                      │
│         │                    │                               │
│         ▼                    ▼                               │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │   Canonical  │    │  Proof Trace │                      │
│  │     JSON     │    │   (TRP v1)   │                      │
│  │              │    │              │                      │
│  │    FIXED     │    │    FIXED     │                      │
│  └──────┬───────┘    └──────┬───────┘                      │
│         │                    │                               │
│         └──────────┬─────────┘                               │
│                    ▼                                         │
│            ┌──────────────┐                                  │
│            │   Hashing    │                                  │
│            │              │                                  │
│            │ HMASTER/     │                                  │
│            │ HRICH        │                                  │
│            │              │                                  │
│            │    FIXED     │                                  │
│            └──────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Component Classification

| Component | Classification | Rationale |
|-----------|----------------|-----------|
| **Lexer** | `PLUGGABLE` | Tokenization is syntax-level; can extend for new keywords/symbols |
| **Parser** | `PLUGGABLE` | AST construction is syntax-level; can add new AST nodes |
| **Resolver** | `PLUGGABLE` | Symbol resolution is syntax-level; can extend symbol table |
| **Type Checker** | `EXTENSION-SAFE` | Type checking must remain deterministic but can add new types |
| **Lowering** | `MUST REMAIN DETERMINISTIC` | IR generation must preserve semantics deterministically |
| **IR** | `PHYSICS LAYER` | IR structure defines execution model; changes break proofs |
| **Canonicalizer** | `FIXED` | Canonical JSON rules cannot change without breaking hashes |
| **Executor** | `MUST REMAIN DETERMINISTIC` | Execution semantics must remain deterministic |
| **Proof System** | `FIXED` | TRP structure is frozen; extensions via versioning |
| **Hashing** | `FIXED` | Hash algorithms and structure are frozen |

### 3.3 Data Flow

```
Source Code
    │
    ├─▶ Lexer → Tokens
    │
    ├─▶ Parser → AST
    │
    ├─▶ Resolver → Resolved AST
    │
    ├─▶ Type Checker → Typed AST
    │
    ├─▶ Lowering → IR Bundle
    │
    ├─▶ Canonicalizer → Canonical JSON
    │                    │
    │                    └─▶ Hash → H_IR
    │
    └─▶ Executor → Proof Trace (TRP)
                        │
                        └─▶ Hash → HRICH
                                │
                                └─▶ Combine → HMASTER
```

---

## 4. Language Semantics (Formal)

### 4.1 Type System

#### 4.1.1 Primitive Types

RLang defines five primitive types:

- **`Int`**: 64-bit signed integers (Python `int`, unbounded)
- **`Float`**: IEEE 754 double-precision floating-point (Python `float`)
- **`String`**: UTF-8 encoded strings (Python `str`)
- **`Bool`**: Boolean values `true` / `false` (Python `bool`)
- **`Unit`**: Unit type (Python `None`)

**Type Semantics:**

```
Type ::= Int | Float | String | Bool | Unit
```

**Type Equivalence:**

Two types `T₁` and `T₂` are equivalent (`T₁ ≡ T₂`) if:
- Both are primitive and have the same name, OR
- Both are generic with same name and equivalent type arguments

#### 4.1.2 Type Aliases

Type aliases provide semantic meaning:

```rlang
type UserId = Int;
type Email = String;
```

**Semantics:**

```
type_alias ::= type IDENTIFIER = TypeExpr;
```

Type aliases are **transparent** during type checking—they resolve to their underlying types.

#### 4.1.3 Future Types (v0.3+)

Planned type extensions:

- **`List[T]`**: Immutable lists of type `T`
- **`Record { f₁: T₁, ..., fₙ: Tₙ }`**: Named field records
- **`Map[K, V]`**: Immutable key-value maps (deterministically ordered)

### 4.2 Expressions

#### 4.2.1 Literal Expressions

```
Literal ::= INTEGER | FLOAT | STRING | BOOLEAN
```

**Evaluation:**

```
Eval(42) = 42
Eval(3.14) = 3.14
Eval("hello") = "hello"
Eval(true) = True
Eval(false) = False
```

#### 4.2.2 Identifier Expressions

```
Identifier ::= IDENTIFIER
```

**Special Identifiers:**

- **`__value`**: Current pipeline value (runtime context)

**Evaluation:**

```
Eval(__value, ctx) = ctx.current_value
```

#### 4.2.3 Binary Operations

```
BinaryOp ::= Expr OP Expr
OP ::= + | - | * | / | > | < | >= | <= | == | !=
```

**Arithmetic Operations:**

```
Eval(e₁ + e₂, ctx) = Eval(e₁, ctx) + Eval(e₂, ctx)
Eval(e₁ - e₂, ctx) = Eval(e₁, ctx) - Eval(e₂, ctx)
Eval(e₁ * e₂, ctx) = Eval(e₁, ctx) * Eval(e₂, ctx)
Eval(e₁ / e₂, ctx) = Eval(e₁, ctx) / Eval(e₂, ctx)  [if Eval(e₂, ctx) ≠ 0]
```

**Comparison Operations:**

```
Eval(e₁ > e₂, ctx) = Eval(e₁, ctx) > Eval(e₂, ctx)
Eval(e₁ < e₂, ctx) = Eval(e₁, ctx) < Eval(e₂, ctx)
Eval(e₁ >= e₂, ctx) = Eval(e₁, ctx) >= Eval(e₂, ctx)
Eval(e₁ <= e₂, ctx) = Eval(e₁, ctx) <= Eval(e₂, ctx)
Eval(e₁ == e₂, ctx) = Eval(e₁, ctx) == Eval(e₂, ctx)
Eval(e₁ != e₂, ctx) = Eval(e₁, ctx) != Eval(e₂, ctx)
```

**Type Rules:**

- Arithmetic: `Int + Int → Int`, `Float + Float → Float`, `Int + Float → Float`
- Comparison: `T × T → Bool` (for comparable types)

#### 4.2.4 Function Calls

```
Call ::= IDENTIFIER ( Expr₁, ..., Exprₙ )
```

**Evaluation:**

```
Eval(f(e₁, ..., eₙ), ctx) = fn_registry[f](Eval(e₁, ctx), ..., Eval(eₙ, ctx))
```

**Type Rules:**

```
f : T₁ × ... × Tₙ → T
e₁ : T₁, ..., eₙ : Tₙ
─────────────────────────
f(e₁, ..., eₙ) : T
```

#### 4.2.5 Conditional Expressions (v0.2+)

```
IfExpr ::= if ( Expr ) { Steps } [ else { Steps } ]
```

**Evaluation:**

```
Eval(if (c) { s₁ } else { s₂ }, ctx) = 
    if Eval(c, ctx) then Eval(s₁, ctx) else Eval(s₂, ctx)
```

**Type Rules:**

```
c : Bool
s₁ : T
s₂ : T
─────────────────────────
if (c) { s₁ } else { s₂ } : T
```

**Determinism Requirement:**

The condition `c` must be a **pure expression**—no side effects, no randomness, no time-dependent operations.

### 4.3 Pipeline Semantics

#### 4.3.1 Pipeline Definition

```
Pipeline ::= pipeline IDENTIFIER ( Type ) -> Type { Steps }
Steps ::= Step₁ -> Step₂ -> ... -> Stepₙ
```

**Evaluation:**

```
Eval(pipeline main(T_in) -> T_out { s₁ -> ... -> sₙ }, x) =
    Eval(sₙ, Eval(sₙ₋₁, ..., Eval(s₁, x)...))
```

**Composition:**

```
Eval(s₁ -> s₂, x) = Eval(s₂, Eval(s₁, x))
```

#### 4.3.2 Step Semantics

**Function Step:**

```
Eval(f, x) = fn_registry[f](x)
```

**Conditional Step:**

```
Eval(if (c) { s₁ } else { s₂ }, x) =
    if Eval(c, x) then Eval(s₁, x) else Eval(s₂, x)
```

### 4.4 Deterministic Requirements

#### 4.4.1 No Randomness

❌ **FORBIDDEN:**
- Random number generation
- Non-deterministic algorithms
- Probabilistic data structures

#### 4.4.2 No I/O

❌ **FORBIDDEN:**
- File system access
- Network operations
- Standard input/output
- Environment variables (except compile-time)

#### 4.4.3 No Time Dependence

❌ **FORBIDDEN:**
- Timestamps
- System time
- Date/time operations

#### 4.4.4 Fixed Evaluation Order

✅ **REQUIRED:**
- Left-to-right evaluation
- Sequential pipeline execution
- Deterministic branch selection

---

## 5. IR Specification (The Real Physics Layer)

### 5.1 IR Design Principles

The Intermediate Representation (IR) is the **physics layer** of RLang. It defines:

1. **What can be executed**: Only IR nodes can appear in execution traces
2. **How execution proceeds**: IR structure determines execution order
3. **What is provable**: Only IR-level operations generate proof records

**IR Invariants:**

1. **Purity**: Every IR node is pure (no side effects)
2. **Determinism**: IR evaluation is deterministic
3. **Canonicalizability**: Every IR node can be serialized to canonical JSON
4. **Completeness**: All semantic constructs must lower to IR

### 5.2 Current IR Node Types (v0.2.1)

#### 5.2.1 IRExpr

Base class for all expressions in IR.

```python
@dataclass(frozen=True)
class IRExpr:
    kind: str  # "literal" | "identifier" | "binary_op" | "call"
    # ... fields depend on kind
```

**Kinds:**

1. **`literal`**: Literal values
   ```python
   IRExpr(kind="literal", value=42)
   ```

2. **`identifier`**: Variable references
   ```python
   IRExpr(kind="identifier", name="__value")
   ```

3. **`binary_op`**: Binary operations
   ```python
   IRExpr(kind="binary_op", op="+", left=..., right=...)
   ```

4. **`call`**: Function calls
   ```python
   IRExpr(kind="call", func="inc", args=[...])
   ```

#### 5.2.2 IRIf

Conditional execution node.

```python
@dataclass(frozen=True)
class IRIf:
    condition: IRExpr
    then_steps: list[PipelineStepIR]
    else_steps: list[PipelineStepIR]
```

**Semantics:**

- Condition must evaluate to `Bool`
- Both branches must produce same output type
- Execution is deterministic based on condition value

#### 5.2.3 PipelineStepIR

Single step in a pipeline.

```python
@dataclass(frozen=True)
class PipelineStepIR:
    index: int
    name: str
    template_id: str
    arg_types: list[str]
    input_type: str | None
    output_type: str | None
```

#### 5.2.4 PipelineIR

Complete pipeline definition.

```python
@dataclass(frozen=True)
class PipelineIR:
    id: str
    name: str
    input_type: str | None
    output_type: str | None
    steps: list[PipelineStepIR | IRIf]
```

#### 5.2.5 StepTemplateIR

Function template definition.

```python
@dataclass(frozen=True)
class StepTemplateIR:
    id: str
    name: str
    fn_name: str
    param_types: list[str]
    return_type: str | None
    rule_repr: str
    version: str
```

### 5.3 Rules for Adding New IR Nodes

#### 5.3.1 IR Node Requirements

Every new IR node **MUST**:

1. **Be Pure**: No side effects, no hidden state
2. **Be Deterministic**: Same inputs → same outputs
3. **Be Canonicalizable**: Implement `to_dict()` with sorted keys
4. **Have Fixed Evaluation Order**: No non-deterministic iteration
5. **Preserve Type Information**: Include type annotations

#### 5.3.2 Example: Adding IRRecord (v0.3)

**Step 1: Define IR Node**

```python
@dataclass(frozen=True)
class IRRecord:
    """IR representation of a record construction."""
    fields: dict[str, IRExpr]  # Field name → expression
    
    def to_dict(self) -> dict[str, Any]:
        """Canonical dictionary representation."""
        return {
            "fields": {
                k: v.to_dict() 
                for k, v in sorted(self.fields.items())  # Sorted!
            },
            "kind": "record"
        }
```

**Step 2: Add to IR Model**

```python
# In rlang/ir/model.py
__all__ = [
    "IRExpr",
    "IRIf",
    "IRRecord",  # NEW
    "PipelineStepIR",
    "PipelineIR",
    ...
]
```

**Step 3: Lower AST to IR**

```python
# In rlang/lowering/lowering.py
def lower_record_expr(expr: RecordExpr) -> IRRecord:
    return IRRecord(
        fields={
            field.name: lower_expr(field.value)
            for field in sorted(expr.fields, key=lambda f: f.name)  # Sorted!
        }
    )
```

**Step 4: Add Execution Semantics**

```python
# In rlang/bor/proofs.py
def _eval_irexpr(expr: IRExpr | IRRecord, ...) -> Any:
    if isinstance(expr, IRRecord):
        return {
            k: _eval_irexpr(v, ...)
            for k, v in sorted(expr.fields.items())  # Sorted!
        }
    # ... existing cases
```

**Step 5: Update Canonicalization**

Canonicalization automatically works if `to_dict()` uses sorted keys.

#### 5.3.3 Example: Adding IRList (v0.3)

```python
@dataclass(frozen=True)
class IRList:
    """IR representation of a list construction."""
    elements: list[IRExpr]  # Ordered list (deterministic!)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "elements": [e.to_dict() for e in self.elements],
            "kind": "list"
        }
```

**Key Point**: Lists are **ordered**—order is part of the semantics. No unordered collections allowed.

#### 5.3.4 Example: Adding IRUnrolledLoop (v0.3)

```python
@dataclass(frozen=True)
class IRUnrolledLoop:
    """IR representation of a statically unrolled loop."""
    bound: int  # Static bound (must be compile-time constant)
    body: PipelineIR  # Loop body (as pipeline)
    accumulator: IRExpr  # Initial accumulator value
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "bound": self.bound,
            "body": self.body.to_dict(),
            "accumulator": self.accumulator.to_dict(),
            "kind": "unrolled_loop"
        }
```

**Key Point**: Loops must be **statically bounded**—the iteration count must be known at compile time.

### 5.4 IR Evaluation Rules

#### 5.4.1 Expression Evaluation

```
Eval_IR(IRExpr(kind="literal", value=v), ctx) = v
Eval_IR(IRExpr(kind="identifier", name="__value"), ctx) = ctx.current_value
Eval_IR(IRExpr(kind="binary_op", op="+", left=l, right=r), ctx) = 
    Eval_IR(l, ctx) + Eval_IR(r, ctx)
Eval_IR(IRExpr(kind="call", func=f, args=[a₁, ..., aₙ]), ctx) =
    fn_registry[f](Eval_IR(a₁, ctx), ..., Eval_IR(aₙ, ctx))
```

#### 5.4.2 Conditional Evaluation

```
Eval_IR(IRIf(condition=c, then_steps=t, else_steps=e), ctx) =
    if Eval_IR(c, ctx) then
        Eval_steps(t, ctx)
    else
        Eval_steps(e, ctx)
```

#### 5.4.3 Pipeline Evaluation

```
Eval_IR(PipelineIR(steps=[s₁, ..., sₙ]), ctx) =
    foldl(Eval_step, ctx, [s₁, ..., sₙ])
```

---

## 6. Canonicalization Specification

### 6.1 Canonical JSON Rules

Canonical JSON is the **stable serialization format** that ensures:

- Same data structure → same JSON string
- Same JSON string → same hash
- Deterministic across platforms and Python versions

### 6.2 Key Ordering Rule

**RULE**: All dictionary keys must be sorted **alphabetically**.

**Implementation:**

```python
def canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

**Example:**

```python
{"b": 2, "a": 1} → '{"a":1,"b":2}'
```

**Why This Matters:**

Non-deterministic key ordering breaks hash stability:

```python
# ❌ WRONG
{"b": 2, "a": 1} → hash₁
{"a": 1, "b": 2} → hash₂  # Different hash!

# ✅ CORRECT
{"b": 2, "a": 1} → '{"a":1,"b":2}' → hash
{"a": 1, "b": 2} → '{"a":1,"b":2}' → hash  # Same hash!
```

### 6.3 Float Normalization Rule

**RULE**: Floats must be normalized to ensure platform-independent representation.

**Implementation:**

```python
def _normalize_floats(obj: Any) -> Any:
    if isinstance(obj, float):
        if obj.is_integer():
            return int(obj)  # 3.0 → 3
        return round(obj, 10)  # Round to 10 decimal places
    elif isinstance(obj, dict):
        return {k: _normalize_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_floats(item) for item in obj]
    return obj
```

**Why This Matters:**

Different platforms may represent floats differently:

```python
# Platform A: 0.1 + 0.2 = 0.30000000000000004
# Platform B: 0.1 + 0.2 = 0.3
# Normalization ensures consistent representation
```

### 6.4 Whitespace Rule

**RULE**: Minimal whitespace (compact JSON) unless indentation is explicitly requested.

**Implementation:**

```python
# Compact (default)
json.dumps(obj, separators=(",", ":"))  # No spaces

# Pretty (for debugging)
json.dumps(obj, indent=2)  # 2-space indentation
```

### 6.5 Encoding Rule

**RULE**: UTF-8 encoding, no BOM, consistent line endings.

**Implementation:**

```python
canonical_json.encode("utf-8")
```

### 6.6 Canonicalization Algorithm

**Pseudocode:**

```
function CANONICALIZE(obj):
    if obj is None:
        return "null"
    if obj is bool:
        return "true" if obj else "false"
    if obj is int:
        return str(obj)
    if obj is float:
        normalized = NORMALIZE_FLOAT(obj)
        return str(normalized)
    if obj is str:
        return JSON_ESCAPE(obj)
    if obj is list:
        elements = [CANONICALIZE(item) for item in obj]
        return "[" + ",".join(elements) + "]"
    if obj is dict:
        keys = SORT_ALPHABETICALLY(obj.keys())
        pairs = [CANONICALIZE(k) + ":" + CANONICALIZE(obj[k]) for k in keys]
        return "{" + ",".join(pairs) + "}"
```

### 6.7 Hash Boundary Rules

**RULE**: Hash boundaries must be **stable**—same data → same hash.

**Implementation:**

```python
def compute_hash(obj: Any) -> str:
    canonical_json = canonical_dumps(obj)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
```

**Invariant:**

```
Hash(canonical(P₁)) = Hash(canonical(P₂)) ⟺ P₁ ≡ P₂
```

### 6.8 What Breaks Determinism

❌ **FORBIDDEN:**

1. Non-deterministic key ordering
2. Platform-dependent float representation
3. Non-canonical JSON serialization
4. Including metadata in canonical form
5. Non-deterministic whitespace

✅ **REQUIRED:**

1. Alphabetically sorted keys
2. Normalized floats
3. Canonical JSON serialization
4. Pure data structures only
5. Consistent encoding

---

## 7. Execution Semantics

### 7.1 Execution Model

RLang execution is **purely functional** and **deterministic**:

- No mutable state
- No side effects
- No I/O operations
- No randomness

### 7.2 Function Application

**Semantics:**

```
Apply(f, x) = fn_registry[f](x)
```

**Requirements:**

1. `fn_registry[f]` must be a **pure function**
2. No side effects allowed
3. Deterministic output for same input

**Example:**

```python
fn_registry = {
    "inc": lambda x: x + 1,
    "double": lambda x: x * 2
}

Apply("inc", 5) = 6
Apply("double", 6) = 12
```

### 7.3 Step Execution

**Sequential Execution:**

```
Execute([s₁, ..., sₙ], x₀) =
    let x₁ = Execute(s₁, x₀) in
    let x₂ = Execute(s₂, x₁) in
    ...
    let xₙ = Execute(sₙ, xₙ₋₁) in
    xₙ
```

**Trace Recording:**

Each step execution produces a **StepExecutionRecord**:

```python
StepExecutionRecord(
    index=i,
    step_name=name,
    template_id=template_id,
    input_snapshot=xᵢ,
    output_snapshot=xᵢ₊₁
)
```

### 7.4 Conditional Execution

**Branch Selection:**

```
Execute(IRIf(condition=c, then_steps=t, else_steps=e), x) =
    if Eval(c, x) then
        Execute(t, x)
    else
        Execute(e, x)
```

**Branch Recording:**

Each conditional execution produces a **BranchExecutionRecord**:

```python
BranchExecutionRecord(
    index=i,
    path="then" | "else",
    condition_value=bool
)
```

**Determinism:**

Same condition value → same branch path → same execution trace.

### 7.5 Error Semantics

**Error Handling:**

1. **Type Errors**: Detected at compile time (type checker)
2. **Runtime Errors**: Division by zero, missing function registry entries
3. **Proof Errors**: Invalid proof bundle structure

**Error Propagation:**

Errors **must** be deterministic—same error condition → same error.

### 7.6 Evaluation Context

**Context Structure:**

```python
@dataclass
class ExecutionContext:
    current_value: Any  # Current pipeline value
    fn_registry: Dict[str, Callable]  # Function registry
    step_index: int  # Current step index
```

**Context Updates:**

```
UpdateContext(ctx, new_value) = ExecutionContext(
    current_value=new_value,
    fn_registry=ctx.fn_registry,  # Immutable
    step_index=ctx.step_index + 1
)
```

### 7.7 Future: Loop Execution (v0.3+)

**Unrolled Loop Semantics:**

```
Execute(IRUnrolledLoop(bound=n, body=p, accumulator=a₀), x) =
    foldl(Execute, a₀, [p, p, ..., p])  # n times
```

**Key Requirement:**

Loop bounds **must** be compile-time constants—no dynamic iteration counts.

---

## 8. Proof System Architecture

### 8.1 TRP v1 (Current)

**TRP (Trace of Reasoning Process)** is the execution trace format.

#### 8.1.1 Structure

```python
PipelineProofBundle(
    version: str,
    language: str,
    entry_pipeline: str | None,
    program_ir: PrimaryProgramIR,
    input_value: Any,
    output_value: Any,
    steps: List[StepExecutionRecord],
    branches: List[BranchExecutionRecord]
)
```

#### 8.1.2 Step Records

```python
StepExecutionRecord(
    index: int,           # 0-based step index
    step_name: str,        # Function name
    template_id: str,      # Template reference
    input_snapshot: Any,   # Input value
    output_snapshot: Any   # Output value
)
```

#### 8.1.3 Branch Records

```python
BranchExecutionRecord(
    index: int,           # IF step index
    path: str,            # "then" | "else"
    condition_value: bool  # Condition evaluation result
)
```

#### 8.1.4 Deterministic ID Labeling

**Template IDs:**

```
template_id = "fn:" + function_name
```

**Pipeline IDs:**

```
pipeline_id = "pipeline:" + pipeline_name
```

**Invariant:**

Same function → same template ID (deterministic).

### 8.2 Hashing Model

#### 8.2.1 HMASTER

**Definition:**

```
HMASTER = Hash(canonical(program_ir))
```

**Computation:**

```python
def compute_HMASTER(program_ir: PrimaryProgramIR) -> str:
    canonical_json = program_ir.to_json()
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
```

**Invariant:**

Same program IR → same HMASTER.

#### 8.2.2 HRICH

**Definition:**

```
HRICH = Hash(canonical(proof_bundle))
```

**Computation:**

```python
def compute_HRICH(proof_bundle: PipelineProofBundle) -> str:
    # Convert to rich bundle format
    rich_bundle = {
        "primary": {
            "master": HMASTER,
            "steps": [step.to_dict() for step in proof_bundle.steps],
            "branches": [branch.to_dict() for branch in proof_bundle.branches]
        },
        "H_RICH": None  # Computed below
    }
    
    # Compute subproof hashes
    subproof_hashes = compute_subproof_hashes(subproofs)
    
    # Compute HRICH from subproof hashes
    HRICH = compute_HRICH_from_subproof_hashes(subproof_hashes)
    
    return HRICH
```

**Subproof Hashes:**

```
subproof_hashes = {
    "DIP": Hash(DIP_subproof),
    "DP": Hash(DP_subproof),
    "PEP": Hash(PEP_subproof),
    "PoPI": Hash(PoPI_subproof),
    "CCP": Hash(CCP_subproof),
    "CMIP": Hash(CMIP_subproof),
    "PP": Hash(PP_subproof),
    "TRP": Hash(TRP_subproof)
}
```

**HRICH Computation:**

```
HRICH = SHA256(
    sorted(subproof_hashes.values()).join("|")
)
```

**Invariant:**

Same execution trace → same HRICH.

#### 8.2.3 Hash Graph

```
Program IR
    │
    └─▶ HMASTER
         │
         ├─▶ Subproofs
         │    │
         │    ├─▶ DIP Hash
         │    ├─▶ DP Hash
         │    ├─▶ PEP Hash
         │    ├─▶ PoPI Hash
         │    ├─▶ CCP Hash
         │    ├─▶ CMIP Hash
         │    ├─▶ PP Hash
         │    └─▶ TRP Hash
         │
         └─▶ HRICH (from subproof hashes)
```

### 8.3 Upgrade Path to TRP v2

#### 8.3.1 Planned Extensions

**Loops:**

```python
LoopExecutionRecord(
    index: int,
    bound: int,
    iterations: List[StepExecutionRecord]  # Per-iteration steps
)
```

**Scopes:**

```python
ScopeExecutionRecord(
    index: int,
    scope_name: str,
    bindings: Dict[str, Any],
    body_steps: List[StepExecutionRecord]
)
```

**Collections:**

```python
CollectionExecutionRecord(
    index: int,
    collection_type: str,  # "list" | "record" | "map"
    elements: List[Any]
)
```

**Pattern Matching:**

```python
MatchExecutionRecord(
    index: int,
    matched_value: Any,
    pattern: str,
    matched_branch: str
)
```

**Connectors:**

```python
ConnectorExecutionRecord(
    index: int,
    connector_type: str,
    inputs: List[Any],
    output: Any
)
```

#### 8.3.2 Versioning Strategy

**TRP Version Field:**

```python
PipelineProofBundle(
    trp_version: str = "v1",  # Current: "v1", Future: "v2"
    ...
)
```

**Backward Compatibility:**

- TRP v1 bundles remain valid
- TRP v2 extends v1 (additive changes only)
- Verification tools support multiple versions

---

## 9. The Untouchable Core (Frozen Physics)

### 9.1 Frozen Components

These components **MUST NEVER BE MODIFIED** without breaking determinism guarantees:

| Component | Frozen? | Why? |
|-----------|---------|------|
| **Canonical JSON Rules** | ✅ YES | Breaks HMASTER stability |
| **Hash Algorithms** | ✅ YES | Breaks verification |
| **TRP Structure Rules** | ✅ YES | Breaks proof compatibility |
| **Branch Decision Semantics** | ✅ YES | Breaks determinism |
| **Deterministic Data Structures** | ✅ YES | Breaks execution determinism |
| **No Non-Deterministic Iteration** | ✅ YES | Breaks execution determinism |
| **No Mutation in IR** | ✅ YES | Breaks purity |

### 9.2 Partially Frozen Components

These components can be **extended** but must preserve determinism:

| Component | Frozen? | Why? |
|-----------|---------|------|
| **AST → IR Lowering** | ⚠️ PARTIAL | Must remain deterministic |
| **Type System** | ⚠️ PARTIAL | Can add types, but rules must be deterministic |
| **Executor** | ⚠️ PARTIAL | Semantics must remain deterministic |
| **Parser** | ❌ NO | Extensions allowed (new syntax) |
| **Resolver** | ❌ NO | Extensions allowed (new symbols) |

### 9.3 Modification Rules

#### 9.3.1 Canonical JSON

**NEVER CHANGE:**

- Key sorting algorithm
- Float normalization rules
- JSON encoding (UTF-8)
- Whitespace rules

**ALLOWED:**

- Adding new fields to existing structures (if canonicalized correctly)

#### 9.3.2 Hash Algorithms

**NEVER CHANGE:**

- SHA-256 algorithm
- Hash computation order
- Subproof hash structure

**ALLOWED:**

- Adding new hash types (with new names)
- Extending hash inputs (additive only)

#### 9.3.3 TRP Structure

**NEVER CHANGE:**

- Step record structure (v1)
- Branch record structure (v1)
- Record field names

**ALLOWED:**

- Adding new record types (TRP v2)
- Extending existing records (additive fields)

---

## 10. Expandable Surfaces (Safe to Extend)

### 10.1 Frontend Extensions

#### 10.1.1 Lexer

**Safe to Add:**

- New keywords
- New operators
- New literal types
- New comment styles

**Example:**

```python
# Adding new keyword "match"
keywords = {"fn", "pipeline", "if", "else", "match"}  # NEW
```

#### 10.1.2 Parser

**Safe to Add:**

- New AST nodes
- New expression forms
- New statement types

**Example:**

```python
# Adding pattern matching AST node
@dataclass
class MatchExpr(Expr):
    value: Expr
    cases: List[MatchCase]
```

#### 10.1.3 Resolver

**Safe to Add:**

- New symbol kinds
- New scoping rules
- New name resolution strategies

**Example:**

```python
# Adding module symbols
class SymbolKind(Enum):
    FUNCTION = "function"
    PIPELINE = "pipeline"
    TYPE = "type"
    MODULE = "module"  # NEW
```

### 10.2 Middle-End Extensions

#### 10.2.1 Type System

**Safe to Add:**

- New primitive types
- New generic types
- New type constructors

**Example:**

```python
# Adding List type
RType(name="List", args=(RType(name="Int"),))
```

#### 10.2.2 Lowering

**Safe to Add:**

- New AST → IR lowering rules
- New IR node types (following IR invariants)

**Example:**

```python
# Lowering pattern matching to IR
def lower_match_expr(expr: MatchExpr) -> IRMatch:
    return IRMatch(
        value=lower_expr(expr.value),
        cases=[lower_case(c) for c in expr.cases]
    )
```

### 10.3 Backend Extensions

#### 10.3.1 Executor

**Safe to Add:**

- New execution strategies
- New optimization passes
- New proof recording formats

**Example:**

```python
# Adding loop execution
def execute_loop(loop: IRUnrolledLoop, ctx: ExecutionContext) -> Any:
    result = ctx.current_value
    for i in range(loop.bound):
        result = execute_pipeline(loop.body, result, ctx)
    return result
```

#### 10.3.2 Proof System

**Safe to Add:**

- New proof record types (TRP v2)
- New subproof types
- New verification strategies

**Example:**

```python
# Adding loop proof record
@dataclass(frozen=True)
class LoopExecutionRecord:
    index: int
    bound: int
    iterations: List[List[StepExecutionRecord]]
```

### 10.4 Extension Guidelines

**Before Adding:**

1. ✅ Verify determinism (same input → same output)
2. ✅ Verify canonicalizability (can serialize to JSON)
3. ✅ Verify purity (no side effects)
4. ✅ Add tests (determinism tests required)
5. ✅ Update documentation

**After Adding:**

1. ✅ Run full test suite
2. ✅ Verify hash stability
3. ✅ Update golden files
4. ✅ Document extension

---

## 11. Rules for Deterministic Expansion

### 11.1 Law 1: Pure Evaluation

**RULE**: Every new semantic feature must have unambiguous, pure evaluation.

**Formal:**

```
∀ feature, input. ∃! output. Eval(feature, input) = output
```

**Positive Examples:**

✅ **List Operations:**

```python
Eval([1, 2, 3], ctx) = [1, 2, 3]  # Deterministic
Eval(map(f, [1, 2, 3]), ctx) = [f(1), f(2), f(3)]  # Deterministic order
```

✅ **Record Operations:**

```python
Eval({a: 1, b: 2}, ctx) = {"a": 1, "b": 2}  # Sorted keys
```

**Negative Examples:**

❌ **Non-Deterministic Iteration:**

```python
# FORBIDDEN: Unordered iteration
for key in some_dict:  # Order not guaranteed!
    process(key)
```

❌ **Random Operations:**

```python
# FORBIDDEN: Randomness
import random
value = random.randint(1, 10)  # Non-deterministic!
```

### 11.2 Law 2: Deterministic Lowering

**RULE**: Every new IR node must have deterministic lowering.

**Formal:**

```
∀ AST_node. ∃! IR_node. Lower(AST_node) = IR_node
```

**Positive Examples:**

✅ **Deterministic List Lowering:**

```python
def lower_list_expr(expr: ListExpr) -> IRList:
    return IRList(
        elements=[lower_expr(e) for e in expr.elements]  # Preserve order
    )
```

✅ **Deterministic Record Lowering:**

```python
def lower_record_expr(expr: RecordExpr) -> IRRecord:
    return IRRecord(
        fields={
            k: lower_expr(v)
            for k, v in sorted(expr.fields.items())  # Sorted!
        }
    )
```

**Negative Examples:**

❌ **Non-Deterministic Lowering:**

```python
# FORBIDDEN: Non-deterministic field order
def lower_record_expr(expr: RecordExpr) -> IRRecord:
    return IRRecord(
        fields=dict(expr.fields)  # Order not guaranteed!
    )
```

### 11.3 Law 3: Statically Finite Collections

**RULE**: Any new collection or loop must be statically finite.

**Formal:**

```
∀ collection. ∃ n ∈ ℕ. |collection| ≤ n  (n known at compile time)
```

**Positive Examples:**

✅ **Bounded Lists:**

```python
# List length known at compile time
list = [1, 2, 3]  # Length: 3 (compile-time constant)
```

✅ **Unrolled Loops:**

```python
# Loop bound known at compile time
for i in 0..10:  # Bound: 10 (compile-time constant)
    process(i)
```

**Negative Examples:**

❌ **Dynamic Bounds:**

```python
# FORBIDDEN: Dynamic loop bound
n = read_input()  # Runtime value!
for i in 0..n:  # Bound unknown at compile time
    process(i)
```

❌ **Unbounded Collections:**

```python
# FORBIDDEN: Unbounded iteration
while True:  # Unbounded!
    process()
```

### 11.4 Law 4: Stable Proofs

**RULE**: All proofs must be stable across executions.

**Formal:**

```
∀ program, input. TRP(program, input) = TRP(program, input)
```

**Positive Examples:**

✅ **Deterministic Step Recording:**

```python
# Steps recorded in execution order
steps = [
    StepExecutionRecord(index=0, ...),
    StepExecutionRecord(index=1, ...),
    StepExecutionRecord(index=2, ...)
]
```

✅ **Deterministic Branch Recording:**

```python
# Branch decisions recorded deterministically
branch = BranchExecutionRecord(
    index=0,
    path="then",  # Based on condition value
    condition_value=True
)
```

**Negative Examples:**

❌ **Non-Deterministic Recording:**

```python
# FORBIDDEN: Non-deterministic step order
steps = sorted(executed_steps, key=lambda s: s.name)  # Order changes!
```

❌ **Non-Deterministic Branch Recording:**

```python
# FORBIDDEN: Recording random branch
branch = BranchExecutionRecord(
    index=0,
    path=random.choice(["then", "else"]),  # Non-deterministic!
    condition_value=True
)
```

### 11.5 Law 5: No Non-Deterministic Ordering

**RULE**: No extension may introduce non-deterministic ordering.

**Formal:**

```
∀ collection. Order(collection) = Order(collection)  (stable)
```

**Positive Examples:**

✅ **Sorted Collections:**

```python
# Deterministic order
sorted_dict = {k: v for k, v in sorted(items.items())}
```

✅ **Indexed Collections:**

```python
# Deterministic order (by index)
list = [a, b, c]  # Order: [0, 1, 2]
```

**Negative Examples:**

❌ **Unordered Collections:**

```python
# FORBIDDEN: Unordered iteration
for key in some_set:  # Order not guaranteed!
    process(key)
```

❌ **Non-Deterministic Sorting:**

```python
# FORBIDDEN: Non-deterministic sort key
sorted_items = sorted(items, key=lambda x: hash(x))  # Hash may vary!
```

---

## 12. Meta-Architecture for v0.3 → v1.0

### 12.1 Planned Language Extensions

#### 12.1.1 Lists (v0.3)

**Syntax:**

```rlang
fn map(f: Int -> Int, xs: List[Int]) -> List[Int];
fn fold(f: (Int, Int) -> Int, acc: Int, xs: List[Int]) -> Int;

pipeline main(List[Int]) -> Int {
    fold(add, 0)
}
```

**IR Representation:**

```python
@dataclass(frozen=True)
class IRList:
    elements: list[IRExpr]
    element_type: str
```

**Execution:**

```python
def execute_list(list: IRList, ctx: ExecutionContext) -> list:
    return [execute_expr(e, ctx) for e in list.elements]
```

**Proof Recording:**

```python
@dataclass(frozen=True)
class ListExecutionRecord:
    index: int
    list_type: str
    elements: list[Any]
```

#### 12.1.2 Records (v0.3)

**Syntax:**

```rlang
type User = Record {
    id: Int,
    name: String,
    email: String
};

fn getUser(id: Int) -> User;
```

**IR Representation:**

```python
@dataclass(frozen=True)
class IRRecord:
    fields: dict[str, IRExpr]  # Sorted keys!
```

**Execution:**

```python
def execute_record(record: IRRecord, ctx: ExecutionContext) -> dict:
    return {
        k: execute_expr(v, ctx)
        for k, v in sorted(record.fields.items())
    }
```

#### 12.1.3 Pattern Matching (v0.4)

**Syntax:**

```rlang
pipeline main(Int) -> String {
    match(__value) {
        case 0 => "zero"
        case n if n > 0 => "positive"
        case _ => "negative"
    }
}
```

**IR Representation:**

```python
@dataclass(frozen=True)
class IRMatch:
    value: IRExpr
    cases: list[MatchCase]
```

**Execution:**

```python
def execute_match(match: IRMatch, ctx: ExecutionContext) -> Any:
    value = execute_expr(match.value, ctx)
    for case in match.cases:
        if matches(case.pattern, value):
            return execute_expr(case.body, ctx)
    raise MatchError("No matching case")
```

#### 12.1.4 Bounded Loops (v0.4)

**Syntax:**

```rlang
pipeline main(Int) -> Int {
    let acc = 0 in
    for i in 0..10 {
        acc = acc + i
    }
    acc
}
```

**IR Representation:**

```python
@dataclass(frozen=True)
class IRUnrolledLoop:
    bound: int  # Compile-time constant!
    body: PipelineIR
    accumulator: IRExpr
```

**Execution:**

```python
def execute_loop(loop: IRUnrolledLoop, ctx: ExecutionContext) -> Any:
    acc = execute_expr(loop.accumulator, ctx)
    for i in range(loop.bound):
        acc = execute_pipeline(loop.body, acc, ctx)
    return acc
```

#### 12.1.5 Modules (v0.5)

**Syntax:**

```rlang
module Math {
    fn add(x: Int, y: Int) -> Int;
    fn multiply(x: Int, y: Int) -> Int;
}

import Math;

pipeline main(Int) -> Int {
    Math.add(__value, 10)
}
```

**IR Representation:**

```python
@dataclass(frozen=True)
class IRModule:
    name: str
    functions: dict[str, StepTemplateIR]
```

#### 12.1.6 Connectors (v0.6)

**Syntax:**

```rlang
connector parallel {
    input: Int
    outputs: [Int, Int]
};

pipeline main(Int) -> [Int, Int] {
    parallel -> merge
}
```

**IR Representation:**

```python
@dataclass(frozen=True)
class IRConnector:
    connector_type: str
    inputs: list[IRExpr]
    outputs: list[str]
```

### 12.2 TRP v2 Architecture

#### 12.2.1 Extended Proof Bundle

```python
@dataclass(frozen=True)
class PipelineProofBundleV2:
    version: str
    language: str
    trp_version: str = "v2"  # NEW
    entry_pipeline: str | None
    program_ir: PrimaryProgramIR
    input_value: Any
    output_value: Any
    steps: List[StepExecutionRecord]
    branches: List[BranchExecutionRecord]
    loops: List[LoopExecutionRecord]  # NEW
    scopes: List[ScopeExecutionRecord]  # NEW
    collections: List[CollectionExecutionRecord]  # NEW
    matches: List[MatchExecutionRecord]  # NEW
```

#### 12.2.2 Loop Records

```python
@dataclass(frozen=True)
class LoopExecutionRecord:
    index: int
    bound: int
    iterations: List[List[StepExecutionRecord]]  # Per-iteration steps
    accumulator_snapshots: List[Any]  # Per-iteration accumulator values
```

#### 12.2.3 Scope Records

```python
@dataclass(frozen=True)
class ScopeExecutionRecord:
    index: int
    scope_name: str
    bindings: Dict[str, Any]  # Sorted keys!
    body_steps: List[StepExecutionRecord]
```

### 12.3 IR Graph Architecture (v1.0)

#### 12.3.1 DAG Execution

**Future IR Structure:**

```python
@dataclass(frozen=True)
class IRGraph:
    nodes: List[IRNode]
    edges: List[IREdge]  # Data flow edges
    execution_order: List[int]  # Topological sort
```

**Benefits:**

- Parallel execution (where possible)
- Better optimization
- More expressive programs

**Constraints:**

- Must remain deterministic
- Execution order must be stable
- No cycles allowed

### 12.4 Multi-Backend Compiler (v1.0)

#### 12.4.1 Backend Interface

```python
class Backend(ABC):
    @abstractmethod
    def compile(self, ir: PrimaryProgramIR) -> CompiledProgram:
        """Compile IR to backend-specific format."""
        pass
    
    @abstractmethod
    def execute(self, program: CompiledProgram, input: Any) -> Any:
        """Execute compiled program."""
        pass
```

#### 12.4.2 Backend Implementations

- **Python Backend**: Current implementation
- **WASM Backend**: WebAssembly compilation
- **LLVM Backend**: Native code generation
- **BoR Backend**: Direct BoR integration

**Invariant:**

All backends must produce **identical results** for same input.

---

## 13. Change Control: Golden Files + Determinism Tests

### 13.1 Golden Files

**Purpose:**

Golden files store **canonical reference outputs** for regression testing.

#### 13.1.1 Golden Canonical JSON

**Location:** `tests/golden/*.json`

**Format:**

```json
{
    "source": "fn inc(x:Int)->Int;\npipeline main(Int)->Int { inc }",
    "canonical_json": "{...}",
    "H_IR": "abc123...",
    "version": "0.2.1"
}
```

**Usage:**

```python
def test_canonical_json_stability():
    source = load_golden("simple_pipeline.json")["source"]
    result = compile_source_to_json(source)
    assert result == load_golden("simple_pipeline.json")["canonical_json"]
```

#### 13.1.2 Golden Hashes

**Location:** `tests/golden/hashes.json`

**Format:**

```json
{
    "simple_pipeline": {
        "H_IR": "abc123...",
        "HRICH_input_5": "def456...",
        "version": "0.2.1"
    }
}
```

**Usage:**

```python
def test_hash_stability():
    source = load_test_source("simple_pipeline")
    ir = compile_source_to_ir(source)
    assert compute_H_IR(ir) == load_golden_hash("simple_pipeline", "H_IR")
```

### 13.2 Determinism Tests

#### 13.2.1 Test Structure

```python
def test_determinism_feature_name():
    """Test that feature produces deterministic results."""
    source = "..."
    input_value = 42
    
    # Run multiple times
    result1 = run_program_with_proof(source, input_value)
    result2 = run_program_with_proof(source, input_value)
    
    # Must be identical
    assert result1.to_dict() == result2.to_dict()
    assert result1.to_json() == result2.to_json()
```

#### 13.2.2 Required Tests

**For Every Feature:**

1. ✅ Determinism test (same input → same output)
2. ✅ Canonical JSON test (stable serialization)
3. ✅ Hash stability test (same program → same hash)
4. ✅ Cross-platform test (works on different OS/Python versions)

**Example:**

```python
def test_multi_if_determinism():
    """Test multi-IF determinism (v0.2.1 fix)."""
    source = """
    fn inc(x:Int)->Int;
    fn dec(x:Int)->Int;
    pipeline main(Int)->Int {
        if(__value>10){inc}else{dec} ->
        if(__value>20){inc}else{dec} ->
        if(__value>30){inc}else{dec}
    }
    """
    
    for v in [0, 5, 12, 25, 35, 99]:
        a = run_program_with_proof(source, v).to_dict()
        b = run_program_with_proof(source, v).to_dict()
        assert a == b
```

### 13.3 CI Invariants

#### 13.3.1 Required Checks

**Every PR Must:**

1. ✅ Pass all existing tests
2. ✅ Maintain golden file compatibility (or update with justification)
3. ✅ Pass determinism tests
4. ✅ Pass hash stability tests
5. ✅ Pass cross-platform tests (if applicable)

#### 13.3.2 Golden File Updates

**When to Update:**

- ✅ New feature added (add new golden file)
- ✅ Bug fix changes output (update existing golden file)
- ✅ Performance optimization (verify golden file unchanged)

**Process:**

1. Run tests locally
2. Generate new golden files
3. Review changes
4. Commit golden files with PR

### 13.4 Test Harness Structure

```
tests/
├── golden/
│   ├── simple_pipeline.json
│   ├── multi_if_pipeline.json
│   └── hashes.json
├── test_determinism.py
├── test_canonical_json.py
├── test_hash_stability.py
└── test_cross_platform.py
```

---

## 14. Reference Appendix

### 14.1 Grammar

#### 14.1.1 Lexical Grammar

```
IDENTIFIER  ::= [a-zA-Z_][a-zA-Z0-9_]*
INTEGER     ::= [0-9]+
FLOAT       ::= [0-9]+\.[0-9]+
STRING      ::= "([^"\\]|\\.)*"
BOOLEAN     ::= true | false
KEYWORD     ::= fn | pipeline | if | else | type | import | module
OPERATOR    ::= + | - | * | / | > | < | >= | <= | == | != | ->
PUNCTUATION ::= ( | ) | { | } | [ | ] | : | ; | , | =
```

#### 14.1.2 Syntax Grammar

```
Program     ::= Declaration*

Declaration ::= FunctionDecl | PipelineDecl | TypeAlias | ModuleDecl

FunctionDecl ::= fn IDENTIFIER ( ParamList? ) -> TypeExpr? ;

ParamList   ::= Param ( , Param )*
Param       ::= IDENTIFIER : TypeExpr

PipelineDecl ::= pipeline IDENTIFIER ( TypeExpr? ) -> TypeExpr? { Steps }

Steps       ::= Step ( -> Step )*
Step        ::= IDENTIFIER | IfExpr | CallExpr

IfExpr      ::= if ( Expr ) { Steps } [ else { Steps } ]

CallExpr    ::= IDENTIFIER ( ExprList? )
ExprList    ::= Expr ( , Expr )*

Expr        ::= Literal | Identifier | BinaryOp | CallExpr | IfExpr

Literal     ::= INTEGER | FLOAT | STRING | BOOLEAN
Identifier  ::= IDENTIFIER | __value

BinaryOp    ::= Expr OPERATOR Expr

TypeExpr    ::= SimpleType | GenericType
SimpleType  ::= IDENTIFIER
GenericType ::= IDENTIFIER [ TypeArgList ]
TypeArgList ::= TypeExpr ( , TypeExpr )*

TypeAlias   ::= type IDENTIFIER = TypeExpr ;
```

### 14.2 Type Rules

#### 14.2.1 Type Inference Rules

**Literal Types:**

```
───────────────
42 : Int

───────────────
3.14 : Float

───────────────
"hello" : String

───────────────
true : Bool
```

**Function Application:**

```
f : T₁ × ... × Tₙ → T
e₁ : T₁, ..., eₙ : Tₙ
─────────────────────────
f(e₁, ..., eₙ) : T
```

**Binary Operations:**

```
e₁ : Int, e₂ : Int
─────────────────────────
e₁ + e₂ : Int

e₁ : Float, e₂ : Float
─────────────────────────
e₁ + e₂ : Float

e₁ : Int, e₂ : Float
─────────────────────────
e₁ + e₂ : Float
```

**Conditionals:**

```
c : Bool
e₁ : T, e₂ : T
─────────────────────────
if (c) { e₁ } else { e₂ } : T
```

**Pipeline Steps:**

```
s₁ : T₁ → T₂
s₂ : T₂ → T₃
─────────────────────────
s₁ -> s₂ : T₁ → T₃
```

### 14.3 IR Schemas

#### 14.3.1 IRExpr Schema

```json
{
    "kind": "literal" | "identifier" | "binary_op" | "call",
    "value": Any,           // if kind == "literal"
    "name": str,             // if kind == "identifier"
    "op": str,               // if kind == "binary_op"
    "left": IRExpr,          // if kind == "binary_op"
    "right": IRExpr,         // if kind == "binary_op"
    "func": str,             // if kind == "call"
    "args": [IRExpr]         // if kind == "call"
}
```

#### 14.3.2 IRIf Schema

```json
{
    "kind": "if",
    "condition": IRExpr,
    "then": [PipelineStepIR],
    "else": [PipelineStepIR]
}
```

#### 14.3.3 PipelineIR Schema

```json
{
    "id": str,
    "name": str,
    "input_type": str | null,
    "output_type": str | null,
    "steps": [PipelineStepIR | IRIf]
}
```

### 14.4 Proof Schemas

#### 14.4.1 StepExecutionRecord Schema

```json
{
    "index": int,
    "step_name": str,
    "template_id": str,
    "input": Any,
    "output": Any
}
```

#### 14.4.2 BranchExecutionRecord Schema

```json
{
    "index": int,
    "path": "then" | "else",
    "condition_value": bool
}
```

#### 14.4.3 PipelineProofBundle Schema

```json
{
    "version": str,
    "language": str,
    "entry_pipeline": str | null,
    "program": PrimaryProgramIR,
    "input": Any,
    "output": Any,
    "steps": [StepExecutionRecord],
    "branches": [BranchExecutionRecord]
}
```

### 14.5 Canonical JSON Schemas

#### 14.5.1 Canonicalization Rules

1. **Key Ordering**: Alphabetically sorted
2. **Float Normalization**: Integers preferred, 10 decimal places
3. **Encoding**: UTF-8, no BOM
4. **Whitespace**: Minimal (compact JSON)

#### 14.5.2 Example

**Input:**

```python
{"b": 2, "a": 1, "c": 3.0}
```

**Canonical Output:**

```json
{"a":1,"b":2,"c":3}
```

---

## Conclusion

This document defines the **physics layer** of the RLang compiler—the invariant rules that ensure deterministic execution and cryptographic verification. All future extensions must respect these invariants to maintain the fundamental guarantees of the language.

**Key Takeaways:**

1. **Determinism is Non-Negotiable**: Every feature must preserve deterministic execution
2. **Canonicalization is Fixed**: JSON serialization rules cannot change
3. **IR is the Physics Layer**: IR structure defines execution semantics
4. **Proofs Must Be Stable**: Execution traces must be deterministic
5. **Extension Must Follow Rules**: New features must follow expansion laws

**For Contributors:**

- Read this document before making changes
- Verify determinism for all new features
- Update golden files when outputs change
- Follow expansion rules for new IR nodes
- Test cross-platform compatibility

**For Users:**

- RLang guarantees bit-for-bit deterministic execution
- Proof bundles enable cryptographic verification
- Same program + same input = same output (always)

---

## 15. Appendix: Change Log of Compiler Physics Updates (Auto-Reconstructed)

This section documents all physics-relevant changes made to the RLang compiler since version 0.2.1. Changes are organized by feature and include detailed analysis of their impact on determinism, canonicalization, IR stability, and proof structure.

### 15.1 Boolean Operators (v0.2.1+)

**Summary:** Added support for boolean logical operators (`&&`, `||`, `!`) as first-class expressions in the language.

**Affected Components:**
- **AST**: Added `BooleanAnd`, `BooleanOr`, `BooleanNot` nodes (`rlang/parser/ast.py`)
- **Lexer**: Added `OP_AND` (`&&`), `OP_OR` (`||`), `OP_NOT` (`!`) tokens (`rlang/lexer/tokens.py`)
- **Parser**: Added parsing logic for boolean operators with proper precedence (`rlang/parser/parser.py`)
- **Type Checker**: Added type checking for boolean expressions (`rlang/types/type_checker.py`)
- **Lowering**: Added lowering rules to `IRExpr` with `kind="boolean_and"`, `kind="boolean_or"`, `kind="boolean_not"` (`rlang/lowering/lowering.py`)
- **IR**: Extended `IRExpr` to support boolean operator kinds (`rlang/ir/model.py`)
- **Executor**: Added evaluation logic for boolean operators (`rlang/bor/proofs.py`)

**Precise Physics Changes:**

1. **Deterministic Evaluation Order**: Boolean operators evaluate left-to-right with short-circuit semantics preserved deterministically:
   ```python
   # Boolean AND: left evaluated first, then right (if left is truthy)
   Eval(boolean_and(left, right), ctx) = bool(Eval(left, ctx)) and bool(Eval(right, ctx))
   
   # Boolean OR: left evaluated first, then right (if left is falsy)
   Eval(boolean_or(left, right), ctx) = bool(Eval(left, ctx)) or bool(Eval(right, ctx))
   
   # Boolean NOT: operand evaluated, then negated
   Eval(boolean_not(operand), ctx) = not bool(Eval(operand, ctx))
   ```

2. **IR Representation**: Boolean operators lower to `IRExpr` nodes with deterministic structure:
   ```python
   IRExpr(kind="boolean_and", left=left_ir, right=right_ir)
   IRExpr(kind="boolean_or", left=left_ir, right=right_ir)
   IRExpr(kind="boolean_not", operand=operand_ir)
   ```

3. **Canonicalization**: Boolean operator IR nodes serialize with sorted keys, ensuring deterministic JSON:
   ```json
   {"kind":"boolean_and","left":{...},"right":{...}}
   ```

**New Invariants Introduced:**

- **Boolean Evaluation Invariant**: Boolean operators always evaluate to Python `bool` type, ensuring consistent truthiness semantics
- **Left-to-Right Evaluation**: Boolean operators evaluate operands in strict left-to-right order, preserving short-circuit behavior deterministically

**Impact on Determinism:**

✅ **Positive Impact**: Boolean operators are pure functions—same inputs always produce same outputs. Evaluation order is deterministic (left-to-right).

**Impact on Canonicalization:**

✅ **No Breaking Changes**: Boolean operator IR nodes follow existing `IRExpr` canonicalization rules. Keys are sorted alphabetically in JSON serialization.

**Impact on Hash / IR Stability:**

✅ **Stable**: Boolean operator IR nodes produce stable hashes because:
- Field order is deterministic (sorted keys)
- Expression structure is deterministic
- No non-deterministic iteration or ordering

**TRP Impact:**

✅ **No Changes**: Boolean operators appear in conditions within `IRIf` nodes, which are already tracked in TRP branch records. No new proof record types required.

**Tests Guaranteeing Behavior:**

- Parser tests for boolean operator syntax (`tests/test_parser.py`)
- Type checker tests for boolean operator type inference (`tests/test_type_checker.py`)
- Lowering tests verify boolean operators lower to correct IR (`tests/test_lowering.py`)
- Executor tests verify boolean evaluation semantics (`rlang/bor/proofs.py`)

**Change Provenance:**

- **AST Nodes**: `rlang/parser/ast.py` lines 180-200
- **Parser Logic**: `rlang/parser/parser.py` lines 920-990
- **Type Checking**: `rlang/types/type_checker.py` lines 885-920
- **Lowering**: `rlang/lowering/lowering.py` lines 268-280
- **IR Model**: `rlang/ir/model.py` lines 110-138
- **Execution**: `rlang/bor/proofs.py` lines 237-252

---

### 15.2 Record Types and Expressions (v0.2.1+)

**Summary:** Added support for record types (`Record { field1: Type1, ... }`) and record literal expressions (`{ field1: expr1, ... }`) with field access (`obj.field`).

**Affected Components:**
- **AST**: Added `RecordType`, `RecordExpr`, `FieldAccess` nodes (`rlang/parser/ast.py`)
- **Parser**: Added parsing logic for record types and record literals (`rlang/parser/parser.py`)
- **Type System**: Added `RecordRType` for type checking (`rlang/types/type_system.py`)
- **Type Checker**: Added type checking for record expressions and field access (`rlang/types/type_checker.py`)
- **Lowering**: Added lowering rules to `IRExpr` with `kind="record"` and `kind="field_access"` (`rlang/lowering/lowering.py`)
- **IR**: Extended `IRExpr` to support record kinds (`rlang/ir/model.py`)
- **Executor**: Added evaluation logic for record construction and field access (`rlang/bor/proofs.py`)

**Precise Physics Changes:**

1. **Deterministic Field Ordering**: Record fields are sorted alphabetically in IR to ensure canonical representation:
   ```python
   # RecordExpr lowering: fields sorted by name
   def lower_record_expr(expr: RecordExpr) -> IRExpr:
       sorted_fields = dict(sorted(lowered_fields.items()))
       return IRExpr(kind="record", fields=sorted_fields)
   ```

2. **IR Representation**: Records lower to `IRExpr` nodes with deterministic field ordering:
   ```python
   IRExpr(kind="record", fields={k: v for k, v in sorted(fields.items())})
   IRExpr(kind="field_access", record=record_ir, field_name="field")
   ```

3. **Type System**: Record types use `RecordRType` with field type mapping:
   ```python
   RecordRType(name="Record", fields={"field1": RType(...), "field2": RType(...)})
   ```

**New Invariants Introduced:**

- **Field Ordering Invariant**: Record fields must be sorted alphabetically in IR to ensure canonical JSON stability
- **Field Access Safety**: Field access operations validate field existence at runtime, raising deterministic errors for missing fields
- **Record Type Matching**: Record literals must match declared record types field-by-field (type checker validates)

**Impact on Determinism:**

✅ **Positive Impact**: Record construction and field access are deterministic operations. Field ordering is fixed (alphabetical) to ensure same record structure produces same IR.

**Impact on Canonicalization:**

✅ **Critical Fix**: Record fields are sorted alphabetically during lowering, ensuring:
- Same semantic record → same canonical JSON
- Hash stability across different source field orders
- Deterministic serialization

**Impact on Hash / IR Stability:**

✅ **Stable**: Record IR nodes produce stable hashes because:
- Field order is deterministic (alphabetically sorted)
- Field names and values are deterministic
- No non-deterministic iteration

**TRP Impact:**

✅ **No Changes**: Record expressions appear as `IRExpr` steps in pipelines, tracked in existing step execution records. No new proof record types required.

**Tests Guaranteeing Behavior:**

- Parser tests for record syntax (`tests/test_parser.py`)
- Type checker tests for record type inference and field access (`tests/test_type_checker.py`)
- Lowering tests verify records lower with sorted fields (`tests/test_lowering.py`)
- Executor tests verify record construction and field access (`rlang/bor/proofs.py`)

**Change Provenance:**

- **AST Nodes**: `rlang/parser/ast.py` lines 55-64, 216-225, 228-233
- **Parser Logic**: `rlang/parser/parser.py` lines 827-880
- **Type System**: `rlang/types/type_system.py` lines 47-72, 107-112
- **Type Checking**: `rlang/types/type_checker.py` lines 961-988, 1129-1150
- **Lowering**: `rlang/lowering/lowering.py` lines 294-301, 303-305
- **IR Model**: `rlang/ir/model.py` lines 134, 163-165
- **Execution**: `rlang/bor/proofs.py` lines 266-298

---

### 15.3 List Types and Expressions (v0.2.1+)

**Summary:** Added support for list literal expressions (`[expr1, expr2, ...]`) with ordered element semantics.

**Affected Components:**
- **AST**: Added `ListExpr` node (`rlang/parser/ast.py`)
- **Parser**: Added parsing logic for list literals (`rlang/parser/parser.py`)
- **Type Checker**: Added type checking for list expressions (`rlang/types/type_checker.py`)
- **Lowering**: Added lowering rules to `IRExpr` with `kind="list"` (`rlang/lowering/lowering.py`)
- **IR**: Extended `IRExpr` to support list kind (`rlang/ir/model.py`)
- **Executor**: Added evaluation logic for list construction (`rlang/bor/proofs.py`)

**Precise Physics Changes:**

1. **Ordered Element Semantics**: Lists preserve element order deterministically:
   ```python
   # ListExpr lowering: elements preserved in source order
   def lower_list_expr(expr: ListExpr) -> IRExpr:
       elements_ir = [lower_expr(elem) for elem in expr.elements]
       return IRExpr(kind="list", elements=elements_ir)
   ```

2. **IR Representation**: Lists lower to `IRExpr` nodes with ordered elements:
   ```python
   IRExpr(kind="list", elements=[elem1_ir, elem2_ir, ...])
   ```

3. **Type System**: List types use generic `RType` with type arguments:
   ```python
   RType(name="List", args=(RType(name="Int"),))
   ```

**New Invariants Introduced:**

- **Order Preservation Invariant**: List elements maintain source order in IR—order is part of the semantics
- **Element Type Consistency**: All list elements must have the same type (type checker validates)
- **Static Boundedness**: List lengths are known at compile time (no dynamic lists)

**Impact on Determinism:**

✅ **Positive Impact**: List construction is deterministic. Element order is preserved, ensuring same list structure produces same IR.

**Impact on Canonicalization:**

✅ **No Breaking Changes**: List IR nodes serialize with elements in order. JSON array order is deterministic.

**Impact on Hash / IR Stability:**

✅ **Stable**: List IR nodes produce stable hashes because:
- Element order is deterministic (preserved from source)
- Element values are deterministic
- No non-deterministic iteration

**TRP Impact:**

✅ **No Changes**: List expressions appear as `IRExpr` steps in pipelines, tracked in existing step execution records. No new proof record types required.

**Tests Guaranteeing Behavior:**

- Parser tests for list syntax (`tests/test_parser.py`)
- Type checker tests for list type inference (`tests/test_type_checker.py`)
- Lowering tests verify lists lower with preserved order (`tests/test_lowering.py`)
- Executor tests verify list construction (`rlang/bor/proofs.py`)

**Change Provenance:**

- **AST Nodes**: `rlang/parser/ast.py` lines 236-245
- **Parser Logic**: `rlang/parser/parser.py` lines 773-819
- **Type Checking**: `rlang/types/type_checker.py` lines 989-1010
- **Lowering**: `rlang/lowering/lowering.py` lines 307-310
- **IR Model**: `rlang/ir/model.py` lines 137, 170-171
- **Execution**: `rlang/bor/proofs.py` lines 300-307

---

### 15.4 Pattern Matching (v0.2.1+)

**Summary:** Added support for pattern matching expressions (`match (expr) { case pattern => steps }`) with multiple pattern types (wildcard, literal, variable, record, list).

**Affected Components:**
- **AST**: Added `MatchExpr`, `Case`, `Pattern` hierarchy (`WildcardPattern`, `LiteralPattern`, `VarPattern`, `RecordPattern`, `ListPattern`) (`rlang/parser/ast.py`)
- **Lexer**: Added `KEYWORD_MATCH`, `KEYWORD_CASE`, `ARROW` (`=>`), `UNDERSCORE` (`_`) tokens (`rlang/lexer/tokens.py`)
- **Parser**: Added parsing logic for match expressions and patterns (`rlang/parser/parser.py`)
- **Type Checker**: Added type checking for match expressions (`rlang/types/type_checker.py`)
- **Lowering**: Added lowering rules converting match expressions to nested `IRIf` chains (`rlang/lowering/lowering.py`)
- **IR**: Match expressions lower to nested `IRIf` nodes (no new IR node type) (`rlang/lowering/lowering.py`)
- **Executor**: Pattern matching executes via nested IF execution (no new execution logic) (`rlang/bor/proofs.py`)

**Precise Physics Changes:**

1. **Deterministic Pattern Matching**: Pattern matching lowers to nested IF-ELSE chains with deterministic case ordering:
   ```python
   # MatchExpr lowering: converts to nested IRIf chain
   # Cases processed in source order, last case becomes else branch
   def lower_match_expr_step(match_expr: MatchExpr) -> IRIf:
       # Build nested IRIf chain from cases (reverse order)
       # Each case becomes: if (pattern_matches) then body else next_case
   ```

2. **Pattern Binding**: Variable patterns bind values deterministically:
   ```python
   # VarPattern binds entire scrutinee
   # RecordPattern binds fields recursively
   # ListPattern binds elements by index
   ```

3. **Pattern Condition Lowering**: Patterns lower to boolean conditions with guarded field/index access:
   ```python
   # RecordPattern: AND of field existence checks and field pattern conditions
   # ListPattern: length check AND element pattern conditions
   # LiteralPattern: equality check
   # WildcardPattern/VarPattern: always true
   ```

**New Invariants Introduced:**

- **Case Order Invariant**: Match cases are processed in source order, ensuring deterministic matching behavior
- **Pattern Binding Invariant**: Pattern-bound variables are available in case bodies, bound deterministically
- **Guarded Access Invariant**: Record and list pattern matching guards field/index access to prevent runtime errors
- **Wildcard Uniqueness**: Only one wildcard case allowed per match expression

**Impact on Determinism:**

✅ **Positive Impact**: Pattern matching is deterministic. Case order is fixed (source order), pattern matching logic is deterministic, and pattern bindings are deterministic.

**Impact on Canonicalization:**

✅ **No Breaking Changes**: Match expressions lower to nested `IRIf` nodes, which already have deterministic canonicalization. Pattern field processing uses sorted field order for determinism.

**Impact on Hash / IR Stability:**

✅ **Stable**: Match expressions produce stable IR because:
- Case order is deterministic (source order)
- Pattern lowering is deterministic
- Nested IF structure is deterministic

**TRP Impact:**

✅ **No Changes**: Pattern matching executes via nested IF execution, tracked in existing branch execution records. No new proof record types required.

**Tests Guaranteeing Behavior:**

- Parser tests for match syntax (`tests/test_parser.py`)
- Type checker tests for match type inference (`tests/test_type_checker.py`)
- Lowering tests verify match lowers to nested IF (`tests/test_lowering.py`)
- Executor tests verify pattern matching semantics (`rlang/bor/proofs.py`)

**Change Provenance:**

- **AST Nodes**: `rlang/parser/ast.py` lines 287-361
- **Parser Logic**: `rlang/parser/parser.py` lines 1329-1400
- **Type Checking**: `rlang/types/type_checker.py` lines 558-640, 1023-1050
- **Lowering**: `rlang/lowering/lowering.py` lines 436-686
- **Execution**: Uses existing nested IF execution (`rlang/bor/proofs.py`)

---

### 15.5 For Loops with Static Unrolling (v0.2.1+)

**Summary:** Added support for bounded for loops (`for i in start..end { steps }`) with compile-time constant bounds, unrolled statically into repeated steps.

**Affected Components:**
- **AST**: Added `ForExpr` node (`rlang/parser/ast.py`)
- **Lexer**: Added `KEYWORD_FOR`, `KEYWORD_IN`, `DOTDOT` (`..`) tokens (`rlang/lexer/tokens.py`)
- **Parser**: Added parsing logic for for expressions (`rlang/parser/parser.py`)
- **Type Checker**: Added type checking for for expressions (`rlang/types/type_checker.py`)
- **Lowering**: Added lowering rules unrolling for loops into repeated steps (`rlang/lowering/lowering.py`)
- **IR**: For loops lower to repeated `PipelineStepIR` nodes (no new IR node type) (`rlang/lowering/lowering.py`)
- **Executor**: For loops execute as repeated steps (no new execution logic) (`rlang/bor/proofs.py`)

**Precise Physics Changes:**

1. **Static Unrolling**: For loops are unrolled at compile time into repeated step sequences:
   ```python
   # ForExpr lowering: unrolls loop body (end - start) times
   def lower_for_expr_step(for_expr: ForExpr, start_index: int):
       count = max(0, for_expr.end - for_expr.start)
       body_steps_ir = lower_pipeline_steps_fragment(for_expr.body)
       # Repeat body_steps_ir 'count' times, updating step indices
   ```

2. **Step Index Management**: Unrolled steps receive sequential indices:
   ```python
   # Each iteration's steps get sequential indices
   # PipelineStepIR nodes are duplicated with updated indices
   ```

3. **Bound Validation**: Loop bounds must be compile-time constants (integers):
   ```python
   # start and end must be integer literals
   # No dynamic bounds allowed
   ```

**New Invariants Introduced:**

- **Static Bound Invariant**: For loop bounds must be compile-time constants—no dynamic iteration counts
- **Unrolling Invariant**: For loops are completely unrolled at compile time—no runtime loop execution
- **Index Continuity**: Unrolled steps maintain sequential index ordering across iterations

**Impact on Determinism:**

✅ **Positive Impact**: For loops are deterministic because:
- Bounds are compile-time constants (no runtime variation)
- Unrolling is deterministic (same bounds → same unrolled steps)
- Step execution order is deterministic (sequential)

**Impact on Canonicalization:**

✅ **No Breaking Changes**: For loops lower to standard `PipelineStepIR` nodes, which already have deterministic canonicalization.

**Impact on Hash / IR Stability:**

✅ **Stable**: For loops produce stable IR because:
- Unrolling is deterministic (same bounds → same steps)
- Step indices are deterministic (sequential)
- No non-deterministic iteration

**TRP Impact:**

✅ **No Changes**: For loops execute as repeated steps, tracked in existing step execution records. No new proof record types required.

**Tests Guaranteeing Behavior:**

- Parser tests for for loop syntax (`tests/test_parser.py`)
- Type checker tests for for loop type checking (`tests/test_type_checker.py`)
- Lowering tests verify for loops unroll correctly (`tests/test_lowering.py`)
- Executor tests verify for loop execution (`rlang/bor/proofs.py`)

**Change Provenance:**

- **AST Nodes**: `rlang/parser/ast.py` lines 272-284
- **Parser Logic**: `rlang/parser/parser.py` lines 1276-1318
- **Type Checking**: `rlang/types/type_checker.py` lines 499-560
- **Lowering**: `rlang/lowering/lowering.py` lines 394-434
- **Execution**: Uses existing step execution (`rlang/bor/proofs.py`)

---

### 15.6 Record Field Canonicalization Fix (v0.2.1+)

**Summary:** Fixed canonicalization of record fields to ensure deterministic field ordering in IR and JSON serialization.

**Affected Components:**
- **Lowering**: Record field sorting during lowering (`rlang/lowering/lowering.py`)
- **IR**: Record field sorting in `IRExpr.to_dict()` (`rlang/ir/model.py`)
- **Type Checker**: Pattern field sorting for deterministic processing (`rlang/types/type_checker.py`)

**Precise Physics Changes:**

1. **Field Sorting in Lowering**: Record fields are sorted alphabetically during AST → IR lowering:
   ```python
   # rlang/lowering/lowering.py:295-300
   sorted_fields = dict(sorted(lowered_fields.items()))
   return IRExpr(kind="record", fields=sorted_fields)
   ```

2. **Field Sorting in IR Serialization**: Record fields are sorted again in `IRExpr.to_dict()`:
   ```python
   # rlang/ir/model.py:163-165
   sorted_fields = {k: v.to_dict() for k, v in sorted(self.fields.items())}
   result["fields"] = sorted_fields
   ```

3. **Pattern Field Sorting**: Pattern matching processes record fields in sorted order:
   ```python
   # rlang/types/type_checker.py:685-686
   sorted_field_names = sorted(pattern.fields.keys())
   ```

**Before/After Behavior:**

**Before:** Record fields could appear in non-deterministic order in IR, causing hash instability.

**After:** Record fields are always sorted alphabetically, ensuring:
- Same semantic record → same canonical JSON
- Hash stability across different source field orders
- Deterministic serialization

**Impact on Canonicalization:**

✅ **Critical Fix**: This fix ensures record canonicalization is deterministic. Without this fix, records with same fields in different orders would produce different hashes.

**Impact on Hash / IR Stability:**

✅ **Stable**: Record hashes are now stable regardless of source field order.

**Change Provenance:**

- **Lowering**: `rlang/lowering/lowering.py` lines 295-300
- **IR Model**: `rlang/ir/model.py` lines 163-165
- **Type Checker**: `rlang/types/type_checker.py` lines 685-686

---

### 15.7 Multi-IF Determinism Guarantee (v0.2.1+)

**Summary:** Ensured deterministic execution and proof recording for nested IF expressions and multi-IF pipelines.

**Affected Components:**
- **Executor**: Nested IF execution with deterministic branch recording (`rlang/bor/proofs.py`)
- **Lowering**: Nested IF lowering preserves structure deterministically (`rlang/lowering/lowering.py`)

**Precise Physics Changes:**

1. **Nested IF Execution**: Nested IF expressions execute recursively with deterministic branch recording:
   ```python
   # rlang/bor/proofs.py:419-428
   # Nested IFs execute recursively, branch records appended in encounter order
   nested_current, nested_step_records, nested_branches = _execute_if_step(...)
   branch_records.extend(nested_step_records)
   nested_branch_records.extend(nested_branches)
   ```

2. **Branch Record Ordering**: Branch records are appended in encounter order (outer IF first, then nested IFs):
   ```python
   # Branch record for outer IF appended first
   # Branch records for nested IFs appended in encounter order
   all_branch_records = [branch_record] + nested_branch_records
   ```

**New Invariants Introduced:**

- **Branch Record Order Invariant**: Branch records appear in execution encounter order—outer IFs before nested IFs
- **Nested IF Determinism**: Nested IF execution is deterministic—same condition values → same execution trace

**Impact on Determinism:**

✅ **Positive Impact**: Multi-IF pipelines execute deterministically. Branch decisions are recorded in deterministic order.

**Impact on Proof Structure:**

✅ **Stable**: Proof bundles with nested IFs produce stable branch records in encounter order.

**Change Provenance:**

- **Executor**: `rlang/bor/proofs.py` lines 365-450
- **Lowering**: `rlang/lowering/lowering.py` lines 362-392

---

### 15.8 Expression Steps in Pipelines (v0.2.1+)

**Summary:** Added support for expression-based pipeline steps (RecordExpr, FieldAccess, ListExpr) that can appear directly in pipelines without function calls.

**Affected Components:**
- **AST**: Expression steps supported in `PipelineStep.expr` (`rlang/parser/ast.py`)
- **Type Checker**: Type checking for expression steps (`rlang/types/type_checker.py`)
- **Lowering**: Lowering of expression steps to `IRExpr` (`rlang/lowering/lowering.py`)
- **Executor**: Execution of expression steps (`rlang/bor/proofs.py`)

**Precise Physics Changes:**

1. **Expression Step Lowering**: Expression steps lower to `IRExpr` nodes directly in pipeline:
   ```python
   # rlang/lowering/lowering.py:167-170
   elif isinstance(step.expr, (RecordExpr, FieldAccess, ListExpr)):
       ir_expr = self._lower_expr(step.expr, pattern_bindings={})
       pipeline_steps.append(ir_expr)
   ```

2. **Expression Step Execution**: Expression steps execute via `_eval_irexpr()`:
   ```python
   # rlang/bor/proofs.py:511-528
   elif isinstance(step_ir, IRExpr):
       out_value = _eval_irexpr(step_ir, registry, current_value)
       record = StepExecutionRecord(index=step_idx, ...)
   ```

**New Invariants Introduced:**

- **Expression Step Invariant**: Expression steps produce step execution records with synthetic `template_id` (`expr:kind`)
- **Value Flow Invariant**: Expression steps transform pipeline value deterministically

**Impact on Determinism:**

✅ **Positive Impact**: Expression steps execute deterministically, producing deterministic step records.

**Impact on Proof Structure:**

✅ **Stable**: Expression steps produce stable step execution records with deterministic `template_id` format.

**Change Provenance:**

- **Lowering**: `rlang/lowering/lowering.py` lines 167-170, 347-350
- **Executor**: `rlang/bor/proofs.py` lines 511-528, 429-442

---

**Document Version:** 0.2.1  
**Last Updated:** November 2025  
**Status:** Active Specification

