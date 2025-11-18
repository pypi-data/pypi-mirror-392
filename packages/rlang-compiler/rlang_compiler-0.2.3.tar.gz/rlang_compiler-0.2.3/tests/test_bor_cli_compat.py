"""Tests for RLang → BoR CLI compatibility (borp verify-bundle)."""

import json
import subprocess
from pathlib import Path

import pytest

from rlang.bor import RLangBoRCrypto, run_program_with_proof


def test_rich_bundle_passes_borp_verify(tmp_path):
    """Test that RLang-generated rich bundle passes borp verify-bundle."""
    src = """
fn inc(x: Int) -> Int;
fn double(x: Int) -> Int;

pipeline main(Int) -> Int { inc -> double }
"""

    bundle = run_program_with_proof(
        source=src,
        input_value=10,
        fn_registry={"inc": lambda x: x + 1, "double": lambda x: x * 2},
    )
    crypto = RLangBoRCrypto(bundle)
    rich = crypto.to_rich_bundle()

    # Serialize to a temp file
    out_file = tmp_path / "rich_from_rlang.json"
    out_file.write_text(json.dumps(rich.rich, indent=2), encoding="utf-8")

    # Call borp verify-bundle
    proc = subprocess.Popen(
        ["borp", "verify-bundle", "--bundle", str(out_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate()

    # Debug prints (useful for development)
    if proc.returncode != 0:
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

    # Expect success (ok: true, VERIFIED)
    assert proc.returncode == 0, f"borp verify-bundle failed: {stderr}"
    assert "[BoR RICH] VERIFIED" in stdout or "[BoR RICH] VERIFIED" in stderr
    assert '"ok": true' in stdout or '"ok": true' in stderr


def test_determinism_on_cli_level(tmp_path):
    """Test that same input produces identical bundles that both verify."""
    src = """
fn multiply(x: Int) -> Int;

pipeline main(Int) -> Int { multiply }
"""

    registry = {"multiply": lambda x: x * 3}

    # Generate two bundles from same source and input
    proof1 = run_program_with_proof(
        source=src,
        input_value=7,
        fn_registry=registry,
    )

    proof2 = run_program_with_proof(
        source=src,
        input_value=7,
        fn_registry=registry,
    )

    crypto1 = RLangBoRCrypto(proof1)
    crypto2 = RLangBoRCrypto(proof2)

    bundle1 = crypto1.to_rich_bundle()
    bundle2 = crypto2.to_rich_bundle()

    # Write both to temp files
    file1 = tmp_path / "bundle1.json"
    file2 = tmp_path / "bundle2.json"

    file1.write_text(json.dumps(bundle1.rich, indent=2), encoding="utf-8")
    file2.write_text(json.dumps(bundle2.rich, indent=2), encoding="utf-8")

    # Verify both bundles
    proc1 = subprocess.Popen(
        ["borp", "verify-bundle", "--bundle", str(file1)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout1, stderr1 = proc1.communicate()

    proc2 = subprocess.Popen(
        ["borp", "verify-bundle", "--bundle", str(file2)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout2, stderr2 = proc2.communicate()

    # Both should verify successfully
    assert proc1.returncode == 0, f"Bundle 1 verification failed: {stderr1}"
    assert proc2.returncode == 0, f"Bundle 2 verification failed: {stderr2}"

    # Both should have identical HRICH
    assert bundle1.H_RICH == bundle2.H_RICH
    assert bundle1.rich["H_RICH"] == bundle2.rich["H_RICH"]


def test_rich_bundle_has_required_fields():
    """Test that rich bundle contains all required fields for verification."""
    src = """
fn square(x: Int) -> Int;

pipeline main(Int) -> Int { square }
"""

    proof = run_program_with_proof(
        source=src,
        input_value=9,
        fn_registry={"square": lambda x: x * x},
    )

    crypto = RLangBoRCrypto(proof)
    bundle = crypto.to_rich_bundle()

    rich = bundle.rich

    # Required fields for borp verify-bundle
    assert "H_RICH" in rich
    assert "primary" in rich
    assert "subproofs" in rich
    assert "subproof_hashes" in rich

    # Verify subproofs structure
    subproofs = rich["subproofs"]
    assert isinstance(subproofs, dict)
    assert "DIP" in subproofs
    assert "DP" in subproofs
    assert "PEP" in subproofs
    assert "PoPI" in subproofs
    assert "CCP" in subproofs
    assert "CMIP" in subproofs
    assert "PP" in subproofs
    assert "TRP" in subproofs

    # Verify subproof_hashes structure
    subproof_hashes = rich["subproof_hashes"]
    assert isinstance(subproof_hashes, dict)
    assert len(subproof_hashes) == 8
    assert all(isinstance(v, str) and len(v) == 64 for v in subproof_hashes.values())


def test_complex_pipeline_cli_verification(tmp_path):
    """Test CLI verification for complex multi-step pipeline."""
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

    # Write to temp file
    out_file = tmp_path / "complex_bundle.json"
    out_file.write_text(json.dumps(bundle.rich, indent=2), encoding="utf-8")

    # Verify with borp
    proc = subprocess.Popen(
        ["borp", "verify-bundle", "--bundle", str(out_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate()

    assert proc.returncode == 0, f"Verification failed: {stderr}"
    assert "[BoR RICH] VERIFIED" in stdout or "[BoR RICH] VERIFIED" in stderr
    assert '"ok": true' in stdout or '"ok": true' in stderr


def test_subproof_hashes_match_subproofs():
    """Test that subproof_hashes correctly hash the subproofs."""
    src = """
fn test(x: Int) -> Int;

pipeline main(Int) -> Int { test }
"""

    proof = run_program_with_proof(
        source=src,
        input_value=1,
        fn_registry={"test": lambda x: x},
    )

    crypto = RLangBoRCrypto(proof)
    bundle = crypto.to_rich_bundle()

    rich = bundle.rich
    subproofs = rich["subproofs"]
    subproof_hashes = rich["subproof_hashes"]

    # Verify each subproof hash matches the hash of its subproof
    import hashlib

    for key in subproofs.keys():
        subproof_data = subproofs[key]
        # Hash the subproof using the same method as compute_subproof_hashes
        import json

        subproof_json = json.dumps(subproof_data, separators=(",", ":"), sort_keys=True)
        expected_hash = hashlib.sha256(subproof_json.encode("utf-8")).hexdigest()

        assert key in subproof_hashes
        assert subproof_hashes[key] == expected_hash


def test_hrich_matches_subproof_hashes():
    """Test that H_RICH correctly aggregates subproof_hashes."""
    src = """
fn identity(x: Int) -> Int;

pipeline main(Int) -> Int { identity }
"""

    proof = run_program_with_proof(
        source=src,
        input_value=42,
        fn_registry={"identity": lambda x: x},
    )

    crypto = RLangBoRCrypto(proof)
    bundle = crypto.to_rich_bundle()

    rich = bundle.rich
    H_RICH = rich["H_RICH"]
    subproof_hashes = rich["subproof_hashes"]

    # Compute expected H_RICH from subproof_hashes
    import hashlib

    sorted_hashes = [subproof_hashes[k] for k in sorted(subproof_hashes.keys())]
    combined = "|".join(sorted_hashes)
    expected_hrich = hashlib.sha256(combined.encode("utf-8")).hexdigest()

    assert H_RICH == expected_hrich
    assert bundle.H_RICH == H_RICH

