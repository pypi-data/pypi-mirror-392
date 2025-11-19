"""Deterministic tokenizer for RLang source code.

Converts source code into a stream of tokens with precise position tracking.
"""

from typing import Iterator, Optional

from rlang.lexer.tokens import KEYWORDS, Token, TokenType


class LexerError(Exception):
    """Exception raised when lexer encounters invalid input."""

    def __init__(self, message: str, line: int, col: int):
        """Initialize lexer error with position information.

        Args:
            message: Error message
            line: 1-based line number
            col: 1-based column number
        """
        super().__init__(f"{message} at line {line}, column {col}")
        self.line = line
        self.col = col


class Tokenizer:
    """Pure, stateless tokenizer for RLang source code."""

    def __init__(self, source: str):
        """Initialize tokenizer with source code.

        Args:
            source: Source code to tokenize
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> Iterator[Token]:
        """Tokenize the source code, yielding tokens.

        Yields:
            Token objects representing the source code

        Raises:
            LexerError: If invalid characters or token patterns are encountered
        """
        while self.pos < len(self.source):
            # Handle newlines (yield as tokens)
            if self._peek() == "\n":
                # Newline is at current column position
                # After skipping comment/whitespace, col points to position before newline
                # The newline itself is at col+1, but since columns are 1-indexed,
                # we need to account for the newline character itself
                newline_col = self.col
                yield Token(TokenType.NEWLINE, "\n", self.line, newline_col)
                self._advance(skip_newline_tracking=True)
                self.line += 1
                self.col = 1
                continue

            # Skip whitespace
            if self._is_whitespace():
                self._advance()
                continue

            # Skip comments
            if self._peek() == "#":
                self._skip_comment()
                continue

            # Start position for this token
            start_line = self.line
            start_col = self.col

            # Try to match tokens in order of specificity
            token = (
                self._try_string()
                or self._try_number()
                or self._try_operator()
                or self._try_punctuation()
                or self._try_identifier_or_keyword()
            )

            if token:
                token.line = start_line
                token.col = start_col
                yield token
            else:
                # Unknown character
                char = self._peek()
                raise LexerError(
                    f"Unexpected character: {char!r}",
                    self.line,
                    self.col,
                )

        # Yield EOF token
        yield Token(TokenType.EOF, "", self.line, self.col)

    def _peek(self, offset: int = 0) -> Optional[str]:
        """Peek at character at current position + offset.

        Args:
            offset: Offset from current position

        Returns:
            Character at position, or None if out of bounds
        """
        idx = self.pos + offset
        if idx >= len(self.source):
            return None
        return self.source[idx]

    def _advance(self, count: int = 1, skip_newline_tracking: bool = False) -> None:
        """Advance position by count characters.

        Args:
            count: Number of characters to advance
            skip_newline_tracking: If True, don't update line/col for newlines
                                  (used when newlines are handled separately)
        """
        for _ in range(count):
            if self.pos < len(self.source):
                if not skip_newline_tracking and self.source[self.pos] == "\n":
                    self.line += 1
                    self.col = 1
                elif not skip_newline_tracking:
                    self.col += 1
                self.pos += 1

    def _is_whitespace(self) -> bool:
        """Check if current character is whitespace (excluding newline).

        Returns:
            True if whitespace, False otherwise
        """
        char = self._peek()
        return char is not None and char in " \t\r" and char != "\n"

    def _skip_comment(self) -> None:
        """Skip a comment line (from # to end of line)."""
        # Advance through comment characters but stop before newline
        # The newline will be handled by the main tokenize loop
        # We advance through all characters including the # and comment text
        while self._peek() is not None and self._peek() != "\n":
            self._advance()
        # After this loop, self.col points to the column where the newline is
        # Don't advance past newline - let main loop handle it

    def _try_string(self) -> Optional[Token]:
        """Try to match a string literal.

        Returns:
            Token if matched, None otherwise
        """
        if self._peek() != '"':
            return None

        start_pos = self.pos
        self._advance()  # Skip opening quote

        value = ""
        while True:
            char = self._peek()
            if char is None:
                raise LexerError("Unterminated string literal", self.line, self.col)
            if char == '"':
                self._advance()  # Skip closing quote
                break
            if char == "\\":
                # Escape sequence
                self._advance()
                next_char = self._peek()
                if next_char is None:
                    raise LexerError("Unterminated escape sequence", self.line, self.col)
                # Handle common escape sequences
                escape_map = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    '"': '"',
                    "\\": "\\",
                }
                value += escape_map.get(next_char, next_char)
                self._advance()
            else:
                value += char
                self._advance()

        return Token(TokenType.STRING, value, self.line, self.col)

    def _try_number(self) -> Optional[Token]:
        """Try to match a number (integer or float).

        Returns:
            Token if matched, None otherwise
        """
        # Check for leading decimal point (.5 style float)
        if self._peek() == ".":
            if self._peek(1) and self._peek(1).isdigit():
                value = "0."  # Add leading zero for .5 style
                self._advance()  # Skip "."
                # Fractional part (including first digit after decimal)
                while self._peek() and self._peek().isdigit():
                    value += self._peek()
                    self._advance()
                return Token(TokenType.FLOAT, value, self.line, self.col)
        
        if not self._peek() or not self._peek().isdigit():
            return None

        start_pos = self.pos
        value = ""

        # Integer part
        while self._peek() and self._peek().isdigit():
            value += self._peek()
            self._advance()

        # Check for float
        if self._peek() == ".":
            # Check if next char is a digit
            if self._peek(1) and self._peek(1).isdigit():
                value += "."
                self._advance()
                # Fractional part
                while self._peek() and self._peek().isdigit():
                    value += self._peek()
                    self._advance()
                return Token(TokenType.FLOAT, value, self.line, self.col)
            else:
                # Just a dot, not a float - don't consume it
                pass

        return Token(TokenType.INTEGER, value, self.line, self.col)

    def _try_operator(self) -> Optional[Token]:
        """Try to match an operator.

        Returns:
            Token if matched, None otherwise
        """
        char = self._peek()
        if char is None:
            return None

        # Two-character operators (check these first)
        two_char = char + (self._peek(1) or "")
        if two_char == "->":
            self._advance(2)
            return Token(TokenType.OP_ARROW, "->", self.line, self.col)
        if two_char == "=>":
            self._advance(2)
            return Token(TokenType.ARROW, "=>", self.line, self.col)
        if two_char == "==":
            self._advance(2)
            return Token(TokenType.OP_EQUAL, "==", self.line, self.col)
        if two_char == "!=":
            self._advance(2)
            return Token(TokenType.OP_NOT_EQUAL, "!=", self.line, self.col)
        if two_char == "<=":
            self._advance(2)
            return Token(TokenType.OP_LESS_EQUAL, "<=", self.line, self.col)
        if two_char == ">=":
            self._advance(2)
            return Token(TokenType.OP_GREATER_EQUAL, ">=", self.line, self.col)
        if two_char == "&&":
            self._advance(2)
            return Token(TokenType.OP_AND, "&&", self.line, self.col)
        if two_char == "||":
            self._advance(2)
            return Token(TokenType.OP_OR, "||", self.line, self.col)

        # Single-character operators
        if char == "+":
            self._advance()
            return Token(TokenType.OP_PLUS, "+", self.line, self.col)
        if char == "-":
            self._advance()
            return Token(TokenType.OP_MINUS, "-", self.line, self.col)
        if char == "*":
            self._advance()
            return Token(TokenType.OP_MULTIPLY, "*", self.line, self.col)
        if char == "/":
            self._advance()
            return Token(TokenType.OP_DIVIDE, "/", self.line, self.col)
        if char == "%":
            self._advance()
            return Token(TokenType.OP_MODULO, "%", self.line, self.col)
        if char == "<":
            self._advance()
            return Token(TokenType.OP_LESS, "<", self.line, self.col)
        if char == ">":
            self._advance()
            return Token(TokenType.OP_GREATER, ">", self.line, self.col)
        if char == "=":
            self._advance()
            return Token(TokenType.OP_ASSIGN, "=", self.line, self.col)
        if char == "!":
            # Check if next char is '=' for !=, otherwise it's NOT
            if self._peek(1) == "=":
                # This will be handled by the two_char check above
                return None
            self._advance()
            return Token(TokenType.OP_NOT, "!", self.line, self.col)

        return None

    def _try_punctuation(self) -> Optional[Token]:
        """Try to match punctuation.

        Returns:
            Token if matched, None otherwise
        """
        char = self._peek()
        if char is None:
            return None

        # Check for two-character punctuation first (..)
        if char == ".":
            if self._peek(1) == ".":
                self._advance(2)
                return Token(TokenType.DOTDOT, "..", self.line, self.col)

        token_map = {
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ":": TokenType.COLON,
            ";": TokenType.SEMICOLON,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
        }

        if char in token_map:
            self._advance()
            return Token(token_map[char], char, self.line, self.col)

        return None

    def _try_identifier_or_keyword(self) -> Optional[Token]:
        """Try to match an identifier or keyword.

        Returns:
            Token if matched, None otherwise
        """
        char = self._peek()
        if char is None or not (char.isalpha() or char == "_"):
            return None

        # Special case: standalone underscore is UNDERSCORE token
        if char == "_":
            # Check if next char is alphanumeric or underscore (part of identifier)
            next_char = self._peek(1)
            if next_char is None or not (next_char.isalnum() or next_char == "_"):
                # Standalone underscore
                self._advance()
                return Token(TokenType.UNDERSCORE, "_", self.line, self.col)

        value = ""
        while self._peek() and (self._peek().isalnum() or self._peek() == "_"):
            value += self._peek()
            self._advance()

        # Check if it's a keyword
        token_type = KEYWORDS.get(value.lower(), TokenType.IDENTIFIER)

        return Token(token_type, value, self.line, self.col)


def tokenize(source: str) -> list[Token]:
    """Convenience function to tokenize source code.

    Args:
        source: Source code to tokenize

    Returns:
        List of tokens

    Raises:
        LexerError: If tokenization fails
    """
    tokenizer = Tokenizer(source)
    return list(tokenizer.tokenize())

