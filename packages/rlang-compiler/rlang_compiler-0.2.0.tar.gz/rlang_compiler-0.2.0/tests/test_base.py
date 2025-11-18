"""Tests for base test utilities to ensure they work correctly."""

import json
from pathlib import Path

import pytest

from tests.base import (
    assert_ast_equal,
    assert_ir_equal,
    assert_json_equal,
    assert_schema_equal,
    load_json_file,
    tempdir,
    write_json_file,
)


def test_tempdir_fixture(tempdir):
    """Test that tempdir fixture provides a working directory."""
    assert tempdir.exists()
    assert tempdir.is_dir()
    
    test_file = tempdir / "test.txt"
    test_file.write_text("hello")
    assert test_file.read_text() == "hello"


def test_assert_json_equal_success():
    """Test assert_json_equal with equal objects."""
    assert_json_equal({"a": 1, "b": 2}, {"b": 2, "a": 1})
    assert_json_equal(1.0, 1)
    assert_json_equal([1, 2, 3], [1, 2, 3])
    assert_json_equal(None, None)


def test_assert_json_equal_failure():
    """Test assert_json_equal raises on unequal objects."""
    with pytest.raises(AssertionError):
        assert_json_equal({"a": 1}, {"a": 2})
    
    with pytest.raises(AssertionError):
        assert_json_equal([1, 2], [1, 2, 3])


def test_assert_ast_equal():
    """Test assert_ast_equal delegates correctly."""
    assert_ast_equal({"type": "Literal", "value": 42}, {"type": "Literal", "value": 42})
    
    with pytest.raises(AssertionError):
        assert_ast_equal({"type": "Literal"}, {"type": "Variable"})


def test_assert_ir_equal():
    """Test assert_ir_equal delegates correctly."""
    assert_ir_equal({"op": "add", "args": [1, 2]}, {"op": "add", "args": [1, 2]})
    
    with pytest.raises(AssertionError):
        assert_ir_equal({"op": "add"}, {"op": "sub"})


def test_assert_schema_equal():
    """Test assert_schema_equal delegates correctly."""
    assert_schema_equal({"fields": ["a", "b"]}, {"fields": ["a", "b"]})
    
    with pytest.raises(AssertionError):
        assert_schema_equal({"fields": ["a"]}, {"fields": ["b"]})


def test_load_json_file(tempdir):
    """Test loading JSON from file."""
    json_file = tempdir / "test.json"
    json_file.write_text('{"a": 1, "b": 2}')
    
    data = load_json_file(json_file)
    assert data == {"a": 1, "b": 2}


def test_write_json_file(tempdir):
    """Test writing canonical JSON to file."""
    json_file = tempdir / "output.json"
    data = {"b": 2, "a": 1}
    
    write_json_file(json_file, data)
    
    assert json_file.exists()
    content = json_file.read_text()
    # Should be canonical (sorted keys)
    assert '"a":' in content
    assert '"b":' in content
    # Verify it's valid JSON
    loaded = json.loads(content)
    assert loaded == {"a": 1, "b": 2}

