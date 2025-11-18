"""Comprehensive tests for branch determinism and HRICH sensitivity."""

import pytest

from rlang.bor import RLangBoRCrypto, run_program_with_proof


def test_hrich_differs_for_then_else_paths():
    """Test that HRICH differs when different branch paths are taken."""
    # Use different source programs with different conditions to force different branches
    source_then = """
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

    source_else = """
fn double(x: Int) -> Int;
fn half(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 2) {
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

    # Run with condition true (1 == 1) - takes then branch
    proof_then = run_program_with_proof(
        source=source_then,
        input_value=10,
        fn_registry=fn_registry,
    )

    # Run with condition false (1 == 2) - takes else branch
    proof_else = run_program_with_proof(
        source=source_else,
        input_value=10,
        fn_registry=fn_registry,
    )

    # Build rich bundles
    crypto_else = RLangBoRCrypto(proof_else)
    rich_else = crypto_else.to_rich_bundle()

    crypto_then = RLangBoRCrypto(proof_then)
    rich_then = crypto_then.to_rich_bundle()

    # Extract H_RICH
    H_RICH_else = rich_else.rich["H_RICH"]
    H_RICH_then = rich_then.rich["H_RICH"]

    # Verify branch paths
    assert rich_else.rich["primary"]["branches"][0]["path"] == "else"
    assert rich_then.rich["primary"]["branches"][0]["path"] == "then"

    # Verify HRICH differs
    assert H_RICH_else != H_RICH_then, "HRICH should differ for different branch paths"


def test_branch_execution_record_correctness():
    """Test that BranchExecutionRecord correctly captures branch execution."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 1) {
    inc
  }
}
"""

    fn_registry = {"inc": lambda x: x + 1}

    # Test with condition true (1 == 1)
    proof_true = run_program_with_proof(
        source=source,
        input_value=10,
        fn_registry=fn_registry,
    )

    # Verify exactly one branch record
    assert len(proof_true.branches) == 1

    branch = proof_true.branches[0]
    assert branch.path == "then"
    assert branch.condition_value is True
    assert branch.index == 0

    # Test with condition false (1 == 2)
    source_false = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 2) {
    inc
  }
}
"""

    proof_false = run_program_with_proof(
        source=source_false,
        input_value=10,
        fn_registry=fn_registry,
    )

    # Verify exactly one branch record
    assert len(proof_false.branches) == 1

    branch = proof_false.branches[0]
    # When condition is false and no explicit else, path is recorded as "else"
    # (implicit identity else branch)
    assert branch.path == "else"
    assert branch.condition_value is False
    assert branch.index == 0


def test_branch_execution_record_with_explicit_else():
    """Test BranchExecutionRecord with explicit else branch."""
    source_then = """
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

    source_else = """
fn double(x: Int) -> Int;
fn half(x: Int) -> Int;

pipeline main(Int) -> Int {
  if (1 == 2) {
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

    # Test then branch (condition true)
    proof_then = run_program_with_proof(
        source=source_then,
        input_value=10,
        fn_registry=fn_registry,
    )

    assert len(proof_then.branches) == 1
    branch = proof_then.branches[0]
    assert branch.path == "then"
    assert branch.condition_value is True

    # Test else branch (condition false)
    proof_else = run_program_with_proof(
        source=source_else,
        input_value=10,
        fn_registry=fn_registry,
    )

    assert len(proof_else.branches) == 1
    branch = proof_else.branches[0]
    assert branch.path == "else"
    assert branch.condition_value is False

