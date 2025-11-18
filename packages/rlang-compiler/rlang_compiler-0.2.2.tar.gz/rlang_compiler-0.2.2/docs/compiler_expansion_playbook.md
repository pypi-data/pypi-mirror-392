# The RLang Compiler Expansion Playbook
## Implementation Checklists, Test Matrices & Modularization Guide

**Version:** 0.2.1 → 0.3.x → 1.0  
**Date:** November 2025  
**Status:** Active Engineering Playbook

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Implementation Checklists](#2-implementation-checklists-for-each-expansion)
3. [Test Matrices](#3-test-matrix-for-every-new-construct)
4. [Golden File Scaffolding](#4-golden-file-scaffolding-scripts)
5. [Refactor-Safe Modularization Plan](#5-refactor-safe-modularization-plan)
6. [Quick Reference](#6-quick-reference)
7. [Appendix: Implementation Status & Change Log (Auto-Reconstructed)](#7-appendix-implementation-status--change-log-auto-reconstructed)

---

## 1. Introduction

This playbook is a **companion document** to [`compiler_physics.md`](./compiler_physics.md). While the physics document defines **what** must remain invariant, this playbook provides **how** to safely extend the compiler.

### 1.1 Purpose

- **Implementation Guidance**: Step-by-step checklists for adding new features
- **Testing Strategy**: Comprehensive test matrices for validation
- **Golden File Management**: Scripts and processes for regression testing
- **Refactoring Safety**: Plans for structural improvements without breaking determinism

### 1.2 Prerequisites

Before using this playbook:

1. ✅ Read [`compiler_physics.md`](./compiler_physics.md) sections 1-11
2. ✅ Understand the three non-negotiable invariants
3. ✅ Familiarize yourself with current IR structure
4. ✅ Review existing test patterns in `tests/`

### 1.3 Expansion Philosophy

**Every expansion must:**

- Preserve deterministic execution
- Maintain canonical JSON stability
- Keep proof trace compatibility (or version appropriately)
- Pass all existing tests
- Add comprehensive new tests

**Never:**

- Break existing golden files without justification
- Introduce non-deterministic behavior
- Change canonical JSON rules
- Modify frozen components (see physics doc)

---

## 2. Implementation Checklists for Each Expansion

### 2.1 Boolean Operators (AND/OR/NOT + Grouping)

**Priority:** High  
**Target Version:** 0.3.0  
**Complexity:** Medium

#### 2.1.1 Spec Update Tasks

- [ ] Update grammar in `docs/compiler_physics.md` section 14.1
- [ ] Add boolean operator semantics to section 4.2.3
- [ ] Document operator precedence rules
- [ ] Add examples to language spec

**Grammar Additions:**

```ebnf
OPERATOR ::= ... | && | || | !
Expr     ::= ... | Expr && Expr | Expr || Expr | ! Expr | ( Expr )
```

#### 2.1.2 Lexer Changes

**File:** `rlang/lexer/tokens.py`

- [ ] Add `AND = "&&"` token
- [ ] Add `OR = "||"` token
- [ ] Add `NOT = "!"` token
- [ ] Add `LPAREN = "("` token (if not exists)
- [ ] Add `RPAREN = ")"` token (if not exists)
- [ ] Update token regex patterns
- [ ] Add unit tests: `tests/test_lexer.py::test_boolean_operators`

**Example Test:**

```python
def test_boolean_operators():
    tokens = tokenize("a && b || !c")
    assert tokens[0].kind == "IDENTIFIER"
    assert tokens[1].kind == "AND"
    assert tokens[2].kind == "IDENTIFIER"
    assert tokens[3].kind == "OR"
    assert tokens[4].kind == "NOT"
    assert tokens[5].kind == "IDENTIFIER"
```

#### 2.1.3 Parser Changes

**File:** `rlang/parser/parser.py`

- [ ] Add `BinaryOp` support for `&&` and `||`
- [ ] Add `UnaryOp` support for `!`
- [ ] Add parenthesized expression parsing
- [ ] Implement operator precedence (NOT > AND > OR)
- [ ] Add AST nodes: `BooleanAnd`, `BooleanOr`, `BooleanNot`
- [ ] Update `parse_expr()` to handle grouping
- [ ] Add unit tests: `tests/test_parser.py::test_boolean_expressions`

**AST Nodes:**

```python
@dataclass
class BooleanAnd(Expr):
    left: Expr
    right: Expr

@dataclass
class BooleanOr(Expr):
    left: Expr
    right: Expr

@dataclass
class BooleanNot(Expr):
    operand: Expr
```

#### 2.1.4 Resolver Changes

**File:** `rlang/semantic/resolver.py`

- [ ] No changes required (boolean operators are built-in)
- [ ] Verify identifier resolution works in boolean expressions
- [ ] Add test: `tests/test_resolver.py::test_boolean_expr_resolution`

#### 2.1.5 Typechecker Checks

**File:** `rlang/types/type_checker.py`

- [ ] Add type rule: `Bool && Bool → Bool`
- [ ] Add type rule: `Bool || Bool → Bool`
- [ ] Add type rule: `!Bool → Bool`
- [ ] Add type error: `Int && Bool` → TypeCheckError
- [ ] Add unit tests: `tests/test_type_checker.py::test_boolean_operators`

**Type Rules:**

```python
def check_boolean_and(self, expr: BooleanAnd) -> RType:
    left_type = self.check_expr(expr.left)
    right_type = self.check_expr(expr.right)
    if left_type.name != "Bool" or right_type.name != "Bool":
        raise TypeCheckError(f"Boolean operators require Bool operands")
    return RType(name="Bool")
```

#### 2.1.6 IR Node Additions

**File:** `rlang/ir/model.py`

- [ ] Extend `IRExpr` to support boolean operators
- [ ] Add `kind="boolean_and"`, `kind="boolean_or"`, `kind="boolean_not"`
- [ ] Update `to_dict()` to serialize boolean operators
- [ ] Ensure canonical ordering (left before right)
- [ ] Add unit tests: `tests/test_primary_ir.py::test_boolean_ir`

**IR Representation:**

```python
# In IRExpr.to_dict()
if self.kind == "boolean_and":
    result["op"] = "&&"
    result["left"] = self.left.to_dict()
    result["right"] = self.right.to_dict()
```

#### 2.1.7 Lowering Rules

**File:** `rlang/lowering/lowering.py`

- [ ] Lower `BooleanAnd` → `IRExpr(kind="boolean_and", ...)`
- [ ] Lower `BooleanOr` → `IRExpr(kind="boolean_or", ...)`
- [ ] Lower `BooleanNot` → `IRExpr(kind="boolean_not", ...)`
- [ ] Preserve operator precedence in lowering
- [ ] Add unit tests: `tests/test_lowering.py::test_boolean_lowering`

**Lowering Code:**

```python
def lower_expr(self, expr: Expr) -> IRExpr:
    if isinstance(expr, BooleanAnd):
        return IRExpr(
            kind="boolean_and",
            left=self.lower_expr(expr.left),
            right=self.lower_expr(expr.right)
        )
    # ... similar for BooleanOr, BooleanNot
```

#### 2.1.8 Executor Changes

**File:** `rlang/bor/proofs.py`

- [ ] Add evaluation for `boolean_and` in `_eval_irexpr()`
- [ ] Add evaluation for `boolean_or` in `_eval_irexpr()`
- [ ] Add evaluation for `boolean_not` in `_eval_irexpr()`
- [ ] Implement short-circuit evaluation (if desired)
- [ ] Add unit tests: `tests/test_proofs.py::test_boolean_execution`

**Execution Code:**

```python
def _eval_irexpr(expr: IRExpr, ...) -> Any:
    if expr.kind == "boolean_and":
        left = _eval_irexpr(expr.left, ...)
        right = _eval_irexpr(expr.right, ...)
        return left and right
    elif expr.kind == "boolean_or":
        left = _eval_irexpr(expr.left, ...)
        right = _eval_irexpr(expr.right, ...)
        return left or right
    elif expr.kind == "boolean_not":
        operand = _eval_irexpr(expr.operand, ...)
        return not operand
```

#### 2.1.9 Canonicalization Extensions

**File:** `rlang/utils/canonical_json.py`

- [ ] Verify boolean operators serialize correctly
- [ ] Ensure operator order is deterministic (left before right)
- [ ] Test nested boolean expressions
- [ ] Add test: `tests/test_base.py::test_boolean_canonical_json`

**Verification:**

```python
def test_boolean_canonical_json():
    expr = {"kind": "boolean_and", "left": {"kind": "literal", "value": True}, "right": {"kind": "literal", "value": False}}
    json1 = canonical_dumps(expr)
    json2 = canonical_dumps(expr)
    assert json1 == json2
```

#### 2.1.10 TRP / Proof Recording Tasks

**File:** `rlang/bor/proofs.py`

- [ ] Boolean operators in conditions are already recorded via `BranchExecutionRecord`
- [ ] Verify condition evaluation includes boolean operators
- [ ] Add test: `tests/test_proofs.py::test_boolean_condition_proof`

#### 2.1.11 Golden File Updates

- [ ] Generate golden file: `tests/golden/v0.3.0/boolean_operators.json`
- [ ] Include canonical JSON for boolean expressions
- [ ] Include H_IR hash
- [ ] Include execution trace with boolean conditions

**Script:** Use `scripts/generate_golden_files.py` (see section 4)

#### 2.1.12 Determinism Tests

**File:** `tests/test_proofs.py`

- [ ] Test: Same boolean expression → same IR
- [ ] Test: Same boolean expression → same H_IR
- [ ] Test: Same execution → same TRP
- [ ] Test: Same TRP → same HRICH
- [ ] Test: Cross-platform determinism

**Test Template:**

```python
def test_boolean_operators_determinism():
    source = """
    fn check(x: Int) -> Bool;
    pipeline main(Int) -> Bool {
        if (check(__value) && __value > 10) {
            check
        } else {
            check
        }
    }
    """
    for v in [5, 15]:
        a = run_program_with_proof(source, v).to_dict()
        b = run_program_with_proof(source, v).to_dict()
        assert a == b
```

#### 2.1.13 Hash Stability Tests

**File:** `tests/test_bor_crypto.py`

- [ ] Test: Boolean operators don't change H_IR for equivalent programs
- [ ] Test: Boolean operators produce stable HRICH
- [ ] Test: Nested boolean expressions hash consistently

#### 2.1.14 Examples + Documentation Update

- [ ] Add examples to `examples/boolean_operators.rlang`
- [ ] Update `docs/language.md` with boolean operator syntax
- [ ] Update `README.md` with boolean operator examples
- [ ] Add to compiler physics doc section 4.2.3

---

### 2.2 Records (IRRecord + Field Access)

**Priority:** High  
**Target Version:** 0.3.0  
**Complexity:** High

#### 2.2.1 Spec Update Tasks

- [ ] Add record type syntax to grammar
- [ ] Add record construction syntax
- [ ] Add field access syntax
- [ ] Document record semantics in compiler physics doc

**Grammar Additions:**

```ebnf
TypeExpr     ::= ... | RecordType
RecordType   ::= Record { FieldList }
FieldList    ::= Field ( , Field )*
Field        ::= IDENTIFIER : TypeExpr
Expr         ::= ... | RecordExpr | FieldAccess
RecordExpr   ::= { FieldValueList }
FieldValueList ::= FieldValue ( , FieldValue )*
FieldValue   ::= IDENTIFIER : Expr
FieldAccess  ::= Expr . IDENTIFIER
```

#### 2.2.2 Lexer Changes

**File:** `rlang/lexer/tokens.py`

- [ ] Add `RECORD = "Record"` keyword
- [ ] Add `DOT = "."` token
- [ ] Update keyword list
- [ ] Add tests: `tests/test_lexer.py::test_record_tokens`

#### 2.2.3 Parser Changes

**File:** `rlang/parser/parser.py`

- [ ] Add `RecordType` AST node
- [ ] Add `RecordExpr` AST node
- [ ] Add `FieldAccess` AST node
- [ ] Parse record type definitions
- [ ] Parse record construction expressions
- [ ] Parse field access expressions
- [ ] Add tests: `tests/test_parser.py::test_record_parsing`

**AST Nodes:**

```python
@dataclass
class RecordType(TypeExpr):
    fields: List[Field]  # Field(name: str, type_expr: TypeExpr)

@dataclass
class RecordExpr(Expr):
    fields: Dict[str, Expr]  # Field name → expression

@dataclass
class FieldAccess(Expr):
    record: Expr
    field_name: str
```

#### 2.2.4 Resolver Changes

**File:** `rlang/semantic/resolver.py`

- [ ] Resolve record type definitions
- [ ] Resolve field names in record expressions
- [ ] Resolve field access (record type → field type)
- [ ] Add symbol table entries for record types
- [ ] Add tests: `tests/test_resolver.py::test_record_resolution`

#### 2.2.5 Typechecker Checks

**File:** `rlang/types/type_checker.py`

- [ ] Type check record construction (field types match)
- [ ] Type check field access (record has field)
- [ ] Type check record type definitions
- [ ] Add type inference for record expressions
- [ ] Add tests: `tests/test_type_checker.py::test_record_types`

**Type Rules:**

```python
def check_record_expr(self, expr: RecordExpr, expected_type: RType) -> RType:
    if not isinstance(expected_type, RecordRType):
        raise TypeCheckError("Expected record type")
    # Check each field matches expected type
    for field_name, field_expr in expr.fields.items():
        expected_field_type = expected_type.get_field_type(field_name)
        actual_field_type = self.check_expr(field_expr, expected_field_type)
        if actual_field_type != expected_field_type:
            raise TypeCheckError(f"Field {field_name} type mismatch")
    return expected_type
```

#### 2.2.6 IR Node Additions

**File:** `rlang/ir/model.py`

- [ ] Add `IRRecord` dataclass
- [ ] Add `IRFieldAccess` to `IRExpr` kinds
- [ ] Ensure field ordering is deterministic (sorted keys)
- [ ] Add `to_dict()` with sorted field keys
- [ ] Add tests: `tests/test_primary_ir.py::test_record_ir`

**IR Node:**

```python
@dataclass(frozen=True)
class IRRecord:
    """IR representation of a record construction."""
    fields: Dict[str, IRExpr]  # Field name → expression
    
    def to_dict(self) -> Dict[str, Any]:
        """Canonical dictionary representation with sorted keys."""
        return {
            "fields": {
                k: v.to_dict() 
                for k, v in sorted(self.fields.items())  # CRITICAL: Sorted!
            },
            "kind": "record"
        }
```

#### 2.2.7 Lowering Rules

**File:** `rlang/lowering/lowering.py`

- [ ] Lower `RecordExpr` → `IRRecord`
- [ ] Lower `FieldAccess` → `IRExpr(kind="field_access", ...)`
- [ ] Ensure field keys are sorted during lowering
- [ ] Add tests: `tests/test_lowering.py::test_record_lowering`

**Lowering Code:**

```python
def lower_record_expr(self, expr: RecordExpr) -> IRRecord:
    return IRRecord(
        fields={
            k: self.lower_expr(v)
            for k, v in sorted(expr.fields.items())  # Sorted!
        }
    )

def lower_field_access(self, expr: FieldAccess) -> IRExpr:
    return IRExpr(
        kind="field_access",
        record=self.lower_expr(expr.record),
        field_name=expr.field_name
    )
```

#### 2.2.8 Executor Changes

**File:** `rlang/bor/proofs.py`

- [ ] Add evaluation for `IRRecord` in `_eval_irexpr()`
- [ ] Add evaluation for `field_access` in `_eval_irexpr()`
- [ ] Ensure field access is deterministic
- [ ] Add tests: `tests/test_proofs.py::test_record_execution`

**Execution Code:**

```python
def _eval_irexpr(expr: IRExpr | IRRecord, ...) -> Any:
    if isinstance(expr, IRRecord):
        return {
            k: _eval_irexpr(v, ...)
            for k, v in sorted(expr.fields.items())  # Sorted!
        }
    elif expr.kind == "field_access":
        record = _eval_irexpr(expr.record, ...)
        return record[expr.field_name]
```

#### 2.2.9 Canonicalization Extensions

**File:** `rlang/utils/canonical_json.py`

- [ ] Verify record fields serialize with sorted keys
- [ ] Test nested records
- [ ] Test records with various field types
- [ ] Add test: `tests/test_base.py::test_record_canonical_json`

#### 2.2.10 TRP / Proof Recording Tasks

**File:** `rlang/bor/proofs.py`

- [ ] Records in proof traces must use sorted keys
- [ ] Field access operations recorded as steps (if needed)
- [ ] Add `CollectionExecutionRecord` for records (TRP v2)
- [ ] Add tests: `tests/test_proofs.py::test_record_proof`

#### 2.2.11 Golden File Updates

- [ ] Generate: `tests/golden/v0.3.0/records.json`
- [ ] Include record type definitions
- [ ] Include record construction
- [ ] Include field access
- [ ] Include nested records

#### 2.2.12 Determinism Tests

**File:** `tests/test_proofs.py`

- [ ] Test: Record field order doesn't affect determinism
- [ ] Test: Same record → same IR (sorted fields)
- [ ] Test: Same record → same H_IR
- [ ] Test: Same execution → same TRP
- [ ] Test: Nested records determinism

**Test Template:**

```python
def test_record_determinism():
    source = """
    type User = Record { id: Int, name: String };
    fn getUser(id: Int) -> User;
    pipeline main(Int) -> String {
        getUser -> __value.name
    }
    """
    for v in [1, 2]:
        a = run_program_with_proof(source, v).to_dict()
        b = run_program_with_proof(source, v).to_dict()
        assert a == b
```

#### 2.2.13 Hash Stability Tests

**File:** `tests/test_bor_crypto.py`

- [ ] Test: Record field order doesn't affect H_IR
- [ ] Test: Records produce stable HRICH
- [ ] Test: Nested records hash consistently

#### 2.2.14 Examples + Documentation Update

- [ ] Add: `examples/records.rlang`
- [ ] Update: `docs/language.md`
- [ ] Update: `README.md`
- [ ] Update: Compiler physics doc section 5.3.3

---

### 2.3 Lists (IRList + map/fold/filter)

**Priority:** High  
**Target Version:** 0.3.0  
**Complexity:** High

#### 2.3.1 Spec Update Tasks

- [ ] Add list type syntax: `List[T]`
- [ ] Add list construction syntax: `[e1, e2, ...]`
- [ ] Add list operations: `map`, `fold`, `filter`
- [ ] Document list semantics (ordered, immutable)

**Grammar Additions:**

```ebnf
TypeExpr     ::= ... | ListType
ListType     ::= List [ TypeExpr ]
Expr         ::= ... | ListExpr | ListOp
ListExpr     ::= [ ExprList? ]
ListOp       ::= map ( Expr , Expr ) | fold ( Expr , Expr , Expr ) | filter ( Expr , Expr )
```

#### 2.3.2 Lexer Changes

**File:** `rlang/lexer/tokens.py`

- [ ] Add `LIST = "List"` keyword
- [ ] Add `LBRACKET = "["` token
- [ ] Add `RBRACKET = "]"` token
- [ ] Add `MAP = "map"` keyword
- [ ] Add `FOLD = "fold"` keyword
- [ ] Add `FILTER = "filter"` keyword
- [ ] Add tests: `tests/test_lexer.py::test_list_tokens`

#### 2.3.3 Parser Changes

**File:** `rlang/parser/parser.py`

- [ ] Add `ListType` AST node
- [ ] Add `ListExpr` AST node
- [ ] Add `MapExpr`, `FoldExpr`, `FilterExpr` AST nodes
- [ ] Parse list type annotations
- [ ] Parse list literals
- [ ] Parse list operations
- [ ] Add tests: `tests/test_parser.py::test_list_parsing`

**AST Nodes:**

```python
@dataclass
class ListType(TypeExpr):
    element_type: TypeExpr

@dataclass
class ListExpr(Expr):
    elements: List[Expr]  # Ordered!

@dataclass
class MapExpr(Expr):
    function: Expr  # Function to apply
    list: Expr      # List to map over

@dataclass
class FoldExpr(Expr):
    function: Expr  # Accumulator function
    initial: Expr   # Initial accumulator value
    list: Expr      # List to fold

@dataclass
class FilterExpr(Expr):
    predicate: Expr # Filter function
    list: Expr      # List to filter
```

#### 2.3.4 Resolver Changes

**File:** `rlang/semantic/resolver.py`

- [ ] Resolve list type definitions
- [ ] Resolve list element types
- [ ] Resolve list operation function types
- [ ] Add tests: `tests/test_resolver.py::test_list_resolution`

#### 2.3.5 Typechecker Checks

**File:** `rlang/types/type_checker.py`

- [ ] Type check list construction (all elements same type)
- [ ] Type check `map`: `(T -> U) × List[T] -> List[U]`
- [ ] Type check `fold`: `((A, T) -> A) × A × List[T] -> A`
- [ ] Type check `filter`: `(T -> Bool) × List[T] -> List[T]`
- [ ] Add tests: `tests/test_type_checker.py::test_list_types`

**Type Rules:**

```python
def check_map_expr(self, expr: MapExpr) -> RType:
    function_type = self.check_expr(expr.function)
    list_type = self.check_expr(expr.list)
    if not isinstance(list_type, ListRType):
        raise TypeCheckError("map requires List type")
    # Verify function type matches: T -> U
    if function_type.input_type != list_type.element_type:
        raise TypeCheckError("map function type mismatch")
    return ListRType(element_type=function_type.output_type)
```

#### 2.3.6 IR Node Additions

**File:** `rlang/ir/model.py`

- [ ] Add `IRList` dataclass
- [ ] Add `IRMap`, `IRFold`, `IRFilter` to IRExpr kinds
- [ ] Ensure list order is preserved (deterministic)
- [ ] Add `to_dict()` for list operations
- [ ] Add tests: `tests/test_primary_ir.py::test_list_ir`

**IR Node:**

```python
@dataclass(frozen=True)
class IRList:
    """IR representation of a list construction."""
    elements: List[IRExpr]  # Ordered list (deterministic!)
    element_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "elements": [e.to_dict() for e in self.elements],
            "element_type": self.element_type,
            "kind": "list"
        }
```

#### 2.3.7 Lowering Rules

**File:** `rlang/lowering/lowering.py`

- [ ] Lower `ListExpr` → `IRList`
- [ ] Lower `MapExpr` → `IRExpr(kind="map", ...)`
- [ ] Lower `FoldExpr` → `IRExpr(kind="fold", ...)`
- [ ] Lower `FilterExpr` → `IRExpr(kind="filter", ...)`
- [ ] Preserve element order
- [ ] Add tests: `tests/test_lowering.py::test_list_lowering`

#### 2.3.8 Executor Changes

**File:** `rlang/bor/proofs.py`

- [ ] Add evaluation for `IRList` in `_eval_irexpr()`
- [ ] Add evaluation for `map` operation
- [ ] Add evaluation for `fold` operation
- [ ] Add evaluation for `filter` operation
- [ ] Ensure order is preserved
- [ ] Add tests: `tests/test_proofs.py::test_list_execution`

**Execution Code:**

```python
def _eval_irexpr(expr: IRExpr | IRList, ...) -> Any:
    if isinstance(expr, IRList):
        return [_eval_irexpr(e, ...) for e in expr.elements]  # Preserve order
    
    elif expr.kind == "map":
        function = _eval_irexpr(expr.function, ...)
        list_value = _eval_irexpr(expr.list, ...)
        return [function(elem) for elem in list_value]  # Preserve order
    
    elif expr.kind == "fold":
        function = _eval_irexpr(expr.function, ...)
        initial = _eval_irexpr(expr.initial, ...)
        list_value = _eval_irexpr(expr.list, ...)
        result = initial
        for elem in list_value:  # Preserve order
            result = function(result, elem)
        return result
    
    elif expr.kind == "filter":
        predicate = _eval_irexpr(expr.predicate, ...)
        list_value = _eval_irexpr(expr.list, ...)
        return [elem for elem in list_value if predicate(elem)]  # Preserve order
```

#### 2.3.9 Canonicalization Extensions

**File:** `rlang/utils/canonical_json.py`

- [ ] Verify list elements serialize in order
- [ ] Test nested lists
- [ ] Test empty lists
- [ ] Add test: `tests/test_base.py::test_list_canonical_json`

#### 2.3.10 TRP / Proof Recording Tasks

**File:** `rlang/bor/proofs.py`

- [ ] Lists in proof traces preserve order
- [ ] List operations recorded as steps
- [ ] Add `CollectionExecutionRecord` for lists (TRP v2)
- [ ] Add tests: `tests/test_proofs.py::test_list_proof`

#### 2.3.11 Golden File Updates

- [ ] Generate: `tests/golden/v0.3.0/lists.json`
- [ ] Include list construction
- [ ] Include map/fold/filter operations
- [ ] Include nested lists

#### 2.3.12 Determinism Tests

**File:** `tests/test_proofs.py`

- [ ] Test: List order is deterministic
- [ ] Test: Same list → same IR
- [ ] Test: Same list → same H_IR
- [ ] Test: Same execution → same TRP
- [ ] Test: Empty lists determinism
- [ ] Test: Large lists determinism

**Test Template:**

```python
def test_list_determinism():
    source = """
    fn inc(x: Int) -> Int;
    pipeline main(List[Int]) -> List[Int] {
        map(inc)
    }
    """
    input_list = [1, 2, 3]
    a = run_program_with_proof(source, input_list).to_dict()
    b = run_program_with_proof(source, input_list).to_dict()
    assert a == b
    assert a["output"] == [2, 3, 4]  # Order preserved
```

#### 2.3.13 Hash Stability Tests

**File:** `tests/test_bor_crypto.py`

- [ ] Test: List order affects H_IR (different lists → different hashes)
- [ ] Test: Same list → same H_IR
- [ ] Test: Lists produce stable HRICH

#### 2.3.14 Examples + Documentation Update

- [ ] Add: `examples/lists.rlang`
- [ ] Update: `docs/language.md`
- [ ] Update: `README.md`
- [ ] Update: Compiler physics doc section 5.3.4

---

### 2.4 Pattern Matching

**Priority:** Medium  
**Target Version:** 0.4.0  
**Complexity:** High

#### 2.4.1 Spec Update Tasks

- [ ] Add match expression syntax
- [ ] Add pattern syntax (literal, variable, wildcard, record, list)
- [ ] Document pattern matching semantics
- [ ] Add exhaustiveness checking rules

**Grammar Additions:**

```ebnf
Expr         ::= ... | MatchExpr
MatchExpr    ::= match ( Expr ) { CaseList }
CaseList     ::= Case+
Case         ::= case Pattern => Steps
Pattern      ::= Literal | IDENTIFIER | _ | RecordPattern | ListPattern
RecordPattern ::= { FieldPatternList }
FieldPatternList ::= FieldPattern ( , FieldPattern )*
FieldPattern ::= IDENTIFIER : Pattern
ListPattern  ::= [ PatternList? ]
```

#### 2.4.2 Lexer Changes

**File:** `rlang/lexer/tokens.py`

- [ ] Add `MATCH = "match"` keyword
- [ ] Add `CASE = "case"` keyword
- [ ] Add `WILDCARD = "_"` token
- [ ] Add `ARROW = "=>"` token
- [ ] Add tests: `tests/test_lexer.py::test_match_tokens`

#### 2.4.3 Parser Changes

**File:** `rlang/parser/parser.py`

- [ ] Add `MatchExpr` AST node
- [ ] Add `Case` AST node
- [ ] Add `Pattern` AST nodes (LiteralPattern, VarPattern, WildcardPattern, RecordPattern, ListPattern)
- [ ] Parse match expressions
- [ ] Parse patterns
- [ ] Add tests: `tests/test_parser.py::test_match_parsing`

**AST Nodes:**

```python
@dataclass
class MatchExpr(Expr):
    value: Expr
    cases: List[Case]

@dataclass
class Case:
    pattern: Pattern
    body: List[Step]

@dataclass
class Pattern:
    pass

@dataclass
class LiteralPattern(Pattern):
    value: Any

@dataclass
class VarPattern(Pattern):
    name: str

@dataclass
class WildcardPattern(Pattern):
    pass

@dataclass
class RecordPattern(Pattern):
    fields: Dict[str, Pattern]

@dataclass
class ListPattern(Pattern):
    elements: List[Pattern]
```

#### 2.4.4 Resolver Changes

**File:** `rlang/semantic/resolver.py`

- [ ] Resolve variable bindings in patterns
- [ ] Resolve field names in record patterns
- [ ] Add tests: `tests/test_resolver.py::test_match_resolution`

#### 2.4.5 Typechecker Checks

**File:** `rlang/types/type_checker.py`

- [ ] Type check match expression (value type matches patterns)
- [ ] Type check pattern exhaustiveness
- [ ] Type check case bodies (all return same type)
- [ ] Add tests: `tests/test_type_checker.py::test_match_types`

**Type Rules:**

```python
def check_match_expr(self, expr: MatchExpr) -> RType:
    value_type = self.check_expr(expr.value)
    case_types = []
    for case in expr.cases:
        # Check pattern matches value type
        pattern_type = self.check_pattern(case.pattern, value_type)
        # Check case body
        body_type = self.check_steps(case.body)
        case_types.append(body_type)
    # All cases must return same type
    if len(set(case_types)) != 1:
        raise TypeCheckError("Match cases must return same type")
    return case_types[0]
```

#### 2.4.6 IR Node Additions

**File:** `rlang/ir/model.py`

- [ ] Add `IRMatch` dataclass
- [ ] Add `IRPattern` types
- [ ] Ensure case order is deterministic
- [ ] Add `to_dict()` for match expressions
- [ ] Add tests: `tests/test_primary_ir.py::test_match_ir`

**IR Node:**

```python
@dataclass(frozen=True)
class IRMatch:
    value: IRExpr
    cases: List[MatchCase]  # Ordered!

@dataclass(frozen=True)
class MatchCase:
    pattern: IRPattern
    body: PipelineIR
```

#### 2.4.7 Lowering Rules

**File:** `rlang/lowering/lowering.py`

- [ ] Lower `MatchExpr` → `IRMatch`
- [ ] Lower patterns → `IRPattern`
- [ ] Preserve case order
- [ ] Add tests: `tests/test_lowering.py::test_match_lowering`

#### 2.4.8 Executor Changes

**File:** `rlang/bor/proofs.py`

- [ ] Add evaluation for `IRMatch` in `_eval_irexpr()`
- [ ] Implement pattern matching algorithm
- [ ] Record matched case in proof trace
- [ ] Add tests: `tests/test_proofs.py::test_match_execution`

**Execution Code:**

```python
def _eval_irexpr(expr: IRExpr | IRMatch, ...) -> Any:
    if isinstance(expr, IRMatch):
        value = _eval_irexpr(expr.value, ...)
        for case in expr.cases:
            if matches(case.pattern, value):
                return execute_pipeline(case.body, value, ...)
        raise MatchError("No matching case")
```

#### 2.4.9 Canonicalization Extensions

**File:** `rlang/utils/canonical_json.py`

- [ ] Verify match expressions serialize correctly
- [ ] Test nested matches
- [ ] Test complex patterns
- [ ] Add test: `tests/test_base.py::test_match_canonical_json`

#### 2.4.10 TRP / Proof Recording Tasks

**File:** `rlang/bor/proofs.py`

- [ ] Add `MatchExecutionRecord` (TRP v2)
- [ ] Record matched pattern
- [ ] Record matched case
- [ ] Add tests: `tests/test_proofs.py::test_match_proof`

#### 2.4.11 Golden File Updates

- [ ] Generate: `tests/golden/v0.4.0/pattern_matching.json`
- [ ] Include various pattern types
- [ ] Include nested patterns

#### 2.4.12 Determinism Tests

**File:** `tests/test_proofs.py`

- [ ] Test: Pattern matching is deterministic
- [ ] Test: Same match → same IR
- [ ] Test: Same execution → same TRP
- [ ] Test: Exhaustive matches determinism

#### 2.4.13 Hash Stability Tests

**File:** `tests/test_bor_crypto.py`

- [ ] Test: Match expressions produce stable H_IR
- [ ] Test: Match expressions produce stable HRICH

#### 2.4.14 Examples + Documentation Update

- [ ] Add: `examples/pattern_matching.rlang`
- [ ] Update: `docs/language.md`
- [ ] Update: `README.md`

---

### 2.5 Bounded Loops (IRUnrolledLoop)

**Priority:** Medium  
**Target Version:** 0.4.0  
**Complexity:** Medium

#### 2.5.1 Spec Update Tasks

- [ ] Add loop syntax with compile-time bounds
- [ ] Document loop unrolling semantics
- [ ] Document accumulator pattern

**Grammar Additions:**

```ebnf
Step         ::= ... | LoopStep
LoopStep     ::= for IDENTIFIER in INTEGER .. INTEGER { Steps }
```

#### 2.5.2 Lexer Changes

**File:** `rlang/lexer/tokens.py`

- [ ] Add `FOR = "for"` keyword
- [ ] Add `IN = "in"` keyword
- [ ] Add `DOTDOT = ".."` token
- [ ] Add tests: `tests/test_lexer.py::test_loop_tokens`

#### 2.5.3 Parser Changes

**File:** `rlang/parser/parser.py`

- [ ] Add `LoopStep` AST node
- [ ] Parse loop syntax
- [ ] Validate loop bounds are compile-time constants
- [ ] Add tests: `tests/test_parser.py::test_loop_parsing`

**AST Node:**

```python
@dataclass
class LoopStep(Step):
    var_name: str
    start: int  # Compile-time constant
    end: int    # Compile-time constant
    body: List[Step]
```

#### 2.5.4 Resolver Changes

**File:** `rlang/semantic/resolver.py`

- [ ] Resolve loop variable in body
- [ ] Add tests: `tests/test_resolver.py::test_loop_resolution`

#### 2.5.5 Typechecker Checks

**File:** `rlang/types/type_checker.py`

- [ ] Type check loop body
- [ ] Verify loop variable type
- [ ] Add tests: `tests/test_type_checker.py::test_loop_types`

#### 2.5.6 IR Node Additions

**File:** `rlang/ir/model.py`

- [ ] Add `IRUnrolledLoop` dataclass
- [ ] Ensure loop body is deterministic
- [ ] Add `to_dict()` for loops
- [ ] Add tests: `tests/test_primary_ir.py::test_loop_ir`

**IR Node:**

```python
@dataclass(frozen=True)
class IRUnrolledLoop:
    """IR representation of a statically unrolled loop."""
    bound: int  # Static bound (must be compile-time constant)
    body: PipelineIR  # Loop body (as pipeline)
    accumulator: IRExpr  # Initial accumulator value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bound": self.bound,
            "body": self.body.to_dict(),
            "accumulator": self.accumulator.to_dict(),
            "kind": "unrolled_loop"
        }
```

#### 2.5.7 Lowering Rules

**File:** `rlang/lowering/lowering.py`

- [ ] Lower `LoopStep` → `IRUnrolledLoop`
- [ ] Unroll loop at compile time
- [ ] Add tests: `tests/test_lowering.py::test_loop_lowering`

#### 2.5.8 Executor Changes

**File:** `rlang/bor/proofs.py`

- [ ] Add evaluation for `IRUnrolledLoop`
- [ ] Execute loop body N times
- [ ] Record each iteration in proof trace
- [ ] Add tests: `tests/test_proofs.py::test_loop_execution`

**Execution Code:**

```python
def execute_loop(loop: IRUnrolledLoop, ctx: ExecutionContext) -> Any:
    result = execute_expr(loop.accumulator, ctx)
    for i in range(loop.bound):
        result = execute_pipeline(loop.body, result, ctx)
    return result
```

#### 2.5.9 Canonicalization Extensions

**File:** `rlang/utils/canonical_json.py`

- [ ] Verify loops serialize correctly
- [ ] Test nested loops
- [ ] Add test: `tests/test_base.py::test_loop_canonical_json`

#### 2.5.10 TRP / Proof Recording Tasks

**File:** `rlang/bor/proofs.py`

- [ ] Add `LoopExecutionRecord` (TRP v2)
- [ ] Record loop iterations
- [ ] Record accumulator snapshots
- [ ] Add tests: `tests/test_proofs.py::test_loop_proof`

#### 2.5.11 Golden File Updates

- [ ] Generate: `tests/golden/v0.4.0/loops.json`
- [ ] Include various loop bounds
- [ ] Include nested loops

#### 2.5.12 Determinism Tests

**File:** `tests/test_proofs.py`

- [ ] Test: Loops are deterministic
- [ ] Test: Same loop → same IR
- [ ] Test: Same execution → same TRP
- [ ] Test: Zero-iteration loops

#### 2.5.13 Hash Stability Tests

**File:** `tests/test_bor_crypto.py`

- [ ] Test: Loops produce stable H_IR
- [ ] Test: Loops produce stable HRICH

#### 2.5.14 Examples + Documentation Update

- [ ] Add: `examples/loops.rlang`
- [ ] Update: `docs/language.md`
- [ ] Update: `README.md`

---

### 2.6 Modules

**Priority:** Low  
**Target Version:** 0.5.0  
**Complexity:** Medium

#### 2.6.1 Spec Update Tasks

- [ ] Add module syntax
- [ ] Add import syntax
- [ ] Document module semantics

**Grammar Additions:**

```ebnf
Program      ::= ModuleDecl* Declaration*
ModuleDecl   ::= module IDENTIFIER { Declaration* }
ImportDecl   ::= import IDENTIFIER ;
```

#### 2.6.2 Implementation Checklist

Follow same pattern as previous features:
- [ ] Lexer: Add `module`, `import` keywords
- [ ] Parser: Parse module declarations and imports
- [ ] Resolver: Resolve module symbols
- [ ] Typechecker: Type check module exports
- [ ] IR: Add `IRModule` node
- [ ] Lowering: Lower modules to IR
- [ ] Executor: Execute module imports
- [ ] Canonicalization: Serialize modules
- [ ] TRP: Record module scopes
- [ ] Golden files: Add module examples
- [ ] Tests: Full test suite

---

### 2.7 Connectors

**Priority:** Low  
**Target Version:** 0.6.0  
**Complexity:** High

#### 2.7.1 Spec Update Tasks

- [ ] Add connector syntax
- [ ] Document connector semantics (parallel execution)

**Grammar Additions:**

```ebnf
ConnectorDecl ::= connector IDENTIFIER { input: TypeExpr outputs: [ TypeExprList ] }
```

#### 2.7.2 Implementation Checklist

Follow same pattern as previous features with focus on:
- [ ] Parallel execution semantics
- [ ] DAG execution model
- [ ] Proof recording for parallel steps

---

### 2.8 TRP v2 Structures

**Priority:** Medium  
**Target Version:** 0.4.0  
**Complexity:** Medium

#### 2.8.1 Implementation Checklist

- [ ] Add `trp_version` field to `PipelineProofBundle`
- [ ] Add `LoopExecutionRecord` dataclass
- [ ] Add `ScopeExecutionRecord` dataclass
- [ ] Add `CollectionExecutionRecord` dataclass
- [ ] Add `MatchExecutionRecord` dataclass
- [ ] Add `ConnectorExecutionRecord` dataclass
- [ ] Update proof bundle serialization
- [ ] Update hash computation for TRP v2
- [ ] Add backward compatibility tests
- [ ] Update golden files

---

### 2.9 IRGraph (DAG Execution)

**Priority:** Low  
**Target Version:** 1.0.0  
**Complexity:** Very High

#### 2.9.1 Implementation Checklist

- [ ] Design DAG IR structure
- [ ] Implement topological sort
- [ ] Add parallel execution support
- [ ] Update proof recording for DAG
- [ ] Add determinism guarantees
- [ ] Comprehensive test suite

---

## 3. Test Matrix for Every New Construct

### 3.1 Unit Test Matrix

For each new construct, create tests in the following categories:

#### 3.1.1 Parser Tests

**File:** `tests/test_parser.py`

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_parse_[construct]_basic` | Parse basic construct | Valid AST node |
| `test_parse_[construct]_nested` | Parse nested construct | Valid nested AST |
| `test_parse_[construct]_empty` | Parse empty construct | Valid empty AST |
| `test_parse_[construct]_invalid` | Parse invalid syntax | ParseError |
| `test_parse_[construct]_edge_cases` | Edge cases | Valid AST or error |

**Example Template:**

```python
def test_parse_record_basic():
    source = "type User = Record { id: Int, name: String };"
    module = parse(source)
    assert isinstance(module.declarations[0], TypeAlias)
    assert isinstance(module.declarations[0].type_expr, RecordType)
```

#### 3.1.2 Typechecker Tests

**File:** `tests/test_type_checker.py`

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_type_check_[construct]_valid` | Valid type | No error |
| `test_type_check_[construct]_invalid` | Invalid type | TypeCheckError |
| `test_type_check_[construct]_inference` | Type inference | Correct type |
| `test_type_check_[construct]_nested` | Nested types | Correct types |
| `test_type_check_[construct]_edge_cases` | Edge cases | Correct handling |

**Example Template:**

```python
def test_type_check_record_valid():
    source = """
    type User = Record { id: Int, name: String };
    fn getUser(id: Int) -> User;
    pipeline main(Int) -> String {
        getUser -> __value.name
    }
    """
    # Should not raise TypeCheckError
    result = compile_source_to_ir(source)
    assert result.program_ir is not None
```

#### 3.1.3 Lowering Tests

**File:** `tests/test_lowering.py`

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_lower_[construct]_basic` | Basic lowering | Valid IR node |
| `test_lower_[construct]_nested` | Nested lowering | Valid nested IR |
| `test_lower_[construct]_deterministic` | Deterministic lowering | Same AST → same IR |
| `test_lower_[construct]_edge_cases` | Edge cases | Valid IR or error |

**Example Template:**

```python
def test_lower_record_deterministic():
    source1 = "type User = Record { id: Int, name: String };"
    source2 = "type User = Record { name: String, id: Int };"
    # Should produce same IR (sorted fields)
    ir1 = lower_to_ir(parse_and_resolve(source1))
    ir2 = lower_to_ir(parse_and_resolve(source2))
    assert ir1.to_json() == ir2.to_json()
```

#### 3.1.4 IR Tests

**File:** `tests/test_primary_ir.py`

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_ir_[construct]_structure` | IR structure | Correct fields |
| `test_ir_[construct]_canonical` | Canonical JSON | Stable JSON |
| `test_ir_[construct]_deterministic` | Determinism | Same IR → same JSON |
| `test_ir_[construct]_edge_cases` | Edge cases | Valid IR |

**Example Template:**

```python
def test_ir_record_canonical():
    record = IRRecord(fields={"b": IRExpr(...), "a": IRExpr(...)})
    json1 = record.to_json()
    json2 = record.to_json()
    assert json1 == json2
    # Verify sorted keys
    data = json.loads(json1)
    assert list(data["fields"].keys()) == ["a", "b"]
```

#### 3.1.5 Executor Tests

**File:** `tests/test_proofs.py`

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_execute_[construct]_basic` | Basic execution | Correct output |
| `test_execute_[construct]_proof` | Proof recording | Valid proof |
| `test_execute_[construct]_deterministic` | Determinism | Same input → same output |
| `test_execute_[construct]_edge_cases` | Edge cases | Correct handling |

**Example Template:**

```python
def test_execute_record_deterministic():
    source = """
    type User = Record { id: Int, name: String };
    fn getUser(id: Int) -> User;
    pipeline main(Int) -> String {
        getUser -> __value.name
    }
    """
    for v in [1, 2]:
        a = run_program_with_proof(source, v).to_dict()
        b = run_program_with_proof(source, v).to_dict()
        assert a == b
```

### 3.2 Determinism Test Matrix

#### 3.2.1 Same Program → Same IR

**Test Pattern:**

```python
def test_[construct]_ir_determinism():
    source = "..."
    ir1 = compile_source_to_ir(source).program_ir
    ir2 = compile_source_to_ir(source).program_ir
    assert ir1.to_json() == ir2.to_json()
```

#### 3.2.2 Same IR → Same H_IR

**Test Pattern:**

```python
def test_[construct]_hir_determinism():
    source = "..."
    ir = compile_source_to_ir(source).program_ir
    h1 = compute_H_IR(ir)
    h2 = compute_H_IR(ir)
    assert h1 == h2
```

#### 3.2.3 Same Execution → Same TRP

**Test Pattern:**

```python
def test_[construct]_trp_determinism():
    source = "..."
    input_value = ...
    trp1 = run_program_with_proof(source, input_value)
    trp2 = run_program_with_proof(source, input_value)
    assert trp1.to_dict() == trp2.to_dict()
```

#### 3.2.4 Same TRP → Same HRICH

**Test Pattern:**

```python
def test_[construct]_hrich_determinism():
    source = "..."
    input_value = ...
    bundle1 = run_program_with_proof(source, input_value)
    bundle2 = run_program_with_proof(source, input_value)
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)
    assert crypto1.to_rich_bundle().H_RICH == crypto2.to_rich_bundle().H_RICH
```

#### 3.2.5 Cross-Platform Determinism

**Test Pattern:**

```python
def test_[construct]_cross_platform():
    source = "..."
    input_value = ...
    # Run on different Python versions / platforms
    # Compare canonical JSON
    # Compare hashes
```

### 3.3 Canonical JSON Test Matrix

#### 3.3.1 Sorted Key Enforcement

**Test Pattern:**

```python
def test_[construct]_sorted_keys():
    construct = {...}  # With unsorted keys
    json1 = canonical_dumps(construct)
    json2 = canonical_dumps(construct)
    assert json1 == json2
    # Verify keys are sorted
    data = json.loads(json1)
    assert list(data.keys()) == sorted(data.keys())
```

#### 3.3.2 Float Normalization

**Test Pattern:**

```python
def test_[construct]_float_normalization():
    construct = {"value": 3.0}
    json_str = canonical_dumps(construct)
    data = json.loads(json_str)
    assert isinstance(data["value"], int)  # 3.0 → 3
```

#### 3.3.3 Stable Representation

**Test Pattern:**

```python
def test_[construct]_stable_representation():
    construct1 = {...}
    construct2 = {...}  # Equivalent but different structure
    json1 = canonical_dumps(construct1)
    json2 = canonical_dumps(construct2)
    assert json1 == json2  # Should be identical
```

#### 3.3.4 Edge Cases

| Edge Case | Test | Expected Result |
|-----------|------|-----------------|
| Empty construct | `test_[construct]_empty` | Valid JSON |
| Nested construct | `test_[construct]_nested` | Valid nested JSON |
| Deep nesting | `test_[construct]_deep_nesting` | Valid deep JSON |
| Large construct | `test_[construct]_large` | Valid large JSON |

### 3.4 Proof Stability Test Matrix

#### 3.4.1 Branching

**Test Pattern:**

```python
def test_[construct]_branch_proof():
    source = """
    if (condition) {
        [construct usage]
    } else {
        [construct usage]
    }
    """
    # Test both branches produce stable proofs
```

#### 3.4.2 Loops

**Test Pattern:**

```python
def test_[construct]_loop_proof():
    source = """
    for i in 0..10 {
        [construct usage]
    }
    """
    # Test loop iterations produce stable proofs
```

#### 3.4.3 Collections

**Test Pattern:**

```python
def test_[construct]_collection_proof():
    source = """
    [construct in collection]
    """
    # Test collection operations produce stable proofs
```

#### 3.4.4 Pattern Matching

**Test Pattern:**

```python
def test_[construct]_match_proof():
    source = """
    match (value) {
        case pattern => [construct usage]
    }
    """
    # Test pattern matching produces stable proofs
```

#### 3.4.5 Modules / Scopes

**Test Pattern:**

```python
def test_[construct]_scope_proof():
    source = """
    module M {
        [construct usage]
    }
    """
    # Test module scopes produce stable proofs
```

---

## 4. Golden File Scaffolding Scripts

### 4.1 Directory Layout

```
tests/golden/
├── v0.2.1/
│   ├── canonical/
│   │   ├── simple_pipeline.json
│   │   ├── multi_if_pipeline.json
│   │   └── ...
│   ├── ir/
│   │   ├── simple_pipeline_ir.json
│   │   └── ...
│   ├── hashes/
│   │   ├── hashes.json
│   │   └── ...
│   └── traces/
│       ├── simple_pipeline_trace.json
│       └── ...
├── v0.3.0/
│   └── ... (same structure)
└── README.md
```

### 4.2 Generate Golden Files Script

**File:** `scripts/generate_golden_files.py`

```python
#!/usr/bin/env python3
"""Generate golden files for regression testing.

This script generates canonical JSON, IR dumps, hashes, and traces
for a set of test programs. Outputs are deterministic and versioned.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rlang import compile_source_to_ir, compile_source_to_json
from rlang.bor import run_program_with_proof
from rlang.bor.crypto import RLangBoRCrypto
from rlang.utils.canonical_json import canonical_dumps


def generate_canonical_json(source: str, output_path: Path) -> None:
    """Generate canonical JSON golden file."""
    canonical_json = compile_source_to_json(source)
    output_path.write_text(canonical_json, encoding="utf-8")
    print(f"Generated: {output_path}")


def generate_ir_dump(source: str, output_path: Path) -> None:
    """Generate IR dump golden file."""
    result = compile_source_to_ir(source)
    ir_dict = result.program_ir.to_dict()
    canonical_json = canonical_dumps(ir_dict)
    output_path.write_text(canonical_json, encoding="utf-8")
    print(f"Generated: {output_path}")


def generate_hash(source: str, hashes_dict: Dict[str, Any]) -> None:
    """Generate hash entry for source."""
    result = compile_source_to_ir(source)
    ir_dict = result.program_ir.to_dict()
    canonical_json = canonical_dumps(ir_dict)
    
    import hashlib
    h_ir = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    
    # Use source hash as key
    source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()[:8]
    hashes_dict[source_hash] = {
        "H_IR": h_ir,
        "source_preview": source[:100].replace("\n", " ")
    }


def generate_trace(source: str, input_value: Any, output_path: Path) -> None:
    """Generate execution trace golden file."""
    bundle = run_program_with_proof(source, input_value)
    trace_dict = bundle.to_dict()
    canonical_json = canonical_dumps(trace_dict)
    output_path.write_text(canonical_json, encoding="utf-8")
    print(f"Generated: {output_path}")


def generate_hrich(source: str, input_value: Any, hashes_dict: Dict[str, Any]) -> None:
    """Generate HRICH entry for source."""
    bundle = run_program_with_proof(source, input_value)
    crypto = RLangBoRCrypto(bundle)
    rich_bundle = crypto.to_rich_bundle()
    
    source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()[:8]
    if source_hash not in hashes_dict:
        hashes_dict[source_hash] = {}
    hashes_dict[source_hash]["HRICH"] = rich_bundle.H_RICH


# Test programs
TEST_PROGRAMS = {
    "simple_pipeline": {
        "source": """
fn inc(x: Int) -> Int;
pipeline main(Int) -> Int { inc }
""",
        "input": 5
    },
    "multi_if_pipeline": {
        "source": """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;
pipeline main(Int) -> Int {
    if (__value > 10) { inc } else { dec } ->
    if (__value > 20) { inc } else { dec }
}
""",
        "input": 15
    },
    # Add more test programs here
}


def main():
    """Generate all golden files."""
    version = "v0.2.1"  # Update for new version
    base_dir = Path(__file__).parent.parent / "tests" / "golden" / version
    
    # Create directories
    (base_dir / "canonical").mkdir(parents=True, exist_ok=True)
    (base_dir / "ir").mkdir(parents=True, exist_ok=True)
    (base_dir / "hashes").mkdir(parents=True, exist_ok=True)
    (base_dir / "traces").mkdir(parents=True, exist_ok=True)
    
    hashes_dict = {}
    
    for name, program in TEST_PROGRAMS.items():
        source = program["source"]
        input_value = program.get("input", None)
        
        # Generate canonical JSON
        generate_canonical_json(
            source,
            base_dir / "canonical" / f"{name}.json"
        )
        
        # Generate IR dump
        generate_ir_dump(
            source,
            base_dir / "ir" / f"{name}_ir.json"
        )
        
        # Generate hash
        generate_hash(source, hashes_dict)
        
        # Generate trace (if input provided)
        if input_value is not None:
            generate_trace(
                source,
                input_value,
                base_dir / "traces" / f"{name}_trace.json"
            )
            
            # Generate HRICH
            generate_hrich(source, input_value, hashes_dict)
    
    # Write hashes file
    hashes_path = base_dir / "hashes" / "hashes.json"
    hashes_path.write_text(
        canonical_dumps(hashes_dict, indent=2),
        encoding="utf-8"
    )
    print(f"Generated: {hashes_path}")


if __name__ == "__main__":
    main()
```

### 4.3 Update Golden After Change Script

**File:** `scripts/update_golden_after_change.py`

```python
#!/usr/bin/env python3
"""Update golden files after adding a new feature.

This script regenerates golden files for a specific feature,
preserving existing golden files for other features.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_golden_files import (
    generate_canonical_json,
    generate_ir_dump,
    generate_trace,
    generate_hrich,
    generate_hash
)


def update_feature_golden(feature_name: str, source: str, input_value: Any = None):
    """Update golden files for a specific feature."""
    version = "v0.3.0"  # Update version as needed
    base_dir = Path(__file__).parent.parent / "tests" / "golden" / version
    
    # Generate all golden files for this feature
    generate_canonical_json(
        source,
        base_dir / "canonical" / f"{feature_name}.json"
    )
    
    generate_ir_dump(
        source,
        base_dir / "ir" / f"{feature_name}_ir.json"
    )
    
    if input_value is not None:
        generate_trace(
            source,
            input_value,
            base_dir / "traces" / f"{feature_name}_trace.json"
        )
    
    # Update hashes file
    hashes_path = base_dir / "hashes" / "hashes.json"
    if hashes_path.exists():
        hashes_dict = json.loads(hashes_path.read_text())
    else:
        hashes_dict = {}
    
    generate_hash(source, hashes_dict)
    if input_value is not None:
        generate_hrich(source, input_value, hashes_dict)
    
    hashes_path.write_text(
        canonical_dumps(hashes_dict, indent=2),
        encoding="utf-8"
    )
    
    print(f"Updated golden files for feature: {feature_name}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: update_golden_after_change.py <feature_name> <source_file> [input_value]")
        sys.exit(1)
    
    feature_name = sys.argv[1]
    source_file = Path(sys.argv[2])
    input_value = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    source = source_file.read_text()
    update_feature_golden(feature_name, source, input_value)
```

### 4.4 Verify Golden Consistency Script

**File:** `scripts/verify_golden_consistency.py`

```python
#!/usr/bin/env python3
"""Verify golden file consistency.

This script checks that:
1. Golden files are valid JSON
2. Canonical JSON matches current compiler output
3. Hashes match current compiler output
4. Traces match current execution
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rlang import compile_source_to_json, compile_source_to_ir
from rlang.bor import run_program_with_proof
from rlang.bor.crypto import RLangBoRCrypto
from rlang.utils.canonical_json import canonical_dumps
import hashlib


def verify_canonical_json(golden_path: Path, source: str) -> bool:
    """Verify canonical JSON matches current output."""
    golden_json = golden_path.read_text(encoding="utf-8")
    current_json = compile_source_to_json(source)
    
    if golden_json != current_json:
        print(f"❌ Mismatch: {golden_path}")
        print(f"Golden: {golden_json[:100]}...")
        print(f"Current: {current_json[:100]}...")
        return False
    return True


def verify_ir_dump(golden_path: Path, source: str) -> bool:
    """Verify IR dump matches current output."""
    golden_data = json.loads(golden_path.read_text(encoding="utf-8"))
    result = compile_source_to_ir(source)
    current_data = result.program_ir.to_dict()
    
    golden_json = canonical_dumps(golden_data)
    current_json = canonical_dumps(current_data)
    
    if golden_json != current_json:
        print(f"❌ IR mismatch: {golden_path}")
        return False
    return True


def verify_hash(golden_hash: str, source: str) -> bool:
    """Verify hash matches current output."""
    result = compile_source_to_ir(source)
    ir_dict = result.program_ir.to_dict()
    canonical_json = canonical_dumps(ir_dict)
    current_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    
    if golden_hash != current_hash:
        print(f"❌ Hash mismatch")
        print(f"Golden: {golden_hash}")
        print(f"Current: {current_hash}")
        return False
    return True


def verify_trace(golden_path: Path, source: str, input_value: Any) -> bool:
    """Verify trace matches current execution."""
    golden_data = json.loads(golden_path.read_text(encoding="utf-8"))
    bundle = run_program_with_proof(source, input_value)
    current_data = bundle.to_dict()
    
    golden_json = canonical_dumps(golden_data)
    current_json = canonical_dumps(current_data)
    
    if golden_json != current_json:
        print(f"❌ Trace mismatch: {golden_path}")
        return False
    return True


def verify_hrich(golden_hrich: str, source: str, input_value: Any) -> bool:
    """Verify HRICH matches current output."""
    bundle = run_program_with_proof(source, input_value)
    crypto = RLangBoRCrypto(bundle)
    rich_bundle = crypto.to_rich_bundle()
    current_hrich = rich_bundle.H_RICH
    
    if golden_hrich != current_hrich:
        print(f"❌ HRICH mismatch")
        print(f"Golden: {golden_hrich}")
        print(f"Current: {current_hrich}")
        return False
    return True


def main():
    """Verify all golden files."""
    version = "v0.2.1"
    base_dir = Path(__file__).parent.parent / "tests" / "golden" / version
    
    # Load test programs (same as generate script)
    # ... (load TEST_PROGRAMS)
    
    all_passed = True
    
    # Verify canonical JSON
    for name in TEST_PROGRAMS:
        golden_path = base_dir / "canonical" / f"{name}.json"
        if golden_path.exists():
            if not verify_canonical_json(golden_path, TEST_PROGRAMS[name]["source"]):
                all_passed = False
    
    # Verify IR dumps
    for name in TEST_PROGRAMS:
        golden_path = base_dir / "ir" / f"{name}_ir.json"
        if golden_path.exists():
            if not verify_ir_dump(golden_path, TEST_PROGRAMS[name]["source"]):
                all_passed = False
    
    # Verify hashes
    hashes_path = base_dir / "hashes" / "hashes.json"
    if hashes_path.exists():
        hashes_dict = json.loads(hashes_path.read_text())
        for source_hash, hash_data in hashes_dict.items():
            # Find source by hash (simplified)
            # ... (match source to hash)
            pass
    
    if all_passed:
        print("✅ All golden files verified")
    else:
        print("❌ Some golden files failed verification")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 5. Refactor-Safe Modularization Plan

### 5.1 Target Structure

```
rlang/
├── frontend/
│   ├── __init__.py
│   ├── lexer.py          # From rlang/lexer/tokenizer.py
│   ├── parser.py         # From rlang/parser/parser.py
│   ├── resolver.py       # From rlang/semantic/resolver.py
│   └── typechecker.py    # From rlang/types/type_checker.py
├── middleend/
│   ├── __init__.py
│   ├── lowering.py       # From rlang/lowering/lowering.py
│   ├── ir_nodes.py       # From rlang/ir/model.py
│   └── ir_utils.py       # IR utility functions
├── backend/
│   ├── __init__.py
│   ├── executor.py       # From rlang/bor/proofs.py (execution parts)
│   ├── canonicalizer.py  # From rlang/utils/canonical_json.py
│   ├── trp.py           # From rlang/bor/proofs.py (proof parts)
│   └── hashing.py       # From rlang/bor/crypto.py
├── spec/
│   ├── __init__.py
│   ├── grammar.md
│   ├── semantics.md
│   ├── ir_spec.md
│   └── proof_system.md
└── __init__.py           # Public API
```

### 5.2 Refactoring Steps

#### Step 1: Create New Directory Structure

**Actions:**

- [ ] Create `rlang/frontend/` directory
- [ ] Create `rlang/middleend/` directory
- [ ] Create `rlang/backend/` directory
- [ ] Create `rlang/spec/` directory
- [ ] Add `__init__.py` files to each directory

**Verification:**

```bash
# Run tests to ensure nothing breaks
pytest tests/ -v
```

#### Step 2: Move Lexer

**Actions:**

- [ ] Copy `rlang/lexer/tokenizer.py` → `rlang/frontend/lexer.py`
- [ ] Copy `rlang/lexer/tokens.py` → `rlang/frontend/tokens.py` (or merge)
- [ ] Update imports in `rlang/frontend/lexer.py`
- [ ] Update imports in files that use lexer
- [ ] Run tests: `pytest tests/test_lexer.py -v`

**Import Updates:**

```python
# Old
from rlang.lexer import tokenize

# New
from rlang.frontend.lexer import tokenize
```

**Verification:**

- [ ] All lexer tests pass
- [ ] No import errors
- [ ] Golden files unchanged

#### Step 3: Move Parser

**Actions:**

- [ ] Copy `rlang/parser/parser.py` → `rlang/frontend/parser.py`
- [ ] Copy `rlang/parser/ast.py` → `rlang/frontend/ast.py`
- [ ] Update imports
- [ ] Run tests: `pytest tests/test_parser.py -v`

**Verification:**

- [ ] All parser tests pass
- [ ] No import errors
- [ ] Golden files unchanged

#### Step 4: Move Resolver

**Actions:**

- [ ] Copy `rlang/semantic/resolver.py` → `rlang/frontend/resolver.py`
- [ ] Copy `rlang/semantic/symbols.py` → `rlang/frontend/symbols.py`
- [ ] Update imports
- [ ] Run tests: `pytest tests/test_resolver.py -v`

**Verification:**

- [ ] All resolver tests pass
- [ ] No import errors
- [ ] Golden files unchanged

#### Step 5: Move Typechecker

**Actions:**

- [ ] Copy `rlang/types/type_checker.py` → `rlang/frontend/typechecker.py`
- [ ] Copy `rlang/types/type_system.py` → `rlang/frontend/type_system.py`
- [ ] Update imports
- [ ] Run tests: `pytest tests/test_type_checker.py -v`

**Verification:**

- [ ] All typechecker tests pass
- [ ] No import errors
- [ ] Golden files unchanged

#### Step 6: Move Lowering

**Actions:**

- [ ] Copy `rlang/lowering/lowering.py` → `rlang/middleend/lowering.py`
- [ ] Update imports
- [ ] Run tests: `pytest tests/test_lowering.py -v`

**Verification:**

- [ ] All lowering tests pass
- [ ] No import errors
- [ ] Golden files unchanged

#### Step 7: Move IR

**Actions:**

- [ ] Copy `rlang/ir/model.py` → `rlang/middleend/ir_nodes.py`
- [ ] Extract IR utilities to `rlang/middleend/ir_utils.py`
- [ ] Update imports
- [ ] Run tests: `pytest tests/test_primary_ir.py -v`

**Verification:**

- [ ] All IR tests pass
- [ ] No import errors
- [ ] Golden files unchanged
- [ ] IR structure unchanged (critical!)

#### Step 8: Move Executor

**Actions:**

- [ ] Extract execution logic from `rlang/bor/proofs.py` → `rlang/backend/executor.py`
- [ ] Keep proof recording in `rlang/bor/proofs.py` (or move to `rlang/backend/trp.py`)
- [ ] Update imports
- [ ] Run tests: `pytest tests/test_proofs.py -v`

**Verification:**

- [ ] All executor tests pass
- [ ] No import errors
- [ ] Golden files unchanged
- [ ] Execution semantics unchanged (critical!)

#### Step 9: Move Canonicalizer

**Actions:**

- [ ] Copy `rlang/utils/canonical_json.py` → `rlang/backend/canonicalizer.py`
- [ ] Update imports
- [ ] Run tests: `pytest tests/test_base.py -v`

**Verification:**

- [ ] All canonicalization tests pass
- [ ] No import errors
- [ ] Golden files unchanged
- [ ] Canonical JSON rules unchanged (critical!)

#### Step 10: Move Hashing

**Actions:**

- [ ] Extract hashing logic from `rlang/bor/crypto.py` → `rlang/backend/hashing.py`
- [ ] Update imports
- [ ] Run tests: `pytest tests/test_bor_crypto.py -v`

**Verification:**

- [ ] All hashing tests pass
- [ ] No import errors
- [ ] Golden files unchanged
- [ ] Hash algorithms unchanged (critical!)

#### Step 11: Update Public API

**Actions:**

- [ ] Update `rlang/__init__.py` with new import paths
- [ ] Maintain backward compatibility (re-export from old locations)
- [ ] Update `rlang/emitter/emitter.py` imports
- [ ] Run full test suite: `pytest tests/ -v`

**Backward Compatibility:**

```python
# rlang/__init__.py
# Maintain old imports for compatibility
from rlang.frontend.parser import parse as _parse
from rlang.frontend.resolver import resolve_module as _resolve_module
# ... etc

# Re-export
parse = _parse
resolve_module = _resolve_module
```

#### Step 12: Move Documentation

**Actions:**

- [ ] Copy relevant sections from `docs/compiler_physics.md` → `rlang/spec/`
- [ ] Create `rlang/spec/grammar.md`
- [ ] Create `rlang/spec/semantics.md`
- [ ] Create `rlang/spec/ir_spec.md`
- [ ] Create `rlang/spec/proof_system.md`

### 5.3 Invariants to Check After Each Step

After **every** refactoring step, verify:

1. ✅ **No Semantically Visible Changes**
   ```bash
   # Compare IR output
   python -c "from rlang import compile_source_to_json; print(compile_source_to_json('...'))"
   ```

2. ✅ **No IR Shape Changes**
   ```bash
   # Compare IR structure
   python -c "from rlang import compile_source_to_ir; print(compile_source_to_ir('...').program_ir.to_json())"
   ```

3. ✅ **No Canonicalization Changes**
   ```bash
   # Compare canonical JSON
   python scripts/verify_golden_consistency.py
   ```

4. ✅ **No Proof Structure Changes**
   ```bash
   # Compare proof traces
   pytest tests/test_proofs.py -v
   ```

5. ✅ **All Tests Pass**
   ```bash
   pytest tests/ -v
   ```

### 5.4 Avoiding Breaking Changes

**Critical Rules:**

1. **Never change IR structure** during refactoring
2. **Never change canonical JSON rules** during refactoring
3. **Never change proof structure** during refactoring
4. **Never change hash algorithms** during refactoring
5. **Always maintain backward compatibility** in public API

**Safe Changes:**

- ✅ Moving files
- ✅ Renaming internal functions
- ✅ Reorganizing code structure
- ✅ Adding new utility functions
- ✅ Improving code organization

**Unsafe Changes:**

- ❌ Changing IR node structure
- ❌ Changing canonical JSON serialization
- ❌ Changing proof record structure
- ❌ Changing hash computation
- ❌ Changing execution semantics

### 5.5 Testing After Refactoring

**Full Test Suite:**

```bash
# Run all tests
pytest tests/ -v

# Run determinism tests
pytest tests/test_proofs.py::test_multi_if_determinism -v

# Run hash stability tests
pytest tests/test_bor_crypto.py::test_determinism -v

# Verify golden files
python scripts/verify_golden_consistency.py
```

**Golden File Verification:**

```bash
# Regenerate and compare
python scripts/generate_golden_files.py
git diff tests/golden/
# Should show NO changes (or only expected changes)
```

---

## 6. Quick Reference

### 6.1 Implementation Checklist Template

For any new feature:

1. [ ] Spec Update Tasks
2. [ ] Lexer Changes
3. [ ] Parser Changes
4. [ ] Resolver Changes
5. [ ] Typechecker Checks
6. [ ] IR Node Additions
7. [ ] Lowering Rules
8. [ ] Executor Changes
9. [ ] Canonicalization Extensions
10. [ ] TRP / Proof Recording Tasks
11. [ ] Golden File Updates
12. [ ] Determinism Tests
13. [ ] Hash Stability Tests
14. [ ] Examples + Documentation Update

### 6.2 Test Matrix Template

For any new construct:

- [ ] Parser tests (basic, nested, empty, invalid, edge cases)
- [ ] Typechecker tests (valid, invalid, inference, nested, edge cases)
- [ ] Lowering tests (basic, nested, deterministic, edge cases)
- [ ] IR tests (structure, canonical, deterministic, edge cases)
- [ ] Executor tests (basic, proof, deterministic, edge cases)
- [ ] Determinism tests (IR, H_IR, TRP, HRICH, cross-platform)
- [ ] Canonical JSON tests (sorted keys, float normalization, stable representation, edge cases)
- [ ] Proof stability tests (branching, loops, collections, pattern matching, modules)

### 6.3 Golden File Workflow

1. **Generate**: `python scripts/generate_golden_files.py`
2. **Update**: `python scripts/update_golden_after_change.py <feature> <source>`
3. **Verify**: `python scripts/verify_golden_consistency.py`
4. **Commit**: `git add tests/golden/ && git commit -m "Add golden files for <feature>"`

### 6.4 Refactoring Workflow

1. **Plan**: Review target structure
2. **Test**: Run full test suite before starting
3. **Step**: Move one component at a time
4. **Verify**: Run tests after each step
5. **Commit**: Commit after each successful step
6. **Final**: Run full test suite and verify golden files

---

## Conclusion

This playbook provides **complete, actionable guidance** for extending the RLang compiler while maintaining determinism guarantees. Follow the checklists, use the test matrices, manage golden files carefully, and refactor safely.

**Remember:**

- ✅ Determinism is non-negotiable
- ✅ Canonical JSON rules are frozen
- ✅ IR structure changes require careful consideration
- ✅ Proof structure changes require versioning
- ✅ Always test thoroughly before committing

**For Questions:**

- See [`compiler_physics.md`](./compiler_physics.md) for theoretical foundations
- See `tests/` for test patterns
- See `examples/` for usage examples

---

## 7. Appendix: Implementation Status & Change Log (Auto-Reconstructed)

This section documents the actual implementation status of features planned in this playbook, comparing what was planned versus what was actually implemented since version 0.2.1.

### 7.1 Boolean Operators (Section 2.1) — ✅ COMPLETED

**Target Version:** 0.3.0  
**Actual Implementation:** Completed in v0.2.1+

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.1.1 Spec Update Tasks** | ✅ Complete | Grammar and semantics documented |
| **2.1.2 Lexer Changes** | ✅ Complete | `OP_AND`, `OP_OR`, `OP_NOT` tokens added (`rlang/lexer/tokens.py`) |
| **2.1.3 Parser Changes** | ✅ Complete | `BooleanAnd`, `BooleanOr`, `BooleanNot` AST nodes added (`rlang/parser/ast.py`) |
| **2.1.4 Resolver Changes** | ✅ Complete | No changes needed (built-in operators) |
| **2.1.5 Typechecker Checks** | ✅ Complete | Boolean operator type checking implemented (`rlang/types/type_checker.py`) |
| **2.1.6 IR Node Additions** | ✅ Complete | Extended `IRExpr` with `kind="boolean_and"`, `kind="boolean_or"`, `kind="boolean_not"` |
| **2.1.7 Lowering Rules** | ✅ Complete | Lowering implemented (`rlang/lowering/lowering.py`) |
| **2.1.8 Executor Changes** | ✅ Complete | Evaluation implemented (`rlang/bor/proofs.py`) |
| **2.1.9 Canonicalization** | ✅ Complete | Works via existing `IRExpr` canonicalization |
| **2.1.10 TRP / Proof Recording** | ✅ Complete | Boolean operators in conditions tracked via `BranchExecutionRecord` |
| **2.1.11 Golden File Updates** | ⚠️ Partial | Golden files may need updates for boolean operators |
| **2.1.12 Determinism Tests** | ✅ Complete | Tests verify deterministic evaluation |
| **2.1.13 Hash Stability Tests** | ✅ Complete | Hash stability verified |
| **2.1.14 Examples + Documentation** | ⚠️ Partial | Examples may need expansion |

#### Deviations from Plan

- **IR Representation**: Boolean operators use `IRExpr` with `kind` field rather than separate IR node types (simpler, consistent with existing design)
- **Operator Precedence**: Implemented as planned (NOT > AND > OR)
- **Short-Circuit Evaluation**: Implemented deterministically (left-to-right evaluation)

#### Implementation Files

- **AST**: `rlang/parser/ast.py` lines 180-200
- **Parser**: `rlang/parser/parser.py` lines 920-990
- **Type Checker**: `rlang/types/type_checker.py` lines 885-920
- **Lowering**: `rlang/lowering/lowering.py` lines 268-280
- **IR**: `rlang/ir/model.py` lines 110-138
- **Executor**: `rlang/bor/proofs.py` lines 237-252

---

### 7.2 Records (Section 2.2) — ✅ COMPLETED

**Target Version:** 0.3.0  
**Actual Implementation:** Completed in v0.2.1+

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.2.1 Spec Update Tasks** | ✅ Complete | Record syntax documented |
| **2.2.2 Lexer Changes** | ✅ Complete | `KEYWORD_RECORD`, `DOT` tokens added |
| **2.2.3 Parser Changes** | ✅ Complete | `RecordType`, `RecordExpr`, `FieldAccess` AST nodes added |
| **2.2.4 Resolver Changes** | ✅ Complete | Record type resolution implemented |
| **2.2.5 Typechecker Checks** | ✅ Complete | Record type checking with `RecordRType` (`rlang/types/type_system.py`) |
| **2.2.6 IR Node Additions** | ⚠️ Deviation | Records use `IRExpr(kind="record")` instead of separate `IRRecord` node |
| **2.2.7 Lowering Rules** | ✅ Complete | Lowering implemented with field sorting (`rlang/lowering/lowering.py`) |
| **2.2.8 Executor Changes** | ✅ Complete | Record construction and field access evaluation implemented |
| **2.2.9 Canonicalization** | ✅ Complete | Field sorting ensures deterministic canonicalization |
| **2.2.10 TRP / Proof Recording** | ✅ Complete | Records tracked as expression steps |
| **2.2.11 Golden File Updates** | ⚠️ Partial | Golden files may need updates |
| **2.2.12 Determinism Tests** | ✅ Complete | Field ordering determinism verified |
| **2.2.13 Hash Stability Tests** | ✅ Complete | Hash stability verified |
| **2.2.14 Examples + Documentation** | ⚠️ Partial | Examples may need expansion |

#### Deviations from Plan

- **IR Representation**: Records use `IRExpr(kind="record", fields={...})` instead of separate `IRRecord` dataclass. This simplifies the IR model while maintaining determinism through field sorting.
- **Field Sorting**: Implemented at both lowering and IR serialization stages to ensure canonical ordering
- **Field Access**: Implemented as `IRExpr(kind="field_access", record=..., field_name=...)`

#### Implementation Files

- **AST**: `rlang/parser/ast.py` lines 55-64, 216-225, 228-233
- **Parser**: `rlang/parser/parser.py` lines 827-880
- **Type System**: `rlang/types/type_system.py` lines 47-72
- **Type Checker**: `rlang/types/type_checker.py` lines 961-988, 1129-1150
- **Lowering**: `rlang/lowering/lowering.py` lines 294-301, 303-305
- **IR**: `rlang/ir/model.py` lines 134, 163-165
- **Executor**: `rlang/bor/proofs.py` lines 266-298

---

### 7.3 Lists (Section 2.3) — ⚠️ PARTIALLY COMPLETED

**Target Version:** 0.3.0  
**Actual Implementation:** List literals completed in v0.2.1+, but list operations (map/fold/filter) not implemented

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.3.1 Spec Update Tasks** | ⚠️ Partial | List literal syntax documented, but list operations not documented |
| **2.3.2 Lexer Changes** | ✅ Complete | `LBRACKET`, `RBRACKET` tokens added (list operations keywords not added) |
| **2.3.3 Parser Changes** | ⚠️ Partial | `ListExpr` AST node added, but `MapExpr`, `FoldExpr`, `FilterExpr` not added |
| **2.3.4 Resolver Changes** | ✅ Complete | List type resolution implemented |
| **2.3.5 Typechecker Checks** | ⚠️ Partial | List literal type checking implemented, but list operation type checking not implemented |
| **2.3.6 IR Node Additions** | ⚠️ Partial | Lists use `IRExpr(kind="list")` instead of separate `IRList` node. List operation IR nodes not added |
| **2.3.7 Lowering Rules** | ⚠️ Partial | List literal lowering implemented, but list operation lowering not implemented |
| **2.3.8 Executor Changes** | ⚠️ Partial | List literal evaluation implemented, but list operation evaluation not implemented |
| **2.3.9 Canonicalization** | ✅ Complete | List element order preserved deterministically |
| **2.3.10 TRP / Proof Recording** | ✅ Complete | Lists tracked as expression steps |
| **2.3.11 Golden File Updates** | ⚠️ Partial | Golden files may need updates |
| **2.3.12 Determinism Tests** | ✅ Complete | List order determinism verified |
| **2.3.13 Hash Stability Tests** | ✅ Complete | Hash stability verified |
| **2.3.14 Examples + Documentation** | ⚠️ Partial | Examples may need expansion |

#### Deviations from Plan

- **List Operations**: `map`, `fold`, and `filter` operations were not implemented. Only list literals (`[expr1, expr2, ...]`) are supported.
- **IR Representation**: Lists use `IRExpr(kind="list", elements=[...])` instead of separate `IRList` dataclass
- **Element Order**: Preserved deterministically (source order maintained)

#### Implementation Files

- **AST**: `rlang/parser/ast.py` lines 236-245
- **Parser**: `rlang/parser/parser.py` lines 773-819
- **Type Checker**: `rlang/types/type_checker.py` lines 989-1010
- **Lowering**: `rlang/lowering/lowering.py` lines 307-310
- **IR**: `rlang/ir/model.py` lines 137, 170-171
- **Executor**: `rlang/bor/proofs.py` lines 300-307

---

### 7.4 Pattern Matching (Section 2.4) — ✅ COMPLETED (with deviation)

**Target Version:** 0.4.0  
**Actual Implementation:** Completed in v0.2.1+ with different IR representation

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.4.1 Spec Update Tasks** | ✅ Complete | Match expression syntax documented |
| **2.4.2 Lexer Changes** | ✅ Complete | `KEYWORD_MATCH`, `KEYWORD_CASE`, `ARROW`, `UNDERSCORE` tokens added |
| **2.4.3 Parser Changes** | ✅ Complete | `MatchExpr`, `Case`, and all pattern AST nodes added |
| **2.4.4 Resolver Changes** | ✅ Complete | Pattern variable binding resolution implemented |
| **2.4.5 Typechecker Checks** | ✅ Complete | Match expression type checking implemented |
| **2.4.6 IR Node Additions** | ⚠️ Deviation | Match expressions lower to nested `IRIf` chains instead of `IRMatch` node |
| **2.4.7 Lowering Rules** | ✅ Complete | Lowering to nested IF implemented (`rlang/lowering/lowering.py`) |
| **2.4.8 Executor Changes** | ✅ Complete | Pattern matching executes via nested IF execution |
| **2.4.9 Canonicalization** | ✅ Complete | Works via existing `IRIf` canonicalization |
| **2.4.10 TRP / Proof Recording** | ⚠️ Deviation | Pattern matching tracked via `BranchExecutionRecord` (TRP v1) instead of `MatchExecutionRecord` (TRP v2) |
| **2.4.11 Golden File Updates** | ⚠️ Partial | Golden files may need updates |
| **2.4.12 Determinism Tests** | ✅ Complete | Pattern matching determinism verified |
| **2.4.13 Hash Stability Tests** | ✅ Complete | Hash stability verified |
| **2.4.14 Examples + Documentation** | ⚠️ Partial | Examples may need expansion |

#### Deviations from Plan

- **IR Representation**: Pattern matching lowers to nested `IRIf` chains instead of a dedicated `IRMatch` node. This simplifies the IR model while preserving semantics.
- **Pattern Binding**: Variable bindings computed during lowering and passed to case bodies
- **Pattern Condition Lowering**: Patterns lower to boolean conditions with guarded field/index access
- **TRP Version**: Uses TRP v1 (`BranchExecutionRecord`) instead of TRP v2 (`MatchExecutionRecord`)

#### Implementation Files

- **AST**: `rlang/parser/ast.py` lines 287-361
- **Parser**: `rlang/parser/parser.py` lines 1329-1400
- **Type Checker**: `rlang/types/type_checker.py` lines 558-640, 1023-1050
- **Lowering**: `rlang/lowering/lowering.py` lines 436-686
- **Executor**: Uses existing nested IF execution (`rlang/bor/proofs.py`)

---

### 7.5 Bounded Loops (Section 2.5) — ✅ COMPLETED (with deviation)

**Target Version:** 0.4.0  
**Actual Implementation:** Completed in v0.2.1+ with different IR representation

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.5.1 Spec Update Tasks** | ✅ Complete | Loop syntax documented |
| **2.5.2 Lexer Changes** | ✅ Complete | `KEYWORD_FOR`, `KEYWORD_IN`, `DOTDOT` tokens added |
| **2.5.3 Parser Changes** | ✅ Complete | `ForExpr` AST node added (as expression, not `LoopStep`) |
| **2.5.4 Resolver Changes** | ✅ Complete | Loop variable resolution implemented |
| **2.5.5 Typechecker Checks** | ✅ Complete | Loop type checking implemented |
| **2.5.6 IR Node Additions** | ⚠️ Deviation | Loops unroll to repeated `PipelineStepIR` instead of `IRUnrolledLoop` node |
| **2.5.7 Lowering Rules** | ✅ Complete | Static unrolling implemented (`rlang/lowering/lowering.py`) |
| **2.5.8 Executor Changes** | ✅ Complete | Loops execute as repeated steps |
| **2.5.9 Canonicalization** | ✅ Complete | Works via existing step canonicalization |
| **2.5.10 TRP / Proof Recording** | ⚠️ Deviation | Loops tracked as repeated steps (TRP v1) instead of `LoopExecutionRecord` (TRP v2) |
| **2.5.11 Golden File Updates** | ⚠️ Partial | Golden files may need updates |
| **2.5.12 Determinism Tests** | ✅ Complete | Loop determinism verified |
| **2.5.13 Hash Stability Tests** | ✅ Complete | Hash stability verified |
| **2.5.14 Examples + Documentation** | ⚠️ Partial | Examples may need expansion |

#### Deviations from Plan

- **AST Representation**: Loops implemented as `ForExpr` (expression) rather than `LoopStep` (statement)
- **IR Representation**: Loops unroll completely at compile time into repeated `PipelineStepIR` nodes instead of using `IRUnrolledLoop` node. This simplifies execution but loses loop structure in IR.
- **Step Index Management**: Unrolled steps receive sequential indices
- **TRP Version**: Uses TRP v1 (repeated step records) instead of TRP v2 (`LoopExecutionRecord`)

#### Implementation Files

- **AST**: `rlang/parser/ast.py` lines 272-284
- **Parser**: `rlang/parser/parser.py` lines 1276-1318
- **Type Checker**: `rlang/types/type_checker.py` lines 499-560
- **Lowering**: `rlang/lowering/lowering.py` lines 394-434
- **Executor**: Uses existing step execution (`rlang/bor/proofs.py`)

---

### 7.6 Modules (Section 2.6) — ❌ NOT IMPLEMENTED

**Target Version:** 0.5.0  
**Actual Implementation:** Not implemented

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.6.1 Spec Update Tasks** | ❌ Not Started | Module syntax not documented |
| **2.6.2 Implementation Checklist** | ❌ Not Started | All items pending |

---

### 7.7 Connectors (Section 2.7) — ❌ NOT IMPLEMENTED

**Target Version:** 0.6.0  
**Actual Implementation:** Not implemented

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.7.1 Spec Update Tasks** | ❌ Not Started | Connector syntax not documented |
| **2.7.2 Implementation Checklist** | ❌ Not Started | All items pending |

---

### 7.8 TRP v2 Structures (Section 2.8) — ❌ NOT IMPLEMENTED

**Target Version:** 0.4.0  
**Actual Implementation:** Not implemented (still using TRP v1)

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.8.1 Implementation Checklist** | ❌ Not Started | All items pending |

**Note**: Pattern matching and loops use TRP v1 structures (`BranchExecutionRecord` and repeated step records) instead of TRP v2 structures (`MatchExecutionRecord`, `LoopExecutionRecord`).

---

### 7.9 IRGraph (DAG Execution) (Section 2.9) — ❌ NOT IMPLEMENTED

**Target Version:** 1.0.0  
**Actual Implementation:** Not implemented

#### Implementation Status

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| **2.9.1 Implementation Checklist** | ❌ Not Started | All items pending |

---

### 7.10 Summary of Implementation Patterns

#### Completed Features

1. **Boolean Operators** — Fully implemented as planned
2. **Records** — Implemented with `IRExpr` instead of `IRRecord`
3. **List Literals** — Implemented with `IRExpr` instead of `IRList`
4. **Pattern Matching** — Implemented with nested `IRIf` instead of `IRMatch`
5. **For Loops** — Implemented with static unrolling instead of `IRUnrolledLoop`

#### Common Implementation Patterns

- **IR Simplification**: Many features use `IRExpr` with `kind` field instead of separate IR node types
- **TRP v1 Usage**: All features use TRP v1 structures instead of TRP v2
- **Deterministic Ordering**: All collection types (records, lists) maintain deterministic ordering
- **Field Sorting**: Record fields sorted alphabetically for canonicalization

#### Pending Features

- List operations (`map`, `fold`, `filter`)
- Modules
- Connectors
- TRP v2 structures
- IRGraph (DAG execution)

---

**Document Version:** 0.2.1  
**Last Updated:** November 2025  
**Status:** Active Engineering Playbook

