"""Comprehensive tests for the RLang PrimaryProgramIR."""

import json

import pytest

from rlang.canonical import (
    PrimaryProgramIR,
    build_primary_from_lowering,
    build_primary_program_ir,
    choose_entry_pipeline,
)
from rlang.ir import LoweringIRBundle
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

