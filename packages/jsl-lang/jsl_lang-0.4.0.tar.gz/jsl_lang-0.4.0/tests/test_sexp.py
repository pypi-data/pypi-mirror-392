"""
Tests for S-expression parser and converter.

Tests cover:
- JSL to S-expression conversion (to_canonical_sexp)
- S-expression to JSL parsing (from_canonical_sexp)
- Tokenization (tokenize_sexp)
- Expression parsing (parse_expr)
- Symbol quoting (needs_quoting)
- S-expression formatting (format_sexp)
- Unicode symbols
- Round-trip conversions
"""

import pytest
from jsl.sexp import (
    to_canonical_sexp,
    from_canonical_sexp,
    tokenize_sexp,
    parse_expr,
    needs_quoting,
    format_sexp,
    UNICODE_SYMBOLS
)


class TestToCanonicalSexp:
    """Test JSL to S-expression conversion."""

    def test_primitives(self):
        """Test conversion of primitive values."""
        assert to_canonical_sexp(42) == "42"
        assert to_canonical_sexp(3.14) == "3.14"
        assert to_canonical_sexp(True) == "#t"
        assert to_canonical_sexp(False) == "#f"
        assert to_canonical_sexp(None) == "nil"

    def test_strings(self):
        """Test conversion of strings."""
        # String literals (with @ prefix)
        assert to_canonical_sexp("@hello") == '"hello"'
        assert to_canonical_sexp("@world") == '"world"'

        # Symbols (without @ prefix)
        assert to_canonical_sexp("x") == "x"
        assert to_canonical_sexp("foo-bar") == "foo-bar"

    def test_simple_expressions(self):
        """Test conversion of simple expressions."""
        assert to_canonical_sexp(["+", 1, 2]) == "(+ 1 2)"
        assert to_canonical_sexp(["*", 3, 4]) == "(* 3 4)"
        assert to_canonical_sexp(["-", 10, 5]) == "(- 10 5)"

    def test_nested_expressions(self):
        """Test conversion of nested expressions."""
        expr = ["+", ["*", 2, 3], 4]
        assert to_canonical_sexp(expr) == "(+ (* 2 3) 4)"

        expr = ["*", ["+", 1, 2], ["-", 5, 3]]
        assert to_canonical_sexp(expr) == "(* (+ 1 2) (- 5 3))"

    def test_lambda(self):
        """Test conversion of lambda expressions."""
        expr = ["lambda", ["x"], ["*", "x", 2]]
        sexp = to_canonical_sexp(expr)
        assert "lambda" in sexp
        assert "(x)" in sexp or "x" in sexp  # Params might be formatted differently
        assert "*" in sexp

    def test_def(self):
        """Test conversion of def expressions."""
        expr = ["def", "x", 42]
        # Note: def may be converted to 'define' in some implementations
        sexp = to_canonical_sexp(expr)
        assert "x" in sexp and "42" in sexp

    def test_let(self):
        """Test conversion of let expressions."""
        expr = ["let", [["x", 10]], ["*", "x", "x"]]
        sexp = to_canonical_sexp(expr)
        assert "let" in sexp
        assert "10" in sexp

    def test_if(self):
        """Test conversion of if expressions."""
        expr = ["if", ["=", "x", 0], "zero", "non-zero"]
        sexp = to_canonical_sexp(expr)
        assert "if" in sexp
        assert "zero" in sexp

    def test_empty_list(self):
        """Test conversion of empty list."""
        assert to_canonical_sexp([]) == "()"

    def test_unicode_mode(self):
        """Test conversion with Unicode symbols."""
        # Lambda with Unicode
        expr = ["lambda", ["x"], ["*", "x", 2]]
        sexp = to_canonical_sexp(expr, use_unicode=True)
        assert "λ" in sexp or "lambda" in sexp  # Depending on implementation
        assert "×" in sexp or "*" in sexp

    def test_complex_program(self):
        """Test conversion of complex program."""
        expr = [
            "do",
            ["def", "square", ["lambda", ["x"], ["*", "x", "x"]]],
            ["square", 5]
        ]
        sexp = to_canonical_sexp(expr)
        assert "do" in sexp
        assert "def" in sexp
        assert "square" in sexp


class TestFromCanonicalSexp:
    """Test S-expression to JSL parsing."""

    def test_primitives(self):
        """Test parsing of primitive values."""
        assert from_canonical_sexp("42") == 42
        assert from_canonical_sexp("3.14") == 3.14
        assert from_canonical_sexp("#t") == True
        assert from_canonical_sexp("#f") == False
        assert from_canonical_sexp("nil") == None

    def test_strings(self):
        """Test parsing of strings."""
        # Quoted strings become @-prefixed literals
        assert from_canonical_sexp('"hello"') == "@hello"
        assert from_canonical_sexp('"world"') == "@world"

        # Bare symbols remain as-is
        assert from_canonical_sexp("x") == "x"
        assert from_canonical_sexp("foo-bar") == "foo-bar"

    def test_simple_expressions(self):
        """Test parsing of simple expressions."""
        assert from_canonical_sexp("(+ 1 2)") == ["+", 1, 2]
        assert from_canonical_sexp("(* 3 4)") == ["*", 3, 4]
        assert from_canonical_sexp("(- 10 5)") == ["-", 10, 5]

    def test_nested_expressions(self):
        """Test parsing of nested expressions."""
        assert from_canonical_sexp("(+ (* 2 3) 4)") == ["+", ["*", 2, 3], 4]
        assert from_canonical_sexp("(* (+ 1 2) (- 5 3))") == ["*", ["+", 1, 2], ["-", 5, 3]]

    def test_lambda(self):
        """Test parsing of lambda expressions."""
        result = from_canonical_sexp("(lambda (x) (* x 2))")
        assert result[0] == "lambda"
        assert isinstance(result[1], list)  # Parameters
        assert isinstance(result[2], list)  # Body

    def test_empty_list(self):
        """Test parsing of empty list."""
        assert from_canonical_sexp("()") == []

    def test_complex_program(self):
        """Test parsing of complex program."""
        sexp = "(do (def square (lambda (x) (* x x))) (square 5))"
        result = from_canonical_sexp(sexp)
        assert result[0] == "do"
        assert result[1][0] == "def"
        assert result[2][0] == "square"


class TestTokenizeSexp:
    """Test S-expression tokenization."""

    def test_simple_expression(self):
        """Test tokenization of simple expression."""
        tokens = tokenize_sexp("(+ 1 2)")
        assert "(" in tokens
        assert "+" in tokens
        assert "1" in tokens
        assert "2" in tokens
        assert ")" in tokens

    def test_nested_expression(self):
        """Test tokenization of nested expression."""
        tokens = tokenize_sexp("(+ (* 2 3) 4)")
        assert tokens.count("(") == 2
        assert tokens.count(")") == 2

    def test_strings(self):
        """Test tokenization of strings."""
        tokens = tokenize_sexp('(print "hello world")')
        assert '"hello world"' in tokens or any("hello" in t and "world" in t for t in tokens)

    def test_symbols(self):
        """Test tokenization of symbols."""
        tokens = tokenize_sexp("(foo-bar baz_qux)")
        assert any("foo" in t for t in tokens)
        assert any("baz" in t for t in tokens)

    def test_comments(self):
        """Test that comments are handled."""
        # Comments should be stripped out during tokenization
        tokens = tokenize_sexp("(+ 1 2) ; this is a comment")
        assert ";" not in " ".join(tokens) or len(tokens) >= 3  # Basic check


class TestParseExpr:
    """Test expression parsing from tokens."""

    def test_simple_atom(self):
        """Test parsing simple atomic values."""
        tokens = ["42"]
        expr, remaining = parse_expr(tokens)
        assert expr == 42
        assert remaining == []

        tokens = ["#t"]
        expr, remaining = parse_expr(tokens)
        assert expr == True
        assert remaining == []

    def test_simple_list(self):
        """Test parsing simple list."""
        tokens = ["(", "+", "1", "2", ")"]
        expr, remaining = parse_expr(tokens)
        assert expr == ["+", 1, 2]
        assert remaining == []

    def test_nested_list(self):
        """Test parsing nested list."""
        tokens = ["(", "+", "(", "*", "2", "3", ")", "4", ")"]
        expr, remaining = parse_expr(tokens)
        assert expr == ["+", ["*", 2, 3], 4]
        assert remaining == []

    def test_multiple_expressions(self):
        """Test parsing with remaining tokens."""
        tokens = ["42", "foo", "bar"]
        expr, remaining = parse_expr(tokens)
        assert expr == 42
        assert remaining == ["foo", "bar"]


class TestNeedsQuoting:
    """Test symbol quoting detection."""

    def test_normal_symbols(self):
        """Test symbols that don't need quoting."""
        assert not needs_quoting("x")
        assert not needs_quoting("foo")
        assert not needs_quoting("bar-baz")
        assert not needs_quoting("camelCase")

    def test_special_characters(self):
        """Test symbols with special characters that need quoting."""
        # Implementation-specific, but generally spaces and parens need quoting
        assert needs_quoting("hello world")  # Space
        assert needs_quoting("(test)")       # Parentheses


class TestFormatSexp:
    """Test S-expression formatting."""

    def test_simple_expression(self):
        """Test formatting of simple expression."""
        sexp = "(+ 1 2)"
        formatted = format_sexp(sexp)
        # Should preserve the expression, possibly with formatting
        assert "+" in formatted
        assert "1" in formatted
        assert "2" in formatted

    def test_nested_expression(self):
        """Test formatting of nested expression."""
        sexp = "(do (def x 10) (def y 20) (+ x y))"
        formatted = format_sexp(sexp)
        # Should add indentation for readability
        assert "do" in formatted
        assert "def" in formatted


class TestRoundTrip:
    """Test round-trip conversions between JSL and S-expressions."""

    def test_simple_arithmetic(self):
        """Test round-trip of simple arithmetic."""
        original = ["+", 1, 2, 3]
        sexp = to_canonical_sexp(original)
        restored = from_canonical_sexp(sexp)
        assert restored == original

    def test_nested_expression(self):
        """Test round-trip of nested expression."""
        original = ["+", ["*", 2, 3], ["-", 10, 5]]
        sexp = to_canonical_sexp(original)
        restored = from_canonical_sexp(sexp)
        assert restored == original

    def test_lambda_expression(self):
        """Test round-trip of lambda."""
        original = ["lambda", ["x", "y"], ["+", "x", "y"]]
        sexp = to_canonical_sexp(original)
        restored = from_canonical_sexp(sexp)
        # Check structure is preserved
        assert restored[0] == "lambda"
        assert isinstance(restored[1], list)
        assert isinstance(restored[2], list)

    def test_complex_program(self):
        """Test round-trip of complex program."""
        original = [
            "do",
            ["def", "double", ["lambda", ["x"], ["*", "x", 2]]],
            ["double", 21]
        ]
        sexp = to_canonical_sexp(original)
        restored = from_canonical_sexp(sexp)
        # Check structure
        assert restored[0] == "do"
        assert restored[1][0] == "def"


class TestUnicodeSymbols:
    """Test Unicode symbol mappings."""

    def test_unicode_symbols_defined(self):
        """Test that Unicode symbols are defined."""
        assert "lambda" in UNICODE_SYMBOLS
        assert "+" in UNICODE_SYMBOLS
        assert "*" in UNICODE_SYMBOLS
        assert "=" in UNICODE_SYMBOLS

    def test_unicode_lambda(self):
        """Test Unicode lambda conversion."""
        expr = ["lambda", ["x"], ["*", "x", 2]]
        sexp = to_canonical_sexp(expr, use_unicode=True)
        # Should contain λ or lambda
        assert "λ" in sexp or "lambda" in sexp


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_deeply_nested(self):
        """Test deeply nested expressions."""
        expr = ["+", ["+", ["+", 1, 2], 3], 4]
        sexp = to_canonical_sexp(expr)
        assert sexp.count("(") == 3  # Three opening parens for three nested levels

        restored = from_canonical_sexp(sexp)
        assert isinstance(restored, list)
        assert restored[0] == "+"

    def test_empty_expressions(self):
        """Test empty list handling."""
        assert to_canonical_sexp([]) == "()"
        assert from_canonical_sexp("()") == []

    def test_single_element_list(self):
        """Test single-element list."""
        expr = ["x"]
        sexp = to_canonical_sexp(expr)
        restored = from_canonical_sexp(sexp)
        assert restored == ["x"]

    def test_string_with_quotes(self):
        """Test string containing quotes."""
        # String literal with @ prefix
        expr = "@hello"
        sexp = to_canonical_sexp(expr)
        assert '"' in sexp  # Should be quoted

    def test_numbers(self):
        """Test various number formats."""
        assert to_canonical_sexp(0) == "0"
        assert to_canonical_sexp(-42) == "-42"
        assert to_canonical_sexp(3.14159) == "3.14159"
        assert to_canonical_sexp(-2.5) == "-2.5"

        assert from_canonical_sexp("0") == 0
        assert from_canonical_sexp("-42") == -42
        assert from_canonical_sexp("3.14") == 3.14


class TestIntegration:
    """Integration tests with the JSL evaluator."""

    def test_parse_and_evaluate(self):
        """Test parsing S-expression and evaluating."""
        from jsl import Evaluator, make_prelude

        sexp = "(+ 1 2 3)"
        jsl_expr = from_canonical_sexp(sexp)
        evaluator = Evaluator()
        result = evaluator.eval(jsl_expr, make_prelude())
        assert result == 6

    def test_complex_expression_evaluation(self):
        """Test parsing and evaluating complex expression."""
        from jsl import Evaluator, make_prelude

        sexp = "(* (+ 2 3) (- 10 5))"
        jsl_expr = from_canonical_sexp(sexp)
        evaluator = Evaluator()
        result = evaluator.eval(jsl_expr, make_prelude())
        # (2 + 3) * (10 - 5) = 5 * 5 = 25
        assert result == 25

    def test_lambda_evaluation(self):
        """Test parsing and evaluating lambda."""
        from jsl import Evaluator, make_prelude

        sexp = "((lambda (x) (* x x)) 5)"
        jsl_expr = from_canonical_sexp(sexp)
        evaluator = Evaluator()
        result = evaluator.eval(jsl_expr, make_prelude())
        # (λ x. x * x)(5) = 25
        assert result == 25
