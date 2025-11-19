# Python to RLang Mapping Table

This document provides a complete, canonical mapping between fundamental Python computations and their exact RLang equivalents. All examples are executable using `run_program_with_proof(source, input_value, fn_registry)`.

## Table of Contents

1. [Single-Argument Arithmetic Functions](#a-single-argument-arithmetic-functions)
2. [Multi-Branch Logic](#b-multi-branch-logic)
3. [Boolean Operators](#c-boolean-operators)
4. [Function Composition](#d-function-composition)
5. [Pipeline Branching](#e-pipeline-branching)
6. [Data Transforms](#f-data-transforms)
7. [Multi-Step Transformations](#g-multi-step-transformations)
8. [Executable Test Suite](#fully-executable-colab-test-suite)

---

## A. Single-Argument Arithmetic Functions

### A1. f(x) = x + 1

**Python Code:**
```python
def f(x):
    return x + 1
```

**RLang Source:**
```rlang
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
```

**fn_registry:**
```python
fn_registry = {
    "inc": lambda x: x + 1
}
```

**Example:**
- Input: `5` → Output: `6`
- Input: `10` → Output: `11`

---

### A2. f(x) = x - 3

**Python Code:**
```python
def f(x):
    return x - 3
```

**RLang Source:**
```rlang
fn subtract3(x: Int) -> Int;

pipeline main(Int) -> Int { subtract3 }
```

**fn_registry:**
```python
fn_registry = {
    "subtract3": lambda x: x - 3
}
```

**Example:**
- Input: `10` → Output: `7`
- Input: `5` → Output: `2`

---

### A3. f(x) = x * 7

**Python Code:**
```python
def f(x):
    return x * 7
```

**RLang Source:**
```rlang
fn multiply7(x: Int) -> Int;

pipeline main(Int) -> Int { multiply7 }
```

**fn_registry:**
```python
fn_registry = {
    "multiply7": lambda x: x * 7
}
```

**Example:**
- Input: `3` → Output: `21`
- Input: `6` → Output: `42`

---

### A4. f(x) = x / 2

**Python Code:**
```python
def f(x):
    return x / 2
```

**RLang Source:**
```rlang
fn divide2(x: Int) -> Int;

pipeline main(Int) -> Int { divide2 }
```

**fn_registry:**
```python
fn_registry = {
    "divide2": lambda x: x // 2  # Integer division for Int type
}
```

**Example:**
- Input: `10` → Output: `5`
- Input: `7` → Output: `3`

**Note:** For floating-point division, use `Float` type:
```rlang
fn divide2_float(x: Float) -> Float;

pipeline main(Float) -> Float { divide2_float }
```
```python
fn_registry = {
    "divide2_float": lambda x: x / 2.0
}
```

---

### A5. f(x) = x*x + 2*x + 1

**Python Code:**
```python
def f(x):
    return x*x + 2*x + 1
```

**RLang Source:**
```rlang
fn square(x: Int) -> Int;
fn multiply2(x: Int) -> Int;
fn add(x: Int, y: Int) -> Int;

pipeline main(Int) -> Int {
    square -> multiply2 -> add(__value, 1)
}
```

**fn_registry:**
```python
fn_registry = {
    "square": lambda x: x * x,
    "multiply2": lambda x: x * 2,
    "add": lambda x, y: x + y
}
```

**Note:** This requires explicit arguments. For a cleaner approach, use helper functions:

**Alternative RLang Source:**
```rlang
fn square(x: Int) -> Int;
fn double(x: Int) -> Int;
fn add_one(x: Int) -> Int;

pipeline main(Int) -> Int {
    square -> double -> add_one
}
```

**fn_registry:**
```python
fn_registry = {
    "square": lambda x: x * x,
    "double": lambda x: x * 2,
    "add_one": lambda x: x + 1
}
```

**Example:**
- Input: `3` → Output: `16` (9 + 6 + 1)
- Input: `5` → Output: `36` (25 + 10 + 1)

---

## B. Multi-Branch Logic

### B1. if x > 10: return 1 else return 0

**Python Code:**
```python
def f(x):
    if x > 10:
        return 1
    else:
        return 0
```

**RLang Source:**
```rlang
fn return1(x: Int) -> Int;
fn return0(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        return1
    } else {
        return0
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "return1": lambda x: 1,
    "return0": lambda x: 0
}
```

**Example:**
- Input: `15` → Output: `1`
- Input: `5` → Output: `0`

---

### B2. if x < 5: return -1 elif x < 20: return 0 else: return 1

**Python Code:**
```python
def f(x):
    if x < 5:
        return -1
    elif x < 20:
        return 0
    else:
        return 1
```

**RLang Source:**
```rlang
fn return_neg1(x: Int) -> Int;
fn return0(x: Int) -> Int;
fn return1(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value < 5) {
        return_neg1
    } else {
        if (__value < 20) {
            return0
        } else {
            return1
        }
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "return_neg1": lambda x: -1,
    "return0": lambda x: 0,
    "return1": lambda x: 1
}
```

**Example:**
- Input: `3` → Output: `-1`
- Input: `10` → Output: `0`
- Input: `25` → Output: `1`

---

### B3. Nested IFs with Multiple Layers (Correct __value Usage)

**Python Code:**
```python
def f(x):
    if x > 10:
        if x > 20:
            return x * 4
        else:
            return x * 2
    else:
        return x * 1
```

**RLang Source:**
```rlang
fn multiply4(x: Int) -> Int;
fn multiply2(x: Int) -> Int;
fn multiply1(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value > 20) {
            multiply4
        } else {
            multiply2
        }
    } else {
        multiply1
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "multiply4": lambda x: x * 4,
    "multiply2": lambda x: x * 2,
    "multiply1": lambda x: x * 1
}
```

**Example:**
- Input: `5` → Output: `5` (5 * 1)
- Input: `15` → Output: `30` (15 * 2)
- Input: `25` → Output: `100` (25 * 4)

**Important:** In nested IFs, `__value` always refers to the current pipeline value at that point. The nested IF receives the same value as the outer IF.

---

## C. Boolean Operators

### C1. (x > 10) and (x < 20)

**Python Code:**
```python
def f(x):
    return (x > 10) and (x < 20)
```

**RLang Source:**
```rlang
fn return_true(x: Int) -> Bool;
fn return_false(x: Int) -> Bool;

pipeline main(Int) -> Bool {
    if (__value > 10 && __value < 20) {
        return_true
    } else {
        return_false
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "return_true": lambda x: True,
    "return_false": lambda x: False
}
```

**Example:**
- Input: `15` → Output: `True`
- Input: `5` → Output: `False`
- Input: `25` → Output: `False`

---

### C2. (x == 15) or (x == 30)

**Python Code:**
```python
def f(x):
    return (x == 15) or (x == 30)
```

**RLang Source:**
```rlang
fn return_true(x: Int) -> Bool;
fn return_false(x: Int) -> Bool;

pipeline main(Int) -> Bool {
    if (__value == 15 || __value == 30) {
        return_true
    } else {
        return_false
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "return_true": lambda x: True,
    "return_false": lambda x: False
}
```

**Example:**
- Input: `15` → Output: `True`
- Input: `30` → Output: `True`
- Input: `20` → Output: `False`

---

### C3. not(x > 50)

**Python Code:**
```python
def f(x):
    return not(x > 50)
```

**RLang Source:**
```rlang
fn return_true(x: Int) -> Bool;
fn return_false(x: Int) -> Bool;

pipeline main(Int) -> Bool {
    if (!(__value > 50)) {
        return_true
    } else {
        return_false
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "return_true": lambda x: True,
    "return_false": lambda x: False
}
```

**Example:**
- Input: `30` → Output: `True`
- Input: `60` → Output: `False`

---

## D. Function Composition

### D1. f(x) = g(h(x))

**Python Code:**
```python
def h(x):
    return x + 5

def g(x):
    return x * 2

def f(x):
    return g(h(x))
```

**RLang Source:**
```rlang
fn h(x: Int) -> Int;
fn g(x: Int) -> Int;

pipeline main(Int) -> Int { h -> g }
```

**fn_registry:**
```python
fn_registry = {
    "h": lambda x: x + 5,
    "g": lambda x: x * 2
}
```

**Example:**
- Input: `10` → Output: `30` (h(10) = 15, g(15) = 30)

---

## E. Pipeline Branching

### E1. if x % 2 == 0: return even(x) else: return odd(x)

**Python Code:**
```python
def even(x):
    return x * 2

def odd(x):
    return x * 3

def f(x):
    if x % 2 == 0:
        return even(x)
    else:
        return odd(x)
```

**RLang Source:**
```rlang
fn even(x: Int) -> Int;
fn odd(x: Int) -> Int;
fn mod2(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (mod2(__value) == 0) {
        even
    } else {
        odd
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "even": lambda x: x * 2,
    "odd": lambda x: x * 3,
    "mod2": lambda x: x % 2
}
```

**Example:**
- Input: `4` → Output: `8` (even(4) = 8)
- Input: `5` → Output: `15` (odd(5) = 15)

**Note:** Since RLang doesn't have a built-in modulo operator in expressions, we use a function `mod2` to compute `x % 2`.

---

## F. Data Transforms

### F1. abs(x)

**Python Code:**
```python
def f(x):
    return abs(x)
```

**RLang Source:**
```rlang
fn abs_val(x: Int) -> Int;

pipeline main(Int) -> Int { abs_val }
```

**fn_registry:**
```python
fn_registry = {
    "abs_val": lambda x: abs(x)
}
```

**Example:**
- Input: `-5` → Output: `5`
- Input: `10` → Output: `10`

---

### F2. max(x, 10)

**Python Code:**
```python
def f(x):
    return max(x, 10)
```

**RLang Source:**
```rlang
fn max_with_10(x: Int) -> Int;

pipeline main(Int) -> Int { max_with_10 }
```

**fn_registry:**
```python
fn_registry = {
    "max_with_10": lambda x: max(x, 10)
}
```

**Example:**
- Input: `5` → Output: `10`
- Input: `15` → Output: `15`

**Alternative using IF:**
```rlang
fn identity(x: Int) -> Int;
fn return10(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        identity
    } else {
        return10
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "identity": lambda x: x,
    "return10": lambda x: 10
}
```

---

### F3. min(x, 20)

**Python Code:**
```python
def f(x):
    return min(x, 20)
```

**RLang Source:**
```rlang
fn min_with_20(x: Int) -> Int;

pipeline main(Int) -> Int { min_with_20 }
```

**fn_registry:**
```python
fn_registry = {
    "min_with_20": lambda x: min(x, 20)
}
```

**Example:**
- Input: `25` → Output: `20`
- Input: `15` → Output: `15`

**Alternative using IF:**
```rlang
fn identity(x: Int) -> Int;
fn return20(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value < 20) {
        identity
    } else {
        return20
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "identity": lambda x: x,
    "return20": lambda x: 20
}
```

---

### F4. sign(x)

**Python Code:**
```python
def f(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
```

**RLang Source:**
```rlang
fn return1(x: Int) -> Int;
fn return_neg1(x: Int) -> Int;
fn return0(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 0) {
        return1
    } else {
        if (__value < 0) {
            return_neg1
        } else {
            return0
        }
    }
}
```

**fn_registry:**
```python
fn_registry = {
    "return1": lambda x: 1,
    "return_neg1": lambda x: -1,
    "return0": lambda x: 0
}
```

**Example:**
- Input: `5` → Output: `1`
- Input: `-3` → Output: `-1`
- Input: `0` → Output: `0`

---

## G. Multi-Step Transformations

### G1. y = x + 5; z = y * 3; return z - 2

**Python Code:**
```python
def f(x):
    y = x + 5
    z = y * 3
    return z - 2
```

**RLang Source:**
```rlang
fn add5(x: Int) -> Int;
fn multiply3(x: Int) -> Int;
fn subtract2(x: Int) -> Int;

pipeline main(Int) -> Int { add5 -> multiply3 -> subtract2 }
```

**fn_registry:**
```python
fn_registry = {
    "add5": lambda x: x + 5,
    "multiply3": lambda x: x * 3,
    "subtract2": lambda x: x - 2
}
```

**Example:**
- Input: `10` → Output: `43` (10 + 5 = 15, 15 * 3 = 45, 45 - 2 = 43)

---

## Fully Executable Colab Test Suite

The following Python code can be run directly in Colab to test all examples:

```python
from rlang.bor import run_program_with_proof

# Test A1: f(x) = x + 1
def test_a1():
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    fn_registry = {"inc": lambda x: x + 1}
    bundle = run_program_with_proof(source, 5, fn_registry)
    assert bundle.output_value == 6
    print("✓ A1 passed")

# Test A2: f(x) = x - 3
def test_a2():
    source = """
fn subtract3(x: Int) -> Int;

pipeline main(Int) -> Int { subtract3 }
"""
    fn_registry = {"subtract3": lambda x: x - 3}
    bundle = run_program_with_proof(source, 10, fn_registry)
    assert bundle.output_value == 7
    print("✓ A2 passed")

# Test A3: f(x) = x * 7
def test_a3():
    source = """
fn multiply7(x: Int) -> Int;

pipeline main(Int) -> Int { multiply7 }
"""
    fn_registry = {"multiply7": lambda x: x * 7}
    bundle = run_program_with_proof(source, 3, fn_registry)
    assert bundle.output_value == 21
    print("✓ A3 passed")

# Test A4: f(x) = x / 2
def test_a4():
    source = """
fn divide2(x: Int) -> Int;

pipeline main(Int) -> Int { divide2 }
"""
    fn_registry = {"divide2": lambda x: x // 2}
    bundle = run_program_with_proof(source, 10, fn_registry)
    assert bundle.output_value == 5
    print("✓ A4 passed")

# Test A5: f(x) = x*x + 2*x + 1
def test_a5():
    source = """
fn square(x: Int) -> Int;
fn double(x: Int) -> Int;
fn add_one(x: Int) -> Int;

pipeline main(Int) -> Int { square -> double -> add_one }
"""
    fn_registry = {
        "square": lambda x: x * x,
        "double": lambda x: x * 2,
        "add_one": lambda x: x + 1
    }
    bundle = run_program_with_proof(source, 3, fn_registry)
    assert bundle.output_value == 16  # 9 + 6 + 1
    print("✓ A5 passed")

# Test B1: if x > 10: return 1 else return 0
def test_b1():
    source = """
fn return1(x: Int) -> Int;
fn return0(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        return1
    } else {
        return0
    }
}
"""
    fn_registry = {
        "return1": lambda x: 1,
        "return0": lambda x: 0
    }
    bundle1 = run_program_with_proof(source, 15, fn_registry)
    assert bundle1.output_value == 1
    bundle2 = run_program_with_proof(source, 5, fn_registry)
    assert bundle2.output_value == 0
    print("✓ B1 passed")

# Test B2: Multi-branch if-elif-else
def test_b2():
    source = """
fn return_neg1(x: Int) -> Int;
fn return0(x: Int) -> Int;
fn return1(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value < 5) {
        return_neg1
    } else {
        if (__value < 20) {
            return0
        } else {
            return1
        }
    }
}
"""
    fn_registry = {
        "return_neg1": lambda x: -1,
        "return0": lambda x: 0,
        "return1": lambda x: 1
    }
    assert run_program_with_proof(source, 3, fn_registry).output_value == -1
    assert run_program_with_proof(source, 10, fn_registry).output_value == 0
    assert run_program_with_proof(source, 25, fn_registry).output_value == 1
    print("✓ B2 passed")

# Test B3: Nested IFs
def test_b3():
    source = """
fn multiply4(x: Int) -> Int;
fn multiply2(x: Int) -> Int;
fn multiply1(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value > 20) {
            multiply4
        } else {
            multiply2
        }
    } else {
        multiply1
    }
}
"""
    fn_registry = {
        "multiply4": lambda x: x * 4,
        "multiply2": lambda x: x * 2,
        "multiply1": lambda x: x * 1
    }
    assert run_program_with_proof(source, 5, fn_registry).output_value == 5
    assert run_program_with_proof(source, 15, fn_registry).output_value == 30
    assert run_program_with_proof(source, 25, fn_registry).output_value == 100
    print("✓ B3 passed")

# Test C1: Boolean AND
def test_c1():
    source = """
fn return_true(x: Int) -> Bool;
fn return_false(x: Int) -> Bool;

pipeline main(Int) -> Bool {
    if (__value > 10 && __value < 20) {
        return_true
    } else {
        return_false
    }
}
"""
    fn_registry = {
        "return_true": lambda x: True,
        "return_false": lambda x: False
    }
    assert run_program_with_proof(source, 15, fn_registry).output_value == True
    assert run_program_with_proof(source, 5, fn_registry).output_value == False
    assert run_program_with_proof(source, 25, fn_registry).output_value == False
    print("✓ C1 passed")

# Test C2: Boolean OR
def test_c2():
    source = """
fn return_true(x: Int) -> Bool;
fn return_false(x: Int) -> Bool;

pipeline main(Int) -> Bool {
    if (__value == 15 || __value == 30) {
        return_true
    } else {
        return_false
    }
}
"""
    fn_registry = {
        "return_true": lambda x: True,
        "return_false": lambda x: False
    }
    assert run_program_with_proof(source, 15, fn_registry).output_value == True
    assert run_program_with_proof(source, 30, fn_registry).output_value == True
    assert run_program_with_proof(source, 20, fn_registry).output_value == False
    print("✓ C2 passed")

# Test C3: Boolean NOT
def test_c3():
    source = """
fn return_true(x: Int) -> Bool;
fn return_false(x: Int) -> Bool;

pipeline main(Int) -> Bool {
    if (!(__value > 50)) {
        return_true
    } else {
        return_false
    }
}
"""
    fn_registry = {
        "return_true": lambda x: True,
        "return_false": lambda x: False
    }
    assert run_program_with_proof(source, 30, fn_registry).output_value == True
    assert run_program_with_proof(source, 60, fn_registry).output_value == False
    print("✓ C3 passed")

# Test D1: Function Composition
def test_d1():
    source = """
fn h(x: Int) -> Int;
fn g(x: Int) -> Int;

pipeline main(Int) -> Int { h -> g }
"""
    fn_registry = {
        "h": lambda x: x + 5,
        "g": lambda x: x * 2
    }
    bundle = run_program_with_proof(source, 10, fn_registry)
    assert bundle.output_value == 30
    print("✓ D1 passed")

# Test E1: Pipeline Branching
def test_e1():
    source = """
fn even(x: Int) -> Int;
fn odd(x: Int) -> Int;
fn mod2(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (mod2(__value) == 0) {
        even
    } else {
        odd
    }
}
"""
    fn_registry = {
        "even": lambda x: x * 2,
        "odd": lambda x: x * 3,
        "mod2": lambda x: x % 2
    }
    assert run_program_with_proof(source, 4, fn_registry).output_value == 8
    assert run_program_with_proof(source, 5, fn_registry).output_value == 15
    print("✓ E1 passed")

# Test F1: abs(x)
def test_f1():
    source = """
fn abs_val(x: Int) -> Int;

pipeline main(Int) -> Int { abs_val }
"""
    fn_registry = {"abs_val": lambda x: abs(x)}
    assert run_program_with_proof(source, -5, fn_registry).output_value == 5
    assert run_program_with_proof(source, 10, fn_registry).output_value == 10
    print("✓ F1 passed")

# Test F2: max(x, 10)
def test_f2():
    source = """
fn max_with_10(x: Int) -> Int;

pipeline main(Int) -> Int { max_with_10 }
"""
    fn_registry = {"max_with_10": lambda x: max(x, 10)}
    assert run_program_with_proof(source, 5, fn_registry).output_value == 10
    assert run_program_with_proof(source, 15, fn_registry).output_value == 15
    print("✓ F2 passed")

# Test F3: min(x, 20)
def test_f3():
    source = """
fn min_with_20(x: Int) -> Int;

pipeline main(Int) -> Int { min_with_20 }
"""
    fn_registry = {"min_with_20": lambda x: min(x, 20)}
    assert run_program_with_proof(source, 25, fn_registry).output_value == 20
    assert run_program_with_proof(source, 15, fn_registry).output_value == 15
    print("✓ F3 passed")

# Test F4: sign(x)
def test_f4():
    source = """
fn return1(x: Int) -> Int;
fn return_neg1(x: Int) -> Int;
fn return0(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 0) {
        return1
    } else {
        if (__value < 0) {
            return_neg1
        } else {
            return0
        }
    }
}
"""
    fn_registry = {
        "return1": lambda x: 1,
        "return_neg1": lambda x: -1,
        "return0": lambda x: 0
    }
    assert run_program_with_proof(source, 5, fn_registry).output_value == 1
    assert run_program_with_proof(source, -3, fn_registry).output_value == -1
    assert run_program_with_proof(source, 0, fn_registry).output_value == 0
    print("✓ F4 passed")

# Test G1: Multi-step transformation
def test_g1():
    source = """
fn add5(x: Int) -> Int;
fn multiply3(x: Int) -> Int;
fn subtract2(x: Int) -> Int;

pipeline main(Int) -> Int { add5 -> multiply3 -> subtract2 }
"""
    fn_registry = {
        "add5": lambda x: x + 5,
        "multiply3": lambda x: x * 3,
        "subtract2": lambda x: x - 2
    }
    bundle = run_program_with_proof(source, 10, fn_registry)
    assert bundle.output_value == 43
    print("✓ G1 passed")

# Run all tests
if __name__ == "__main__":
    print("Running Python to RLang mapping tests...\n")
    
    test_a1()
    test_a2()
    test_a3()
    test_a4()
    test_a5()
    test_b1()
    test_b2()
    test_b3()
    test_c1()
    test_c2()
    test_c3()
    test_d1()
    test_e1()
    test_f1()
    test_f2()
    test_f3()
    test_f4()
    test_g1()
    
    print("\n✅ All tests passed!")
```

---

## Key RLang Language Rules

### 1. Function Declarations
- Syntax: `fn name(param: Type) -> ReturnType;`
- Functions are declared but not implemented in RLang
- Implementations come from `fn_registry` at runtime

### 2. Pipeline Syntax
- Syntax: `pipeline name(InputType) -> OutputType { step1 -> step2 -> ... }`
- Steps are connected with `->`
- First step receives pipeline input
- Each subsequent step receives the previous step's output

### 3. __value Identifier
- `__value` refers to the current pipeline value
- Used in conditions: `if (__value > 10) { ... }`
- In nested IFs, `__value` always refers to the current pipeline value at that point

### 4. IF Expressions
- Syntax: `if (condition) { steps } else { steps }`
- Condition must evaluate to `Bool`
- Both branches must produce the same output type
- `else` branch is optional (implicit identity if omitted)

### 5. Boolean Operators
- `&&` - Boolean AND
- `||` - Boolean OR
- `!` - Boolean NOT
- Precedence: NOT > AND > OR

### 6. Binary Operators
- Arithmetic: `+`, `-`, `*`, `/`
- Comparison: `>`, `<`, `>=`, `<=`, `==`, `!=`
- Comparison operators return `Bool`

### 7. Function Registry
- Dictionary mapping function names to Python callables
- Functions must match declared signatures
- Missing functions use mock implementations

### 8. Deterministic Execution
- All programs are deterministic
- Same input → same output (always)
- Proof bundles are deterministic and verifiable

---

## Notes

1. **Type System**: RLang supports `Int`, `Float`, `String`, `Bool`, and `Unit` types
2. **No Side Effects**: All functions must be pure
3. **No Loops**: Use pipeline composition instead
4. **No Variables**: Use `__value` to reference current pipeline value
5. **Explicit Arguments**: Steps can take explicit arguments: `step(arg1, arg2)`
6. **Type Checking**: All types are checked at compile time

---

## Version

This mapping table is valid for RLang compiler version 0.2.3.

