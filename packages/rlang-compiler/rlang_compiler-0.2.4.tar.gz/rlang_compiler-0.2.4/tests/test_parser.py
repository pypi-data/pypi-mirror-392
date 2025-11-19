"""Comprehensive tests for the RLang parser."""

import pytest

from rlang.parser import (
    BinaryOp,
    BooleanAnd,
    BooleanNot,
    BooleanOr,
    Call,
    Case,
    FieldAccess,
    ForExpr,
    FunctionDecl,
    Identifier,
    IfExpr,
    Literal,
    LiteralPattern,
    ListPattern,
    MatchExpr,
    Module,
    Param,
    ParseError,
    PipelineDecl,
    PipelineStep,
    RecordExpr,
    RecordPattern,
    RecordType,
    SimpleType,
    TypeAlias,
    VarPattern,
    WildcardPattern,
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


def test_parse_nested_if_in_then_branch():
    """Test parsing nested IF in THEN branch."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;
pipeline main(Int) -> Int {
    if (__value > 10) {
        if (__value > 20) {
            inc
        } else {
            dec
        }
    } else {
        dec
    }
}
"""
    module = parse(source)

    assert len(module.decls) == 3
    pipeline = module.decls[2]
    assert isinstance(pipeline, PipelineDecl)
    assert pipeline.name == "main"
    assert len(pipeline.steps) == 1

    # Top-level step should be an IfExpr
    step = pipeline.steps[0]
    assert isinstance(step, PipelineStep)
    assert step.expr is not None
    assert isinstance(step.expr, IfExpr)

    # Outer IF: THEN branch contains nested IF
    outer_if = step.expr
    assert len(outer_if.then_steps) == 1
    assert len(outer_if.else_steps) == 1
    assert outer_if.else_steps[0].name == "dec"

    # Inner IF should be in THEN branch
    inner_step = outer_if.then_steps[0]
    assert isinstance(inner_step, PipelineStep)
    assert inner_step.expr is not None
    assert isinstance(inner_step.expr, IfExpr)

    inner_if = inner_step.expr
    assert len(inner_if.then_steps) == 1
    assert len(inner_if.else_steps) == 1
    assert inner_if.then_steps[0].name == "inc"
    assert inner_if.else_steps[0].name == "dec"


def test_parse_nested_if_in_else_branch():
    """Test parsing nested IF in ELSE branch."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;
pipeline main(Int) -> Int {
    if (__value > 10) {
        inc
    } else {
        if (__value > 0) {
            inc
        } else {
            dec
        }
    }
}
"""
    module = parse(source)

    assert len(module.decls) == 3
    pipeline = module.decls[2]
    assert isinstance(pipeline, PipelineDecl)
    assert pipeline.name == "main"
    assert len(pipeline.steps) == 1

    # Top-level step should be an IfExpr
    step = pipeline.steps[0]
    assert isinstance(step, PipelineStep)
    assert step.expr is not None
    assert isinstance(step.expr, IfExpr)

    # Outer IF: ELSE branch contains nested IF
    outer_if = step.expr
    assert len(outer_if.then_steps) == 1
    assert len(outer_if.else_steps) == 1
    assert outer_if.then_steps[0].name == "inc"

    # Inner IF should be in ELSE branch
    inner_step = outer_if.else_steps[0]
    assert isinstance(inner_step, PipelineStep)
    assert inner_step.expr is not None
    assert isinstance(inner_step.expr, IfExpr)

    inner_if = inner_step.expr
    assert len(inner_if.then_steps) == 1
    assert len(inner_if.else_steps) == 1
    assert inner_if.then_steps[0].name == "inc"
    assert inner_if.else_steps[0].name == "dec"


def test_parse_deeply_nested_if():
    """Test parsing deeply nested IF (3-4 levels)."""
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

    assert len(module.decls) == 5
    pipeline = module.decls[4]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1

    # Level 1: Top-level IF
    step1 = pipeline.steps[0]
    assert isinstance(step1.expr, IfExpr)
    level1_if = step1.expr
    assert len(level1_if.then_steps) == 1
    assert len(level1_if.else_steps) == 1
    assert level1_if.else_steps[0].name == "f1"

    # Level 2: IF in THEN branch
    step2 = level1_if.then_steps[0]
    assert isinstance(step2.expr, IfExpr)
    level2_if = step2.expr
    assert len(level2_if.then_steps) == 1
    assert len(level2_if.else_steps) == 1
    assert level2_if.else_steps[0].name == "f2"

    # Level 3: IF in Level 2's THEN branch
    step3 = level2_if.then_steps[0]
    assert isinstance(step3.expr, IfExpr)
    level3_if = step3.expr
    assert len(level3_if.then_steps) == 1
    assert len(level3_if.else_steps) == 1
    assert level3_if.then_steps[0].name == "f4"
    assert level3_if.else_steps[0].name == "f3"

    # Verify depth: 3 levels of nesting
    depth = 0
    current = step1.expr
    while current and isinstance(current, IfExpr):
        depth += 1
        if current.then_steps and isinstance(current.then_steps[0].expr, IfExpr):
            current = current.then_steps[0].expr
        else:
            break
    assert depth == 3


def test_parse_nested_if_with_multiple_steps():
    """Test parsing nested IF with multiple steps in branches."""
    source = """
fn inc(x: Int) -> Int;
fn dec(x: Int) -> Int;
fn double(x: Int) -> Int;
pipeline main(Int) -> Int {
    if (__value > 10) {
        inc -> double
    } else {
        if (__value > 0) {
            inc -> dec
        } else {
            dec -> double
        }
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
    outer_if = step.expr

    # THEN branch has 2 steps
    assert len(outer_if.then_steps) == 2
    assert outer_if.then_steps[0].name == "inc"
    assert outer_if.then_steps[1].name == "double"

    # ELSE branch has nested IF
    assert len(outer_if.else_steps) == 1
    inner_step = outer_if.else_steps[0]
    assert isinstance(inner_step.expr, IfExpr)
    inner_if = inner_step.expr

    # Inner THEN has 2 steps
    assert len(inner_if.then_steps) == 2
    assert inner_if.then_steps[0].name == "inc"
    assert inner_if.then_steps[1].name == "dec"

    # Inner ELSE has 2 steps
    assert len(inner_if.else_steps) == 2
    assert inner_if.else_steps[0].name == "dec"
    assert inner_if.else_steps[1].name == "double"


def test_parse_boolean_and():
    """Test parsing boolean AND operator."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20) {
        inc
    }
}
"""
    module = parse(source)
    # Find the pipeline declaration (second declaration after function)
    pipeline = None
    for decl in module.decls:
        if isinstance(decl, PipelineDecl):
            pipeline = decl
            break
    assert pipeline is not None
    assert isinstance(pipeline, PipelineDecl)
    
    if_expr = pipeline.steps[0].expr
    assert isinstance(if_expr, IfExpr)
    
    condition = if_expr.condition
    assert isinstance(condition, BooleanAnd)
    assert isinstance(condition.left, BinaryOp)
    assert condition.left.op == ">"
    assert isinstance(condition.right, BinaryOp)
    assert condition.right.op == "<"


def test_parse_boolean_or():
    """Test parsing boolean OR operator."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 || __value < 0) {
        inc
    }
}
"""
    module = parse(source)
    # Find the pipeline declaration (second declaration after function)
    pipeline = None
    for decl in module.decls:
        if isinstance(decl, PipelineDecl):
            pipeline = decl
            break
    assert pipeline is not None
    assert isinstance(pipeline, PipelineDecl)
    
    if_expr = pipeline.steps[0].expr
    assert isinstance(if_expr, IfExpr)
    
    condition = if_expr.condition
    assert isinstance(condition, BooleanOr)
    assert isinstance(condition.left, BinaryOp)
    assert condition.left.op == ">"
    assert isinstance(condition.right, BinaryOp)
    assert condition.right.op == "<"


def test_parse_boolean_not():
    """Test parsing boolean NOT operator."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (!(__value > 10)) {
        inc
    }
}
"""
    module = parse(source)
    # Find the pipeline declaration (second declaration after function)
    pipeline = None
    for decl in module.decls:
        if isinstance(decl, PipelineDecl):
            pipeline = decl
            break
    assert pipeline is not None
    assert isinstance(pipeline, PipelineDecl)
    
    if_expr = pipeline.steps[0].expr
    assert isinstance(if_expr, IfExpr)
    
    condition = if_expr.condition
    assert isinstance(condition, BooleanNot)
    assert isinstance(condition.operand, BinaryOp)
    assert condition.operand.op == ">"


def test_parse_boolean_precedence_and_before_or():
    """Test that AND has higher precedence than OR."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 || __value < 0 && __value == 5) {
        inc
    }
}
"""
    module = parse(source)
    # Find the pipeline declaration (second declaration after function)
    pipeline = None
    for decl in module.decls:
        if isinstance(decl, PipelineDecl):
            pipeline = decl
            break
    assert pipeline is not None
    assert isinstance(pipeline, PipelineDecl)
    
    if_expr = pipeline.steps[0].expr
    assert isinstance(if_expr, IfExpr)
    
    condition = if_expr.condition
    # Should parse as: (__value > 10) || ((__value < 0) && (__value == 5))
    assert isinstance(condition, BooleanOr)
    assert isinstance(condition.left, BinaryOp)
    assert condition.left.op == ">"
    assert isinstance(condition.right, BooleanAnd)
    assert isinstance(condition.right.left, BinaryOp)
    assert condition.right.left.op == "<"
    assert isinstance(condition.right.right, BinaryOp)
    assert condition.right.right.op == "=="


def test_parse_boolean_precedence_not_before_and():
    """Test that NOT has higher precedence than AND."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (!__value > 10 && __value < 20) {
        inc
    }
}
"""
    module = parse(source)
    # Find the pipeline declaration (second declaration after function)
    pipeline = None
    for decl in module.decls:
        if isinstance(decl, PipelineDecl):
            pipeline = decl
            break
    assert pipeline is not None
    assert isinstance(pipeline, PipelineDecl)
    
    if_expr = pipeline.steps[0].expr
    assert isinstance(if_expr, IfExpr)
    
    condition = if_expr.condition
    # Should parse as: (!(__value > 10)) && (__value < 20)
    assert isinstance(condition, BooleanAnd)
    assert isinstance(condition.left, BooleanNot)
    assert isinstance(condition.left.operand, BinaryOp)
    assert condition.left.operand.op == ">"
    assert isinstance(condition.right, BinaryOp)
    assert condition.right.op == "<"


def test_parse_boolean_grouping_with_parentheses():
    """Test that parentheses override precedence."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if ((__value > 10 || __value < 0) && __value == 5) {
        inc
    }
}
"""
    module = parse(source)
    # Find the pipeline declaration (second declaration after function)
    pipeline = None
    for decl in module.decls:
        if isinstance(decl, PipelineDecl):
            pipeline = decl
            break
    assert pipeline is not None
    assert isinstance(pipeline, PipelineDecl)
    
    if_expr = pipeline.steps[0].expr
    assert isinstance(if_expr, IfExpr)
    
    condition = if_expr.condition
    # Should parse as: ((__value > 10) || (__value < 0)) && (__value == 5)
    assert isinstance(condition, BooleanAnd)
    assert isinstance(condition.left, BooleanOr)
    assert isinstance(condition.right, BinaryOp)
    assert condition.right.op == "=="


def test_parse_boolean_nested_not():
    """Test parsing nested NOT operators."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (!(__value > 10 || __value < 0)) {
        inc
    }
}
"""
    module = parse(source)
    # Find the pipeline declaration (second declaration after function)
    pipeline = None
    for decl in module.decls:
        if isinstance(decl, PipelineDecl):
            pipeline = decl
            break
    assert pipeline is not None
    assert isinstance(pipeline, PipelineDecl)
    
    if_expr = pipeline.steps[0].expr
    assert isinstance(if_expr, IfExpr)
    
    condition = if_expr.condition
    assert isinstance(condition, BooleanNot)
    assert isinstance(condition.operand, BooleanOr)
    assert isinstance(condition.operand.left, BinaryOp)
    assert isinstance(condition.operand.right, BinaryOp)


def test_parse_boolean_complex_expression():
    """Test parsing complex boolean expression with all operators."""
    source = """
fn inc(x: Int) -> Int;

pipeline main(Int) -> Int {
    if (__value > 10 && __value < 20 || !(__value == 0)) {
        inc
    }
}
"""
    module = parse(source)
    # Find the pipeline declaration (second declaration after function)
    pipeline = None
    for decl in module.decls:
        if isinstance(decl, PipelineDecl):
            pipeline = decl
            break
    assert pipeline is not None
    assert isinstance(pipeline, PipelineDecl)
    
    if_expr = pipeline.steps[0].expr
    assert isinstance(if_expr, IfExpr)
    
    condition = if_expr.condition
    # Should parse as: ((__value > 10) && (__value < 20)) || (!(__value == 0))
    assert isinstance(condition, BooleanOr)
    assert isinstance(condition.left, BooleanAnd)
    assert isinstance(condition.right, BooleanNot)


def test_parse_record_type_basic():
    """Test parsing a basic record type declaration."""
    source = "type User = Record { id: Int, name: String };"
    module = parse(source)

    assert len(module.decls) == 1
    decl = module.decls[0]
    assert isinstance(decl, TypeAlias)
    assert decl.name == "User"
    assert isinstance(decl.target, RecordType)
    
    record_type = decl.target
    assert len(record_type.fields) == 2
    assert "id" in record_type.fields
    assert "name" in record_type.fields
    assert isinstance(record_type.fields["id"], SimpleType)
    assert isinstance(record_type.fields["name"], SimpleType)
    assert record_type.fields["id"].name == "Int"
    assert record_type.fields["name"].name == "String"


def test_parse_record_literal_basic():
    """Test parsing a basic record literal."""
    source = """
pipeline main(Int) -> Record { id: Int, name: String } {
    { id: __value, name: "Alice" }
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1
    
    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, RecordExpr)
    
    record_expr = step.expr
    assert len(record_expr.fields) == 2
    assert "id" in record_expr.fields
    assert "name" in record_expr.fields
    
    # Check field values
    id_field = record_expr.fields["id"]
    assert isinstance(id_field, Identifier)
    assert id_field.name == "__value"
    
    name_field = record_expr.fields["name"]
    assert isinstance(name_field, Literal)
    assert name_field.value == "Alice"


def test_parse_record_literal_nested():
    """Test parsing a nested record literal."""
    source = """
pipeline main(Int) -> Record { id: Int, meta: Record { age: Int } } {
    { id: 1, meta: { age: 30 } }
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1
    
    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, RecordExpr)
    
    record_expr = step.expr
    assert len(record_expr.fields) == 2
    assert "id" in record_expr.fields
    assert "meta" in record_expr.fields
    
    # Check nested record
    meta_field = record_expr.fields["meta"]
    assert isinstance(meta_field, RecordExpr)
    assert len(meta_field.fields) == 1
    assert "age" in meta_field.fields
    assert isinstance(meta_field.fields["age"], Literal)
    assert meta_field.fields["age"].value == 30


def test_parse_field_access_basic():
    """Test parsing basic field access."""
    source = """
pipeline main(Record { id: Int, name: String }) -> String {
    __value.name
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1
    
    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, FieldAccess)
    
    field_access = step.expr
    assert isinstance(field_access.record, Identifier)
    assert field_access.record.name == "__value"
    assert field_access.field == "name"


def test_parse_field_access_chained():
    """Test parsing chained field access."""
    source = """
pipeline main(Record { inner: Record { user: Record { name: String } } }) -> String {
    __value.inner.user.name
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1
    
    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, FieldAccess)
    
    # Unwrap nested FieldAccess nodes
    field_access = step.expr
    assert field_access.field == "name"
    
    # Check inner.user
    inner_access = field_access.record
    assert isinstance(inner_access, FieldAccess)
    assert inner_access.field == "user"
    
    # Check inner
    inner_inner_access = inner_access.record
    assert isinstance(inner_inner_access, FieldAccess)
    assert inner_inner_access.field == "inner"
    
    # Check base identifier
    base = inner_inner_access.record
    assert isinstance(base, Identifier)
    assert base.name == "__value"


def test_parse_for_step_basic():
    """Test parsing a basic for loop step."""
    source = """
pipeline main(Int) -> Int {
  for i in 0 .. 3 {
    inc
  }
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, ForExpr)

    for_expr = step.expr
    assert for_expr.var_name == "i"
    assert for_expr.start == 0
    assert for_expr.end == 3
    assert len(for_expr.body) == 1

    body_step = for_expr.body[0]
    assert isinstance(body_step, PipelineStep)
    assert body_step.name == "inc"


def test_parse_for_step_with_multiple_body_steps():
    """Test parsing a for loop with multiple body steps."""
    source = """
pipeline main(Int) -> Int {
  for i in 0 .. 2 {
    inc -> double
  }
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, ForExpr)

    for_expr = step.expr
    assert for_expr.var_name == "i"
    assert for_expr.start == 0
    assert for_expr.end == 2
    assert len(for_expr.body) == 2

    assert for_expr.body[0].name == "inc"
    assert for_expr.body[1].name == "double"


def test_parse_for_step_zero_iterations():
    """Test parsing a for loop with zero iterations (start >= end)."""
    source = """
pipeline main(Int) -> Int {
  for i in 3 .. 3 {
    inc
  }
}
"""
    module = parse(source)

    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, ForExpr)

    for_expr = step.expr
    assert for_expr.start == 3
    assert for_expr.end == 3
    # Zero iterations, but body is still parsed
    assert len(for_expr.body) == 1


# Pattern Matching Tests

def test_parse_match_expr_with_literal_patterns():
    """Test parsing a match expression with literal patterns."""
    source = """
pipeline test() {
    match (__value) {
        case 42 => { inc(); }
        case _ => { dec(); }
    }
}
"""
    module = parse(source)
    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, MatchExpr)

    match_expr = step.expr
    assert isinstance(match_expr.value, Identifier)
    assert match_expr.value.name == "__value"
    assert len(match_expr.cases) == 2

    # First case: literal pattern 42
    case1 = match_expr.cases[0]
    assert isinstance(case1.pattern, LiteralPattern)
    assert case1.pattern.value == 42
    assert len(case1.body) == 1
    assert case1.body[0].name == "inc"

    # Second case: wildcard pattern
    case2 = match_expr.cases[1]
    assert isinstance(case2.pattern, WildcardPattern)
    assert len(case2.body) == 1
    assert case2.body[0].name == "dec"


def test_parse_match_expr_with_record_pattern():
    """Test parsing a match expression with record pattern."""
    source = """
pipeline test() {
    match (x) {
        case { id: 1, name: _ } => { inc(); }
        case _ => { dec(); }
    }
}
"""
    module = parse(source)
    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, MatchExpr)

    match_expr = step.expr
    assert len(match_expr.cases) == 2

    # First case: record pattern
    case1 = match_expr.cases[0]
    assert isinstance(case1.pattern, RecordPattern)
    assert len(case1.pattern.fields) == 2
    assert "id" in case1.pattern.fields
    assert "name" in case1.pattern.fields
    assert isinstance(case1.pattern.fields["id"], LiteralPattern)
    assert case1.pattern.fields["id"].value == 1
    assert isinstance(case1.pattern.fields["name"], WildcardPattern)


def test_parse_match_expr_with_list_pattern():
    """Test parsing a match expression with list pattern."""
    source = """
pipeline test() {
    match (x) {
        case [a, b, 3] => { inc(); }
        case _ => { dec(); }
    }
}
"""
    module = parse(source)
    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 1

    step = pipeline.steps[0]
    assert step.expr is not None
    assert isinstance(step.expr, MatchExpr)

    match_expr = step.expr
    assert len(match_expr.cases) == 2

    # First case: list pattern
    case1 = match_expr.cases[0]
    assert isinstance(case1.pattern, ListPattern)
    assert len(case1.pattern.elements) == 3
    assert isinstance(case1.pattern.elements[0], VarPattern)
    assert case1.pattern.elements[0].name == "a"
    assert isinstance(case1.pattern.elements[1], VarPattern)
    assert case1.pattern.elements[1].name == "b"
    assert isinstance(case1.pattern.elements[2], LiteralPattern)
    assert case1.pattern.elements[2].value == 3


def test_parse_match_expr_with_var_pattern():
    """Test parsing a match expression with variable pattern."""
    source = """
pipeline test() {
    match (x) {
        case value => { process(value); }
        case _ => { skip(); }
    }
}
"""
    module = parse(source)
    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)

    step = pipeline.steps[0]
    match_expr = step.expr
    assert len(match_expr.cases) == 2

    # First case: var pattern
    case1 = match_expr.cases[0]
    assert isinstance(case1.pattern, VarPattern)
    assert case1.pattern.name == "value"


def test_parse_match_expr_with_nested_patterns():
    """Test parsing a match expression with nested patterns."""
    source = """
pipeline test() {
    match (x) {
        case { items: [first, second], count: 2 } => { process(); }
        case _ => { skip(); }
    }
}
"""
    module = parse(source)
    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)

    step = pipeline.steps[0]
    match_expr = step.expr
    assert len(match_expr.cases) == 2

    # First case: nested record and list patterns
    case1 = match_expr.cases[0]
    assert isinstance(case1.pattern, RecordPattern)
    assert "items" in case1.pattern.fields
    assert "count" in case1.pattern.fields
    assert isinstance(case1.pattern.fields["items"], ListPattern)
    assert len(case1.pattern.fields["items"].elements) == 2
    assert isinstance(case1.pattern.fields["count"], LiteralPattern)
    assert case1.pattern.fields["count"].value == 2


def test_parse_match_expr_empty_cases():
    """Test parsing a match expression with empty case bodies."""
    source = """
pipeline test() {
    match (x) {
        case 1 => { }
        case _ => { }
    }
}
"""
    module = parse(source)
    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)

    step = pipeline.steps[0]
    match_expr = step.expr
    assert len(match_expr.cases) == 2
    assert len(match_expr.cases[0].body) == 0
    assert len(match_expr.cases[1].body) == 0


def test_parse_match_expr_missing_arrow():
    """Test that missing arrow in case raises ParseError."""
    source = """
pipeline test() {
    match (x) {
        case 42 { inc(); }
    }
}
"""
    with pytest.raises(ParseError) as exc_info:
        parse(source)
    assert "Expected '=>'" in str(exc_info.value)


def test_parse_match_expr_missing_case_body():
    """Test that missing case body raises ParseError."""
    source = """
pipeline test() {
    match (x) {
        case 42 =>
    }
}
"""
    with pytest.raises(ParseError) as exc_info:
        parse(source)
    # Should fail on missing brace or body
    assert "Expected" in str(exc_info.value)


def test_parse_match_expr_invalid_pattern():
    """Test that invalid pattern syntax raises ParseError."""
    source = """
pipeline test() {
    match (x) {
        case { id pattern } => { inc(); }
    }
}
"""
    with pytest.raises(ParseError) as exc_info:
        parse(source)
    # Should fail on missing colon
    assert "Expected" in str(exc_info.value)


def test_parse_match_expr_as_expression():
    """Test that match expression can be used as a regular expression."""
    source = """
pipeline test() {
    match (x) {
        case 1 => { step1(); }
        case _ => { step2(); }
    } -> process();
}
"""
    module = parse(source)
    assert len(module.decls) == 1
    pipeline = module.decls[0]
    assert isinstance(pipeline, PipelineDecl)
    assert len(pipeline.steps) == 2

    # First step should be match expression
    step1 = pipeline.steps[0]
    assert isinstance(step1.expr, MatchExpr)

    # Second step should be regular step
    step2 = pipeline.steps[1]
    assert step2.name == "process"

