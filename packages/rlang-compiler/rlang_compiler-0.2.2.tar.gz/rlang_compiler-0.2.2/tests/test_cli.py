"""Comprehensive tests for the RLang CLI."""

import json
import os
from pathlib import Path

import pytest

from rlang.cli import main, run_compiler


def test_cli_compile_to_stdout(tmp_path, capsys):
    """Test compiling a simple program to stdout."""
    src = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    src_path = tmp_path / "prog.rlang"
    src_path.write_text(src.strip() + "\n", encoding="utf-8")

    exit_code = main([str(src_path)])
    assert exit_code == 0

    captured = capsys.readouterr()
    out = captured.out
    assert out.strip()  # some JSON

    data = json.loads(out)
    assert data["entry_pipeline"] == "main"
    assert len(data["step_templates"]) == 1
    assert len(data["pipelines"]) == 1


def test_cli_compile_with_out_to_file(tmp_path, capsys):
    """Test compiling with --out to a file."""
    src = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    src_path = tmp_path / "prog.rlang"
    src_path.write_text(src.strip() + "\n", encoding="utf-8")

    out_path = tmp_path / "prog.json"
    exit_code = main([str(src_path), "--out", str(out_path)])

    assert exit_code == 0
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["entry_pipeline"] == "main"

    # stdout should be empty when --out is used
    captured = capsys.readouterr()
    assert not captured.out.strip()


def test_cli_explicit_entry_override(tmp_path, capsys):
    """Test explicit entry override via CLI."""
    src = """
fn a(x: Int) -> Int;
fn b(x: Int) -> Int;

pipeline first(Int) -> Int {
  a(42)
}

pipeline second(Int) -> Int {
  b(42)
}
"""
    src_path = tmp_path / "prog.rlang"
    src_path.write_text(src.strip() + "\n", encoding="utf-8")

    exit_code = main([str(src_path), "--entry", "second"])
    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["entry_pipeline"] == "second"


def test_cli_nonexistent_file_returns_error(tmp_path, capsys):
    """Test that non-existent file returns error code and prints message to stderr."""
    exit_code = main(["does_not_exist.rlang"])

    assert exit_code != 0
    captured = capsys.readouterr()
    assert "cannot read file" in captured.err.lower()


def test_cli_bad_syntax_returns_error(tmp_path, capsys):
    """Test that bad syntax returns non-zero exit code and message."""
    src = "fn bad( -> Int;"
    src_path = tmp_path / "bad.rlang"
    src_path.write_text(src, encoding="utf-8")

    exit_code = main([str(src_path)])
    assert exit_code != 0

    captured = capsys.readouterr()
    assert "Compilation failed" in captured.err


def test_cli_json_determinism(tmp_path, capsys):
    """Test JSON determinism via CLI."""
    src = """
fn step1(x: Int) -> Int;
fn step2(x: Int) -> Int;

pipeline pipeline1(Int) -> Int {
  step1(42)
}

pipeline pipeline2(Int) -> Int {
  step2(42)
}
"""
    src_path = tmp_path / "prog.rlang"
    src_path.write_text(src.strip() + "\n", encoding="utf-8")

    # Call twice
    exit_code1 = main([str(src_path)])
    assert exit_code1 == 0
    captured1 = capsys.readouterr()
    json1 = captured1.out

    exit_code2 = main([str(src_path)])
    assert exit_code2 == 0
    captured2 = capsys.readouterr()
    json2 = captured2.out

    # Should be exactly equal
    assert json1 == json2


def test_cli_custom_version_and_language(tmp_path, capsys):
    """Test that custom version and language are respected."""
    src = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    src_path = tmp_path / "prog.rlang"
    src_path.write_text(src.strip() + "\n", encoding="utf-8")

    exit_code = main([str(src_path), "--version", "v1.0", "--language", "rlang-v2"])
    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["version"] == "v1.0"
    assert data["language"] == "rlang-v2"


def test_run_compiler_function(tmp_path):
    """Test run_compiler function directly."""
    src = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    src_path = tmp_path / "prog.rlang"
    src_path.write_text(src.strip() + "\n", encoding="utf-8")

    out_path = tmp_path / "output.json"

    exit_code = run_compiler(
        source_path=str(src_path),
        out_path=str(out_path),
    )

    assert exit_code == 0
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["entry_pipeline"] == "main"


def test_run_compiler_with_explicit_entry(tmp_path):
    """Test run_compiler with explicit entry."""
    src = """
fn a(x: Int) -> Int;
fn b(x: Int) -> Int;

pipeline first(Int) -> Int { a(42) }
pipeline second(Int) -> Int { b(42) }
"""
    src_path = tmp_path / "prog.rlang"
    src_path.write_text(src.strip() + "\n", encoding="utf-8")

    out_path = tmp_path / "output.json"

    exit_code = run_compiler(
        source_path=str(src_path),
        entry="second",
        out_path=str(out_path),
    )

    assert exit_code == 0
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["entry_pipeline"] == "second"


def test_run_compiler_file_read_error(tmp_path, capsys):
    """Test run_compiler handles file read errors."""
    nonexistent_path = tmp_path / "nonexistent.rlang"

    exit_code = run_compiler(source_path=str(nonexistent_path))

    assert exit_code != 0
    captured = capsys.readouterr()
    assert "cannot read file" in captured.err.lower()


def test_run_compiler_file_write_error(tmp_path, capsys):
    """Test run_compiler handles file write errors."""
    src = """
fn step1(x: Int) -> Int;

pipeline main(Int) -> Int {
  step1(42)
}
"""
    src_path = tmp_path / "prog.rlang"
    src_path.write_text(src.strip() + "\n", encoding="utf-8")

    # Try to write to a directory (should fail)
    invalid_out = tmp_path / "nonexistent" / "output.json"

    exit_code = run_compiler(
        source_path=str(src_path),
        out_path=str(invalid_out),
    )

    assert exit_code != 0
    captured = capsys.readouterr()
    assert "cannot write output" in captured.err.lower()

