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
    """Test that HMASTER computation is correct (from canonical IR)."""
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

    # Compute HMASTER from canonical IR
    HMASTER = crypto.compute_HMASTER()

    # Verify HMASTER matches direct computation from IR JSON
    import hashlib
    ir_json = proof.program_ir.to_json()
    expected_master = hashlib.sha256(ir_json.encode("utf-8")).hexdigest()

    assert HMASTER == expected_master
    assert isinstance(HMASTER, str)
    assert len(HMASTER) == 64  # SHA-256 hex digest length


def test_HRICH_correctness():
    """Test that HRICH computation is correct (from canonical proof bundle)."""
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
    HMASTER = crypto.compute_HMASTER()
    
    # Build proof bundle dict
    primary_data = crypto.build_primary_data(HMASTER)
    trp = crypto.build_trp()
    ir_dict = proof.program_ir.to_dict()
    
    proof_bundle_dict = {
        "primary": primary_data,
        "ir": ir_dict,
        "trp": trp,
        "input": proof.input_value,
        "output": proof.output_value,
        "metadata": {
            "version": proof.version,
            "language": proof.language,
            "entry_pipeline": proof.entry_pipeline,
        },
    }

    # Compute HRICH
    HRICH = crypto.compute_HRICH(proof_bundle_dict)

    # Verify HRICH matches direct computation from proof bundle JSON
    import hashlib
    from rlang.utils.canonical_json import canonical_dumps
    proof_json = canonical_dumps(proof_bundle_dict)
    expected_hrich = hashlib.sha256(proof_json.encode("utf-8")).hexdigest()

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
    
    # Verify TRP contains steps
    assert "trp" in bundle.rich
    trp = bundle.rich["trp"]
    assert "steps" in trp
    assert len(trp["steps"]) == 1
    step_data = trp["steps"][0]
    assert "index" in step_data
    assert "step_name" in step_data
    assert "input_snapshot" in step_data
    assert "output_snapshot" in step_data
    
    # Verify metadata
    assert "metadata" in bundle.rich
    metadata = bundle.rich["metadata"]
    assert metadata["version"] == "v0"
    assert metadata["language"] == "rlang"
    assert metadata["entry_pipeline"] == "main"


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

    # Verify primary contains master
    assert "master" in bundle.primary
    
    # Verify rich bundle contains IR, TRP, input, output
    assert "ir" in bundle.rich
    assert "trp" in bundle.rich
    assert "input" in bundle.rich
    assert "output" in bundle.rich
    assert "metadata" in bundle.rich
    
    # Verify TRP contains steps
    assert "steps" in bundle.rich["trp"]
    assert len(bundle.rich["trp"]["steps"]) == 2


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
    HMASTER = crypto.compute_HMASTER()
    primary_data = crypto.build_primary_data(HMASTER)

    assert primary_data["master"] == HMASTER
    # Primary data now only contains master
    assert len(primary_data) == 1
    
    # Verify rich bundle contains metadata
    bundle = crypto.to_rich_bundle()
    assert bundle.rich["metadata"]["version"] == "v1.0"
    assert bundle.rich["metadata"]["language"] == "rlang-v2"
    assert bundle.rich["metadata"]["entry_pipeline"] == "main"
    
    # Verify TRP contains steps
    assert len(bundle.rich["trp"]["steps"]) == 1
    step_data = bundle.rich["trp"]["steps"][0]
    assert step_data["index"] == 0
    assert "step_name" in step_data
    assert "input_snapshot" in step_data
    assert "output_snapshot" in step_data


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

    # Verify TRP contains all steps
    assert len(bundle.rich["trp"]["steps"]) == 3

    # Verify HMASTER and HRICH are computed
    assert bundle.primary["master"] is not None
    assert bundle.H_RICH is not None

    # Verify step execution records are present
    step_names = [s["step_name"] for s in bundle.rich["trp"]["steps"]]
    assert len(set(step_names)) == 3  # All unique step names


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

    # Verify branch paths in TRP
    assert rich_then.rich["trp"]["branches"][0]["path"] == "then"
    assert rich_else.rich["trp"]["branches"][0]["path"] == "else"

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
    assert "trp" in rich.rich
    assert "branches" in rich.rich["trp"]
    assert len(rich.rich["trp"]["branches"]) == 1
    assert rich.rich["trp"]["branches"][0]["path"] == "then"


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

    # Verify TRP has branches field and is empty
    assert "branches" in rich.rich["trp"]
    assert rich.rich["trp"]["branches"] == []

    # Verify all previously expected keys are still present
    assert "master" in rich.rich["primary"]
    assert "steps" in rich.rich["trp"]
    assert "version" in rich.rich["metadata"]
    assert "language" in rich.rich["metadata"]
    assert "entry_pipeline" in rich.rich["metadata"]

    # Verify TRP structure
    assert "steps" in rich.rich["trp"]
    assert "branches" in rich.rich["trp"]


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

    # Tamper with branch path in TRP
    rich_tampered = rich_original.rich.copy()
    rich_tampered["trp"] = rich_original.rich["trp"].copy()
    rich_tampered["trp"]["branches"] = rich_original.rich["trp"]["branches"].copy()
    rich_tampered["trp"]["branches"][0] = rich_original.rich["trp"]["branches"][0].copy()
    rich_tampered["trp"]["branches"][0]["path"] = "else"  # Changed from "then"

    # Recompute HRICH from tampered data
    from rlang.utils.canonical_json import canonical_dumps
    import hashlib
    proof_json_tampered = canonical_dumps(rich_tampered)
    H_RICH_tampered = hashlib.sha256(proof_json_tampered.encode("utf-8")).hexdigest()

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
    assert rich1.rich["trp"]["branches"] == rich2.rich["trp"]["branches"]
    assert len(rich1.rich["trp"]["branches"]) == 2  # Outer + inner IF


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
    assert len(rich1.rich["trp"]["branches"]) == 3
    assert rich1.rich["trp"]["branches"] == rich2.rich["trp"]["branches"]

    # Verify all branches took "then" path
    assert all(b["path"] == "then" for b in rich1.rich["trp"]["branches"])
    assert all(b["condition_value"] is True for b in rich1.rich["trp"]["branches"])


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
    assert rich_then_then.rich["trp"]["branches"][0]["path"] == "then"
    assert rich_then_then.rich["trp"]["branches"][1]["path"] == "then"

    assert rich_then_else.rich["trp"]["branches"][0]["path"] == "then"
    assert rich_then_else.rich["trp"]["branches"][1]["path"] == "else"

    assert rich_else.rich["trp"]["branches"][0]["path"] == "else"
    assert len(rich_else.rich["trp"]["branches"]) == 1

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
    assert rich1.rich["trp"]["branches"] == rich2.rich["trp"]["branches"]
    assert len(rich1.rich["trp"]["branches"]) == 1


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
    assert rich_true.rich["trp"]["branches"][0]["path"] == "then"
    assert rich_false.rich["trp"]["branches"][0]["path"] == "else"
    assert rich_true.rich["trp"]["branches"][0]["condition_value"] is True
    assert rich_false.rich["trp"]["branches"][0]["condition_value"] is False

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
    assert rich1.rich["trp"]["branches"] == rich2.rich["trp"]["branches"]
    assert len(rich1.rich["trp"]["branches"]) == 1


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

    h_master1 = crypto1.compute_HMASTER()
    h_master2 = crypto2.compute_HMASTER()
    assert h_master1 == h_master2, "H_MASTER should be stable"

    # Build proof bundle dicts for HRICH computation
    bundle1 = crypto1.to_rich_bundle()
    bundle2 = crypto2.to_rich_bundle()
    
    # HRICH should be identical for same input
    assert bundle1.H_RICH == bundle2.H_RICH, "H_RICH should be stable"


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
    h_master_loop = crypto_loop.compute_HMASTER()
    h_master_manual = crypto_manual.compute_HMASTER()
    assert h_master_loop == h_master_manual, "H_MASTER should match"

    # Build rich bundles for HRICH comparison
    bundle_loop = crypto_loop.to_rich_bundle()
    bundle_manual = crypto_manual.to_rich_bundle()
    assert bundle_loop.H_RICH == bundle_manual.H_RICH, "H_RICH should match"


def test_hmaster_independent_of_input():
    """Test that HMASTER is independent of input (same program logic = same HMASTER)."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    fn_registry = {"inc": lambda x: x + 1}
    
    # Run with different inputs
    proof1 = run_program_with_proof(source=src, input_value=10, fn_registry=fn_registry)
    proof2 = run_program_with_proof(source=src, input_value=20, fn_registry=fn_registry)
    proof3 = run_program_with_proof(source=src, input_value=100, fn_registry=fn_registry)
    
    crypto1 = RLangBoRCrypto(proof1)
    crypto2 = RLangBoRCrypto(proof2)
    crypto3 = RLangBoRCrypto(proof3)
    
    hmaster1 = crypto1.compute_HMASTER()
    hmaster2 = crypto2.compute_HMASTER()
    hmaster3 = crypto3.compute_HMASTER()
    
    # HMASTER should be identical for same program logic
    assert hmaster1 == hmaster2 == hmaster3, "HMASTER should be identical for same program logic"


def test_hrich_depends_on_input():
    """Test that HRICH changes when input changes (same program logic, different input)."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    fn_registry = {"inc": lambda x: x + 1}
    
    # Run with different inputs
    proof1 = run_program_with_proof(source=src, input_value=10, fn_registry=fn_registry)
    proof2 = run_program_with_proof(source=src, input_value=20, fn_registry=fn_registry)
    
    crypto1 = RLangBoRCrypto(proof1)
    crypto2 = RLangBoRCrypto(proof2)
    
    bundle1 = crypto1.to_rich_bundle()
    bundle2 = crypto2.to_rich_bundle()
    
    # HMASTER should be identical
    assert bundle1.primary["master"] == bundle2.primary["master"], "HMASTER should be identical"
    
    # HRICH should differ (different input/output)
    assert bundle1.H_RICH != bundle2.H_RICH, "HRICH should differ for different inputs"


def test_hmaster_changes_with_logic():
    """Test that HMASTER changes when program logic changes."""
    src1 = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    src2 = """
fn double(x: Int) -> Int;

pipeline main(Int) -> Int { double }
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "double": lambda x: x * 2,
    }
    
    # Run with same input but different logic
    proof1 = run_program_with_proof(source=src1, input_value=10, fn_registry=fn_registry)
    proof2 = run_program_with_proof(source=src2, input_value=10, fn_registry=fn_registry)
    
    crypto1 = RLangBoRCrypto(proof1)
    crypto2 = RLangBoRCrypto(proof2)
    
    hmaster1 = crypto1.compute_HMASTER()
    hmaster2 = crypto2.compute_HMASTER()
    
    # HMASTER should differ (different program logic)
    assert hmaster1 != hmaster2, "HMASTER should differ for different program logic"


def test_determinism_100_runs():
    """Test that determinism is preserved across 100 repeated runs."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    fn_registry = {"inc": lambda x: x + 1}
    input_value = 42
    
    # Run 100 times
    results = []
    for _ in range(100):
        proof = run_program_with_proof(source=src, input_value=input_value, fn_registry=fn_registry)
        crypto = RLangBoRCrypto(proof)
        bundle = crypto.to_rich_bundle()
        results.append({
            "hmaster": bundle.primary["master"],
            "hrich": bundle.H_RICH,
            "output": proof.output_value,
        })
    
    # All results should be identical
    first_result = results[0]
    for i, result in enumerate(results[1:], 1):
        assert result["hmaster"] == first_result["hmaster"], f"HMASTER differs at run {i+1}"
        assert result["hrich"] == first_result["hrich"], f"HRICH differs at run {i+1}"
        assert result["output"] == first_result["output"], f"Output differs at run {i+1}"


def test_avalanche_effect_logic_change():
    """Test avalanche effect: bitwise difference > 40% when logic changes."""
    src1 = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    src2 = """
fn double(x: Int) -> Int;

pipeline main(Int) -> Int { double }
"""
    fn_registry = {
        "inc": lambda x: x + 1,
        "double": lambda x: x * 2,
    }
    
    proof1 = run_program_with_proof(source=src1, input_value=10, fn_registry=fn_registry)
    proof2 = run_program_with_proof(source=src2, input_value=10, fn_registry=fn_registry)
    
    crypto1 = RLangBoRCrypto(proof1)
    crypto2 = RLangBoRCrypto(proof2)
    
    hmaster1 = crypto1.compute_HMASTER()
    hmaster2 = crypto2.compute_HMASTER()
    
    # Compute bitwise difference
    def bitwise_difference(h1: str, h2: str) -> float:
        """Compute percentage of bits that differ between two hex strings."""
        # Convert hex to binary
        bin1 = bin(int(h1, 16))[2:].zfill(256)  # SHA-256 = 256 bits
        bin2 = bin(int(h2, 16))[2:].zfill(256)
        
        # Count differing bits
        diff_bits = sum(1 for b1, b2 in zip(bin1, bin2) if b1 != b2)
        return (diff_bits / 256) * 100
    
    diff_percent = bitwise_difference(hmaster1, hmaster2)
    
    # Avalanche effect: > 40% of bits should differ
    assert diff_percent > 40, f"Bitwise difference ({diff_percent:.2f}%) should be > 40% for avalanche effect"


def test_same_program_same_input_same_hashes():
    """Test that same program + same input => SAME HMASTER, SAME HRICH."""
    src = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
"""
    fn_registry = {"inc": lambda x: x + 1}
    input_value = 10
    
    # Run twice with same program and input
    proof1 = run_program_with_proof(source=src, input_value=input_value, fn_registry=fn_registry)
    proof2 = run_program_with_proof(source=src, input_value=input_value, fn_registry=fn_registry)
    
    crypto1 = RLangBoRCrypto(proof1)
    crypto2 = RLangBoRCrypto(proof2)
    
    bundle1 = crypto1.to_rich_bundle()
    bundle2 = crypto2.to_rich_bundle()
    
    # HMASTER should be identical
    assert bundle1.primary["master"] == bundle2.primary["master"], "HMASTER should be identical"
    
    # HRICH should be identical
    assert bundle1.H_RICH == bundle2.H_RICH, "HRICH should be identical"
    
    # Output should be identical
    assert proof1.output_value == proof2.output_value, "Output should be identical"
