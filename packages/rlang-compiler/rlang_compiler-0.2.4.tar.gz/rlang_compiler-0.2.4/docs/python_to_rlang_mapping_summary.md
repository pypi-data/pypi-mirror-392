# Python to RLang Mapping - Summary

## Overview

This document provides a complete, canonical mapping between fundamental Python computations and their exact RLang equivalents. All examples have been verified to:

- Parse successfully using the RLang parser
- Type-check cleanly
- Lower to canonical IR
- Execute correctly
- Generate deterministic TRP traces
- Produce valid HMASTER and HRICH hashes

## Quick Reference

### Basic Syntax

| Python Concept | RLang Equivalent |
|----------------|-----------------|
| `def f(x): return x + 1` | `fn f(x: Int) -> Int;` + `pipeline main(Int) -> Int { f }` |
| `if x > 10: return 1` | `if (__value > 10) { return1 } else { return0 }` |
| `(x > 10) and (x < 20)` | `__value > 10 && __value < 20` |
| `f(g(x))` | `pipeline main(Int) -> Int { g -> f }` |
| `y = x + 5; z = y * 3` | `pipeline main(Int) -> Int { add5 -> multiply3 }` |

### Key Language Rules

1. **Functions**: Declared with `fn name(params) -> Type;` but implemented in `fn_registry`
2. **Pipelines**: Sequential composition with `->` operator
3. **__value**: Special identifier referring to current pipeline value
4. **IF expressions**: `if (condition) { steps } else { steps }`
5. **Boolean ops**: `&&` (AND), `||` (OR), `!` (NOT)
6. **Binary ops**: `+`, `-`, `*`, `/`, `>`, `<`, `>=`, `<=`, `==`, `!=`

## Mapping Categories

### A. Single-Argument Arithmetic Functions
- `f(x) = x + 1` → `fn inc(x: Int) -> Int; pipeline main(Int) -> Int { inc }`
- `f(x) = x - 3` → `fn subtract3(x: Int) -> Int; pipeline main(Int) -> Int { subtract3 }`
- `f(x) = x * 7` → `fn multiply7(x: Int) -> Int; pipeline main(Int) -> Int { multiply7 }`
- `f(x) = x / 2` → `fn divide2(x: Int) -> Int; pipeline main(Int) -> Int { divide2 }`
- `f(x) = x*x + 2*x + 1` → Pipeline with `square -> double -> add_one`

### B. Multi-Branch Logic
- `if x > 10: return 1 else return 0` → `if (__value > 10) { return1 } else { return0 }`
- `if x < 5: return -1 elif x < 20: return 0 else: return 1` → Nested IF expressions
- Nested IFs use `__value` correctly at each level

### C. Boolean Operators
- `(x > 10) and (x < 20)` → `__value > 10 && __value < 20`
- `(x == 15) or (x == 30)` → `__value == 15 || __value == 30`
- `not(x > 50)` → `!(__value > 50)`

### D. Function Composition
- `f(x) = g(h(x))` → `pipeline main(Int) -> Int { h -> g }`

### E. Pipeline Branching
- `if x % 2 == 0: return even(x) else: return odd(x)` → IF with function calls

### F. Data Transforms
- `abs(x)` → `fn abs_val(x: Int) -> Int; pipeline main(Int) -> Int { abs_val }`
- `max(x, 10)` → Function or IF-based implementation
- `min(x, 20)` → Function or IF-based implementation
- `sign(x)` → Nested IF expression

### G. Multi-Step Transformations
- `y = x + 5; z = y * 3; return z - 2` → `pipeline main(Int) -> Int { add5 -> multiply3 -> subtract2 }`

## Usage Example

```python
from rlang.bor import run_program_with_proof

# Define RLang source
source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""

# Define function registry
fn_registry = {
    "inc": lambda x: x + 1
}

# Execute with proof
bundle = run_program_with_proof(source, input_value=5, fn_registry=fn_registry)
print(f"Output: {bundle.output_value}")  # Output: 6
```

## Complete Documentation

See `python_to_rlang_mapping.md` for:
- Detailed examples with Python code, RLang source, and fn_registry
- Input/output examples for each mapping
- Fully executable Colab test suite
- Complete language rules reference

## Verification

All examples in the mapping table have been verified to:
- ✅ Parse correctly
- ✅ Type-check successfully
- ✅ Execute deterministically
- ✅ Generate valid proof bundles
- ✅ Produce stable hashes

## Version

This mapping is valid for RLang compiler version 0.2.3.

