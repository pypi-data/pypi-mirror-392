"""Comprehensive end-to-end tests for the RLang compiler emitter."""

import json

import pytest

from rlang.emitter import CompileResult, compile_source_to_ir, compile_source_to_json
from rlang.lowering import LoweringError
from rlang.parser import ParseError
from rlang.semantic import ResolutionError
from rlang.types import TypeCheckError


def test_empty_source_compiles_to_empty_program():
    """Test that empty source compiles to empty program."""
    source = ""
    result = compile_source_to_ir(source)

    assert isinstance(result, CompileResult)
    assert result.program_ir.entry_pipeline is None
    assert result.program_ir.step_templates == []
    assert result.program_ir.pipelines == []

    # JSON round-trip
    data = json.loads(result.to_json())
    assert data["entry_pipeline"] is None
    assert data["step_templates"] == []
    assert data["pipelines"] == []
    assert data["version"] == "v0"
    assert data["language"] == "rlang"


def test_simple_pipeline_end_to_end():
    """Test simple pipeline end-to-end compilation."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    result = compile_source_to_ir(source)

    assert isinstance(result, CompileResult)
    assert result.program_ir.entry_pipeline == "main"
    assert len(result.program_ir.pipelines) == 1
    assert len(result.program_ir.step_templates) == 1

    # Verify JSON structure
    json_str = result.to_json()
    data = json.loads(json_str)

    assert data["entry_pipeline"] == "main"
    assert len(data["pipelines"]) == 1
    assert data["pipelines"][0]["name"] == "main"
    assert len(data["step_templates"]) == 1
    assert data["step_templates"][0]["name"] == "step1"


def test_explicit_entry_override():
    """Test that explicit entry override works."""
    source = """
fn a(x: Int) -> Int;
fn b(x: Int) -> Int;

pipeline first(Int) -> Int {
  a(42)
}

pipeline second(Int) -> Int {
  b(42)
}
"""
    # Default entry (should be lexicographically smallest)
    result_default = compile_source_to_ir(source)
    assert result_default.program_ir.entry_pipeline == "first"

    # Explicit entry
    result_explicit = compile_source_to_ir(source, explicit_entry="second")
    assert result_explicit.program_ir.entry_pipeline == "second"


def test_json_determinism_end_to_end():
    """Test that JSON output is deterministic end-to-end."""
    source = """
fn step1(x: Int) -> Int;
fn step2(x: Int) -> Int;

pipeline pipeline1(Int) -> Int {
  step1(42)
}

pipeline pipeline2(Int) -> Int {
  step2(42)
}
"""
    # Compile twice
    json1 = compile_source_to_json(source)
    json2 = compile_source_to_json(source)

    # Should be exactly equal
    assert json1 == json2

    # Verify it's valid JSON
    data1 = json.loads(json1)
    data2 = json.loads(json2)
    assert data1 == data2


def test_error_propagation_bad_syntax():
    """Test that parse errors propagate correctly."""
    source = "fn bad( -> Int;"

    with pytest.raises(ParseError) as exc_info:
        compile_source_to_ir(source)

    assert "Expected" in str(exc_info.value) or "parse" in str(exc_info.value).lower()


def test_error_propagation_unknown_type():
    """Test that resolution/type check errors propagate correctly."""
    source = "fn f(x: Unknown) -> Int;"

    # This should raise ResolutionError or TypeCheckError
    with pytest.raises((ResolutionError, TypeCheckError)) as exc_info:
        compile_source_to_ir(source)

    assert "Unknown type" in str(exc_info.value) or "Unknown" in str(exc_info.value)


def test_error_propagation_type_mismatch():
    """Test that type check errors propagate correctly."""
    source = """
fn step1(x: Float) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    with pytest.raises(TypeCheckError) as exc_info:
        compile_source_to_ir(source)

    assert "does not match" in str(exc_info.value) or "Pipeline input type" in str(exc_info.value)


def test_compile_result_to_json():
    """Test that CompileResult.to_json() works correctly."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    result = compile_source_to_ir(source)
    json_str = result.to_json()

    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert data["entry_pipeline"] == "main"
    assert len(data["pipelines"]) == 1


def test_custom_version_and_language():
    """Test that custom version and language are respected."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    result = compile_source_to_ir(source, version="v1.0", language="rlang-v2")

    assert result.program_ir.version == "v1.0"
    assert result.program_ir.language == "rlang-v2"

    data = json.loads(result.to_json())
    assert data["version"] == "v1.0"
    assert data["language"] == "rlang-v2"


def test_complex_program_end_to_end():
    """Test compilation of a complex program end-to-end."""
    source = """
type UserId = Int;
type Email = String;

fn getUser(id: UserId) -> Email;
fn createUser(email: Email) -> UserId;

pipeline processUsers(Input) -> Output {
  getUser(1) -> createUser("test@example.com")
}

type Input = Int;
type Output = Int;
"""
    result = compile_source_to_ir(source)

    assert isinstance(result, CompileResult)
    assert result.program_ir.entry_pipeline == "processUsers"
    assert len(result.program_ir.step_templates) == 2
    assert len(result.program_ir.pipelines) == 1

    # Verify JSON
    data = json.loads(result.to_json())
    assert data["entry_pipeline"] == "processUsers"
    assert len(data["step_templates"]) == 2
    assert len(data["pipelines"]) == 1


def test_compile_source_to_json_direct():
    """Test compile_source_to_json convenience function."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    json_str = compile_source_to_json(source)

    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert data["entry_pipeline"] == "main"
    assert len(data["pipelines"]) == 1
    assert len(data["step_templates"]) == 1


def test_explicit_entry_validation():
    """Test that invalid explicit entry raises ValueError."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    with pytest.raises(ValueError) as exc_info:
        compile_source_to_ir(source, explicit_entry="nonexistent")

    assert "not found" in str(exc_info.value).lower()


def test_emitter_if_expr_canonical_structure():
    """Test that emitter produces canonical JSON for if expressions."""
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
    json_str = compile_source_to_json(source)
    data = json.loads(json_str)

    # Check pipeline structure
    assert len(data["pipelines"]) == 1
    pipeline = data["pipelines"][0]
    assert len(pipeline["steps"]) == 1

    step = pipeline["steps"][0]
    assert step["kind"] == "if"
    assert "condition" in step
    assert "then" in step
    assert "else" in step

    # Verify condition structure
    condition = step["condition"]
    assert condition["kind"] == "binary_op"
    assert condition["op"] == "=="

    # Verify branches
    assert len(step["then"]) == 1
    assert step["then"][0]["name"] == "double"
    assert len(step["else"]) == 1
    assert step["else"][0]["name"] == "half"
