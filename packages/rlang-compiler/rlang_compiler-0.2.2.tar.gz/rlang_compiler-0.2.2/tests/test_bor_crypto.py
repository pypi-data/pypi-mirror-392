"""Comprehensive tests for RLang → BoR cryptographic integration."""

import json

import pytest

from rlang.bor import RLangBoRCrypto, run_program_with_proof
from rlang.bor.crypto import compute_subproofs, hash_master, hash_step
from rlang.utils.canonical_json import canonical_dumps

# Try to import RichProofBundle, fall back to mock if not available
try:
    from bor.bundle import RichProofBundle
except ImportError:
    from rlang.bor.crypto import RichProofBundle


def test_step_hashing_correctness():
    """Test that step hashing produces correct hashes."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=10,
        fn_registry={"inc": lambda x: x + 1},
    )

    crypto = RLangBoRCrypto(proof)
    step_records = crypto.compute_step_hashes()

    assert len(step_records) == 1

    # Verify step hash matches direct hash computation
    step = proof.steps[0]
    step_dict = step.to_dict()
    expected_hash = hash_step(step_dict)

    assert step_records[0].step_hash == expected_hash
    assert step_records[0].index == 0
    assert step_records[0].template_id == step.template_id


def test_step_hashing_multi_step():
    """Test step hashing for multi-step pipeline."""
    src = """
fn inc(x: Int) -> Int;
fn double(x: Int) -> Int;

pipeline main(Int) -> Int { inc -> double }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry={"inc": lambda x: x + 1, "double": lambda x: x * 2},
    )

    crypto = RLangBoRCrypto(proof)
    step_records = crypto.compute_step_hashes()

    assert len(step_records) == 2

    # Verify each step hash matches direct computation
    for i, step in enumerate(proof.steps):
        step_dict = step.to_dict()
        expected_hash = hash_step(step_dict)
        assert step_records[i].step_hash == expected_hash
        assert step_records[i].index == step.index


def test_HMASTER_correctness():
    """Test that HMASTER computation is correct."""
    src = """
fn step1(x: Int) -> Int;
fn step2(x: Int) -> Int;

pipeline main(Int) -> Int { step1 -> step2 }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=1,
        fn_registry={"step1": lambda x: x + 1, "step2": lambda x: x * 2},
    )

    crypto = RLangBoRCrypto(proof)
    step_records = crypto.compute_step_hashes()

    # Compute HMASTER
    HMASTER = crypto.compute_HMASTER(step_records)

    # Verify HMASTER matches direct computation
    step_hashes = [r.step_hash for r in step_records]
    expected_master = hash_master(step_hashes)

    assert HMASTER == expected_master
    assert isinstance(HMASTER, str)
    assert len(HMASTER) == 64  # SHA-256 hex digest length


def test_HRICH_correctness():
    """Test that HRICH computation is correct."""
    src = """
fn test(x: Int) -> Int;

pipeline main(Int) -> Int { test }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=42,
        fn_registry={"test": lambda x: x},
    )

    crypto = RLangBoRCrypto(proof)
    step_records = crypto.compute_step_hashes()
    HMASTER = crypto.compute_HMASTER(step_records)

    # Compute HRICH
    HRICH = crypto.compute_HRICH(HMASTER)

    # Verify HRICH matches direct computation via subproofs
    from rlang.bor.crypto import compute_subproof_hashes, compute_HRICH_from_subproof_hashes
    subproofs = compute_subproofs(primary_hash=HMASTER)
    subproof_hashes = compute_subproof_hashes(subproofs)
    expected_hrich = compute_HRICH_from_subproof_hashes(subproof_hashes)

    assert HRICH == expected_hrich
    assert isinstance(HRICH, str)
    assert len(HRICH) == 64  # SHA-256 hex digest length


def test_full_rich_bundle_generation():
    """Test complete rich bundle generation."""
    src = """
fn multiply(x: Int) -> Int;

pipeline main(Int) -> Int { multiply }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=7,
        fn_registry={"multiply": lambda x: x * 3},
    )

    crypto = RLangBoRCrypto(proof)
    bundle = crypto.to_rich_bundle()

    assert isinstance(bundle, RichProofBundle)
    assert "H_RICH" in bundle.rich
    assert bundle.rich["H_RICH"] == bundle.H_RICH

    # Verify primary data structure
    assert "primary" in bundle.rich
    primary = bundle.rich["primary"]
    assert "master" in primary
    assert "steps" in primary
    assert primary["version"] == "v0"
    assert primary["language"] == "rlang"
    assert primary["entry_pipeline"] == "main"

    # Verify steps in primary
    assert len(primary["steps"]) == 1
    step_data = primary["steps"][0]
    assert "index" in step_data
    assert "template_id" in step_data
    assert "hash" in step_data


def test_rich_bundle_structure():
    """Test that rich bundle has correct structure."""
    src = """
fn add(x: Int) -> Int;
fn square(x: Int) -> Int;

pipeline main(Int) -> Int { add -> square }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=3,
        fn_registry={"add": lambda x: x + 2, "square": lambda x: x * x},
    )

    crypto = RLangBoRCrypto(proof)
    bundle = crypto.to_rich_bundle()

    # Verify bundle structure
    assert hasattr(bundle, "primary")
    assert hasattr(bundle, "H_RICH")
    assert hasattr(bundle, "rich")

    # Verify rich data contains H_RICH and primary
    assert bundle.rich["H_RICH"] == bundle.H_RICH
    assert bundle.rich["primary"] == bundle.primary

    # Verify primary contains master and steps
    assert "master" in bundle.primary
    assert "steps" in bundle.primary
    assert len(bundle.primary["steps"]) == 2


def test_determinism():
    """Test that same input produces identical rich bundle JSON."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    registry = {"inc": lambda x: x + 1}

    # Generate proof twice
    proof1 = run_program_with_proof(
        source=src,
        input_value=10,
        fn_registry=registry,
    )

    proof2 = run_program_with_proof(
        source=src,
        input_value=10,
        fn_registry=registry,
    )

    # Generate rich bundles
    crypto1 = RLangBoRCrypto(proof1)
    crypto2 = RLangBoRCrypto(proof2)

    bundle1 = crypto1.to_rich_bundle()
    bundle2 = crypto2.to_rich_bundle()

    # Verify deterministic JSON
    json1 = bundle1.to_json()
    json2 = bundle2.to_json()

    assert json1 == json2

    # Verify data structures are identical
    data1 = json.loads(json1)
    data2 = json.loads(json2)

    assert data1 == data2
    assert data1["H_RICH"] == data2["H_RICH"]
    assert data1["primary"]["master"] == data2["primary"]["master"]


def test_hashed_program_structure():
    """Test HashedProgram structure."""
    src = """
fn test(x: Int) -> Int;

pipeline main(Int) -> Int { test }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry={"test": lambda x: x * 2},
    )

    crypto = RLangBoRCrypto(proof)
    hashed = crypto.to_hashed_program()

    assert hashed.HMASTER is not None
    assert hashed.HRICH is not None
    assert len(hashed.step_hashes) == 1
    assert hashed.primary_data["master"] == hashed.HMASTER
    assert hashed.rich_data["H_RICH"] == hashed.HRICH


def test_empty_steps_error():
    """Test that empty proof bundle raises error."""
    from rlang.bor.proofs import PipelineProofBundle
    from rlang.canonical import PrimaryProgramIR

    # Create proof bundle with no steps
    ir = PrimaryProgramIR(
        version="v0",
        language="rlang",
        entry_pipeline="main",
        step_templates=[],
        pipelines=[],
    )

    proof = PipelineProofBundle(
        version="v0",
        language="rlang",
        entry_pipeline="main",
        program_ir=ir,
        input_value=1,
        output_value=1,
        steps=[],
    )

    crypto = RLangBoRCrypto(proof)

    with pytest.raises(ValueError) as exc_info:
        crypto.to_rich_bundle()

    assert "no steps" in str(exc_info.value).lower()


def test_step_hash_record_structure():
    """Test StepHashRecord structure."""
    src = """
fn double(x: Int) -> Int;

pipeline main(Int) -> Int { double }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=21,
        fn_registry={"double": lambda x: x * 2},
    )

    crypto = RLangBoRCrypto(proof)
    step_records = crypto.compute_step_hashes()

    assert len(step_records) == 1
    record = step_records[0]

    assert record.index == 0
    assert record.template_id.startswith("fn:")
    assert isinstance(record.step_hash, str)
    assert len(record.step_hash) == 64  # SHA-256 hex


def test_primary_data_structure():
    """Test that primary data has correct structure."""
    src = """
fn add(x: Int) -> Int;

pipeline main(Int) -> Int { add }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=10,
        fn_registry={"add": lambda x: x + 5},
        version="v1.0",
        language="rlang-v2",
    )

    crypto = RLangBoRCrypto(proof)
    step_records = crypto.compute_step_hashes()
    HMASTER = crypto.compute_HMASTER(step_records)
    primary_data = crypto.build_primary_data(HMASTER, step_records)

    assert primary_data["master"] == HMASTER
    assert primary_data["version"] == "v1.0"
    assert primary_data["language"] == "rlang-v2"
    assert primary_data["entry_pipeline"] == "main"
    assert len(primary_data["steps"]) == 1

    step_data = primary_data["steps"][0]
    assert step_data["index"] == 0
    assert "template_id" in step_data
    assert "hash" in step_data


def test_complex_pipeline_hashing():
    """Test hashing for complex multi-step pipeline."""
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

    proof = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry=registry,
    )

    crypto = RLangBoRCrypto(proof)
    bundle = crypto.to_rich_bundle()

    # Verify all steps are hashed
    assert len(bundle.primary["steps"]) == 3

    # Verify HMASTER and HRICH are computed
    assert bundle.primary["master"] is not None
    assert bundle.H_RICH is not None

    # Verify step hashes are unique
    step_hashes = [s["hash"] for s in bundle.primary["steps"]]
    assert len(set(step_hashes)) == 3  # All unique


def test_rich_bundle_json_serialization():
    """Test that rich bundle can be serialized to JSON."""
    src = """
fn identity(x: Int) -> Int;

pipeline main(Int) -> Int { identity }
"""
    proof = run_program_with_proof(
        source=src,
        input_value=100,
        fn_registry={"identity": lambda x: x},
    )

    crypto = RLangBoRCrypto(proof)
    bundle = crypto.to_rich_bundle()

    # Serialize to JSON
    json_str = bundle.to_json()
    assert isinstance(json_str, str)

    # Parse back
    data = json.loads(json_str)
    assert "H_RICH" in data
    assert "primary" in data
    assert data["primary"]["master"] is not None


def test_hrich_differs_for_different_branches():
    """Test that HRICH differs when different branches are taken."""
    # Program 1: condition true, then-branch
    src_then = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    inc
  } else {
    dec
  }
}
"""

    # Program 2: logically inverted condition (force else)
    src_else = """
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

    # Run both programs with same input
    proof_then = run_program_with_proof(
        source=src_then,
        input_value=10,
        fn_registry=fn_registry,
    )

    proof_else = run_program_with_proof(
        source=src_else,
        input_value=10,
        fn_registry=fn_registry,
    )

    # Build rich bundles
    crypto_then = RLangBoRCrypto(proof_then)
    rich_then = crypto_then.to_rich_bundle()

    crypto_else = RLangBoRCrypto(proof_else)
    rich_else = crypto_else.to_rich_bundle()

    # Extract H_RICH
    H_RICH_then = rich_then.rich["H_RICH"]
    H_RICH_else = rich_else.rich["H_RICH"]

    # Verify branch paths
    assert rich_then.rich["primary"]["branches"][0]["path"] == "then"
    assert rich_else.rich["primary"]["branches"][0]["path"] == "else"

    # Verify HRICH differs
    assert H_RICH_then != H_RICH_else


def test_trp_subproof_contains_branches():
    """Test that TRP subproof contains branch information."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    inc
  }
}
"""

    proof = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry={"inc": lambda x: x + 1},
    )

    crypto = RLangBoRCrypto(proof)
    rich = crypto.to_rich_bundle()

    # Verify TRP exists and contains branches
    assert "TRP" in rich.rich["subproofs"]
    assert "branches" in rich.rich["subproofs"]["TRP"]
    assert len(rich.rich["subproofs"]["TRP"]["branches"]) == 1
    assert rich.rich["subproofs"]["TRP"]["branches"][0]["path"] == "then"


def test_no_if_program_has_empty_branches_and_same_core_structure():
    """Test that programs without if have empty branches and same core structure."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
  inc
}
"""

    proof = run_program_with_proof(
        source=src,
        input_value=10,
        fn_registry={"inc": lambda x: x + 1},
    )

    crypto = RLangBoRCrypto(proof)
    rich = crypto.to_rich_bundle()

    # Verify branches field exists and is empty
    assert "branches" in rich.rich["primary"]
    assert rich.rich["primary"]["branches"] == []

    # Verify TRP has branches field and is empty
    assert "branches" in rich.rich["subproofs"]["TRP"]
    assert rich.rich["subproofs"]["TRP"]["branches"] == []

    # Verify all previously expected keys are still present
    assert "master" in rich.rich["primary"]
    assert "steps" in rich.rich["primary"]
    assert "version" in rich.rich["primary"]
    assert "language" in rich.rich["primary"]
    assert "entry_pipeline" in rich.rich["primary"]

    # Verify TRP structure
    assert "hash" in rich.rich["subproofs"]["TRP"]
    assert "verified" in rich.rich["subproofs"]["TRP"]
    assert "steps" in rich.rich["subproofs"]["TRP"]


def test_branch_tamper_detection():
    """Test that tampering with branch data is detected via HRICH mismatch."""
    src = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    inc
  } else {
    dec
  }
}
"""

    proof = run_program_with_proof(
        source=src,
        input_value=10,
        fn_registry={"inc": lambda x: x + 1, "dec": lambda x: x - 1},
    )

    crypto = RLangBoRCrypto(proof)
    rich_original = crypto.to_rich_bundle()
    H_RICH_original = rich_original.rich["H_RICH"]

    # Tamper with branch path
    rich_tampered = rich_original.rich.copy()
    rich_tampered["primary"] = rich_original.rich["primary"].copy()
    rich_tampered["primary"]["branches"] = rich_original.rich["primary"]["branches"].copy()
    rich_tampered["primary"]["branches"][0] = rich_original.rich["primary"]["branches"][0].copy()
    rich_tampered["primary"]["branches"][0]["path"] = "else"  # Changed from "then"

    # Recompute HRICH from tampered data
    # We need to recompute TRP hash and then HRICH
    rich_tampered["subproofs"] = rich_original.rich["subproofs"].copy()
    rich_tampered["subproofs"]["TRP"] = rich_original.rich["subproofs"]["TRP"].copy()
    rich_tampered["subproofs"]["TRP"]["branches"] = rich_tampered["primary"]["branches"].copy()

    # Recompute TRP hash
    from rlang.bor.crypto import compute_subproof_hashes, compute_HRICH_from_subproof_hashes
    trp_hash_tampered = compute_subproof_hashes({"TRP": rich_tampered["subproofs"]["TRP"]})["TRP"]

    # Recompute HRICH
    rich_tampered["subproof_hashes"] = rich_original.rich["subproof_hashes"].copy()
    rich_tampered["subproof_hashes"]["TRP"] = trp_hash_tampered
    H_RICH_tampered = compute_HRICH_from_subproof_hashes(rich_tampered["subproof_hashes"])

    # Verify HRICH differs
    assert H_RICH_original != H_RICH_tampered


def test_nested_if_IR_canonical_json_stability():
    """Test that nested IF produces stable canonical JSON (H_IR equivalent)."""
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
    from rlang.emitter import compile_source_to_ir

    # Compile twice
    ir1 = compile_source_to_ir(source).program_ir
    ir2 = compile_source_to_ir(source).program_ir

    # Canonical JSON should be identical (H_IR stability)
    json1 = ir1.to_json()
    json2 = ir2.to_json()

    assert json1 == json2

    # Verify IR dictionaries are identical
    assert ir1.to_dict() == ir2.to_dict()


def test_nested_if_HRICH_stability():
    """Test that nested IF produces stable HRICH across multiple runs."""
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

    input_value = 25

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Build rich bundles
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH is identical
    assert rich1.H_RICH == rich2.H_RICH
    assert rich1.rich["H_RICH"] == rich2.rich["H_RICH"]

    # Verify HMASTER is identical
    assert rich1.primary["master"] == rich2.primary["master"]

    # Verify branch records are identical
    assert rich1.rich["primary"]["branches"] == rich2.rich["primary"]["branches"]
    assert len(rich1.rich["primary"]["branches"]) == 2  # Outer + inner IF


def test_nested_if_proof_bundle_canonical_json_stability():
    """Test that nested IF proof bundles produce stable canonical JSON."""
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

    input_value = 25

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Verify proof bundle JSON is identical
    json1 = bundle1.to_json()
    json2 = bundle2.to_json()

    assert json1 == json2

    # Verify proof bundle dictionaries are identical
    dict1 = bundle1.to_dict()
    dict2 = bundle2.to_dict()

    assert dict1 == dict2

    # Verify branch records are identical
    assert dict1["branches"] == dict2["branches"]
    assert len(dict1["branches"]) == 2


def test_deeply_nested_if_HRICH_stability():
    """Test that deeply nested IF (3 levels) produces stable HRICH."""
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

    input_value = 35

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Build rich bundles
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH is identical
    assert rich1.H_RICH == rich2.H_RICH

    # Verify all 3 branch records are present and identical
    assert len(rich1.rich["primary"]["branches"]) == 3
    assert rich1.rich["primary"]["branches"] == rich2.rich["primary"]["branches"]

    # Verify all branches took "then" path
    assert all(b["path"] == "then" for b in rich1.rich["primary"]["branches"])
    assert all(b["condition_value"] is True for b in rich1.rich["primary"]["branches"])


def test_nested_if_HRICH_differs_for_different_branches():
    """Test that HRICH differs when different nested branches are taken."""
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

    # Input 25: outer then, inner then → inc
    bundle_then_then = run_program_with_proof(source, 25, fn_registry=fn_registry)
    crypto_then_then = RLangBoRCrypto(bundle_then_then)
    rich_then_then = crypto_then_then.to_rich_bundle()

    # Input 15: outer then, inner else → dec
    bundle_then_else = run_program_with_proof(source, 15, fn_registry=fn_registry)
    crypto_then_else = RLangBoRCrypto(bundle_then_else)
    rich_then_else = crypto_then_else.to_rich_bundle()

    # Input 5: outer else → dec
    bundle_else = run_program_with_proof(source, 5, fn_registry=fn_registry)
    crypto_else = RLangBoRCrypto(bundle_else)
    rich_else = crypto_else.to_rich_bundle()

    # Verify branch paths
    assert rich_then_then.rich["primary"]["branches"][0]["path"] == "then"
    assert rich_then_then.rich["primary"]["branches"][1]["path"] == "then"

    assert rich_then_else.rich["primary"]["branches"][0]["path"] == "then"
    assert rich_then_else.rich["primary"]["branches"][1]["path"] == "else"

    assert rich_else.rich["primary"]["branches"][0]["path"] == "else"
    assert len(rich_else.rich["primary"]["branches"]) == 1

    # Verify HRICH differs for different branch combinations
    assert rich_then_then.H_RICH != rich_then_else.H_RICH
    assert rich_then_then.H_RICH != rich_else.H_RICH
    assert rich_then_else.H_RICH != rich_else.H_RICH


def test_boolean_ops_IR_canonical_json_stability():
    """Test that boolean operators produce stable canonical JSON (H_IR equivalent)."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20 || !(__value == 15)) {
        inc
    } else {
        dec
    }
}
"""
    from rlang.emitter import compile_source_to_ir

    # Compile twice
    ir1 = compile_source_to_ir(source).program_ir
    ir2 = compile_source_to_ir(source).program_ir

    # Canonical JSON should be identical (H_IR stability)
    json1 = ir1.to_json()
    json2 = ir2.to_json()

    assert json1 == json2

    # Verify IR dictionaries are identical
    assert ir1.to_dict() == ir2.to_dict()


def test_boolean_ops_HRICH_stability():
    """Test that boolean operators produce stable HRICH across multiple runs."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20 || !(__value == 15)) {
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

    input_value = 17

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Build rich bundles
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH is identical
    assert rich1.H_RICH == rich2.H_RICH
    assert rich1.rich["H_RICH"] == rich2.rich["H_RICH"]

    # Verify HMASTER is identical
    assert rich1.primary["master"] == rich2.primary["master"]

    # Verify branch records are identical
    assert rich1.rich["primary"]["branches"] == rich2.rich["primary"]["branches"]
    assert len(rich1.rich["primary"]["branches"]) == 1


def test_boolean_ops_proof_bundle_canonical_json_stability():
    """Test that boolean operator proof bundles produce stable canonical JSON."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20 || !(__value == 15)) {
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

    input_value = 17

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Verify proof bundle JSON is identical
    json1 = bundle1.to_json()
    json2 = bundle2.to_json()

    assert json1 == json2

    # Verify proof bundle dictionaries are identical
    dict1 = bundle1.to_dict()
    dict2 = bundle2.to_dict()

    assert dict1 == dict2

    # Verify branch records are identical
    assert dict1["branches"] == dict2["branches"]
    assert len(dict1["branches"]) == 1


def test_boolean_ops_HRICH_differs_for_different_boolean_paths():
    """Test that HRICH differs when different boolean condition outcomes occur."""
    # Use a simpler condition that can actually be False
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

    # Input 15: condition True (True && True = True) → inc
    bundle_true = run_program_with_proof(source, 15, fn_registry=fn_registry)
    crypto_true = RLangBoRCrypto(bundle_true)
    rich_true = crypto_true.to_rich_bundle()

    # Input 25: condition False (True && False = False) → dec
    bundle_false = run_program_with_proof(source, 25, fn_registry=fn_registry)
    crypto_false = RLangBoRCrypto(bundle_false)
    rich_false = crypto_false.to_rich_bundle()

    # Verify branch paths differ
    assert rich_true.rich["primary"]["branches"][0]["path"] == "then"
    assert rich_false.rich["primary"]["branches"][0]["path"] == "else"
    assert rich_true.rich["primary"]["branches"][0]["condition_value"] is True
    assert rich_false.rich["primary"]["branches"][0]["condition_value"] is False

    # Verify HRICH differs
    assert rich_true.H_RICH != rich_false.H_RICH


def test_boolean_ops_complex_expression_HRICH_stability():
    """Test HRICH stability for complex nested boolean expressions."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;

pipeline main(Int) -> Int {
    if ((__value > 10 || __value < 0) && __value != 5 && !(__value == 15)) {
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

    input_value = 20

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Build rich bundles
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH is identical
    assert rich1.H_RICH == rich2.H_RICH

    # Verify branch records are identical
    assert rich1.rich["primary"]["branches"] == rich2.rich["primary"]["branches"]
    assert len(rich1.rich["primary"]["branches"]) == 1


def test_record_ir_canonical_json_stability():
    """Test that record IR produces stable canonical JSON regardless of source field order."""
    source_a = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { name: "Alice", id: __value }
}
"""

    source_b = """
type User = Record { name: String, id: Int };

pipeline main(Int) -> User {
    { id: __value, name: "Alice" }
}
"""

    from rlang.emitter import compile_source_to_ir

    # Compile both sources
    ir_a = compile_source_to_ir(source_a).program_ir
    ir_b = compile_source_to_ir(source_b).program_ir

    # Canonical JSON should be identical (H_IR stability)
    json_a = ir_a.to_json()
    json_b = ir_b.to_json()

    assert json_a == json_b

    # Verify IR dictionaries are identical
    dict_a = ir_a.to_dict()
    dict_b = ir_b.to_dict()
    assert dict_a == dict_b


def test_record_hash_and_proof_stability():
    """Test that record programs produce stable HRICH/HMASTER across multiple runs."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { name: "Alice", id: __value }
}
"""

    fn_registry = {}

    input_value = 42

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Build rich bundles
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH is identical
    assert rich1.H_RICH == rich2.H_RICH
    assert rich1.rich["H_RICH"] == rich2.rich["H_RICH"]

    # Verify HMASTER is identical
    assert rich1.primary["master"] == rich2.primary["master"]

    # Verify proof bundle JSON is identical
    json1 = bundle1.to_json()
    json2 = bundle2.to_json()
    assert json1 == json2


def test_record_hash_changes_when_field_value_changes():
    """Test that record hash changes when field values change."""
    source1 = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { id: __value, name: "Alice" }
}
"""

    source2 = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { id: __value, name: "Bob" }
}
"""

    fn_registry = {}
    input_value = 10

    bundle1 = run_program_with_proof(source1, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source2, input_value, fn_registry=fn_registry)

    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH differs
    assert rich1.H_RICH != rich2.H_RICH

    # Verify HMASTER differs
    assert rich1.primary["master"] != rich2.primary["master"]


def test_trp_snapshots_include_record_value_deterministically():
    """Test that TRP step snapshots include record values in sorted order."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> User {
    { name: "Alice", id: __value }
}
"""

    fn_registry = {}
    input_value = 7

    proof = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Find the step where the record is produced
    # Look for step with dict output containing id and name
    record_steps = [
        s for s in proof.steps
        if isinstance(s.output_snapshot, dict)
        and set(s.output_snapshot.keys()) == {"id", "name"}
    ]

    assert len(record_steps) > 0, "Expected at least one step with record output"

    rec = record_steps[0].output_snapshot

    # Verify keys are in alphabetical order (id comes before name)
    assert list(rec.keys()) == ["id", "name"]

    # Verify values
    assert rec["id"] == 7
    assert rec["name"] == "Alice"


def test_field_access_hash_stability():
    """Test that field access produces stable HRICH."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(User) -> String {
    __value.name
}
"""

    fn_registry = {}
    input_value = {"id": 42, "name": "Alice"}

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Build rich bundles
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH is identical
    assert rich1.H_RICH == rich2.H_RICH

    # Verify output is correct
    assert bundle1.output_value == "Alice"
    assert bundle2.output_value == "Alice"


def test_records_with_lists_hash_stability():
    """Test that records with list fields produce stable HRICH/HMASTER."""
    source = """
type User = Record { id: Int, tags: List<String> };

pipeline main(Int) -> User {
    { tags: ["low", "mid", "high"], id: __value }
}
"""

    fn_registry = {}
    input_value = 5

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Build rich bundles
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH is identical
    assert rich1.H_RICH == rich2.H_RICH
    assert rich1.rich["H_RICH"] == rich2.rich["H_RICH"]

    # Verify HMASTER is identical
    assert rich1.primary["master"] == rich2.primary["master"]

    # Verify proof bundle JSON is identical
    json1 = bundle1.to_json()
    json2 = bundle2.to_json()
    assert json1 == json2

    # Verify IR canonical JSON is identical
    from rlang.emitter import compile_source_to_ir
    ir1 = compile_source_to_ir(source).program_ir
    ir2 = compile_source_to_ir(source).program_ir
    assert ir1.to_json() == ir2.to_json()


def test_list_of_records_hash_stability():
    """Test that list of records produces stable HRICH/HMASTER."""
    source = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> List<User> {
    [
        { name: "Alice", id: __value },
        { name: "Bob",   id: __value + 1 }
    ]
}
"""

    fn_registry = {}
    input_value = 10

    # Generate proof bundles twice
    bundle1 = run_program_with_proof(source, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Build rich bundles
    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH is identical
    assert rich1.H_RICH == rich2.H_RICH

    # Verify HMASTER is identical
    assert rich1.primary["master"] == rich2.primary["master"]

    # Verify output is correct
    assert isinstance(bundle1.output_value, list)
    assert len(bundle1.output_value) == 2
    assert bundle1.output_value[0]["id"] == 10
    assert bundle1.output_value[0]["name"] == "Alice"
    assert bundle1.output_value[1]["id"] == 11
    assert bundle1.output_value[1]["name"] == "Bob"


def test_list_of_records_hash_difference():
    """Test that changing an inner field value changes the hash."""
    source1 = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> List<User> {
    [
        { id: __value, name: "Alice" },
        { id: __value + 1, name: "Bob" }
    ]
}
"""

    source2 = """
type User = Record { id: Int, name: String };

pipeline main(Int) -> List<User> {
    [
        { id: __value, name: "Alice" },
        { id: __value + 1, name: "Charlie" }
    ]
}
"""

    fn_registry = {}
    input_value = 10

    bundle1 = run_program_with_proof(source1, input_value, fn_registry=fn_registry)
    bundle2 = run_program_with_proof(source2, input_value, fn_registry=fn_registry)

    crypto1 = RLangBoRCrypto(bundle1)
    crypto2 = RLangBoRCrypto(bundle2)

    rich1 = crypto1.to_rich_bundle()
    rich2 = crypto2.to_rich_bundle()

    # Verify HRICH differs
    assert rich1.H_RICH != rich2.H_RICH

    # Verify HMASTER differs
    assert rich1.primary["master"] != rich2.primary["master"]


def test_trp_snapshots_with_nested_records_and_lists():
    """Test that TRP snapshots include nested records and lists deterministically."""
    source = """
type User = Record { id: Int, name: String };
type Report = Record {
    users: List<User>,
    count: Int
};

pipeline main(Int) -> Report {
    {
        users: [
            { id: __value,     name: "A" },
            { id: __value + 1, name: "B" }
        ],
        count: 2
    }
}
"""

    fn_registry = {}
    input_value = 10

    proof = run_program_with_proof(source, input_value, fn_registry=fn_registry)

    # Find the step where the final output is stored
    # Look for step with dict output containing count and users
    record_steps = [
        s for s in proof.steps
        if isinstance(s.output_snapshot, dict)
        and "count" in s.output_snapshot
        and "users" in s.output_snapshot
    ]

    assert len(record_steps) > 0, "Expected at least one step with record output"

    rec = record_steps[0].output_snapshot

    # Verify keys are in alphabetical order (count comes before users)
    assert list(rec.keys()) == ["count", "users"]

    # Verify count value
    assert rec["count"] == 2

    # Verify users is a list
    assert isinstance(rec["users"], list)
    assert len(rec["users"]) == 2

    # Verify each user record has sorted keys
    user1 = rec["users"][0]
    assert list(user1.keys()) == ["id", "name"]  # alphabetical order
    assert user1["id"] == 10
    assert user1["name"] == "A"

    user2 = rec["users"][1]
    assert list(user2.keys()) == ["id", "name"]  # alphabetical order
    assert user2["id"] == 11
    assert user2["name"] == "B"


def test_for_loop_hash_stability():
    """Test that for loop produces stable hashes across multiple runs."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
  for i in 0 .. 3 {
    inc
  }
}
"""
    # Run twice and compare hashes
    proof1 = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry={"inc": lambda x: x + 1},
    )
    proof2 = run_program_with_proof(
        source=src,
        input_value=5,
        fn_registry={"inc": lambda x: x + 1},
    )

    crypto1 = RLangBoRCrypto(proof1)
    crypto2 = RLangBoRCrypto(proof2)

    # Compare canonical JSON (H_IR equivalent)
    json1 = proof1.program_ir.to_json()
    json2 = proof2.program_ir.to_json()
    assert json1 == json2, "H_IR (canonical JSON) should be stable"

    step_records1 = crypto1.compute_step_hashes()
    step_records2 = crypto2.compute_step_hashes()
    h_master1 = crypto1.compute_HMASTER(step_records1)
    h_master2 = crypto2.compute_HMASTER(step_records2)
    assert h_master1 == h_master2, "H_MASTER should be stable"

    h_rich1 = crypto1.compute_HRICH(h_master1)
    h_rich2 = crypto2.compute_HRICH(h_master2)
    assert h_rich1 == h_rich2, "H_RICH should be stable"


def test_for_loop_same_as_unrolled_manual_pipeline():
    """Test that for loop produces same IR and hashes as manually unrolled pipeline."""
    src_with_loop = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
  for i in 0 .. 3 {
    inc
  }
}
"""

    src_manual = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
  inc -> inc -> inc
}
"""

    # Compile both
    from rlang.emitter import compile_source_to_ir

    result_loop = compile_source_to_ir(src_with_loop)
    result_manual = compile_source_to_ir(src_manual)

    # Compare IR canonical JSON
    ir_json_loop = result_loop.program_ir.to_json()
    ir_json_manual = result_manual.program_ir.to_json()
    assert ir_json_loop == ir_json_manual, "IR should match between loop and manual unrolling"

    # Compare proof hashes for same input
    proof_loop = run_program_with_proof(
        source=src_with_loop,
        input_value=5,
        fn_registry={"inc": lambda x: x + 1},
    )
    proof_manual = run_program_with_proof(
        source=src_manual,
        input_value=5,
        fn_registry={"inc": lambda x: x + 1},
    )

    crypto_loop = RLangBoRCrypto(proof_loop)
    crypto_manual = RLangBoRCrypto(proof_manual)

    # H_IR comparison already done above via JSON comparison
    step_records_loop = crypto_loop.compute_step_hashes()
    step_records_manual = crypto_manual.compute_step_hashes()
    h_master_loop = crypto_loop.compute_HMASTER(step_records_loop)
    h_master_manual = crypto_manual.compute_HMASTER(step_records_manual)
    assert h_master_loop == h_master_manual, "H_MASTER should match"

    h_rich_loop = crypto_loop.compute_HRICH(h_master_loop)
    h_rich_manual = crypto_manual.compute_HRICH(h_master_manual)
    assert h_rich_loop == h_rich_manual, "H_RICH should match"
