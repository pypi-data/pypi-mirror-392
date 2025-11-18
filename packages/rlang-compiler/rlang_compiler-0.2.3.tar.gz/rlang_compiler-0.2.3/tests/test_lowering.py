"""Comprehensive tests for the RLang IR lowering."""

import json

import pytest

from rlang.ir import IRExpr, IRIf, LoweringIRBundle, PipelineIR, PipelineStepIR, StepTemplateIR, rtype_to_string
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


def test_lowering_nested_if_deterministic():
    """Test that lowering nested IF produces deterministic IR."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value > 20) { inc } else { dec }
    } else {
        dec
    }
}
"""
    def build_ir():
        module = parse(source)
        resolution = resolve_module(module)
        tc_result = type_check(resolution)
        return lower_to_ir(tc_result).ir
    
    ir1 = build_ir()
    ir2 = build_ir()
    
    # IR dictionaries should be identical
    assert ir1.to_dict() == ir2.to_dict()
    
    # JSON should be identical
    assert ir1.to_json() == ir2.to_json()
    
    # Verify nested structure
    pipeline1 = ir1.pipelines["main"]
    pipeline2 = ir2.pipelines["main"]
    
    assert len(pipeline1.steps) == len(pipeline2.steps) == 1
    assert isinstance(pipeline1.steps[0], IRIf)
    assert isinstance(pipeline2.steps[0], IRIf)
    
    top_if1 = pipeline1.steps[0]
    top_if2 = pipeline2.steps[0]
    
    # Verify nested IF in THEN branch
    assert len(top_if1.then_steps) == len(top_if2.then_steps) == 1
    assert isinstance(top_if1.then_steps[0], IRIf)
    assert isinstance(top_if2.then_steps[0], IRIf)
    
    nested_if1 = top_if1.then_steps[0]
    nested_if2 = top_if2.then_steps[0]
    
    assert nested_if1.to_dict() == nested_if2.to_dict()


def test_lowering_deeply_nested_if_deterministic():
    """Test that lowering deeply nested IF produces deterministic IR."""
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
    def build_ir():
        module = parse(source)
        resolution = resolve_module(module)
        tc_result = type_check(resolution)
        return lower_to_ir(tc_result).ir
    
    ir1 = build_ir()
    ir2 = build_ir()
    
    # IR dictionaries should be identical
    assert ir1.to_dict() == ir2.to_dict()
    
    # JSON should be identical
    assert ir1.to_json() == ir2.to_json()
    
    # Verify deeply nested structure
    pipeline1 = ir1.pipelines["main"]
    pipeline2 = ir2.pipelines["main"]
    
    # Both should have same structure
    assert pipeline1.to_dict() == pipeline2.to_dict()


def test_lowering_nested_if_with_multiple_steps():
    """Test lowering nested IF with multiple steps in branches."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)
    
    pipeline_ir = result.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1
    
    top_if = pipeline_ir.steps[0]
    assert isinstance(top_if, IRIf)
    
    # THEN branch has 2 steps
    assert len(top_if.then_steps) == 2
    assert isinstance(top_if.then_steps[0], PipelineStepIR)
    assert top_if.then_steps[0].name == "inc"
    assert isinstance(top_if.then_steps[1], PipelineStepIR)
    assert top_if.then_steps[1].name == "double"
    
    # ELSE branch has nested IF
    assert len(top_if.else_steps) == 1
    nested_if = top_if.else_steps[0]
    assert isinstance(nested_if, IRIf)
    
    # Nested THEN has 2 steps
    assert len(nested_if.then_steps) == 2
    assert nested_if.then_steps[0].name == "inc"
    assert nested_if.then_steps[1].name == "dec"
    
    # Nested ELSE has 2 steps
    assert len(nested_if.else_steps) == 2
    assert nested_if.else_steps[0].name == "dec"
    assert nested_if.else_steps[1].name == "double"


def test_lowering_boolean_and_deterministic():
    """Test that lowering boolean AND produces deterministic IR."""
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
    from rlang.emitter import compile_source_to_ir
    
    ir1 = compile_source_to_ir(source).program_ir
    ir2 = compile_source_to_ir(source).program_ir
    
    # IR dictionaries should be identical
    assert ir1.to_dict() == ir2.to_dict()
    
    # JSON should be identical
    assert ir1.to_json() == ir2.to_json()
    
    # Verify boolean_and structure
    pipeline1 = ir1.pipelines[0]
    pipeline2 = ir2.pipelines[0]
    
    assert len(pipeline1.steps) == len(pipeline2.steps) == 1
    assert isinstance(pipeline1.steps[0], IRIf)
    assert isinstance(pipeline2.steps[0], IRIf)
    
    condition1 = pipeline1.steps[0].condition
    condition2 = pipeline2.steps[0].condition
    
    assert condition1.kind == condition2.kind == "boolean_and"
    assert condition1.to_dict() == condition2.to_dict()


def test_lowering_boolean_or_deterministic():
    """Test that lowering boolean OR produces deterministic IR."""
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
    from rlang.emitter import compile_source_to_ir
    
    ir1 = compile_source_to_ir(source).program_ir
    ir2 = compile_source_to_ir(source).program_ir
    
    # IR dictionaries should be identical
    assert ir1.to_dict() == ir2.to_dict()
    
    # JSON should be identical
    assert ir1.to_json() == ir2.to_json()
    
    # Verify boolean_or structure
    pipeline1 = ir1.pipelines[0]
    pipeline2 = ir2.pipelines[0]
    
    condition1 = pipeline1.steps[0].condition
    condition2 = pipeline2.steps[0].condition
    
    assert condition1.kind == condition2.kind == "boolean_or"
    assert condition1.to_dict() == condition2.to_dict()


def test_lowering_boolean_not_deterministic():
    """Test that lowering boolean NOT produces deterministic IR."""
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
    from rlang.emitter import compile_source_to_ir
    
    ir1 = compile_source_to_ir(source).program_ir
    ir2 = compile_source_to_ir(source).program_ir
    
    # IR dictionaries should be identical
    assert ir1.to_dict() == ir2.to_dict()
    
    # JSON should be identical
    assert ir1.to_json() == ir2.to_json()
    
    # Verify boolean_not structure
    pipeline1 = ir1.pipelines[0]
    pipeline2 = ir2.pipelines[0]
    
    condition1 = pipeline1.steps[0].condition
    condition2 = pipeline2.steps[0].condition
    
    assert condition1.kind == condition2.kind == "boolean_not"
    assert condition1.to_dict() == condition2.to_dict()


def test_lowering_boolean_complex_expression_deterministic():
    """Test that lowering complex nested boolean expression produces deterministic IR."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
    if ((__value > 10 && __value < 20) || !(__value == 0)) {
        inc
    } else {
        inc
    }
}
"""
    from rlang.emitter import compile_source_to_ir
    
    ir1 = compile_source_to_ir(source).program_ir
    ir2 = compile_source_to_ir(source).program_ir
    
    # IR dictionaries should be identical
    assert ir1.to_dict() == ir2.to_dict()
    
    # JSON should be identical
    assert ir1.to_json() == ir2.to_json()
    
    # Verify complex structure
    pipeline1 = ir1.pipelines[0]
    pipeline2 = ir2.pipelines[0]
    
    condition1 = pipeline1.steps[0].condition
    condition2 = pipeline2.steps[0].condition
    
    # Should be boolean_or
    assert condition1.kind == condition2.kind == "boolean_or"
    
    # Left should be boolean_and
    assert condition1.left.kind == condition2.left.kind == "boolean_and"
    
    # Right should be boolean_not
    assert condition1.right.kind == condition2.right.kind == "boolean_not"
    
    # Verify full structure matches
    assert condition1.to_dict() == condition2.to_dict()


def test_lower_record_with_list_field():
    """Test lowering a record with a list field."""
    source = """
type User = Record { id: Int, tags: List<String> };

pipeline main(Int) -> User {
    { id: __value, tags: ["x", "y"] }
}
"""
    from rlang.parser import parse
    from rlang.semantic import resolve_module
    from rlang.types import type_check
    from rlang.lowering import lower_to_ir
    
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]

    assert len(pipeline_ir.steps) == 1
    step = pipeline_ir.steps[0]
    assert isinstance(step, IRExpr)
    assert step.kind == "record"
    assert step.fields is not None
    assert "id" in step.fields
    assert "tags" in step.fields
    
    # Check that fields are sorted alphabetically
    field_keys = list(step.fields.keys())
    assert field_keys == ["id", "tags"]  # alphabetical order
    
    # Check that tags field is a list IR node
    tags_field = step.fields["tags"]
    assert isinstance(tags_field, IRExpr)
    assert tags_field.kind == "list"
    assert len(tags_field.elements) == 2
    assert tags_field.elements[0].kind == "literal"
    assert tags_field.elements[0].value == "x"
    assert tags_field.elements[1].kind == "literal"
    assert tags_field.elements[1].value == "y"


def test_lower_list_of_records():
    """Test lowering a list of records."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> List<User> {
    [
        { id: __value,     name: "A" },
        { id: __value + 1, name: "B" }
    ]
}
"""
    from rlang.parser import parse
    from rlang.semantic import resolve_module
    from rlang.types import type_check
    from rlang.lowering import lower_to_ir
    
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]

    assert len(pipeline_ir.steps) == 1
    step = pipeline_ir.steps[0]
    assert isinstance(step, IRExpr)
    assert step.kind == "list"
    assert len(step.elements) == 2
    
    # Check first element is a record with sorted fields
    elem1 = step.elements[0]
    assert isinstance(elem1, IRExpr)
    assert elem1.kind == "record"
    assert elem1.fields is not None
    assert list(elem1.fields.keys()) == ["id", "name"]  # alphabetical order
    
    # Check second element
    elem2 = step.elements[1]
    assert isinstance(elem2, IRExpr)
    assert elem2.kind == "record"
    assert elem2.fields is not None
    assert list(elem2.fields.keys()) == ["id", "name"]  # alphabetical order


def test_lower_for_step_unrolls_correctly():
    """Test that for loop unrolls correctly to repeated steps."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]

    # Should have 3 steps (unrolled from loop)
    assert len(pipeline_ir.steps) == 3

    # All steps should be PipelineStepIR with name "inc"
    for i, step in enumerate(pipeline_ir.steps):
        assert isinstance(step, PipelineStepIR)
        assert step.index == i
        assert step.name == "inc"
        assert step.template_id == "fn:inc"


def test_lower_for_step_zero_iterations():
    """Test that for loop with zero iterations produces no steps."""
    source = """
fn inc(x: Int) -> Int;
fn process(x: Record { id: Int, name: String }) -> Int;

pipeline main(Int) -> Int {
  for i in 3 .. 3 {
    inc
  }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]

    # Should have 0 steps (zero iterations)
    assert len(pipeline_ir.steps) == 0


# Pattern Matching Lowering Tests

def test_match_expr_lowers_to_nested_if():
    """Test that match expression lowers to nested IRIf."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    match (__value) {
        case 0 => { inc(); }
        case 1 => { dec(); }
        case _ => { inc(); }
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
    
    # First step should be an IRIf
    step = pipeline_ir.steps[0]
    assert isinstance(step, IRIf)
    
    # Should have condition checking for 0
    assert step.condition.kind == "binary_op"
    assert step.condition.op == "=="
    
    # Should have nested else branch
    assert len(step.else_steps) == 1
    assert isinstance(step.else_steps[0], IRIf)


def test_match_expr_with_literal_pattern():
    """Test lowering match expression with literal pattern."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    match (__value) {
        case 42 => { inc(); }
        case _ => { inc(); }
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]
    step = pipeline_ir.steps[0]
    assert isinstance(step, IRIf)
    
    # Condition should be equality check
    assert step.condition.kind == "binary_op"
    assert step.condition.op == "=="
    assert step.condition.right.value == 42


def test_match_expr_with_record_pattern():
    """Test lowering match expression with record pattern."""
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
    tc_result = type_check(resolution)
    result = lower_to_ir(tc_result)

    assert "main" in result.ir.pipelines
    pipeline_ir = result.ir.pipelines["main"]
    step = pipeline_ir.steps[0]
    assert isinstance(step, IRIf)
    
    # Condition should be boolean_and combining field checks
    assert step.condition.kind == "boolean_and"
