"""Test public API for RLang executor.

Verifies that run_program_with_proof and RLangBoRCrypto are properly exposed
and work correctly from the rlang.bor module.
"""

import pytest

from rlang.bor import run_program_with_proof, RLangBoRCrypto


def test_simple_gt():
    """Test simple if/else pipeline with __value > 10 condition."""
    source = '''
fn ret_0(x: Int) -> Int;
fn ret_1(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        ret_1
    } else {
        ret_0
    }
}
'''

    fn_registry = {
        "ret_0": lambda x: 0,
        "ret_1": lambda x: 1,
    }

    bundle = run_program_with_proof(source, 15, fn_registry=fn_registry)
    
    # Verify output is an integer, not a mock dict
    assert isinstance(bundle.output_value, int)
    assert bundle.output_value == 1
    
    # Verify bundle structure
    assert bundle.entry_pipeline == "main"
    assert bundle.input_value == 15
    assert len(bundle.steps) == 1
    assert bundle.steps[0].step_name == "ret_1"
    assert len(bundle.branches) == 1
    assert bundle.branches[0].path == "then"
    assert bundle.branches[0].condition_value is True
    
    # Test crypto layer
    crypto = RLangBoRCrypto(bundle)
    rich = crypto.to_rich_bundle()
    
    # Verify rich bundle structure
    assert "primary" in rich.rich
    assert "programs" in rich.rich.get("primary", {}) or "master" in rich.rich.get("primary", {})
    assert "H_RICH" in rich.rich
    assert "ir" in rich.rich
    assert "trp" in rich.rich
    assert "input" in rich.rich
    assert "output" in rich.rich


def test_else_branch():
    """Test else branch execution."""
    source = '''
fn ret_0(x: Int) -> Int;
fn ret_1(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        ret_1
    } else {
        ret_0
    }
}
'''

    fn_registry = {
        "ret_0": lambda x: 0,
        "ret_1": lambda x: 1,
    }

    bundle = run_program_with_proof(source, 5, fn_registry=fn_registry)
    
    # Verify output is an integer
    assert isinstance(bundle.output_value, int)
    assert bundle.output_value == 0
    
    # Verify else branch was taken
    assert len(bundle.branches) == 1
    assert bundle.branches[0].path == "else"
    assert bundle.branches[0].condition_value is False


def test_missing_function_raises_error():
    """Test that missing function raises ValueError."""
    source = '''
fn ret_0(x: Int) -> Int;
fn ret_1(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10) {
        ret_1
    } else {
        ret_0
    }
}
'''

    # Missing ret_1 function
    fn_registry = {
        "ret_0": lambda x: 0,
    }

    with pytest.raises(ValueError) as exc_info:
        run_program_with_proof(source, 15, fn_registry=fn_registry)
    
    assert "not found in fn_registry" in str(exc_info.value)


def test_crypto_rich_bundle_structure():
    """Test that RLangBoRCrypto produces correct rich bundle structure."""
    source = '''
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int { inc }
'''

    fn_registry = {
        "inc": lambda x: x + 1,
    }

    bundle = run_program_with_proof(source, 10, fn_registry=fn_registry)
    crypto = RLangBoRCrypto(bundle)
    rich = crypto.to_rich_bundle()
    
    # Verify all required fields are present
    assert hasattr(rich, "primary")
    assert hasattr(rich, "H_RICH")
    assert hasattr(rich, "rich")
    
    # Verify rich dict structure
    assert "primary" in rich.rich
    assert "H_RICH" in rich.rich
    assert "ir" in rich.rich
    assert "trp" in rich.rich
    assert "input" in rich.rich
    assert "output" in rich.rich
    
    # Verify H_RICH is a string (hash)
    assert isinstance(rich.rich["H_RICH"], str)
    assert len(rich.rich["H_RICH"]) == 64  # SHA-256 hex string length
    
    # Verify primary contains master hash
    assert "master" in rich.rich["primary"]
    assert isinstance(rich.rich["primary"]["master"], str)
    assert len(rich.rich["primary"]["master"]) == 64

