"""Comprehensive tests for RLang → BoR Runtime Bridge."""

import pytest

from rlang.bor import BoRPipelineInstance, BoRStepMapping, RLangBoRBridge
from rlang.emitter import compile_source_to_ir


def test_simple_mock_execution():
    """Test simple pipeline execution with mock function."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir)
    execution_result = bridge.run(10)

    assert execution_result.output is not None
    assert execution_result.output == {"mock": "step1", "input": 10}


def test_real_function_registry():
    """Test pipeline execution with real function implementation."""
    def mul2(x):
        return x * 2

    source = """
fn mul2(x: Int) -> Int;

pipeline main(Int) -> Int {
  mul2
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir, fn_registry={"mul2": mul2})
    execution_result = bridge.run(21)

    assert execution_result.output == 42


def test_multiple_step_execution():
    """Test pipeline execution with multiple steps."""
    def inc(x):
        return x + 1

    def double(x):
        return x * 2

    source = """
fn inc(x: Int) -> Int;
fn double(x: Int) -> Int;

pipeline main(Int) -> Int {
  inc -> double
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(
        result.program_ir,
        fn_registry={"inc": inc, "double": double}
    )
    execution_result = bridge.run(5)

    assert execution_result.output == 12  # (5 + 1) * 2 = 12


def test_mixed_mock_and_real_functions():
    """Test pipeline with mix of mock and real functions."""
    def add_one(x):
        return x + 1

    source = """
fn add_one(x: Int) -> Int;
fn unknown_fn(x: Int) -> Int;

pipeline main(Int) -> Int {
  add_one -> unknown_fn
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir, fn_registry={"add_one": add_one})
    execution_result = bridge.run(10)

    # add_one(10) = 11, then unknown_fn uses mock
    assert execution_result.output == {"mock": "unknown_fn", "input": 11}


def test_incorrect_registry_function_type():
    """Test that incorrect function arity raises error during execution."""
    def wrong_arity(x, y):
        return x + y

    source = """
fn step(x: Int) -> Int;

pipeline main(Int) -> Int {
  step
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir, fn_registry={"step": wrong_arity})

    # The error should occur during execution, not during bridge construction
    # Since we're using mock implementations, the actual error depends on
    # how the function is called. For now, we'll test that the bridge builds
    # successfully (registry validation only checks name existence, not arity)
    instance = bridge.build()
    assert instance is not None

    # Execution will fail if function signature doesn't match
    # In a real scenario, this would be caught by type checking
    # For now, we test that execution attempts to use the function
    with pytest.raises((TypeError, ValueError)):
        bridge.run(10)


def test_missing_function_implementation():
    """Test that missing function implementations use mock without failure."""
    source = """
fn step1(x: Int) -> Int;
fn step2(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1 -> step2
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir)  # No registry provided
    execution_result = bridge.run(42)

    # Both steps should use mock implementations
    assert execution_result.output is not None
    # First mock returns {"mock": "step1", "input": 42}
    # Second mock receives that dict and returns {"mock": "step2", "input": {...}}
    assert "mock" in str(execution_result.output)
    assert "step2" in str(execution_result.output)


def test_build_returns_pipeline_instance():
    """Test that build() returns proper BoRPipelineInstance."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir)
    instance = bridge.build()

    assert isinstance(instance, BoRPipelineInstance)
    assert instance.ir == result.program_ir
    assert instance.bor_pipeline is not None
    assert instance.bor_pipeline.name == "main"
    assert len(instance.step_map) == 1


def test_step_mapping_structure():
    """Test that step mappings contain correct structure."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir)
    instance = bridge.build()

    assert len(instance.step_map) == 1
    template_id = list(instance.step_map.keys())[0]
    mapping = instance.step_map[template_id]

    assert isinstance(mapping, BoRStepMapping)
    assert mapping.template.name == "step1"
    assert mapping.step_def.name == "step1"
    assert callable(mapping.fn_impl)


def test_invalid_registry_function_name():
    """Test that invalid function name in registry raises ValueError."""
    def some_fn(x):
        return x

    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    result = compile_source_to_ir(source)

    with pytest.raises(ValueError) as exc_info:
        RLangBoRBridge(result.program_ir, fn_registry={"nonexistent": some_fn})

    assert "does not exist in IR templates" in str(exc_info.value)


def test_no_entry_pipeline_error():
    """Test that missing entry pipeline raises ValueError."""
    source = """
fn step1(x: Int) -> Int;
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir)

    with pytest.raises(ValueError) as exc_info:
        bridge.build()

    assert "entry_pipeline is None" in str(exc_info.value)


def test_entry_pipeline_not_found_error():
    """Test that invalid entry pipeline name raises ValueError."""
    # Manually create IR with invalid entry pipeline name
    from rlang.canonical import PrimaryProgramIR
    from rlang.ir import PipelineIR, PipelineStepIR, StepTemplateIR

    template = StepTemplateIR(
        id="fn:step1",
        name="step1",
        fn_name="step1",
        param_types=["Int"],
        return_type="Int",
        rule_repr="step1(x: Int) -> Int",
    )

    step = PipelineStepIR(
        index=0,
        name="step1",
        template_id="fn:step1",
        arg_types=[],
        input_type="Int",
        output_type="Int",
    )

    pipeline = PipelineIR(
        id="pipeline:other",
        name="other",
        input_type="Int",
        output_type="Int",
        steps=[step],
    )

    # Create PrimaryProgramIR directly with invalid entry pipeline name
    ir = PrimaryProgramIR(
        version="v0",
        language="rlang",
        entry_pipeline="nonexistent",  # Invalid entry pipeline name
        step_templates=[template],
        pipelines=[pipeline],
    )

    bridge = RLangBoRBridge(ir)

    with pytest.raises(ValueError) as exc_info:
        bridge.build()

    assert "not found in IR pipelines" in str(exc_info.value)


def test_complex_pipeline_execution():
    """Test execution of complex multi-step pipeline."""
    def add(x):
        return x + 1

    def multiply(x):
        return x * 3

    def subtract(x):
        return x - 2

    source = """
fn add(x: Int) -> Int;
fn multiply(x: Int) -> Int;
fn subtract(x: Int) -> Int;

pipeline main(Int) -> Int {
  add -> multiply -> subtract
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(
        result.program_ir,
        fn_registry={"add": add, "multiply": multiply, "subtract": subtract}
    )
    execution_result = bridge.run(5)

    # (5 + 1) * 3 - 2 = 6 * 3 - 2 = 18 - 2 = 16
    assert execution_result.output == 16


def test_pipeline_with_string_types():
    """Test pipeline execution with string input/output."""
    def uppercase(s):
        return s.upper()

    source = """
fn uppercase(s: String) -> String;

pipeline main(String) -> String {
  uppercase
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir, fn_registry={"uppercase": uppercase})
    execution_result = bridge.run("hello")

    assert execution_result.output == "HELLO"


def test_step_definitions_have_correct_attributes():
    """Test that StepDefinitions are created with correct attributes."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(result.program_ir)
    instance = bridge.build()

    template_id = list(instance.step_map.keys())[0]
    mapping = instance.step_map[template_id]

    assert mapping.step_def.name == "step1"
    assert mapping.step_def.version == "v0"
    assert "step1" in mapping.step_def.rule_repr


def test_multiple_templates_single_pipeline():
    """Test pipeline that uses multiple different templates."""
    def fn1(x):
        return x * 2

    def fn2(x):
        return x + 10

    source = """
fn fn1(x: Int) -> Int;
fn fn2(x: Int) -> Int;

pipeline main(Int) -> Int {
  fn1 -> fn2
}
"""
    result = compile_source_to_ir(source)
    bridge = RLangBoRBridge(
        result.program_ir,
        fn_registry={"fn1": fn1, "fn2": fn2}
    )
    execution_result = bridge.run(5)

    # 5 * 2 + 10 = 20
    assert execution_result.output == 20

