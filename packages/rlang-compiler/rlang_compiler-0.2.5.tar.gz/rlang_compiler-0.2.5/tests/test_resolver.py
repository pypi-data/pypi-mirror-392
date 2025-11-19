"""Comprehensive tests for the RLang symbol resolver."""

import pytest

from rlang.parser import FunctionDecl, SimpleType, TypeAlias, parse
from rlang.semantic import (
    PRIMITIVE_TYPES,
    ResolutionError,
    SymbolKind,
    resolve_module,
)


def test_empty_module_has_primitive_types():
    """Test that empty module has only primitive types."""
    source = ""
    module = parse(source)
    result = resolve_module(module)

    # Check that all primitives are in the table
    for primitive_name in PRIMITIVE_TYPES:
        assert primitive_name in result.global_table
        symbol = result.global_table[primitive_name]
        assert symbol.kind == SymbolKind.TYPE
        assert symbol.name == primitive_name


def test_type_alias_registration():
    """Test that type aliases are registered correctly."""
    source = "type UserId = Int;"
    module = parse(source)
    result = resolve_module(module)

    # Check that UserId is in the table
    assert "UserId" in result.global_table
    symbol = result.global_table["UserId"]
    assert symbol.kind == SymbolKind.TYPE
    assert isinstance(symbol.node, TypeAlias)
    assert symbol.node.name == "UserId"

    # Check that type_expr is resolved
    assert symbol.type_expr is not None
    assert isinstance(symbol.type_expr, SimpleType)
    assert symbol.type_expr.name == "Int"


def test_duplicate_type_alias_error():
    """Test that duplicate type aliases raise ResolutionError."""
    source = """
type A = Int;
type A = String;
"""
    module = parse(source)

    with pytest.raises(ResolutionError) as exc_info:
        resolve_module(module)

    assert "Duplicate type alias" in str(exc_info.value)
    assert "A" in str(exc_info.value)


def test_unknown_type_in_alias_raises_error():
    """Test that unknown types in aliases raise ResolutionError."""
    source = "type Foo = UnknownType;"
    module = parse(source)

    with pytest.raises(ResolutionError) as exc_info:
        resolve_module(module)

    assert "Unknown type" in str(exc_info.value)
    assert "UnknownType" in str(exc_info.value)


def test_function_registration_and_type_validation():
    """Test that functions are registered and types are validated."""
    source = "fn add(a: Int, b: Int) -> Int;"
    module = parse(source)
    result = resolve_module(module)

    # Check that function is registered
    assert "add" in result.global_table
    symbol = result.global_table["add"]
    assert symbol.kind == SymbolKind.FUNCTION
    assert isinstance(symbol.node, FunctionDecl)
    assert symbol.node.name == "add"

    # Check parameter types
    assert symbol.params is not None
    assert len(symbol.params) == 2
    assert isinstance(symbol.params[0], SimpleType)
    assert symbol.params[0].name == "Int"
    assert isinstance(symbol.params[1], SimpleType)
    assert symbol.params[1].name == "Int"

    # Check return type
    assert symbol.return_type is not None
    assert isinstance(symbol.return_type, SimpleType)
    assert symbol.return_type.name == "Int"


def test_function_with_unknown_type_raises_error():
    """Test that functions with unknown types raise ResolutionError."""
    source = "fn bad(x: UnknownType) -> Int;"
    module = parse(source)

    with pytest.raises(ResolutionError) as exc_info:
        resolve_module(module)

    assert "Unknown type" in str(exc_info.value)
    assert "UnknownType" in str(exc_info.value)


def test_function_with_unknown_return_type_raises_error():
    """Test that functions with unknown return types raise ResolutionError."""
    source = "fn bad(x: Int) -> UnknownType;"
    module = parse(source)

    with pytest.raises(ResolutionError) as exc_info:
        resolve_module(module)

    assert "Unknown type" in str(exc_info.value)
    assert "UnknownType" in str(exc_info.value)


def test_pipeline_registration_and_type_validation():
    """Test that pipelines are registered and types are validated."""
    source = """
type Input = Int;
type Output = Int;
pipeline main(Input) -> Output {
  step1 -> step2
}
"""
    module = parse(source)
    result = resolve_module(module)

    # Check that pipeline is registered
    assert "main" in result.global_table
    symbol = result.global_table["main"]
    assert symbol.kind == SymbolKind.PIPELINE

    # Check input type
    assert symbol.input_type is not None
    assert isinstance(symbol.input_type, SimpleType)
    assert symbol.input_type.name == "Input"

    # Check output type
    assert symbol.output_type is not None
    assert isinstance(symbol.output_type, SimpleType)
    assert symbol.output_type.name == "Output"


def test_pipeline_with_unknown_input_type():
    """Test that pipelines with unknown input types raise ResolutionError."""
    source = "pipeline main(Unknown) -> Int { step1 }"
    module = parse(source)

    with pytest.raises(ResolutionError) as exc_info:
        resolve_module(module)

    assert "Unknown type" in str(exc_info.value)
    assert "Unknown" in str(exc_info.value)


def test_pipeline_with_unknown_output_type():
    """Test that pipelines with unknown output types raise ResolutionError."""
    source = "pipeline main(Int) -> Unknown { step1 }"
    module = parse(source)

    with pytest.raises(ResolutionError) as exc_info:
        resolve_module(module)

    assert "Unknown type" in str(exc_info.value)
    assert "Unknown" in str(exc_info.value)


def test_duplicate_function_error():
    """Test that duplicate functions raise ResolutionError."""
    source = """
fn add(a: Int, b: Int) -> Int;
fn add(x: String, y: String) -> String;
"""
    module = parse(source)

    with pytest.raises(ResolutionError) as exc_info:
        resolve_module(module)

    assert "Duplicate function" in str(exc_info.value)
    assert "add" in str(exc_info.value)


def test_duplicate_pipeline_error():
    """Test that duplicate pipelines raise ResolutionError."""
    source = """
pipeline main(Int) -> Int { step1 }
pipeline main(String) -> String { step2 }
"""
    module = parse(source)

    with pytest.raises(ResolutionError) as exc_info:
        resolve_module(module)

    assert "Duplicate pipeline" in str(exc_info.value)
    assert "main" in str(exc_info.value)


def test_type_alias_can_reference_other_alias():
    """Test that type aliases can reference other type aliases."""
    source = """
type UserId = Int;
type Email = String;
type User = UserId;
"""
    module = parse(source)
    result = resolve_module(module)

    # Check that all aliases are registered
    assert "UserId" in result.global_table
    assert "Email" in result.global_table
    assert "User" in result.global_table

    # Check that User references UserId
    user_symbol = result.global_table["User"]
    assert user_symbol.type_expr is not None
    assert isinstance(user_symbol.type_expr, SimpleType)
    assert user_symbol.type_expr.name == "UserId"


def test_function_without_return_type():
    """Test function without return type annotation."""
    source = "fn greet(name: String);"
    module = parse(source)
    result = resolve_module(module)

    symbol = result.global_table["greet"]
    assert symbol.kind == SymbolKind.FUNCTION
    assert symbol.return_type is None
    assert len(symbol.params) == 1
    assert symbol.params[0].name == "String"


def test_pipeline_without_types():
    """Test pipeline without input/output types."""
    source = "pipeline run() { step1 -> step2 }"
    module = parse(source)
    result = resolve_module(module)

    symbol = result.global_table["run"]
    assert symbol.kind == SymbolKind.PIPELINE
    assert symbol.input_type is None
    assert symbol.output_type is None


def test_complex_module_resolution():
    """Test resolution of a complex module with multiple declarations."""
    source = """
type UserId = Int;
type Email = String;

fn getUser(id: UserId) -> Email;
fn createUser(email: Email) -> UserId;

pipeline processUsers(Input) -> Output {
  load -> validate -> transform -> save
}

type Input = Int;
type Output = Int;
"""
    module = parse(source)
    result = resolve_module(module)

    # Check all symbols are registered
    assert "UserId" in result.global_table
    assert "Email" in result.global_table
    assert "getUser" in result.global_table
    assert "createUser" in result.global_table
    assert "processUsers" in result.global_table
    assert "Input" in result.global_table
    assert "Output" in result.global_table

    # Check function types
    getUser_symbol = result.global_table["getUser"]
    assert getUser_symbol.params[0].name == "UserId"
    assert getUser_symbol.return_type.name == "Email"

    # Check pipeline types
    pipeline_symbol = result.global_table["processUsers"]
    assert pipeline_symbol.input_type.name == "Input"
    assert pipeline_symbol.output_type.name == "Output"


def test_resolve_nested_if_in_then_branch():
    """Test that resolver handles nested IF in THEN branch correctly."""
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
    result = resolve_module(module)

    # All functions should be resolved
    assert "inc" in result.global_table
    assert "dec" in result.global_table
    assert "main" in result.global_table

    # Pipeline should be registered
    pipeline_symbol = result.global_table["main"]
    assert pipeline_symbol.kind == SymbolKind.PIPELINE


def test_resolve_nested_if_in_else_branch():
    """Test that resolver handles nested IF in ELSE branch correctly."""
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
    result = resolve_module(module)

    # All functions should be resolved
    assert "inc" in result.global_table
    assert "dec" in result.global_table
    assert "main" in result.global_table

    # Pipeline should be registered
    pipeline_symbol = result.global_table["main"]
    assert pipeline_symbol.kind == SymbolKind.PIPELINE


def test_resolve_deeply_nested_if():
    """Test that resolver handles deeply nested IF correctly."""
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
    result = resolve_module(module)

    # All functions should be resolved
    assert "f1" in result.global_table
    assert "f2" in result.global_table
    assert "f3" in result.global_table
    assert "f4" in result.global_table
    assert "main" in result.global_table

    # Pipeline should be registered
    pipeline_symbol = result.global_table["main"]
    assert pipeline_symbol.kind == SymbolKind.PIPELINE

