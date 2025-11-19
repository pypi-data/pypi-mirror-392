"""Comprehensive tests for RLang execution proof bundle generation."""

import json

import pytest

from rlang.bor import PipelineProofBundle, StepExecutionRecord, run_program_with_proof


def test_single_step_proof():
    """Test proof generation for single-step pipeline."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    bundle = run_program_with_proof(
        source=src,
        input_value=10,
        fn_registry={"inc": lambda x: x + 1},
    )

    assert isinstance(bundle, PipelineProofBundle)
    assert bundle.entry_pipeline == "main"
    assert bundle.input_value == 10
    assert bundle.output_value == 11
    assert len(bundle.steps) == 1

    step = bundle.steps[0]
    assert step.index == 0
    assert step.step_name == "inc"
    assert step.input_snapshot == 10
    assert step.output_snapshot == 11


def test_multi_step_proof():
    """Test proof generation for multi-step pipeline."""
    src = """
fn inc(x: Int) -> Int;
fn double(x: Int) -> Int;

pipeline main(Int) -> Int { inc -> double }
"""
    registry = {
        "inc": lambda x: x + 1,
        "double": lambda x: x * 2,
    }

    bundle = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry=registry,
    )

    assert bundle.output_value == 12  # (5 + 1) * 2
    assert len(bundle.steps) == 2
    assert [s.step_name for s in bundle.steps] == ["inc", "double"]
    assert bundle.steps[0].output_snapshot == 6
    assert bundle.steps[1].input_snapshot == 6


def test_missing_function_raises_error():
    """Test that missing function in registry raises ValueError."""
    src = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int { step1 }
"""
    with pytest.raises(ValueError) as exc_info:
        run_program_with_proof(
            source=src,
            input_value=42,
            fn_registry=None,
        )
    
    assert "not found in fn_registry" in str(exc_info.value)


def test_proof_json_determinism():
    """Test that proof JSON is deterministic."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    bundle1 = run_program_with_proof(
        source=src,
        input_value=7,
        fn_registry={"inc": lambda x: x + 1},
    )

    bundle2 = run_program_with_proof(
        source=src,
        input_value=7,
        fn_registry={"inc": lambda x: x + 1},
    )

    json1 = bundle1.to_json()
    json2 = bundle2.to_json()

    assert json1 == json2

    data = json.loads(json1)
    assert data["input"] == 7
    assert data["output"] == 8
    assert len(data["steps"]) == 1


def test_no_entry_pipeline_error():
    """Test that missing entry pipeline raises ValueError."""
    src = "fn f(x: Int) -> Int;"

    with pytest.raises(ValueError) as exc_info:
        run_program_with_proof(source=src, input_value=1)

    assert "No entry pipeline" in str(exc_info.value)


def test_proof_bundle_structure():
    """Test that proof bundle has correct structure."""
    src = """
fn add(x: Int) -> Int;

pipeline main(Int) -> Int { add }
"""
    bundle = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry={"add": lambda x: x + 3},
    )

    assert bundle.version == "v0"
    assert bundle.language == "rlang"
    assert bundle.entry_pipeline == "main"
    assert bundle.input_value == 5
    assert bundle.output_value == 8
    assert len(bundle.steps) == 1

    # Verify program IR is included
    assert bundle.program_ir is not None
    assert bundle.program_ir.entry_pipeline == "main"


def test_step_execution_record_structure():
    """Test that step execution records have correct structure."""
    src = """
fn multiply(x: Int) -> Int;

pipeline main(Int) -> Int { multiply }
"""
    bundle = run_program_with_proof(
        source=src,
        input_value=6,
        fn_registry={"multiply": lambda x: x * 7},
    )

    step = bundle.steps[0]
    assert isinstance(step, StepExecutionRecord)
    assert step.index == 0
    assert step.step_name == "multiply"
    assert step.template_id.startswith("fn:")
    assert step.input_snapshot == 6
    assert step.output_snapshot == 42

    # Verify to_dict works
    step_dict = step.to_dict()
    assert step_dict["index"] == 0
    assert step_dict["step_name"] == "multiply"
    assert step_dict["input"] == 6
    assert step_dict["output"] == 42


def test_proof_bundle_to_dict():
    """Test that proof bundle to_dict() works correctly."""
    src = """
fn square(x: Int) -> Int;

pipeline main(Int) -> Int { square }
"""
    bundle = run_program_with_proof(
        source=src,
        input_value=9,
        fn_registry={"square": lambda x: x * x},
    )

    bundle_dict = bundle.to_dict()

    assert bundle_dict["version"] == "v0"
    assert bundle_dict["language"] == "rlang"
    assert bundle_dict["entry_pipeline"] == "main"
    assert bundle_dict["input"] == 9
    assert bundle_dict["output"] == 81
    assert len(bundle_dict["steps"]) == 1
    assert "program" in bundle_dict


def test_proof_bundle_to_json():
    """Test that proof bundle to_json() produces valid JSON."""
    src = """
fn identity(x: Int) -> Int;

pipeline main(Int) -> Int { identity }
"""
    bundle = run_program_with_proof(
        source=src,
        input_value=100,
        fn_registry={"identity": lambda x: x},
    )

    json_str = bundle.to_json()
    assert isinstance(json_str, str)

    # Should be valid JSON
    data = json.loads(json_str)
    assert data["input"] == 100
    assert data["output"] == 100


def test_missing_function_in_middle_raises_error():
    """Test that missing function in middle of pipeline raises ValueError."""
    src = """
fn real_fn(x: Int) -> Int;
fn missing_fn(x: Int) -> Int;

pipeline main(Int) -> Int { real_fn -> missing_fn }
"""
    with pytest.raises(ValueError) as exc_info:
        run_program_with_proof(
            source=src,
            input_value=10,
            fn_registry={"real_fn": lambda x: x * 2},
        )
    
    assert "not found in fn_registry" in str(exc_info.value)
    assert "missing_fn" in str(exc_info.value)


def test_complex_pipeline_proof():
    """Test proof generation for complex multi-step pipeline."""
    src = """
fn add_one(x: Int) -> Int;
fn multiply(x: Int) -> Int;
fn subtract(x: Int) -> Int;

pipeline main(Int) -> Int { add_one -> multiply -> subtract }
"""
    registry = {
        "add_one": lambda x: x + 1,
        "multiply": lambda x: x * 3,
        "subtract": lambda x: x - 2,
    }

    bundle = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry=registry,
    )

    assert len(bundle.steps) == 3
    assert bundle.input_value == 5
    assert bundle.output_value == 16  # (5 + 1) * 3 - 2 = 16

    # Verify step-by-step execution
    assert bundle.steps[0].input_snapshot == 5
    assert bundle.steps[0].output_snapshot == 6
    assert bundle.steps[1].input_snapshot == 6
    assert bundle.steps[1].output_snapshot == 18
    assert bundle.steps[2].input_snapshot == 18
    assert bundle.steps[2].output_snapshot == 16


def test_custom_version_and_language():
    """Test that custom version and language are preserved in proof bundle."""
    src = """
fn test(x: Int) -> Int;

pipeline main(Int) -> Int { test }
"""
    bundle = run_program_with_proof(
        source=src,
        input_value=1,
        fn_registry={"test": lambda x: x},
        version="v1.0",
        language="rlang-v2",
    )

    assert bundle.version == "v1.0"
    assert bundle.language == "rlang-v2"

    bundle_dict = bundle.to_dict()
    assert bundle_dict["version"] == "v1.0"
    assert bundle_dict["language"] == "rlang-v2"


def test_proof_bundle_immutability():
    """Test that proof bundle and records are immutable (frozen dataclasses)."""
    src = """
fn test(x: Int) -> Int;

pipeline main(Int) -> Int { test }
"""
    bundle = run_program_with_proof(
        source=src,
        input_value=1,
        fn_registry={"test": lambda x: x},
    )

    # Should not be able to modify frozen dataclass
    with pytest.raises(Exception):  # dataclass.FrozenInstanceError
        bundle.input_value = 999

    with pytest.raises(Exception):  # dataclass.FrozenInstanceError
        bundle.steps[0].input_snapshot = 999


def test_template_id_in_records():
    """Test that step execution records include correct template_id."""
    src = """
fn step1(x: Int) -> Int;
fn step2(x: Int) -> Int;

pipeline main(Int) -> Int { step1 -> step2 }
"""
    bundle = run_program_with_proof(
        source=src,
        input_value=1,
        fn_registry={"step1": lambda x: x + 1, "step2": lambda x: x * 2},
    )

    assert len(bundle.steps) == 2
    assert bundle.steps[0].template_id.startswith("fn:")
    assert bundle.steps[1].template_id.startswith("fn:")
    assert bundle.steps[0].template_id != bundle.steps[1].template_id

    # Verify template_id is in dict representation
    step_dict = bundle.steps[0].to_dict()
    assert "template_id" in step_dict
    assert step_dict["template_id"].startswith("fn:")


def test_run_program_with_if_then_branch_only():
    """Test runtime execution with if expression taking then branch."""
    source = """
fn double(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    double
  }
}
"""
    fn_registry = {"double": lambda x: x * 2}
    bundle = run_program_with_proof(
        source=source,
        input_value=10,
        fn_registry=fn_registry,
    )

    assert bundle.output_value == 20
    assert len(bundle.steps) == 1
    assert bundle.steps[0].step_name == "double"
    assert bundle.steps[0].input_snapshot == 10
    assert bundle.steps[0].output_snapshot == 20

    # Check branch record
    assert len(bundle.branches) == 1
    assert bundle.branches[0].path == "then"
    assert bundle.branches[0].condition_value is True


def test_run_program_with_if_else_false_branch():
    """Test runtime execution with if expression taking else branch."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 2) {
    inc
  } else {
    dec
  }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }
    bundle = run_program_with_proof(
        source=source,
        input_value=10,
        fn_registry=fn_registry,
    )

    assert bundle.output_value == 9  # false condition → else branch (dec)
    assert len(bundle.steps) == 1
    assert bundle.steps[0].step_name == "dec"
    assert bundle.steps[0].input_snapshot == 10
    assert bundle.steps[0].output_snapshot == 9

    # Check branch record
    assert len(bundle.branches) == 1
    assert bundle.branches[0].path == "else"
    assert bundle.branches[0].condition_value is False


def test_run_program_with_if_both_branches_same_type():
    """Test runtime execution with if expression having both branches."""
    source = """
fn double(x: Int) -> Int;
fn half(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (5 > 3) {
    double
  } else {
    half
  }
}
"""
    fn_registry = {
        "double": lambda x: x * 2,
        "half": lambda x: x // 2,
    }
    bundle = run_program_with_proof(
        source=source,
        input_value=10,
        fn_registry=fn_registry,
    )

    # Condition is True, so then branch executes
    assert bundle.output_value == 20
    assert len(bundle.steps) == 1
    assert bundle.steps[0].step_name == "double"
    assert len(bundle.branches) == 1
    assert bundle.branches[0].path == "then"
    assert bundle.branches[0].condition_value is True


def test_if_expr_branch_trace_in_json():
    """Test that branch trace appears in proof bundle JSON."""
    source = """
fn double(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    double
  }
}
"""
    bundle = run_program_with_proof(
        source=source,
        input_value=5,
        fn_registry={"double": lambda x: x * 2},
    )

    bundle_dict = bundle.to_dict()
    assert "branches" in bundle_dict
    assert len(bundle_dict["branches"]) == 1
    branch = bundle_dict["branches"][0]
    assert branch["path"] == "then"
    assert branch["condition_value"] is True
    assert "index" in branch

def test_if_expr_with_value_identifier_runtime():
    """Test runtime execution with __value identifier in condition."""
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
    fn_registry = {
        "double": lambda x: x * 2,
        "half": lambda x: x // 2,
    }

    # Test with value > 10 (takes then branch)
    bundle1 = run_program_with_proof(
        source=source,
        input_value=20,
        fn_registry=fn_registry,
    )
    assert bundle1.output_value == 40  # 20 * 2
    assert bundle1.branches[0].path == "then"
    assert bundle1.branches[0].condition_value is True

    # Test with value <= 10 (takes else branch)
    bundle2 = run_program_with_proof(
        source=source,
        input_value=5,
        fn_registry=fn_registry,
    )
    assert bundle2.output_value == 2  # 5 // 2
    assert bundle2.branches[0].path == "else"
    assert bundle2.branches[0].condition_value is False


def test_multi_if_determinism():
    """Test that multi-IF pipelines produce deterministic results."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (__value > 10) {
    inc
  } else {
    dec
  } ->
  if (__value > 20) {
    inc
  } else {
    dec
  } ->
  if (__value > 30) {
    inc
  } else {
    dec
  }
}
"""

    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Test determinism: same input should produce identical results
    for v in [0, 5, 12, 25, 35, 99]:
        a = run_program_with_proof(source, v, fn_registry=fn_registry).to_dict()
        b = run_program_with_proof(source, v, fn_registry=fn_registry).to_dict()
        assert a == b, f"Multi-IF determinism failed for input {v}"


def test_nested_if_execution_correctness_then_then():
    """Test execution correctness for nested IF in THEN branch."""
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
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input 5: outer else branch → dec(5) = 4
    bundle1 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle1.output_value == 4
    assert len(bundle1.branches) == 1
    assert bundle1.branches[0].path == "else"
    assert bundle1.branches[0].condition_value is False

    # Input 15: outer then, inner else → dec(15) = 14
    bundle2 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle2.output_value == 14
    assert len(bundle2.branches) == 2
    assert bundle2.branches[0].path == "then"
    assert bundle2.branches[0].condition_value is True
    assert bundle2.branches[1].path == "else"
    assert bundle2.branches[1].condition_value is False

    # Input 25: outer then, inner then → inc(25) = 26
    bundle3 = run_program_with_proof(source, 25, fn_registry=fn_registry)
    assert bundle3.output_value == 26
    assert len(bundle3.branches) == 2
    assert bundle3.branches[0].path == "then"
    assert bundle3.branches[0].condition_value is True
    assert bundle3.branches[1].path == "then"
    assert bundle3.branches[1].condition_value is True


def test_nested_if_execution_correctness_else_nested():
    """Test execution correctness for nested IF in ELSE branch."""
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
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input 15: outer then → inc(15) = 16
    bundle1 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle1.output_value == 16
    assert len(bundle1.branches) == 1
    assert bundle1.branches[0].path == "then"
    assert bundle1.branches[0].condition_value is True

    # Input 5: outer else, inner then → inc(5) = 6
    bundle2 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle2.output_value == 6
    assert len(bundle2.branches) == 2
    assert bundle2.branches[0].path == "else"
    assert bundle2.branches[0].condition_value is False
    assert bundle2.branches[1].path == "then"
    assert bundle2.branches[1].condition_value is True

    # Input -5: outer else, inner else → dec(-5) = -6
    bundle3 = run_program_with_proof(source, -5, fn_registry=fn_registry)
    assert bundle3.output_value == -6
    assert len(bundle3.branches) == 2
    assert bundle3.branches[0].path == "else"
    assert bundle3.branches[0].condition_value is False
    assert bundle3.branches[1].path == "else"
    assert bundle3.branches[1].condition_value is False


def test_nested_if_branch_trace_structure():
    """Test branch trace structure for nested IF."""
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
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input 25: both then-branches
    bundle1 = run_program_with_proof(source, 25, fn_registry=fn_registry)
    assert len(bundle1.branches) == 2
    # Outer IF: then branch
    assert bundle1.branches[0].path == "then"
    assert bundle1.branches[0].condition_value is True
    assert bundle1.branches[0].index == 0  # Top-level IF at index 0
    # Inner IF: then branch
    assert bundle1.branches[1].path == "then"
    assert bundle1.branches[1].condition_value is True
    assert bundle1.branches[1].index == -1  # Nested IF uses -1

    # Input 15: outer then, inner else
    bundle2 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert len(bundle2.branches) == 2
    # Outer IF: then branch
    assert bundle2.branches[0].path == "then"
    assert bundle2.branches[0].condition_value is True
    # Inner IF: else branch
    assert bundle2.branches[1].path == "else"
    assert bundle2.branches[1].condition_value is False

    # Input 5: outer else only
    bundle3 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert len(bundle3.branches) == 1
    # Outer IF: else branch
    assert bundle3.branches[0].path == "else"
    assert bundle3.branches[0].condition_value is False
    assert bundle3.branches[0].index == 0


def test_nested_if_proof_determinism():
    """Test that nested IF proof bundles are deterministic."""
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
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Test determinism for input 25
    a = run_program_with_proof(source, 25, fn_registry=fn_registry).to_dict()
    b = run_program_with_proof(source, 25, fn_registry=fn_registry).to_dict()
    assert a == b

    # Test determinism for input 15
    c = run_program_with_proof(source, 15, fn_registry=fn_registry).to_dict()
    d = run_program_with_proof(source, 15, fn_registry=fn_registry).to_dict()
    assert c == d

    # Test determinism for input 5
    e = run_program_with_proof(source, 5, fn_registry=fn_registry).to_dict()
    f = run_program_with_proof(source, 5, fn_registry=fn_registry).to_dict()
    assert e == f

    # Test JSON determinism
    json1 = run_program_with_proof(source, 25, fn_registry=fn_registry).to_json()
    json2 = run_program_with_proof(source, 25, fn_registry=fn_registry).to_json()
    assert json1 == json2


def test_deeply_nested_if_execution():
    """Test execution correctness for deeply nested IF (3 levels)."""
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
    fn_registry = {
        "f1": lambda x: x * 1,
        "f2": lambda x: x * 2,
        "f3": lambda x: x * 3,
        "f4": lambda x: x * 4,
    }

    # Input 5: outer else → f1(5) = 5
    bundle1 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle1.output_value == 5
    assert len(bundle1.branches) == 1
    assert bundle1.branches[0].path == "else"

    # Input 15: outer then, level2 else → f2(15) = 30
    bundle2 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle2.output_value == 30
    assert len(bundle2.branches) == 2
    assert bundle2.branches[0].path == "then"
    assert bundle2.branches[1].path == "else"

    # Input 25: outer then, level2 then, level3 else → f3(25) = 75
    bundle3 = run_program_with_proof(source, 25, fn_registry=fn_registry)
    assert bundle3.output_value == 75
    assert len(bundle3.branches) == 3
    assert bundle3.branches[0].path == "then"
    assert bundle3.branches[1].path == "then"
    assert bundle3.branches[2].path == "else"

    # Input 35: all then branches → f4(35) = 140
    bundle4 = run_program_with_proof(source, 35, fn_registry=fn_registry)
    assert bundle4.output_value == 140
    assert len(bundle4.branches) == 3
    assert all(b.path == "then" for b in bundle4.branches)
    assert all(b.condition_value is True for b in bundle4.branches)


def test_boolean_and_execution_correctness():
    """Test execution correctness for boolean AND operator."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20) {
        inc
    } else {
        dec
    }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input 5: condition False && False = False → dec(5) = 4
    bundle1 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle1.output_value == 4
    assert bundle1.branches[0].condition_value is False

    # Input 15: condition True && True = True → inc(15) = 16
    bundle2 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle2.output_value == 16
    assert bundle2.branches[0].condition_value is True

    # Input 25: condition True && False = False → dec(25) = 24
    bundle3 = run_program_with_proof(source, 25, fn_registry=fn_registry)
    assert bundle3.output_value == 24
    assert bundle3.branches[0].condition_value is False


def test_boolean_or_execution_correctness():
    """Test execution correctness for boolean OR operator."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 20 || __value < 0) {
        inc
    } else {
        dec
    }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input -5: condition False || True = True → inc(-5) = -4
    bundle1 = run_program_with_proof(source, -5, fn_registry=fn_registry)
    assert bundle1.output_value == -4
    assert bundle1.branches[0].condition_value is True

    # Input 10: condition False || False = False → dec(10) = 9
    bundle2 = run_program_with_proof(source, 10, fn_registry=fn_registry)
    assert bundle2.output_value == 9
    assert bundle2.branches[0].condition_value is False

    # Input 25: condition True || False = True → inc(25) = 26
    bundle3 = run_program_with_proof(source, 25, fn_registry=fn_registry)
    assert bundle3.output_value == 26
    assert bundle3.branches[0].condition_value is True


def test_boolean_not_execution_correctness():
    """Test execution correctness for boolean NOT operator."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (!(__value > 10)) {
        inc
    } else {
        dec
    }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input 5: condition !(False) = True → inc(5) = 6
    bundle1 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle1.output_value == 6
    assert bundle1.branches[0].condition_value is True

    # Input 15: condition !(True) = False → dec(15) = 14
    bundle2 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle2.output_value == 14
    assert bundle2.branches[0].condition_value is False


def test_boolean_complex_execution_correctness():
    """Test execution correctness for complex boolean expression."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (!(__value > 10 && __value < 20) || __value == 42) {
        inc
    } else {
        dec
    }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input 5: !(False && False) || False = !False || False = True || False = True → inc(5) = 6
    bundle1 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle1.output_value == 6
    assert bundle1.branches[0].condition_value is True

    # Input 15: !(True && True) || False = !True || False = False || False = False → dec(15) = 14
    bundle2 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle2.output_value == 14
    assert bundle2.branches[0].condition_value is False

    # Input 42: !(True && False) || True = !False || True = True || True = True → inc(42) = 43
    bundle3 = run_program_with_proof(source, 42, fn_registry=fn_registry)
    assert bundle3.output_value == 43
    assert bundle3.branches[0].condition_value is True


def test_if_condition_with_boolean_and():
    """Test IF condition with boolean AND operator."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20) {
        inc
    } else {
        dec
    }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input 5: condition False → dec(5) = 4
    bundle1 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle1.output_value == 4
    assert bundle1.branches[0].path == "else"
    assert bundle1.branches[0].condition_value is False

    # Input 15: condition True → inc(15) = 16
    bundle2 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle2.output_value == 16
    assert bundle2.branches[0].path == "then"
    assert bundle2.branches[0].condition_value is True

    # Input 25: condition False → dec(25) = 24
    bundle3 = run_program_with_proof(source, 25, fn_registry=fn_registry)
    assert bundle3.output_value == 24
    assert bundle3.branches[0].path == "else"
    assert bundle3.branches[0].condition_value is False


def test_if_condition_with_complex_boolean_expression():
    """Test IF condition with complex boolean expression (AND, OR, NOT, parentheses)."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if ((__value > 10 || __value < 0) && __value != 5) {
        inc
    } else {
        dec
    }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input -5: (True || True) && True = True && True = True → inc(-5) = -4
    bundle1 = run_program_with_proof(source, -5, fn_registry=fn_registry)
    assert bundle1.output_value == -4
    assert bundle1.branches[0].path == "then"
    assert bundle1.branches[0].condition_value is True

    # Input 5: (False || False) && False = False && False = False → dec(5) = 4
    bundle2 = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle2.output_value == 4
    assert bundle2.branches[0].path == "else"
    assert bundle2.branches[0].condition_value is False

    # Input 15: (True || False) && True = True && True = True → inc(15) = 16
    bundle3 = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle3.output_value == 16
    assert bundle3.branches[0].path == "then"
    assert bundle3.branches[0].condition_value is True


def test_boolean_condition_branch_trace_differs():
    """Test that boolean conditions produce different branch traces for different outcomes."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20) {
        inc
    } else {
        dec
    }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    # Input 15: condition True → then branch
    bundle_true = run_program_with_proof(source, 15, fn_registry=fn_registry)
    assert bundle_true.branches[0].path == "then"
    assert bundle_true.branches[0].condition_value is True

    # Input 5: condition False → else branch
    bundle_false = run_program_with_proof(source, 5, fn_registry=fn_registry)
    assert bundle_false.branches[0].path == "else"
    assert bundle_false.branches[0].condition_value is False

    # Verify branch records differ
    assert bundle_true.branches[0].path != bundle_false.branches[0].path
    assert bundle_true.branches[0].condition_value != bundle_false.branches[0].condition_value


def test_boolean_condition_proof_determinism():
    """Test that boolean condition proof bundles are deterministic."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20 || !(__value == 0)) {
        inc
    } else {
        dec
    }
}
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "dec": lambda x: x - 1,
    }

    input_value = 15

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Verify dictionaries are identical
    dict1 = bundle1.to_dict()
    dict2 = bundle2.to_dict()
    assert dict1 == dict2

    # Verify JSON is identical
    json1 = bundle1.to_json()
    json2 = bundle2.to_json()
    assert json1 == json2

    # Verify branch records are identical
    assert bundle1.branches == bundle2.branches
    assert len(bundle1.branches) == 1
    assert bundle1.branches[0].path == bundle2.branches[0].path
    assert bundle1.branches[0].condition_value == bundle2.branches[0].condition_value
