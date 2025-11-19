"""Comprehensive tests for the RLang type checker."""

import pytest

from rlang.parser import PipelineDecl, parse
from rlang.semantic import resolve_module
from rlang.types import RType, TypeCheckError, type_check
from rlang.types.type_system import RecordRType, rtype_from_type_expr


def test_empty_module_type_checks():
    """Test that empty module type-checks successfully."""
    source = ""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    assert result.module is module
    assert result.symbols is resolution.global_table
    assert len(result.expr_types) == 0


def test_simple_function_and_pipeline_wiring():
    """Test simple function and pipeline wiring (happy path)."""
    source = """
type Input = Int;
type Output = Int;

fn step1(x: Input) -> Output;
fn step2(y: Output) -> Output;

pipeline main(Input) -> Output {
  step1 -> step2
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should not raise any errors
    assert result.module is module


def test_pipeline_input_type_mismatch():
    """Test that pipeline input type mismatch raises TypeCheckError."""
    source = """
type Input = Int;
type Output = Int;

fn step1(x: Float) -> Output;

pipeline main(Input) -> Output {
  step1
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "Pipeline input type" in str(exc_info.value)
    assert "does not match" in str(exc_info.value)


def test_step_to_step_wiring_mismatch():
    """Test that step-to-step wiring mismatch raises TypeCheckError."""
    source = """
type A = Int;
type B = Float;

fn step1(x: A) -> A;
fn step2(y: B) -> B;

pipeline main(A) -> B {
  step1 -> step2
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "does not match previous step return type" in str(exc_info.value) or "parameter type" in str(
        exc_info.value
    )


def test_pipeline_output_type_mismatch():
    """Test that pipeline output type mismatch raises TypeCheckError."""
    source = """
type Input = Int;
type Output = Int;
type Other = Float;

fn step1(x: Input) -> Other;

pipeline main(Input) -> Output {
  step1
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "Pipeline output type" in str(exc_info.value)
    assert "does not match" in str(exc_info.value)


def test_step_argument_literal_types_checked():
    """Test that step argument literal types are checked."""
    source = """
fn step1(x: Int, label: String) -> Int;

pipeline main(Int) -> Int {
  step1(42, "ok")
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_step_argument_literal_type_mismatch():
    """Test that step argument literal type mismatch raises TypeCheckError."""
    source = """
fn step1(x: Int, label: String) -> Int;

pipeline main(Int) -> Int {
  step1("not-int", 42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "expected" in str(exc_info.value).lower()
    assert "got" in str(exc_info.value).lower()


def test_unbound_identifier_in_pipeline_arguments():
    """Test that unbound identifier in pipeline arguments raises TypeCheckError."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(x)
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "Unbound identifier" in str(exc_info.value)
    assert "x" in str(exc_info.value)


def test_step_arity_mismatch():
    """Test that step arity mismatch raises TypeCheckError."""
    source = """
fn step1(x: Int, y: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "expects" in str(exc_info.value).lower()
    assert "arguments" in str(exc_info.value).lower()


def test_unknown_step():
    """Test that unknown step raises TypeCheckError."""
    source = """
pipeline main(Int) -> Int {
  unknownStep
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "Unknown step" in str(exc_info.value)
    assert "unknownStep" in str(exc_info.value)


def test_step_not_a_function():
    """Test that step that is not a function raises TypeCheckError."""
    source = """
type NotAFunction = Int;

pipeline main(Int) -> Int {
  NotAFunction
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "is not a function" in str(exc_info.value)


def test_empty_pipeline_with_types():
    """Test that empty pipeline with types raises TypeCheckError."""
    source = """
pipeline main(Int) -> Int {
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "Empty pipeline" in str(exc_info.value)


def test_pipeline_first_step_no_parameters():
    """Test that pipeline with input type but first step has no parameters raises error."""
    source = """
fn step1() -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "has no parameters" in str(exc_info.value)


def test_pipeline_step_follows_no_return_type():
    """Test that step following step with no return type raises error."""
    source = """
fn step1(x: Int);
fn step2(y: Int) -> Int;

pipeline main(Int) -> Int {
  step1 -> step2
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "cannot follow step with no return type" in str(exc_info.value)


def test_complex_pipeline_type_checking():
    """Test type checking of a complex pipeline."""
    source = """
type Data = Int;
type Processed = Int;
type Result = Int;

fn load(x: Data) -> Processed;
fn transform(y: Processed) -> Processed;
fn save(z: Processed) -> Result;

pipeline process(Data) -> Result {
  load -> transform -> save
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_if_expr_typecheck_without_else_identity():
    """Test type checking if expression without else (implicit identity)."""
    source = """
fn double(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    double
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_if_expr_typecheck_with_else_same_type():
    """Test type checking if expression with else, both branches same type."""
    source = """
fn double(x: Int) -> Int;
fn half(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    double
  } else {
    half
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_if_expr_typecheck_condition_not_bool():
    """Test that if condition not Bool raises TypeCheckError."""
    source = """
fn double(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (42) {
    double
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "if condition must be Bool" in str(exc_info.value)


def test_if_expr_typecheck_branch_type_mismatch():
    """Test that if branches with different output types raise TypeCheckError."""
    source = """
fn toString(x: Int) -> String;
fn double(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    toString
  } else {
    double
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "if branches must have the same output type" in str(exc_info.value)


def test_if_expr_typecheck_branch_type_mismatch_implicit_else():
    """Test that if without else but branch type mismatch raises TypeCheckError."""
    source = """
fn toString(x: Int) -> String;

pipeline main(Int) -> Int {
  if (1 == 1) {
    toString
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "if branches must have the same output type" in str(exc_info.value)

def test_if_expr_with_value_identifier():
    """Test type checking if expression with __value identifier."""
    source = """
fn double(x: Int) -> Int;
fn half(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (__value > 10) {
    double
  } else {
    half
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_if_expr_with_unsupported_identifier():
    """Test that unsupported identifiers in conditions raise TypeCheckError."""
    source = """
fn double(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (input > 10) {
    double
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "Unbound identifier" in str(exc_info.value)
    assert "__value" in str(exc_info.value)  # Should mention __value is supported


def test_typecheck_nested_if_valid():
    """Test type checking nested IF in THEN branch (valid case)."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value > 20) { inc } else { dec }
    } else {
        dec
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_typecheck_nested_if_in_else_branch_valid():
    """Test type checking nested IF in ELSE branch (valid case)."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        inc
    } else {
        if (__value > 0) { inc } else { dec }
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_typecheck_nested_if_condition_not_bool():
    """Test that nested IF condition not Bool raises TypeCheckError."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value + 1) { inc } else { dec }
    } else {
        dec
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "if condition must be Bool" in str(exc_info.value)


def test_typecheck_nested_if_branch_type_mismatch():
    """Test that nested IF branches with different output types raise TypeCheckError."""
    source = """
fn toInt(x: Int) -> Int;
fn toString(x: Int) -> String;

pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value > 20) { toInt } else { toString }
    } else {
        toInt
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "if branches must have the same output type" in str(exc_info.value)


def test_typecheck_nested_if_outer_branch_type_mismatch():
    """Test that outer IF branches with different output types raise TypeCheckError."""
    source = """
fn toInt(x: Int) -> Int;
fn toString(x: Int) -> String;

pipeline main(Int) -> Int {
    if (__value > 10) {
        toInt
    } else {
        toString
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)

    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)

    assert "if branches must have the same output type" in str(exc_info.value)


def test_typecheck_deeply_nested_if_valid():
    """Test type checking deeply nested IF (3-4 levels, all valid)."""
    source = """
fn f1(x: Int) -> Int;
fn f2(x: Int) -> Int;
fn f3(x: Int) -> Int;
fn f4(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value > 20) {
            if (__value > 30) {
                f4
            } else {
                f3
            }
        } else {
            f2
        }
    } else {
        f1
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_typecheck_nested_if_with_multiple_steps():
    """Test type checking nested IF with multiple steps in branches."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;
fn dec(x: Int) -> Int;
fn double(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        inc -> double
    } else {
        if (__value > 0) {
            inc -> dec
        } else {
            dec -> double
        }
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully
    assert result.module is module


def test_typecheck_nested_if_condition_in_nested_branch():
    """Test type checking nested IF where condition uses __value correctly."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value > 20) {
            inc
        } else {
            dec
        }
    } else {
        if (__value > 0) {
            inc
        } else {
            dec
        }
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should type-check successfully - __value is correctly inferred as Int in all nested contexts
    assert result.module is module


def test_typecheck_boolean_and_valid():
    """Test typechecking valid boolean AND expressions."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_boolean_or_valid():
    """Test typechecking valid boolean OR expressions."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 || __value < 0) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_boolean_not_valid():
    """Test typechecking valid boolean NOT expressions."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (!(__value > 10)) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_boolean_nested_valid():
    """Test typechecking nested boolean expressions."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if ((__value > 10 || __value < 0) && __value != 5) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_boolean_complex_valid():
    """Test typechecking complex boolean expressions."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20 || !(__value == 0)) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_boolean_and_invalid_left():
    """Test that boolean AND with non-Bool left operand raises error."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (__value && __value < 20) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "Boolean AND operator '&&' requires Bool operands" in str(exc_info.value)
    assert "Int" in str(exc_info.value)


def test_typecheck_boolean_and_invalid_right():
    """Test that boolean AND with non-Bool right operand raises error."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "Boolean AND operator '&&' requires Bool operands" in str(exc_info.value)
    assert "Int" in str(exc_info.value)


def test_typecheck_boolean_or_invalid_left():
    """Test that boolean OR with non-Bool left operand raises error."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (__value || __value < 20) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "Boolean OR operator '||' requires Bool operands" in str(exc_info.value)
    assert "Int" in str(exc_info.value)


def test_typecheck_boolean_or_invalid_right():
    """Test that boolean OR with non-Bool right operand raises error."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 || __value) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "Boolean OR operator '||' requires Bool operands" in str(exc_info.value)
    assert "Int" in str(exc_info.value)


def test_typecheck_boolean_not_invalid():
    """Test that boolean NOT with non-Bool operand raises error."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (!__value) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "Boolean NOT operator '!' requires Bool operand" in str(exc_info.value)
    assert "Int" in str(exc_info.value)


def test_typecheck_boolean_deeply_nested_not():
    """Test typechecking deeply nested NOT operators."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (!!!(__value > 10)) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors (multiple NOTs are valid)
    assert result.module is module


def test_typecheck_boolean_with_comparison_operators():
    """Test that comparison operators produce Bool that can be used in boolean ops."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if ((__value > 10) && (__value < 20) && (__value != 15)) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_boolean_mixed_with_arithmetic():
    """Test that boolean ops work correctly with comparison results."""
    # Note: Parentheses are needed because arithmetic has lower precedence than comparisons
    # So (__value + 5) > 10 needs parentheses, but __value + 5 > 10 would parse as __value + (5 > 10)
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if (((__value + 5) > 10) && ((__value * 2) < 20)) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_record_literal_basic():
    """Test typechecking a basic record literal."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { id: __value, name: "Alice" }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_record_literal_missing_field():
    """Test that missing field in record literal raises error."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { id: __value }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "missing field 'name'" in str(exc_info.value).lower()


def test_typecheck_record_literal_extra_field():
    """Test that extra field in record literal raises error."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { id: __value, name: "Alice", foo: 123 }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "unexpected field 'foo'" in str(exc_info.value).lower()


def test_typecheck_field_access_basic():
    """Test typechecking basic field access."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(User) -> String {
    __value.name
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_typecheck_field_access_unknown_field():
    """Test that accessing unknown field raises error."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(User) -> Int {
    __value.age
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "unknown field 'age'" in str(exc_info.value).lower()


def test_typecheck_nested_records():
    """Test typechecking nested record field access."""
    source = """
type Meta = Record { age: Int };
type User = Record { id: Int, meta: Meta };

pipeline main(User) -> Int {
    __value.meta.age
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_type_inference_anonymous_record():
    """Test that anonymous record types are allowed."""
    source = """
pipeline main(Int) -> Record { x: Int } {
    { x: __value }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)
    
    # Should not raise any errors
    assert result.module is module


def test_mismatched_record_literal_type():
    """Test that mismatched field type raises error."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { id: __value, name: 123 }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "type mismatch in field 'name'" in str(exc_info.value).lower() or "expected" in str(exc_info.value).lower()


def test_typecheck_record_with_list_field():
    """Test typechecking a record with a list field."""
    source = """
type User = Record { id: Int, tags: List<String> };

pipeline main(Int) -> User {
    { id: __value, tags: ["a", "b", "c"] }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should succeed
    assert result.module is module
    
    # Check that the pipeline output type is User
    pipeline_decl = [d for d in result.module.decls if isinstance(d, PipelineDecl) and d.name == "main"][0]
    output_type = rtype_from_type_expr(pipeline_decl.output_type, result.symbols)
    assert isinstance(output_type, RecordRType)
    assert "id" in output_type.fields
    assert "tags" in output_type.fields
    assert output_type.fields["id"].name == "Int"
    assert output_type.fields["tags"].name == "List"
    assert len(output_type.fields["tags"].args) == 1
    assert output_type.fields["tags"].args[0].name == "String"


def test_typecheck_list_of_records():
    """Test typechecking a list of records."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> List<User> {
    [
        { id: __value,     name: "A" },
        { id: __value + 1, name: "B" }
    ]
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    # Should succeed
    assert result.module is module
    
    # Check that the pipeline output type is List[User]
    pipeline_decl = [d for d in result.module.decls if isinstance(d, PipelineDecl) and d.name == "main"][0]
    output_type = rtype_from_type_expr(pipeline_decl.output_type, result.symbols)
    assert output_type.name == "List"
    assert len(output_type.args) == 1
    assert isinstance(output_type.args[0], RecordRType)
    assert "id" in output_type.args[0].fields
    assert "name" in output_type.args[0].fields


def test_typecheck_record_with_list_field_mismatch():
    """Test that mismatched list element type raises error."""
    source = """
type User = Record { id: Int, tags: List<String> };

pipeline main(Int) -> User {
    { id: __value, tags: [1, 2, 3] }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    
    assert "list element" in str(exc_info.value).lower() or "type mismatch" in str(exc_info.value).lower() or "expected" in str(exc_info.value).lower()


def test_typecheck_for_step_basic():
    """Test typechecking a basic for loop step."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
  for i in 0 .. 3 {
    inc
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    assert result.module is module
    # Typechecking should succeed
    assert result.expr_types is not None


def test_typecheck_for_step_with_records():
    """Test typechecking a for loop with records."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
  for i in 0 .. 2 {
    { id: __value, name: "test" }
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    assert result.module is module
    # Typechecking should succeed
    assert result.expr_types is not None


# Pattern Matching Typechecker Tests

def test_match_expr_with_literal_patterns():
    """Test typechecking match expression with literal patterns."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    match (__value) {
        case 42 => { inc(); }
        case 0 => { dec(); }
        case _ => { inc(); }
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    assert result.module is module
    # Should typecheck successfully


def test_match_expr_with_record_pattern():
    """Test typechecking match expression with record pattern."""
    source = """
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Record { id: Int, name: String }) -> Int {
    match (__value) {
        case { id: 1, name: _ } => { process(); }
        case _ => { process(); }
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    result = type_check(resolution)

    assert result.module is module
    # Should typecheck successfully


def test_match_expr_type_mismatch():
    """Test that match expression with type mismatch raises error."""
    source = """
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    match (__value) {
        case "hello" => { process(); }
        case _ => { process(); }
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    assert "does not match value type" in str(exc_info.value) or "Literal pattern" in str(exc_info.value)


def test_match_expr_case_type_mismatch():
    """Test that match cases with different return types raise error."""
    source = """
fn inc(x: Int) -> Int;
fn to_string(x: Int) -> String;

pipeline main(Int) -> Int {
    match (__value) {
        case 1 => { inc(); }
        case 2 => { to_string(); }
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    
    with pytest.raises(TypeCheckError) as exc_info:
        type_check(resolution)
    assert "All match cases must return the same type" in str(exc_info.value)
