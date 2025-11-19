"""Token definitions for the RLang lexer.

Defines all token types and the Token dataclass used throughout the lexing phase.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TokenType(Enum):
    """Enumeration of all token types in RLang."""

    # Identifiers and literals
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"

    # Keywords
    KEYWORD_IF = "KEYWORD_IF"
    KEYWORD_ELSE = "KEYWORD_ELSE"
    KEYWORD_WHILE = "KEYWORD_WHILE"
    KEYWORD_FOR = "KEYWORD_FOR"
    KEYWORD_FUNCTION = "KEYWORD_FUNCTION"
    KEYWORD_RETURN = "KEYWORD_RETURN"
    KEYWORD_LET = "KEYWORD_LET"
    KEYWORD_CONST = "KEYWORD_CONST"
    KEYWORD_TRUE = "KEYWORD_TRUE"
    KEYWORD_FALSE = "KEYWORD_FALSE"
    KEYWORD_NULL = "KEYWORD_NULL"
    KEYWORD_AND = "KEYWORD_AND"
    KEYWORD_OR = "KEYWORD_OR"
    KEYWORD_NOT = "KEYWORD_NOT"
    KEYWORD_RECORD = "KEYWORD_RECORD"
    KEYWORD_IN = "KEYWORD_IN"
    KEYWORD_MATCH = "KEYWORD_MATCH"
    KEYWORD_CASE = "KEYWORD_CASE"

    # Operators
    OP_PLUS = "OP_PLUS"
    OP_MINUS = "OP_MINUS"
    OP_MULTIPLY = "OP_MULTIPLY"
    OP_DIVIDE = "OP_DIVIDE"
    OP_MODULO = "OP_MODULO"
    OP_EQUAL = "OP_EQUAL"
    OP_NOT_EQUAL = "OP_NOT_EQUAL"
    OP_LESS = "OP_LESS"
    OP_LESS_EQUAL = "OP_LESS_EQUAL"
    OP_GREATER = "OP_GREATER"
    OP_GREATER_EQUAL = "OP_GREATER_EQUAL"
    OP_ASSIGN = "OP_ASSIGN"
    OP_ARROW = "OP_ARROW"
    OP_AND = "OP_AND"  # &&
    OP_OR = "OP_OR"  # ||
    OP_NOT = "OP_NOT"  # !
    ARROW = "ARROW"  # =>
    UNDERSCORE = "UNDERSCORE"  # _

    # Punctuation
    LPAREN = "LPAREN"  # (
    RPAREN = "RPAREN"  # )
    LBRACE = "LBRACE"  # {
    RBRACE = "RBRACE"  # }
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    COLON = "COLON"  # :
    SEMICOLON = "SEMICOLON"  # ;
    COMMA = "COMMA"  # ,
    DOT = "DOT"  # .
    DOTDOT = "DOTDOT"  # ..

    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"


# Keyword mapping: lowercase keyword -> TokenType
KEYWORDS = {
    "if": TokenType.KEYWORD_IF,
    "else": TokenType.KEYWORD_ELSE,
    "while": TokenType.KEYWORD_WHILE,
    "for": TokenType.KEYWORD_FOR,
    "function": TokenType.KEYWORD_FUNCTION,
    "return": TokenType.KEYWORD_RETURN,
    "let": TokenType.KEYWORD_LET,
    "const": TokenType.KEYWORD_CONST,
    "true": TokenType.KEYWORD_TRUE,
    "false": TokenType.KEYWORD_FALSE,
    "null": TokenType.KEYWORD_NULL,
    "and": TokenType.KEYWORD_AND,
    "or": TokenType.KEYWORD_OR,
    "not": TokenType.KEYWORD_NOT,
    "record": TokenType.KEYWORD_RECORD,
    "in": TokenType.KEYWORD_IN,
    "match": TokenType.KEYWORD_MATCH,
    "case": TokenType.KEYWORD_CASE,
}


@dataclass
class Token:
    """Represents a single token in the source code.

    Attributes:
        type: The type of token (TokenType enum)
        value: The literal string value of the token
        line: 1-based line number where token starts
        col: 1-based column number where token starts
    """

    type: TokenType
    value: str
    line: int
    col: int

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Token({self.type.value}, {self.value!r}, {self.line}, {self.col})"

    def __eq__(self, other: object) -> bool:
        """Equality comparison for testing."""
        if not isinstance(other, Token):
            return False
        return (
            self.type == other.type
            and self.value == other.value
            and self.line == other.line
            and self.col == other.col
        )


__all__ = ["TokenType", "Token", "KEYWORDS"]

