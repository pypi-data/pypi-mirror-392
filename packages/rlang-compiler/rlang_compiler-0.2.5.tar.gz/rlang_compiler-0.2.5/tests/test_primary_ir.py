"""Comprehensive tests for the RLang PrimaryProgramIR."""

import json

import pytest

from rlang.canonical import (
    PrimaryProgramIR,
    build_primary_from_lowering,
    build_primary_program_ir,
    choose_entry_pipeline,
)
from rlang.ir import IRIf, LoweringIRBundle, PipelineStepIR
from rlang.lowering import lower_to_ir
from rlang.parser import parse
from rlang.semantic import resolve_module
from rlang.types import type_check


def test_empty_module_no_entry_empty_lists():
    """Test that empty module produces no entry, empty lists."""
    source = ""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    primary = build_primary_from_lowering(lowering)

    assert primary.entry_pipeline is None
    assert primary.step_templates == []
    assert primary.pipelines == []

    # JSON round-trip
    data = json.loads(primary.to_json())
    assert data["entry_pipeline"] is None
    assert data["step_templates"] == []
    assert data["pipelines"] == []
    assert data["version"] == "v0"
    assert data["language"] == "rlang"


def test_single_pipeline_becomes_entry():
    """Test that single pipeline becomes entry."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    primary = build_primary_from_lowering(lowering)

    assert primary.entry_pipeline == "main"
    assert len(primary.pipelines) == 1
    assert primary.pipelines[0].name == "main"
    assert len(primary.step_templates) == 1


def test_entry_pipeline_selected_by_name_main():
    """Test that entry pipeline is selected by name 'main'."""
    source = """
fn a(x: Int) -> Int;
fn b(x: Int) -> Int;

pipeline other(Int) -> Int {
  a(42)
}

pipeline main(Int) -> Int {
  b(42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    primary = build_primary_from_lowering(lowering)

    assert primary.entry_pipeline == "main"
    assert len(primary.pipelines) == 2

    # Pipelines should be sorted by name
    pipeline_names = [p.name for p in primary.pipelines]
    assert pipeline_names == sorted(pipeline_names)


def test_entry_pipeline_chosen_lexicographically_when_no_main():
    """Test that entry pipeline is chosen lexicographically when no 'main'."""
    source = """
fn a(x: Int) -> Int;
fn b(x: Int) -> Int;

pipeline zeta(Int) -> Int {
  a(42)
}

pipeline alpha(Int) -> Int {
  b(42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    primary = build_primary_from_lowering(lowering)

    assert primary.entry_pipeline == "alpha"  # Lexicographically smallest
    assert len(primary.pipelines) == 2

    # Pipelines should be sorted by name
    pipeline_names = [p.name for p in primary.pipelines]
    assert pipeline_names == ["alpha", "zeta"]


def test_explicit_entry_respected():
    """Test that explicit entry is respected."""
    source = """
fn a(x: Int) -> Int;
fn b(x: Int) -> Int;

pipeline zeta(Int) -> Int {
  a(42)
}

pipeline alpha(Int) -> Int {
  b(42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)

    # Use explicit entry
    primary = build_primary_program_ir(
        bundle=lowering.ir,
        explicit_entry="zeta",
    )

    assert primary.entry_pipeline == "zeta"

    # Test that non-existent explicit entry raises ValueError
    with pytest.raises(ValueError) as exc_info:
        build_primary_program_ir(
            bundle=lowering.ir,
            explicit_entry="nonexistent",
        )

    assert "not found" in str(exc_info.value).lower()


def test_json_is_deterministic():
    """Test that JSON is deterministic."""
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
    # Build primary twice from fresh parse/resolve/type_check/lower
    def build_primary():
        module = parse(source)
        resolution = resolve_module(module)
        tc_result = type_check(resolution)
        lowering = lower_to_ir(tc_result)
        return build_primary_from_lowering(lowering)

    primary1 = build_primary()
    primary2 = build_primary()

    # Call to_json() twice on each
    json1a = primary1.to_json()
    json1b = primary1.to_json()
    json2a = primary2.to_json()
    json2b = primary2.to_json()

    # All should be byte-for-byte identical
    assert json1a == json1b
    assert json2a == json2b
    assert json1a == json2a


def test_step_templates_sorted_by_id():
    """Test that step templates are sorted by id."""
    source = """
fn zeta(x: Int) -> Int;
fn alpha(x: Int) -> Int;
fn beta(x: Int) -> Int;

pipeline main(Int) -> Int {
  zeta(42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    primary = build_primary_from_lowering(lowering)

    # Step templates should be sorted by id
    template_ids = [t.id for t in primary.step_templates]
    assert template_ids == sorted(template_ids)
    assert template_ids == ["fn:alpha", "fn:beta", "fn:zeta"]


def test_primary_ir_to_dict():
    """Test that PrimaryProgramIR can be converted to dict."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    primary = build_primary_from_lowering(lowering)

    primary_dict = primary.to_dict()

    assert primary_dict["version"] == "v0"
    assert primary_dict["language"] == "rlang"
    assert primary_dict["entry_pipeline"] == "main"
    assert len(primary_dict["step_templates"]) == 1
    assert len(primary_dict["pipelines"]) == 1


def test_custom_version_and_language():
    """Test that custom version and language are respected."""
    source = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)

    primary = build_primary_from_lowering(
        lowering,
        version="v1.0",
        language="rlang-v2",
    )

    assert primary.version == "v1.0"
    assert primary.language == "rlang-v2"

    data = json.loads(primary.to_json())
    assert data["version"] == "v1.0"
    assert data["language"] == "rlang-v2"


def test_choose_entry_pipeline_helper():
    """Test choose_entry_pipeline helper function."""
    from rlang.ir import LoweringIRBundle

    # Empty bundle
    empty_bundle = LoweringIRBundle(step_templates={}, pipelines={})
    assert choose_entry_pipeline(empty_bundle) is None

    # Bundle with "main"
    from rlang.ir import PipelineIR

    bundle_with_main = LoweringIRBundle(
        step_templates={},
        pipelines={"main": None, "other": None},  # type: ignore
    )
    assert choose_entry_pipeline(bundle_with_main) == "main"

    # Bundle without "main"
    bundle_no_main = LoweringIRBundle(
        step_templates={},
        pipelines={"zeta": None, "alpha": None},  # type: ignore
    )
    assert choose_entry_pipeline(bundle_no_main) == "alpha"


def test_ir_nested_if_in_then_branch():
    """Test IR structure for nested IF in THEN branch."""
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
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    
    pipeline_ir = lowering.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1
    
    # Top-level step should be IRIf
    top_if = pipeline_ir.steps[0]
    assert isinstance(top_if, IRIf)
    
    # THEN branch should contain nested IRIf
    assert len(top_if.then_steps) == 1
    nested_if = top_if.then_steps[0]
    assert isinstance(nested_if, IRIf)
    
    # Nested IF should have correct structure
    assert len(nested_if.then_steps) == 1
    assert len(nested_if.else_steps) == 1
    assert isinstance(nested_if.then_steps[0], PipelineStepIR)
    assert nested_if.then_steps[0].name == "inc"
    assert isinstance(nested_if.else_steps[0], PipelineStepIR)
    assert nested_if.else_steps[0].name == "dec"
    
    # ELSE branch should contain regular step
    assert len(top_if.else_steps) == 1
    assert isinstance(top_if.else_steps[0], PipelineStepIR)
    assert top_if.else_steps[0].name == "dec"


def test_ir_nested_if_in_else_branch():
    """Test IR structure for nested IF in ELSE branch."""
    source = """
fn inc(x: Int) -> Int;
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
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    
    pipeline_ir = lowering.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1
    
    # Top-level step should be IRIf
    top_if = pipeline_ir.steps[0]
    assert isinstance(top_if, IRIf)
    
    # THEN branch should contain regular step
    assert len(top_if.then_steps) == 1
    assert isinstance(top_if.then_steps[0], PipelineStepIR)
    assert top_if.then_steps[0].name == "inc"
    
    # ELSE branch should contain nested IRIf
    assert len(top_if.else_steps) == 1
    nested_if = top_if.else_steps[0]
    assert isinstance(nested_if, IRIf)
    
    # Nested IF should have correct structure
    assert len(nested_if.then_steps) == 1
    assert len(nested_if.else_steps) == 1
    assert isinstance(nested_if.then_steps[0], PipelineStepIR)
    assert nested_if.then_steps[0].name == "inc"
    assert isinstance(nested_if.else_steps[0], PipelineStepIR)
    assert nested_if.else_steps[0].name == "dec"


def test_ir_deeply_nested_if_structure():
    """Test IR structure for deeply nested IF (3 levels)."""
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
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    
    pipeline_ir = lowering.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1
    
    # Level 1: Top-level IF
    level1_if = pipeline_ir.steps[0]
    assert isinstance(level1_if, IRIf)
    assert len(level1_if.then_steps) == 1
    assert len(level1_if.else_steps) == 1
    assert isinstance(level1_if.else_steps[0], PipelineStepIR)
    assert level1_if.else_steps[0].name == "f1"
    
    # Level 2: IF in THEN branch
    level2_if = level1_if.then_steps[0]
    assert isinstance(level2_if, IRIf)
    assert len(level2_if.then_steps) == 1
    assert len(level2_if.else_steps) == 1
    assert isinstance(level2_if.else_steps[0], PipelineStepIR)
    assert level2_if.else_steps[0].name == "f2"
    
    # Level 3: IF in Level 2's THEN branch
    level3_if = level2_if.then_steps[0]
    assert isinstance(level3_if, IRIf)
    assert len(level3_if.then_steps) == 1
    assert len(level3_if.else_steps) == 1
    assert isinstance(level3_if.then_steps[0], PipelineStepIR)
    assert level3_if.then_steps[0].name == "f4"
    assert isinstance(level3_if.else_steps[0], PipelineStepIR)
    assert level3_if.else_steps[0].name == "f3"


def test_ir_boolean_and_structure():
    """Test IR structure for boolean AND operator."""
    source = """
fn inc(x: Int) -> Int;

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
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    
    pipeline_ir = lowering.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1
    
    # Top-level step should be IRIf
    top_if = pipeline_ir.steps[0]
    assert isinstance(top_if, IRIf)
    
    # Condition should be boolean_and
    condition = top_if.condition
    assert condition.kind == "boolean_and"
    assert condition.left is not None
    assert condition.right is not None
    
    # Left should be comparison (>)
    assert condition.left.kind == "binary_op"
    assert condition.left.op == ">"
    
    # Right should be comparison (<)
    assert condition.right.kind == "binary_op"
    assert condition.right.op == "<"


def test_ir_boolean_or_structure():
    """Test IR structure for boolean OR operator."""
    source = """
fn inc(x: Int) -> Int;

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
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    
    pipeline_ir = lowering.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1
    
    # Top-level step should be IRIf
    top_if = pipeline_ir.steps[0]
    assert isinstance(top_if, IRIf)
    
    # Condition should be boolean_or
    condition = top_if.condition
    assert condition.kind == "boolean_or"
    assert condition.left is not None
    assert condition.right is not None
    
    # Left should be comparison (>)
    assert condition.left.kind == "binary_op"
    assert condition.left.op == ">"
    
    # Right should be comparison (<)
    assert condition.right.kind == "binary_op"
    assert condition.right.op == "<"


def test_ir_boolean_not_structure():
    """Test IR structure for boolean NOT operator."""
    source = """
fn inc(x: Int) -> Int;

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
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    
    pipeline_ir = lowering.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1
    
    # Top-level step should be IRIf
    top_if = pipeline_ir.steps[0]
    assert isinstance(top_if, IRIf)
    
    # Condition should be boolean_not
    condition = top_if.condition
    assert condition.kind == "boolean_not"
    assert condition.operand is not None
    
    # Operand should be comparison (>)
    assert condition.operand.kind == "binary_op"
    assert condition.operand.op == ">"


def test_ir_boolean_complex_expression_structure():
    """Test IR structure for complex nested boolean expression."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (!(__value > 10 && __value < 20) || __value == 0) {
        inc
    } else {
        inc
    }
}
"""
    module = parse(source)
    resolution = resolve_module(module)
    tc_result = type_check(resolution)
    lowering = lower_to_ir(tc_result)
    
    pipeline_ir = lowering.ir.pipelines["main"]
    assert len(pipeline_ir.steps) == 1
    
    # Top-level step should be IRIf
    top_if = pipeline_ir.steps[0]
    assert isinstance(top_if, IRIf)
    
    # Condition should be boolean_or
    condition = top_if.condition
    assert condition.kind == "boolean_or"
    
    # Left should be boolean_not
    assert condition.left is not None
    assert condition.left.kind == "boolean_not"
    
    # NOT's operand should be boolean_and
    assert condition.left.operand is not None
    assert condition.left.operand.kind == "boolean_and"
    
    # AND's left should be comparison (>)
    assert condition.left.operand.left.kind == "binary_op"
    assert condition.left.operand.left.op == ">"
    
    # AND's right should be comparison (<)
    assert condition.left.operand.right.kind == "binary_op"
    assert condition.left.operand.right.op == "<"
    
    # OR's right should be comparison (==)
    assert condition.right is not None
    assert condition.right.kind == "binary_op"
    assert condition.right.op == "=="

