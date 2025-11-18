"""Comprehensive tests for the RLang parser."""

import pytest

from rlang.parser import (
    Call,
    FunctionDecl,
    Identifier,
    IfExpr,
    Literal,
    Module,
    Param,
    ParseError,
    PipelineDecl,
    PipelineStep,
    SimpleType,
    TypeAlias,
    parse,
)


def test_parse_empty_module():
    """Test parsing an empty module."""
    source = ""
    module = parse(source)

    assert isinstance(module, Module)
    assert len(module.decls) == 0


def test_parse_simple_type_alias():
    """Test parsing a simple type alias."""
    source = "type UserId = Int;"
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert isinstance(decl, TypeAlias)
    assert decl.name == "UserId"
    assert isinstance(decl.target, SimpleType)
    assert decl.target.name == "Int"


def test_parse_multiple_type_aliases():
    """Test parsing multiple type aliases."""
    source = """
type UserId = Int;
type Email = String;
"""
    module = parse(source)

    assert len(module.decls) == 2
    assert isinstance(module.decls[0], TypeAlias)
    assert module.decls[0].name == "UserId"
    assert isinstance(module.decls[1], TypeAlias)
    assert module.decls[1].name == "Email"


def test_parse_simple_function_signature():
    """Test parsing a simple function signature."""
    source = "fn add(a: Int, b: Int) -> Int;"
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert isinstance(decl, FunctionDecl)
    assert decl.name == "add"
    assert len(decl.params) == 2

    param1 = decl.params[0]
    assert isinstance(param1, Param)
    assert param1.name == "a"
    assert isinstance(param1.type, SimpleType)
    assert param1.type.name == "Int"

    param2 = decl.params[1]
    assert isinstance(param2, Param)
    assert param2.name == "b"
    assert isinstance(param2.type, SimpleType)
    assert param2.type.name == "Int"

    assert isinstance(decl.return_type, SimpleType)
    assert decl.return_type.name == "Int"


def test_parse_function_without_return_type():
    """Test parsing a function without return type."""
    source = "fn greet(name: String);"
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert isinstance(decl, FunctionDecl)
    assert decl.name == "greet"
    assert len(decl.params) == 1
    assert decl.return_type is None


def test_parse_function_without_params():
    """Test parsing a function without parameters."""
    source = "fn getValue() -> Int;"
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert isinstance(decl, FunctionDecl)
    assert decl.name == "getValue"
    assert len(decl.params) == 0
    assert isinstance(decl.return_type, SimpleType)
    assert decl.return_type.name == "Int"


def test_parse_simple_pipeline():
    """Test parsing a simple pipeline."""
    source = """
pipeline main(Input) -> Output {
  validate -> transform -> persist
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert isinstance(decl, PipelineDecl)
    assert decl.name == "main"
    assert isinstance(decl.input_type, SimpleType)
    assert decl.input_type.name == "Input"
    assert isinstance(decl.output_type, SimpleType)
    assert decl.output_type.name == "Output"
    assert len(decl.steps) == 3

    assert decl.steps[0].name == "validate"
    assert len(decl.steps[0].args) == 0

    assert decl.steps[1].name == "transform"
    assert len(decl.steps[1].args) == 0

    assert decl.steps[2].name == "persist"
    assert len(decl.steps[2].args) == 0


def test_parse_pipeline_without_types():
    """Test parsing a pipeline without input/output types."""
    source = """
pipeline run() {
  step1 -> step2
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert isinstance(decl, PipelineDecl)
    assert decl.name == "run"
    assert decl.input_type is None
    assert decl.output_type is None
    assert len(decl.steps) == 2


def test_parse_pipeline_with_step_arguments():
    """Test parsing a pipeline with step arguments."""
    source = """
pipeline run(Input) -> Output {
  load("file.json") -> normalize(42, "x")
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert isinstance(decl, PipelineDecl)
    assert len(decl.steps) == 2

    # First step: load("file.json")
    step1 = decl.steps[0]
    assert step1.name == "load"
    assert len(step1.args) == 1
    assert isinstance(step1.args[0], Literal)
    assert step1.args[0].value == "file.json"

    # Second step: normalize(42, "x")
    step2 = decl.steps[1]
    assert step2.name == "normalize"
    assert len(step2.args) == 2
    assert isinstance(step2.args[0], Literal)
    assert step2.args[0].value == 42
    assert isinstance(step2.args[1], Literal)
    assert step2.args[1].value == "x"


def test_parse_pipeline_with_identifier_arguments():
    """Test parsing a pipeline step with identifier arguments."""
    source = """
pipeline process(Data) -> Result {
  transform(x, y) -> output(result)
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert len(decl.steps) == 2

    step1 = decl.steps[0]
    assert step1.name == "transform"
    assert len(step1.args) == 2
    assert isinstance(step1.args[0], Identifier)
    assert step1.args[0].name == "x"
    assert isinstance(step1.args[1], Identifier)
    assert step1.args[1].name == "y"

    step2 = decl.steps[1]
    assert step2.name == "output"
    assert len(step2.args) == 1
    assert isinstance(step2.args[0], Identifier)
    assert step2.args[0].name == "result"


def test_parse_literals():
    """Test parsing various literal expressions."""
    source = """
pipeline test() {
  step(42, 3.14, "hello", true, false, null)
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    step = decl.steps[0]
    assert len(step.args) == 6

    assert isinstance(step.args[0], Literal)
    assert step.args[0].value == 42

    assert isinstance(step.args[1], Literal)
    assert step.args[1].value == 3.14

    assert isinstance(step.args[2], Literal)
    assert step.args[2].value == "hello"

    assert isinstance(step.args[3], Literal)
    assert step.args[3].value is True

    assert isinstance(step.args[4], Literal)
    assert step.args[4].value is False

    assert isinstance(step.args[5], Literal)
    assert step.args[5].value is None


def test_parse_binary_operations():
    """Test parsing binary operations in expressions."""
    source = """
pipeline calc() {
  compute(1 + 2, 3 * 4, 10 / 2)
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    step = decl.steps[0]
    assert len(step.args) == 3

    # All args should be Call expressions (function calls)
    # Actually, wait - the parser should parse these as BinaryOp
    # Let me check what the parser actually produces
    from rlang.parser import BinaryOp

    # The args should be BinaryOp expressions
    assert isinstance(step.args[0], BinaryOp)
    assert step.args[0].op == "+"

    assert isinstance(step.args[1], BinaryOp)
    assert step.args[1].op == "*"

    assert isinstance(step.args[2], BinaryOp)
    assert step.args[2].op == "/"


def test_parse_nested_calls():
    """Test parsing nested function calls."""
    source = """
pipeline test() {
  process(transform(data))
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    step = decl.steps[0]
    assert len(step.args) == 1

    # The argument should be a Call
    arg = step.args[0]
    assert isinstance(arg, Call)
    assert isinstance(arg.func, Identifier)
    assert arg.func.name == "transform"
    assert len(arg.args) == 1
    assert isinstance(arg.args[0], Identifier)
    assert arg.args[0].name == "data"


def test_parse_error_missing_semicolon():
    """Test that missing semicolon raises ParseError."""
    with pytest.raises(ParseError) as exc_info:
        parse("type UserId = Int")  # Missing semicolon

    assert "Expected" in str(exc_info.value) or "semicolon" in str(exc_info.value).lower()


def test_parse_error_invalid_syntax():
    """Test that invalid syntax raises ParseError."""
    with pytest.raises(ParseError) as exc_info:
        parse("fn bad( -> Int;")  # Missing parameter

    assert "Expected" in str(exc_info.value)


def test_parse_error_unclosed_brace():
    """Test that unclosed brace raises ParseError."""
    with pytest.raises(ParseError) as exc_info:
        parse("pipeline test() { step1 -> step2")  # Missing closing brace

    assert "Expected" in str(exc_info.value)


def test_parse_complex_module():
    """Test parsing a complex module with multiple declarations."""
    source = """
type UserId = Int;
type Email = String;

fn getUser(id: UserId) -> Email;
fn createUser(email: Email) -> UserId;

pipeline processUsers(Input) -> Output {
  load -> validate -> transform -> save
}
"""
    module = parse(source)

    assert len(module.decls) == 5

    # Check type aliases
    assert isinstance(module.decls[0], TypeAlias)
    assert module.decls[0].name == "UserId"
    assert isinstance(module.decls[1], TypeAlias)
    assert module.decls[1].name == "Email"

    # Check functions
    assert isinstance(module.decls[2], FunctionDecl)
    assert module.decls[2].name == "getUser"
    assert isinstance(module.decls[3], FunctionDecl)
    assert module.decls[3].name == "createUser"

    # Check pipeline
    assert isinstance(module.decls[4], PipelineDecl)
    assert module.decls[4].name == "processUsers"
    assert len(module.decls[4].steps) == 4


def test_parse_if_expr_without_else_pipeline_body():
    """Test parsing if expression without else block in pipeline body."""
    source = """
fn double(x: Int) -> Int;
pipeline main(Int) -> Int {
  if (x > 10) {
    double
  }
}
"""
    module = parse(source)

    assert len(module.decls) == 2
    pipeline = module.decls[1]
    assert isinstance(pipeline, PipelineDecl)
    assert pipeline.name == "main"
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert isinstance(step, PipelineStep)
    assert step.expr is not None
    assert isinstance(step.expr, IfExpr)
    assert step.expr.else_steps is None
    assert len(step.expr.then_steps) == 1
    assert step.expr.then_steps[0].name == "double"


def test_parse_if_expr_with_else_pipeline_body():
    """Test parsing if expression with else block in pipeline body."""
    source = """
fn double(x: Int) -> Int;
fn half(x: Int) -> Int;
pipeline main(Int) -> Int {
  if (x > 10) {
    double
  } else {
    half
  }
}
"""
    module = parse(source)

    assert len(module.decls) == 3
    pipeline = module.decls[2]
    assert isinstance(pipeline, PipelineDecl)
    assert pipeline.name == "main"
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert isinstance(step, PipelineStep)
    assert step.expr is not None
    assert isinstance(step.expr, IfExpr)
    assert step.expr.else_steps is not None
    assert len(step.expr.then_steps) == 1
    assert step.expr.then_steps[0].name == "double"
    assert len(step.expr.else_steps) == 1
    assert step.expr.else_steps[0].name == "half"


def test_parse_if_expr_nested():
    """Test parsing nested if expressions."""
    source = """
fn f1(x: Int) -> Int;
fn f2(x: Int) -> Int;
fn f3(x: Int) -> Int;
pipeline main(Int) -> Int {
  if (x > 10) {
    if (x > 20) {
      f2
    } else {
      f3
    }
  } else {
    f1
  }
}
"""
    module = parse(source)

    assert len(module.decls) == 4
    pipeline = module.decls[3]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert isinstance(step.expr, IfExpr)
    # Outer if
    assert len(step.expr.then_steps) == 1
    # Inner if should be in then_steps
    inner_step = step.expr.then_steps[0]
    assert isinstance(inner_step.expr, IfExpr)
    assert len(inner_step.expr.then_steps) == 1
    assert inner_step.expr.then_steps[0].name == "f2"
    assert len(inner_step.expr.else_steps) == 1
    assert inner_step.expr.else_steps[0].name == "f3"

