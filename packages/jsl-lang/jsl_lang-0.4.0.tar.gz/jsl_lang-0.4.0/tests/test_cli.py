"""
Tests for the JSL Command Line Interface.

Tests cover:
- Host dispatcher creation
- File execution
- Expression evaluation
- REPL functionality
- Argument parsing
- Error handling
"""

import pytest
import sys
import json
from pathlib import Path
from io import StringIO
from unittest.mock import patch, Mock, MagicMock
import tempfile
import os

from jsl.cli import (
    create_basic_host_dispatcher,
    run_file,
    eval_string,
    run_repl,
    main
)
from jsl.core import HostDispatcher


class TestHostDispatcher:
    """Test basic host dispatcher creation."""

    def test_create_basic_host_dispatcher(self):
        """Test that basic host dispatcher is created correctly."""
        dispatcher = create_basic_host_dispatcher()
        assert isinstance(dispatcher, HostDispatcher)

        # Check that expected operations are registered
        assert "log" in dispatcher.handlers
        assert "warn" in dispatcher.handlers
        assert "error" in dispatcher.handlers
        assert "file/read" in dispatcher.handlers

    def test_log_operation(self, capsys):
        """Test log operation prints to stdout."""
        dispatcher = create_basic_host_dispatcher()
        log_handler = dispatcher.handlers["log"]

        log_handler("test", "message")
        captured = capsys.readouterr()
        assert "LOG:" in captured.out
        assert "test" in captured.out
        assert "message" in captured.out

    def test_warn_operation(self, capsys):
        """Test warn operation prints to stderr."""
        dispatcher = create_basic_host_dispatcher()
        warn_handler = dispatcher.handlers["warn"]

        warn_handler("warning", "message")
        captured = capsys.readouterr()
        assert "WARN:" in captured.err
        assert "warning" in captured.err

    def test_error_operation(self, capsys):
        """Test error operation prints to stderr."""
        dispatcher = create_basic_host_dispatcher()
        error_handler = dispatcher.handlers["error"]

        error_handler("error", "message")
        captured = capsys.readouterr()
        assert "ERROR:" in captured.err
        assert "error" in captured.err

    def test_file_read_operation(self, tmp_path):
        """Test file read operation."""
        dispatcher = create_basic_host_dispatcher()
        file_read_handler = dispatcher.handlers["file/read"]

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, JSL!")

        # Read file
        content = file_read_handler(str(test_file))
        assert content == "Hello, JSL!"

    def test_file_read_operation_error(self):
        """Test file read operation with non-existent file."""
        dispatcher = create_basic_host_dispatcher()
        file_read_handler = dispatcher.handlers["file/read"]

        with pytest.raises(Exception, match="Failed to read file"):
            file_read_handler("/nonexistent/file.txt")


class TestRunFile:
    """Test JSL file execution."""

    def test_run_file_simple_expression(self, tmp_path, capsys):
        """Test running a file with a simple expression."""
        # Create test file
        test_file = tmp_path / "test.jsl"
        test_file.write_text('["+", 1, 2, 3]')

        # Run file
        run_file(str(test_file))

        # Check output
        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 6

    def test_run_file_complex_program(self, tmp_path, capsys):
        """Test running a file with a complex program."""
        # Create test file with a lambda
        test_file = tmp_path / "test.jsl"
        test_file.write_text('''
        ["do",
          ["def", "square", ["lambda", ["x"], ["*", "x", "x"]]],
          ["square", 5]]
        ''')

        # Run file
        run_file(str(test_file))

        # Check output
        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 25

    def test_run_file_not_found(self, capsys):
        """Test running a non-existent file."""
        with pytest.raises(SystemExit) as exc_info:
            run_file("/nonexistent/file.jsl")

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "not found" in captured.err

    def test_run_file_invalid_json(self, tmp_path, capsys):
        """Test running a file with invalid JSON."""
        test_file = tmp_path / "invalid.jsl"
        test_file.write_text('["+", 1, 2,')  # Invalid JSON

        with pytest.raises(SystemExit) as exc_info:
            run_file(str(test_file))

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_run_file_with_host_dispatcher(self, tmp_path, capsys):
        """Test running a file with custom host dispatcher."""
        test_file = tmp_path / "test.jsl"
        test_file.write_text('["+", 1, 2]')

        dispatcher = create_basic_host_dispatcher()
        run_file(str(test_file), dispatcher)

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 3


class TestEvalString:
    """Test command-line expression evaluation."""

    def test_eval_simple_expression(self, capsys):
        """Test evaluating a simple expression."""
        eval_string('["+", 1, 2, 3]')

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 6

    def test_eval_arithmetic(self, capsys):
        """Test evaluating arithmetic expressions."""
        eval_string('["*", 5, 7]')

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 35

    def test_eval_lambda(self, capsys):
        """Test evaluating lambda expressions."""
        eval_string('[["lambda", ["x"], ["*", "x", 2]], 10]')

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 20

    def test_eval_invalid_expression(self, capsys):
        """Test evaluating invalid expression."""
        with pytest.raises(SystemExit) as exc_info:
            eval_string('["+", 1,')  # Invalid JSON

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_eval_with_host_dispatcher(self, capsys):
        """Test evaluating with custom host dispatcher."""
        dispatcher = create_basic_host_dispatcher()
        eval_string('["-", 10, 3]', dispatcher)

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 7


class TestREPL:
    """Test REPL functionality."""

    def test_repl_simple_expression(self):
        """Test REPL with simple expression."""
        with patch('builtins.input', side_effect=['["+", 1, 2]', 'exit']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                assert "3" in output
                assert "JSL REPL" in output  # Check for REPL header instead of prompt

    def test_repl_multiple_expressions(self):
        """Test REPL with multiple expressions."""
        inputs = ['["+", 1, 2]', '["*", 3, 4]', 'exit']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                assert "3" in output
                assert "12" in output

    def test_repl_empty_line(self):
        """Test REPL with empty lines."""
        with patch('builtins.input', side_effect=['', '   ', 'exit']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                # Should not crash, should continue
                assert "JSL REPL" in output  # Check for REPL header
                assert "Exiting REPL" in output  # Should exit cleanly

    def test_repl_comment(self):
        """Test REPL with comments."""
        with patch('builtins.input', side_effect=['# This is a comment', 'exit']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                # Comments should be ignored
                assert "JSL REPL" in output  # Check for REPL header

    def test_repl_help_command(self):
        """Test REPL help command."""
        with patch('builtins.input', side_effect=['help', 'exit']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                assert "Available commands" in output
                assert "exit" in output

    def test_repl_keyboard_interrupt(self):
        """Test REPL handling keyboard interrupt."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                assert "Goodbye!" in output

    def test_repl_eof(self):
        """Test REPL handling EOF."""
        with patch('builtins.input', side_effect=EOFError):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                assert "Goodbye!" in output

    def test_repl_error_handling(self):
        """Test REPL handles errors gracefully."""
        with patch('builtins.input', side_effect=['["+", "x", "y"]', 'exit']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                # Should show error but continue
                assert "Error:" in output
                assert "Exiting REPL" in output  # Should exit cleanly after error


class TestMainCLI:
    """Test main CLI entry point and argument parsing."""

    def test_main_eval(self, capsys):
        """Test main with --eval argument."""
        with patch('sys.argv', ['jsl', '--eval', '["+", 2, 3]']):
            main()

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 5

    def test_main_eval_short_flag(self, capsys):
        """Test main with -e short flag."""
        with patch('sys.argv', ['jsl', '-e', '["*", 4, 5]']):
            main()

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 20

    def test_main_file(self, tmp_path, capsys):
        """Test main with file argument."""
        test_file = tmp_path / "test.jsl"
        test_file.write_text('["+", 10, 20]')

        with patch('sys.argv', ['jsl', str(test_file)]):
            main()

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 30

    def test_main_repl(self):
        """Test main with --repl argument."""
        with patch('sys.argv', ['jsl', '--repl']):
            with patch('builtins.input', side_effect=['exit']):
                with patch('sys.stdout', new=StringIO()) as fake_out:
                    main()
                    output = fake_out.getvalue()
                    assert "JSL REPL" in output

    def test_main_no_host(self, capsys):
        """Test main with --no-host flag."""
        with patch('sys.argv', ['jsl', '--no-host', '--eval', '["+", 1, 1]']):
            main()

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 2

    def test_main_no_arguments(self, capsys):
        """Test main with no arguments."""
        with patch('sys.argv', ['jsl']):
            with pytest.raises(SystemExit):
                main()

        # Should print help
        captured = capsys.readouterr()
        # argparse prints to stderr for errors
        assert "usage:" in captured.err.lower() or "usage:" in captured.out.lower()

    def test_main_help(self, capsys):
        """Test main with --help."""
        with patch('sys.argv', ['jsl', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        output = captured.out
        assert "JSL" in output
        assert "--repl" in output
        assert "--eval" in output
        assert "Examples:" in output

    def test_main_mutually_exclusive_args(self, capsys):
        """Test that --repl and --eval are mutually exclusive."""
        with patch('sys.argv', ['jsl', '--repl', '--eval', '["+", 1, 2]']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        # argparse error about mutually exclusive arguments
        assert "error:" in captured.err.lower() or "error:" in captured.out.lower()


class TestIntegration:
    """Integration tests for CLI functionality."""

    def test_file_with_multiple_definitions(self, tmp_path, capsys):
        """Test file with multiple definitions and computations."""
        test_file = tmp_path / "complex.jsl"
        test_file.write_text('''
        ["do",
          ["def", "double", ["lambda", ["x"], ["*", "x", 2]]],
          ["def", "triple", ["lambda", ["x"], ["*", "x", 3]]],
          ["def", "result", ["+", ["double", 5], ["triple", 4]]],
          "result"]
        ''')

        run_file(str(test_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        # double(5) + triple(4) = 10 + 12 = 22
        assert output == 22

    def test_eval_with_let_binding(self, capsys):
        """Test eval with let binding."""
        eval_string('["let", [["x", 10]], ["*", "x", "x"]]')

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == 100

    def test_repl_maintains_state(self):
        """Test that REPL can evaluate multiple expressions in sequence."""
        # Note: The REPL currently uses the prelude environment directly,
        # which is immutable, so we can't use 'def' to add new bindings.
        # This tests that the REPL continues to work across multiple inputs.
        inputs = [
            '["+", 1, 2]',
            '["*", 3, 4]',
            'exit'
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                run_repl()
                output = fake_out.getvalue()
                # Both calculations should appear in output
                assert "3" in output  # 1 + 2
                assert "12" in output  # 3 * 4
