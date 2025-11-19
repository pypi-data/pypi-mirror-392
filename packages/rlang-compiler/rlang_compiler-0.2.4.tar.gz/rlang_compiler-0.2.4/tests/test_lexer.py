"""Comprehensive tests for the RLang lexer."""

import pytest

from rlang.lexer import LexerError, Token, TokenType, tokenize
from tests.base import tempdir


def test_identifier_lexing():
    """Test that identifiers are correctly tokenized."""
    tokens = tokenize("foo bar123 _underscore")
    assert len(tokens) == 4  # 3 identifiers + EOF

    assert tokens[0] == Token(TokenType.IDENTIFIER, "foo", 1, 1)
    assert tokens[1] == Token(TokenType.IDENTIFIER, "bar123", 1, 5)
    assert tokens[2] == Token(TokenType.IDENTIFIER, "_underscore", 1, 12)


def test_keyword_recognition():
    """Test that keywords are correctly recognized."""
    tokens = tokenize("if else while for function return let const")
    assert len(tokens) == 9  # 8 keywords + EOF

    assert tokens[0].type == TokenType.KEYWORD_IF
    assert tokens[1].type == TokenType.KEYWORD_ELSE
    assert tokens[2].type == TokenType.KEYWORD_WHILE
    assert tokens[3].type == TokenType.KEYWORD_FOR
    assert tokens[4].type == TokenType.KEYWORD_FUNCTION
    assert tokens[5].type == TokenType.KEYWORD_RETURN
    assert tokens[6].type == TokenType.KEYWORD_LET
    assert tokens[7].type == TokenType.KEYWORD_CONST


def test_boolean_keywords():
    """Test boolean and null keywords."""
    tokens = tokenize("true false null")
    assert len(tokens) == 4  # 3 keywords + EOF

    assert tokens[0].type == TokenType.KEYWORD_TRUE
    assert tokens[1].type == TokenType.KEYWORD_FALSE
    assert tokens[2].type == TokenType.KEYWORD_NULL


def test_logical_operators():
    """Test logical operator keywords."""
    tokens = tokenize("and or not")
    assert len(tokens) == 4  # 3 keywords + EOF

    assert tokens[0].type == TokenType.KEYWORD_AND
    assert tokens[1].type == TokenType.KEYWORD_OR
    assert tokens[2].type == TokenType.KEYWORD_NOT


def test_integer_lexing():
    """Test that integers are correctly tokenized."""
    tokens = tokenize("0 42 999")
    assert len(tokens) == 4  # 3 integers + EOF

    assert tokens[0] == Token(TokenType.INTEGER, "0", 1, 1)
    assert tokens[1] == Token(TokenType.INTEGER, "42", 1, 3)
    assert tokens[2] == Token(TokenType.INTEGER, "999", 1, 6)


def test_float_lexing():
    """Test that floats are correctly tokenized."""
    tokens = tokenize("3.14 0.5 42.0")
    assert len(tokens) == 4  # 3 floats + EOF

    assert tokens[0] == Token(TokenType.FLOAT, "3.14", 1, 1)
    assert tokens[1] == Token(TokenType.FLOAT, "0.5", 1, 6)
    assert tokens[2] == Token(TokenType.FLOAT, "42.0", 1, 10)


def test_string_lexing():
    """Test that string literals are correctly tokenized."""
    tokens = tokenize('"hello" "world"')
    assert len(tokens) == 3  # 2 strings + EOF

    assert tokens[0] == Token(TokenType.STRING, "hello", 1, 1)
    assert tokens[1] == Token(TokenType.STRING, "world", 1, 9)


def test_string_escape_sequences():
    """Test escape sequences in strings."""
    tokens = tokenize('"hello\\nworld" "tab\\there"')
    assert len(tokens) == 3  # 2 strings + EOF

    assert tokens[0].value == "hello\nworld"
    assert tokens[1].value == "tab\there"


def test_arithmetic_operators():
    """Test arithmetic operators."""
    tokens = tokenize("+ - * / %")
    assert len(tokens) == 6  # 5 operators + EOF

    assert tokens[0].type == TokenType.OP_PLUS
    assert tokens[1].type == TokenType.OP_MINUS
    assert tokens[2].type == TokenType.OP_MULTIPLY
    assert tokens[3].type == TokenType.OP_DIVIDE
    assert tokens[4].type == TokenType.OP_MODULO


def test_comparison_operators():
    """Test comparison operators."""
    tokens = tokenize("== != < <= > >=")
    assert len(tokens) == 7  # 6 operators + EOF

    assert tokens[0].type == TokenType.OP_EQUAL
    assert tokens[1].type == TokenType.OP_NOT_EQUAL
    assert tokens[2].type == TokenType.OP_LESS
    assert tokens[3].type == TokenType.OP_LESS_EQUAL
    assert tokens[4].type == TokenType.OP_GREATER
    assert tokens[5].type == TokenType.OP_GREATER_EQUAL


def test_assignment_and_arrow():
    """Test assignment and arrow operators."""
    tokens = tokenize("= ->")
    assert len(tokens) == 3  # 2 operators + EOF

    assert tokens[0].type == TokenType.OP_ASSIGN
    assert tokens[1].type == TokenType.OP_ARROW


def test_punctuation():
    """Test punctuation tokens."""
    tokens = tokenize("(){}:;,")
    assert len(tokens) == 8  # 7 punctuation + EOF

    assert tokens[0].type == TokenType.LPAREN
    assert tokens[1].type == TokenType.RPAREN
    assert tokens[2].type == TokenType.LBRACE
    assert tokens[3].type == TokenType.RBRACE
    assert tokens[4].type == TokenType.COLON
    assert tokens[5].type == TokenType.SEMICOLON
    assert tokens[6].type == TokenType.COMMA


def test_whitespace_handling():
    """Test that whitespace is correctly skipped."""
    tokens = tokenize("  foo   bar  ")
    assert len(tokens) == 3  # 2 identifiers + EOF

    assert tokens[0] == Token(TokenType.IDENTIFIER, "foo", 1, 3)
    assert tokens[1] == Token(TokenType.IDENTIFIER, "bar", 1, 9)


def test_newline_handling():
    """Test that newlines are tracked and tokenized."""
    tokens = tokenize("foo\nbar")
    assert len(tokens) == 4  # 2 identifiers + 1 newline + EOF

    assert tokens[0] == Token(TokenType.IDENTIFIER, "foo", 1, 1)
    assert tokens[1] == Token(TokenType.NEWLINE, "\n", 1, 4)
    assert tokens[2] == Token(TokenType.IDENTIFIER, "bar", 2, 1)


def test_comment_skipping():
    """Test that comments are correctly skipped."""
    tokens = tokenize("foo # this is a comment\nbar")
    assert len(tokens) == 4  # 2 identifiers + 1 newline + EOF

    assert tokens[0] == Token(TokenType.IDENTIFIER, "foo", 1, 1)
    # Newline is at column 24 (23 characters before it: "foo # this is a comment")
    assert tokens[1] == Token(TokenType.NEWLINE, "\n", 1, 24)
    assert tokens[2] == Token(TokenType.IDENTIFIER, "bar", 2, 1)


def test_eof_token():
    """Test that EOF token is always present."""
    tokens = tokenize("")
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF

    tokens = tokenize("foo")
    assert len(tokens) == 2
    assert tokens[-1].type == TokenType.EOF


def test_position_tracking():
    """Test that line and column positions are correctly tracked."""
    source = "foo\n  bar\nbaz"
    tokens = tokenize(source)

    assert tokens[0].line == 1 and tokens[0].col == 1  # foo
    assert tokens[1].line == 1 and tokens[1].col == 4  # newline
    assert tokens[2].line == 2 and tokens[2].col == 3  # bar
    assert tokens[3].line == 2 and tokens[3].col == 6  # newline
    assert tokens[4].line == 3 and tokens[4].col == 1  # baz


def test_complex_expression():
    """Test tokenizing a complex expression."""
    tokens = tokenize("let x = 42 + 3.14")
    expected_types = [
        TokenType.KEYWORD_LET,
        TokenType.IDENTIFIER,
        TokenType.OP_ASSIGN,
        TokenType.INTEGER,
        TokenType.OP_PLUS,
        TokenType.FLOAT,
        TokenType.EOF,
    ]

    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type


def test_function_declaration():
    """Test tokenizing a function declaration."""
    tokens = tokenize("function add(a, b) -> { return a + b }")
    expected_types = [
        TokenType.KEYWORD_FUNCTION,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.COMMA,
        TokenType.IDENTIFIER,
        TokenType.RPAREN,
        TokenType.OP_ARROW,
        TokenType.LBRACE,
        TokenType.KEYWORD_RETURN,
        TokenType.IDENTIFIER,
        TokenType.OP_PLUS,
        TokenType.IDENTIFIER,
        TokenType.RBRACE,
        TokenType.EOF,
    ]

    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type


def test_error_unterminated_string():
    """Test that unterminated string raises LexerError."""
    with pytest.raises(LexerError) as exc_info:
        tokenize('"unterminated string')

    assert "Unterminated string literal" in str(exc_info.value)
    assert exc_info.value.line == 1


def test_error_unexpected_character():
    """Test that unexpected characters raise LexerError."""
    with pytest.raises(LexerError) as exc_info:
        tokenize("foo @ bar")

    assert "Unexpected character" in str(exc_info.value)
    assert "@" in str(exc_info.value)


def test_keyword_case_insensitive():
    """Test that keywords are case-insensitive."""
    tokens = tokenize("IF ELSE While")
    assert tokens[0].type == TokenType.KEYWORD_IF
    assert tokens[1].type == TokenType.KEYWORD_ELSE
    assert tokens[2].type == TokenType.KEYWORD_WHILE


def test_identifier_vs_keyword():
    """Test that identifiers are not confused with keywords."""
    tokens = tokenize("if_condition else_var")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "if_condition"
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "else_var"


def test_float_edge_cases():
    """Test edge cases for float parsing."""
    tokens = tokenize("0.0 0.123 .5 is not a float")
    # .5 should be parsed as float (leading decimal point supported)
    # So we get: 0.0, 0.123, FLOAT(0.5), IDENTIFIER(is), ...

    assert tokens[0].type == TokenType.FLOAT
    assert tokens[0].value == "0.0"
    assert tokens[1].type == TokenType.FLOAT
    assert tokens[1].value == "0.123"
    # .5 is parsed as float with leading zero: 0.5
    assert tokens[2].type == TokenType.FLOAT
    assert tokens[2].value == "0.5"
    assert tokens[3].type == TokenType.IDENTIFIER
    assert tokens[3].value == "is"


def test_multiline_string():
    """Test string with newline escape sequence."""
    tokens = tokenize('"line1\\nline2"')
    assert len(tokens) == 2  # 1 string + EOF
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "line1\nline2"

