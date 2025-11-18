"""Recursive-descent parser for RLang.

Converts token streams into Abstract Syntax Trees.
"""

from __future__ import annotations

from typing import Optional

from rlang.lexer import LexerError, Token, TokenType, tokenize

from .ast import (
    AttributeRef,
    BinaryOp,
    Call,
    Expr,
    ExprStmt,
    FunctionDecl,
    GenericType,
    Identifier,
    IfExpr,
    Literal,
    Module,
    Param,
    PipelineDecl,
    PipelineStep,
    SimpleType,
    Statement,
    TopLevelDecl,
    TypeAlias,
    TypeExpr,
)


class ParseError(Exception):
    """Exception raised when parser encounters invalid syntax."""

    def __init__(self, message: str, line: int, col: int):
        """Initialize parse error with position information.

        Args:
            message: Error message
            line: 1-based line number
            col: 1-based column number
        """
        super().__init__(f"{message} at line {line}, column {col}")
        self.line = line
        self.col = col


class Parser:
    """Recursive-descent parser for RLang."""

    def __init__(self, tokens: list[Token]):
        """Initialize parser with token list.

        Args:
            tokens: List of tokens to parse
        """
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Optional[Token]:
        """Get current token.

        Returns:
            Current token, or None if at end
        """
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def _advance(self) -> Optional[Token]:
        """Advance to next token.

        Returns:
            New current token, or None if at end
        """
        if self.pos < len(self.tokens):
            self.pos += 1
        return self._current()

    def _check(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types.

        Args:
            *types: Token types to check

        Returns:
            True if current token matches any type
        """
        token = self._current()
        if token is None:
            return False
        return token.type in types

    def _match(self, *types: TokenType) -> bool:
        """Match and consume token if it matches any of the given types.

        Args:
            *types: Token types to match

        Returns:
            True if matched and consumed
        """
        if self._check(*types):
            self._advance()
            return True
        return False

    def _expect(self, *types: TokenType, message: Optional[str] = None) -> Token:
        """Expect and consume a token of one of the given types.

        Args:
            *types: Expected token types
            message: Optional custom error message

        Returns:
            The consumed token

        Raises:
            ParseError: If token doesn't match expected types
        """
        token = self._current()
        if token is None:
            msg = message or f"Expected {types}, got EOF"
            raise ParseError(msg, self.tokens[-1].line if self.tokens else 1, 1)

        if token.type not in types:
            msg = message or f"Expected {types}, got {token.type.value}"
            raise ParseError(msg, token.line, token.col)

        self._advance()
        return token

    def parse_module(self) -> Module:
        """Parse a complete module.

        Returns:
            Module AST node

        Grammar:
            module := { top_level_decl }
        """
        start_token = self._current() or self.tokens[0] if self.tokens else None
        start_line = start_token.line if start_token else 1
        start_col = start_token.col if start_token else 1

        decls: list[TopLevelDecl] = []

        while not self._check(TokenType.EOF):
            # Skip newlines between declarations
            while self._match(TokenType.NEWLINE):
                pass

            if self._check(TokenType.EOF):
                break

            decl = self._parse_top_level_decl()
            if decl:
                decls.append(decl)

            # Expect semicolon after declarations (except pipelines which use braces)
            if isinstance(decl, PipelineDecl):
                # Skip newlines after pipeline
                while self._match(TokenType.NEWLINE):
                    pass
            else:
                self._expect(TokenType.SEMICOLON, message="Expected ';' after declaration")

        end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token
        end_line = end_token.line if end_token else start_line
        end_col = end_token.col if end_token else start_col

        return Module(decls=decls, start_line=start_line, start_col=start_col, end_line=end_line, end_col=end_col)

    def _parse_top_level_decl(self) -> TopLevelDecl:
        """Parse a top-level declaration.

        Returns:
            Top-level declaration AST node

        Grammar:
            top_level_decl := type_alias | function_decl | pipeline_decl
        """
        token = self._current()
        if token is None:
            raise ParseError("Unexpected EOF", 1, 1)

        # Check for "fn", "type", or "pipeline" identifiers
        if token.type == TokenType.IDENTIFIER:
            value_lower = token.value.lower()
            if value_lower == "fn":
                self._advance()
                return self._parse_function_decl()
            elif value_lower == "type":
                self._advance()
                return self._parse_type_alias()
            elif value_lower == "pipeline":
                self._advance()
                return self._parse_pipeline_decl()

        # Also check for KEYWORD_FUNCTION (if "function" keyword exists)
        if self._match(TokenType.KEYWORD_FUNCTION):
            return self._parse_function_decl()

        # Provide more helpful error messages for common mistakes
        if token.type == TokenType.RBRACE:
            raise ParseError(
                f"Unexpected closing brace '}}' - did you add an extra closing brace?",
                token.line,
                token.col,
            )

        raise ParseError(
            f"Expected top-level declaration (fn, type, or pipeline), got {token.type.value}",
            token.line,
            token.col,
        )

    def _parse_type_alias(self) -> TypeAlias:
        """Parse a type alias declaration.

        Returns:
            TypeAlias AST node

        Grammar:
            type_alias := 'type' IDENT '=' type_expr
        """
        start_token = self.tokens[self.pos - 1] if self.pos > 0 else self._current()
        if not start_token:
            raise ParseError("Unexpected EOF", 1, 1)

        name_token = self._expect(TokenType.IDENTIFIER, message="Expected type name")
        self._expect(TokenType.OP_ASSIGN, message="Expected '='")

        target = self._parse_type_expr()

        end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token

        return TypeAlias(
            name=name_token.value,
            target=target,
            start_line=start_token.line,
            start_col=start_token.col,
            end_line=end_token.line,
            end_col=end_token.col,
        )

    def _parse_function_decl(self) -> FunctionDecl:
        """Parse a function declaration.

        Returns:
            FunctionDecl AST node

        Grammar:
            function_decl := 'fn' IDENT '(' param_list? ')' '->' type_expr? ';'
        """
        # "fn" was already consumed in _parse_top_level_decl
        start_token = self.tokens[self.pos - 1] if self.pos > 0 else self._current()

        name_token = self._expect(TokenType.IDENTIFIER, message="Expected function name")
        self._expect(TokenType.LPAREN, message="Expected '('")

        params: list[Param] = []
        if not self._check(TokenType.RPAREN):
            params = self._parse_param_list()

        self._expect(TokenType.RPAREN, message="Expected ')'")

        return_type: Optional[TypeExpr] = None
        if self._match(TokenType.OP_ARROW):
            return_type = self._parse_type_expr()

        end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token

        return FunctionDecl(
            name=name_token.value,
            params=params,
            return_type=return_type,
            body=[],
            start_line=start_token.line if start_token else 1,
            start_col=start_token.col if start_token else 1,
            end_line=end_token.line,
            end_col=end_token.col,
        )

    def _parse_param_list(self) -> list[Param]:
        """Parse a parameter list.

        Returns:
            List of Param nodes

        Grammar:
            param_list := param (',' param)*
        """
        params: list[Param] = []

        while True:
            param = self._parse_param()
            params.append(param)

            if not self._match(TokenType.COMMA):
                break

        return params

    def _parse_param(self) -> Param:
        """Parse a single parameter.

        Returns:
            Param AST node

        Grammar:
            param := IDENT (':' type_expr)?
        """
        start_token = self._expect(TokenType.IDENTIFIER, message="Expected parameter name")

        param_type: Optional[TypeExpr] = None
        if self._match(TokenType.COLON):
            param_type = self._parse_type_expr()

        end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token

        return Param(
            name=start_token.value,
            type=param_type,
            start_line=start_token.line,
            start_col=start_token.col,
            end_line=end_token.line,
            end_col=end_token.col,
        )

    def _parse_pipeline_decl(self) -> PipelineDecl:
        """Parse a pipeline declaration.

        Returns:
            PipelineDecl AST node

        Grammar:
            pipeline_decl := 'pipeline' IDENT '(' type_expr? ')' '->' type_expr? '{' pipeline_steps '}'
        """
        start_token = self.tokens[self.pos - 1] if self.pos > 0 else self._current()

        name_token = self._expect(TokenType.IDENTIFIER, message="Expected pipeline name")
        self._expect(TokenType.LPAREN, message="Expected '('")

        input_type: Optional[TypeExpr] = None
        if not self._check(TokenType.RPAREN):
            input_type = self._parse_type_expr()

        self._expect(TokenType.RPAREN, message="Expected ')'")

        output_type: Optional[TypeExpr] = None
        if self._match(TokenType.OP_ARROW):
            output_type = self._parse_type_expr()

        self._expect(TokenType.LBRACE, message="Expected '{'")

        steps = self._parse_pipeline_steps()

        self._expect(TokenType.RBRACE, message="Expected '}'")

        end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token

        return PipelineDecl(
            name=name_token.value,
            input_type=input_type,
            output_type=output_type,
            steps=steps,
            start_line=start_token.line if start_token else 1,
            start_col=start_token.col if start_token else 1,
            end_line=end_token.line,
            end_col=end_token.col,
        )

    def _parse_pipeline_steps(self) -> list[PipelineStep]:
        """Parse pipeline steps.

        Returns:
            List of PipelineStep nodes

        Grammar:
            pipeline_steps := step ('->' step)*
        """
        steps: list[PipelineStep] = []

        # Skip leading whitespace/newlines
        while self._match(TokenType.NEWLINE):
            pass

        # Parse first step (can be identifier or if expression)
        if self._check(TokenType.KEYWORD_IF):
            # If expression - parse and store in PipelineStep.expr field
            if_expr = self._parse_if_expr()
            step = PipelineStep(
                name="",  # Empty name for expression steps
                args=[],
                expr=if_expr,
                start_line=if_expr.start_line,
                start_col=if_expr.start_col,
                end_line=if_expr.end_line,
                end_col=if_expr.end_col,
            )
            steps.append(step)
        elif not self._check(TokenType.IDENTIFIER):
            # Empty pipeline
            return steps
        else:
            step = self._parse_pipeline_step()
            steps.append(step)

        # Parse remaining steps connected by '->'
        while True:
            # Skip whitespace/newlines
            while self._match(TokenType.NEWLINE):
                pass

            if not self._match(TokenType.OP_ARROW):
                break

            # Skip whitespace after '->'
            while self._match(TokenType.NEWLINE):
                pass

            # Check for if expression or regular step
            if self._check(TokenType.KEYWORD_IF):
                if_expr = self._parse_if_expr()
                step = PipelineStep(
                    name="",
                    args=[],
                    expr=if_expr,
                    start_line=if_expr.start_line,
                    start_col=if_expr.start_col,
                    end_line=if_expr.end_line,
                    end_col=if_expr.end_col,
                )
            else:
                step = self._parse_pipeline_step()
            steps.append(step)

        return steps

    def _parse_pipeline_step(self) -> PipelineStep:
        """Parse a single pipeline step.

        Returns:
            PipelineStep AST node

        Grammar:
            step := IDENT ('(' expr_list? ')')?
        """
        start_token = self._expect(TokenType.IDENTIFIER, message="Expected step name")

        args: list[Expr] = []
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                args = self._parse_expr_list()
            self._expect(TokenType.RPAREN, message="Expected ')'")

        end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token

        return PipelineStep(
            name=start_token.value,
            args=args,
            start_line=start_token.line,
            start_col=start_token.col,
            end_line=end_token.line,
            end_col=end_token.col,
        )

    def _parse_expr_list(self) -> list[Expr]:
        """Parse a comma-separated expression list.

        Returns:
            List of Expr nodes

        Grammar:
            expr_list := expr (',' expr)*
        """
        exprs: list[Expr] = []

        while True:
            expr = self.parse_expr()
            exprs.append(expr)

            if not self._match(TokenType.COMMA):
                break

        return exprs

    def _parse_type_expr(self) -> TypeExpr:
        """Parse a type expression.

        Returns:
            TypeExpr AST node

        Grammar:
            type_expr := IDENT ('<' type_expr (',' type_expr)* '>')?
        """
        start_token = self._expect(TokenType.IDENTIFIER, message="Expected type name")

        # Check for generic type arguments
        if self._match(TokenType.OP_LESS):
            type_args: list[TypeExpr] = []

            # Parse first type argument
            type_args.append(self._parse_type_expr())

            # Parse remaining arguments
            while self._match(TokenType.COMMA):
                type_args.append(self._parse_type_expr())

            self._expect(TokenType.OP_GREATER, message="Expected '>'")

            end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token

            return GenericType(
                name=start_token.value,
                type_args=type_args,
                start_line=start_token.line,
                start_col=start_token.col,
                end_line=end_token.line,
                end_col=end_token.col,
            )

        end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token

        return SimpleType(
            name=start_token.value,
            start_line=start_token.line,
            start_col=start_token.col,
            end_line=end_token.line,
            end_col=end_token.col,
        )

    def parse_expr(self) -> Expr:
        """Parse an expression with operator precedence.

        Returns:
            Expr AST node

        Grammar:
            expr := comparison (('+' | '-') comparison)*
        """
        left = self._parse_comparison()

        while self._match(TokenType.OP_PLUS, TokenType.OP_MINUS):
            op_token = self.tokens[self.pos - 1]
            right = self._parse_comparison()
            left = BinaryOp(
                op=op_token.value,
                left=left,
                right=right,
                start_line=left.start_line,
                start_col=left.start_col,
                end_line=right.end_line,
                end_col=right.end_col,
            )

        return left

    def _parse_comparison(self) -> Expr:
        """Parse a comparison expression (>, <, >=, <=, ==, !=).

        Returns:
            Expr AST node

        Grammar:
            comparison := term (('>' | '<' | '>=' | '<=' | '==' | '!=') term)*
        """
        left = self._parse_term()

        while self._match(
            TokenType.OP_GREATER,
            TokenType.OP_LESS,
            TokenType.OP_GREATER_EQUAL,
            TokenType.OP_LESS_EQUAL,
            TokenType.OP_EQUAL,
            TokenType.OP_NOT_EQUAL,
        ):
            op_token = self.tokens[self.pos - 1]
            right = self._parse_term()
            left = BinaryOp(
                op=op_token.value,
                left=left,
                right=right,
                start_line=left.start_line,
                start_col=left.start_col,
                end_line=right.end_line,
                end_col=right.end_col,
            )

        return left

    def _parse_term(self) -> Expr:
        """Parse a term (multiplication/division).

        Returns:
            Expr AST node

        Grammar:
            term := factor (('*' | '/') factor)*
        """
        left = self._parse_factor()

        while self._match(TokenType.OP_MULTIPLY, TokenType.OP_DIVIDE):
            op_token = self.tokens[self.pos - 1]
            right = self._parse_factor()
            left = BinaryOp(
                op=op_token.value,
                left=left,
                right=right,
                start_line=left.start_line,
                start_col=left.start_col,
                end_line=right.end_line,
                end_col=right.end_col,
            )

        return left

    def _parse_factor(self) -> Expr:
        """Parse a factor (unary plus/minus, primary).

        Returns:
            Expr AST node

        Grammar:
            factor := ('+' | '-')? primary
        """
        # Handle unary +/-
        if self._match(TokenType.OP_PLUS, TokenType.OP_MINUS):
            op_token = self.tokens[self.pos - 1]
            # For now, we'll just parse the primary
            # In a full implementation, we'd create a UnaryOp node
            primary = self._parse_primary()
            # Return primary as-is (unary ops can be added later)
            return primary

        return self._parse_primary()

    def _parse_primary(self) -> Expr:
        """Parse a primary expression.

        Returns:
            Expr AST node

        Grammar:
            primary := literal | identifier | call | '(' expr ')' | if_expr
        """
        token = self._current()
        if token is None:
            raise ParseError("Unexpected EOF in expression", 1, 1)

        # If expression
        if token.type == TokenType.KEYWORD_IF:
            return self._parse_if_expr()

        # Literals
        if token.type == TokenType.INTEGER:
            self._advance()
            return Literal(
                value=int(token.value),
                start_line=token.line,
                start_col=token.col,
                end_line=token.line,
                end_col=token.col + len(token.value),
            )

        if token.type == TokenType.FLOAT:
            self._advance()
            return Literal(
                value=float(token.value),
                start_line=token.line,
                start_col=token.col,
                end_line=token.line,
                end_col=token.col + len(token.value),
            )

        if token.type == TokenType.STRING:
            self._advance()
            return Literal(
                value=token.value,
                start_line=token.line,
                start_col=token.col,
                end_line=token.line,
                end_col=token.col + len(token.value) + 2,  # +2 for quotes
            )

        if token.type == TokenType.KEYWORD_TRUE:
            self._advance()
            return Literal(
                value=True,
                start_line=token.line,
                start_col=token.col,
                end_line=token.line,
                end_col=token.col + len(token.value),
            )

        if token.type == TokenType.KEYWORD_FALSE:
            self._advance()
            return Literal(
                value=False,
                start_line=token.line,
                start_col=token.col,
                end_line=token.line,
                end_col=token.col + len(token.value),
            )

        if token.type == TokenType.KEYWORD_NULL:
            self._advance()
            return Literal(
                value=None,
                start_line=token.line,
                start_col=token.col,
                end_line=token.line,
                end_col=token.col + len(token.value),
            )

        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self._advance()
            expr = self.parse_expr()
            self._expect(TokenType.RPAREN, message="Expected ')'")
            return expr

        # Identifier or call
        if token.type == TokenType.IDENTIFIER:
            self._advance()
            ident = Identifier(
                name=token.value,
                start_line=token.line,
                start_col=token.col,
                end_line=token.line,
                end_col=token.col + len(token.value),
            )

            # Check if it's a function call
            if self._match(TokenType.LPAREN):
                args: list[Expr] = []
                if not self._check(TokenType.RPAREN):
                    args = self._parse_expr_list()
                self._expect(TokenType.RPAREN, message="Expected ')'")

                end_token = self.tokens[self.pos - 1] if self.pos > 0 else token

                return Call(
                    func=ident,
                    args=args,
                    start_line=ident.start_line,
                    start_col=ident.start_col,
                    end_line=end_token.line,
                    end_col=end_token.col,
                )

            return ident

        raise ParseError(f"Unexpected token in expression: {token.type.value}", token.line, token.col)

    def _parse_if_expr(self) -> IfExpr:
        """Parse an if/else conditional expression.

        Returns:
            IfExpr AST node

        Grammar:
            if_expr := 'if' '(' expr ')' '{' pipeline_steps? '}' ('else' '{' pipeline_steps? '}')?
        """
        start_token = self._expect(TokenType.KEYWORD_IF, message="Expected 'if'")

        # Parse condition in parentheses
        self._expect(TokenType.LPAREN, message="Expected '(' after 'if'")
        condition = self.parse_expr()
        self._expect(TokenType.RPAREN, message="Expected ')' after if condition")

        # Parse THEN block
        self._expect(TokenType.LBRACE, message="Expected '{' to start then-block")
        then_steps: list[PipelineStep] = []
        if not self._check(TokenType.RBRACE):
            then_steps = self._parse_pipeline_steps()
        self._expect(TokenType.RBRACE, message="Expected '}' to end then-block")

        # Optional ELSE block
        else_steps: Optional[list[PipelineStep]] = None
        if self._match(TokenType.KEYWORD_ELSE):
            self._expect(TokenType.LBRACE, message="Expected '{' to start else-block")
            steps: list[PipelineStep] = []
            if not self._check(TokenType.RBRACE):
                steps = self._parse_pipeline_steps()
            self._expect(TokenType.RBRACE, message="Expected '}' to end else-block")
            else_steps = steps

        end_token = self.tokens[self.pos - 1] if self.pos > 0 else start_token

        return IfExpr(
            condition=condition,
            then_steps=then_steps,
            else_steps=else_steps,
            start_line=start_token.line,
            start_col=start_token.col,
            end_line=end_token.line,
            end_col=end_token.col,
        )


def parse(source: str) -> Module:
    """Parse RLang source code into an AST.

    Args:
        source: Source code to parse

    Returns:
        Module AST node

    Raises:
        LexerError: If tokenization fails
        ParseError: If parsing fails
    """
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse_module()


__all__ = ["ParseError", "Parser", "parse"]

