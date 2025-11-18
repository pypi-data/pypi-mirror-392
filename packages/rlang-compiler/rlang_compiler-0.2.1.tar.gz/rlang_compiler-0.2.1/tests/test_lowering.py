"""Comprehensive tests for the RLang IR lowering."""

import json

import pytest

from rlang.ir import IRIf, LoweringIRBundle, PipelineIR, StepTemplateIR, rtype_to_string
from rlang.lowering import LoweringError, lower_to_ir
from rlang.parser import parse
from rlang.semantic import resolve_module
from rlang.types import RType, type_check


def test_empty_module_produces_empty_ir_bundle():
    """Test that empty module produces empty IR bundle."""
    source = ""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert len(result.ir.step_templates) == 0
    assert len(result.ir.pipelines) == 0


def test_single_function_no_pipelines():
    """Test lowering a single function with no pipelines."""
    source = "fn step1(x: Int) -> Int;"
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert len(result.ir.step_templates) == 1
    assert "fn:step1" in result.ir.step_templates

    template = result.ir.step_templates["fn:step1"]
    assert template.id == "fn:step1"
    assert template.name == "step1"
    assert template.fn_name == "step1"
    assert template.param_types == ["Int"]
    assert template.return_type == "Int"
    assert "fn step1(Int) -> Int" in template.rule_repr


def test_simple_pipeline_lowering():
    """Test lowering a simple pipeline."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]

    assert pipeline_ir.id == "pipeline:main"
    assert pipeline_ir.name == "main"
    # Input/output types should be stringified (could be "Input" or "Int" depending on implementation)
    assert pipeline_ir.input_type is not None
    assert pipeline_ir.output_type is not None

    assert len(pipeline_ir.steps) == 2

    step1 = pipeline_ir.steps[0]
    assert step1.index == 0
    assert step1.name == "step1"
    assert step1.template_id == "fn:step1"
    assert step1.input_type is not None
    assert step1.output_type is not None

    step2 = pipeline_ir.steps[1]
    assert step2.index == 1
    assert step2.name == "step2"
    assert step2.template_id == "fn:step2"
    assert step2.input_type is not None
    assert step2.output_type is not None


def test_pipeline_with_literal_arguments():
    """Test lowering a pipeline with literal arguments."""
    source = """
fn step1(x: Int, label: String) -> Int;

pipeline main(Int) -> Int {
  step1(42, "ok")
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]

    assert len(pipeline_ir.steps) == 1
    step = pipeline_ir.steps[0]

    assert step.name == "step1"
    assert len(step.arg_types) == 2
    assert "Int" in step.arg_types
    assert "String" in step.arg_types
    assert step.input_type is not None


def test_bundle_json_is_stable_and_canonical():
    """Test that bundle JSON is stable and canonical."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    # Get JSON twice
    json1 = result.ir.to_json()
    json2 = result.ir.to_json()

    # Should be byte-for-byte identical
    assert json1 == json2

    # Should be valid JSON
    data = json.loads(json1)
    assert "step_templates" in data
    assert "pipelines" in data
    assert len(data["step_templates"]) == 1
    assert len(data["pipelines"]) == 1


def test_rtype_to_string():
    """Test rtype_to_string helper function."""
    # Simple type
    rtype1 = RType("Int")
    assert rtype_to_string(rtype1) == "Int"

    # Generic type
    rtype2 = RType("List", (RType("Int"),))
    assert rtype_to_string(rtype2) == "List[Int]"

    # Nested generic
    rtype3 = RType("Map", (RType("String"), RType("Int")))
    assert rtype_to_string(rtype3) == "Map[String,Int]"

    # Complex nested
    rtype4 = RType("List", (RType("Map", (RType("String"), RType("Int"))),))
    assert rtype_to_string(rtype4) == "List[Map[String,Int]]"


def test_step_template_rule_repr():
    """Test that step template rule_repr is correctly formatted."""
    source = """
fn add(a: Int, b: Int) -> Int;
fn greet(name: String);
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    add_template = result.ir.step_templates["fn:add"]
    assert "fn add(Int, Int) -> Int" in add_template.rule_repr

    greet_template = result.ir.step_templates["fn:greet"]
    assert "fn greet(String) -> Unit" in greet_template.rule_repr or "fn greet(String)" in greet_template.rule_repr


def test_pipeline_step_without_explicit_args():
    """Test pipeline step without explicit arguments."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    pipeline_ir = result.ir.pipelines["main"]
    step = pipeline_ir.steps[0]

    # Should have empty arg_types when no explicit args
    assert step.arg_types == []
    assert step.input_type is not None
    assert step.output_type is not None


def test_complex_pipeline_lowering():
    """Test lowering a complex pipeline with multiple steps."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert len(result.ir.step_templates) == 3
    assert "process" in result.ir.pipelines

    pipeline_ir = result.ir.pipelines["process"]
    assert len(pipeline_ir.steps) == 3

    assert pipeline_ir.steps[0].name == "load"
    assert pipeline_ir.steps[1].name == "transform"
    assert pipeline_ir.steps[2].name == "save"

    # Check indices
    assert pipeline_ir.steps[0].index == 0
    assert pipeline_ir.steps[1].index == 1
    assert pipeline_ir.steps[2].index == 2


def test_step_template_to_dict():
    """Test that step template can be converted to dict."""
    source = "fn test(x: Int) -> String;"
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    template = result.ir.step_templates["fn:test"]
    template_dict = template.to_dict()

    assert template_dict["id"] == "fn:test"
    assert template_dict["name"] == "test"
    assert template_dict["param_types"] == ["Int"]
    assert template_dict["return_type"] == "String"


def test_pipeline_ir_to_dict():
    """Test that pipeline IR can be converted to dict."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    pipeline_ir = result.ir.pipelines["main"]
    pipeline_dict = pipeline_ir.to_dict()

    assert pipeline_dict["id"] == "pipeline:main"
    assert pipeline_dict["name"] == "main"
    assert len(pipeline_dict["steps"]) == 1
    assert pipeline_dict["steps"][0]["name"] == "step1"


def test_lower_if_expr_without_else():
    """Test lowering if expression without else branch."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1

    step = pipeline_ir.steps[0]
    assert isinstance(step, IRIf)
    assert step.condition.kind == "binary_op"
    assert step.condition.op == "=="
    assert len(step.then_steps) == 1
    assert step.then_steps[0].name == "double"
    assert len(step.else_steps) == 0


def test_lower_if_expr_with_else():
    """Test lowering if expression with else branch."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1

    step = pipeline_ir.steps[0]
    assert isinstance(step, IRIf)
    assert len(step.then_steps) == 1
    assert step.then_steps[0].name == "double"
    assert len(step.else_steps) == 1
    assert step.else_steps[0].name == "half"

def test_if_expr_canonical_json_structure():
    """Test that if expressions produce canonical JSON structure."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    pipeline_ir = result.ir.pipelines["main"]
    pipeline_dict = pipeline_ir.to_dict()

    # Check structure
    assert len(pipeline_dict["steps"]) == 1
    step_dict = pipeline_dict["steps"][0]

    # Check if step has "kind": "if"
    assert step_dict["kind"] == "if"
    assert "condition" in step_dict
    assert "then" in step_dict
    assert "else" in step_dict

    # Check condition structure
    condition = step_dict["condition"]
    assert condition["kind"] == "binary_op"
    assert condition["op"] == "=="

    # Check branches
    assert len(step_dict["then"]) == 1
    assert step_dict["then"][0]["name"] == "double"
    assert len(step_dict["else"]) == 1
    assert step_dict["else"][0]["name"] == "half"


def test_if_expr_no_else_canonical_json():
    """Test canonical JSON for if without else."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    pipeline_ir = result.ir.pipelines["main"]
    pipeline_dict = pipeline_ir.to_dict()

    step_dict = pipeline_dict["steps"][0]
    assert step_dict["kind"] == "if"
    assert len(step_dict["then"]) == 1
    assert len(step_dict["else"]) == 0  # Empty list, not missing
