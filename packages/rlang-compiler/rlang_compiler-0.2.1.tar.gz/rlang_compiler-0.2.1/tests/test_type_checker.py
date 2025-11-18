"""Comprehensive tests for the RLang type checker."""

import pytest

from rlang.parser import parse
from rlang.semantic import resolve_module
from rlang.types import RType, TypeCheckError, type_check


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
