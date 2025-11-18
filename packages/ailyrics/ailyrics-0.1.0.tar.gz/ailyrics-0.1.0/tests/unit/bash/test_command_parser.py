"""
Unit tests for the Command Parser module.
"""

import pytest

from lyrics.bash.command_parser import (
    CommandParser,
    CommandType,
    PythonCommand,
    ReadCommand,
    ShellBuiltinCommand,
    SystemToolCommand,
    parse_command,
)


class TestCommandParser:
    """Test cases for CommandParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_parse_read_command(self):
        """Test parsing read commands."""
        result = self.parser.parse("read xlsx/SKILL.md")

        assert isinstance(result, ReadCommand)
        assert result.command_type == CommandType.READ
        assert result.target == "xlsx/SKILL.md"
        assert result.raw_command == "read xlsx/SKILL.md"
        assert result.working_dir is None

    def test_parse_python_command(self):
        """Test parsing python commands."""
        result = self.parser.parse("python xlsx/recalc.py output.xlsx 30")

        assert isinstance(result, PythonCommand)
        assert result.command_type == CommandType.PYTHON
        assert result.script == "xlsx/recalc.py"
        assert result.args == ["output.xlsx", "30"]
        assert result.raw_command == "python xlsx/recalc.py output.xlsx 30"

    def test_parse_system_tool_command(self):
        """Test parsing system tool commands."""
        result = self.parser.parse("pdftotext -layout input.pdf output.txt")

        assert isinstance(result, SystemToolCommand)
        assert result.command_type == CommandType.SYSTEM_TOOL
        assert result.tool == "pdftotext"
        assert result.args == ["-layout", "input.pdf", "output.txt"]

    def test_parse_shell_builtin_command(self):
        """Test parsing shell builtin commands."""
        result = self.parser.parse("echo hello")

        assert isinstance(result, ShellBuiltinCommand)
        assert result.command_type == CommandType.SHELL_BUILTIN
        assert result.builtin == "echo"
        assert result.args == ["hello"]

    def test_parse_unknown_command(self):
        """Test parsing unknown commands."""
        result = self.parser.parse("unknown-tool arg1 arg2")

        assert isinstance(result, SystemToolCommand)
        assert result.command_type == CommandType.SYSTEM_TOOL
        assert result.tool == "unknown-tool"
        assert result.args == ["arg1", "arg2"]

    def test_parse_empty_command(self):
        """Test parsing empty command raises ValueError."""
        with pytest.raises(ValueError, match="Empty command provided"):
            self.parser.parse("")

    def test_parse_whitespace_only_command(self):
        """Test parsing whitespace-only command raises ValueError."""
        with pytest.raises(ValueError, match="Empty command provided"):
            self.parser.parse("   \t\n  ")

    def test_parse_command_with_working_dir(self):
        """Test parsing command with working directory."""
        result = self.parser.parse("read test.txt", working_dir="/tmp")

        assert result.working_dir == "/tmp"

    def test_parse_command_with_shell_operators(self):
        """Test parsing commands with shell operators."""
        result = self.parser.parse("echo hello > output.txt")

        assert isinstance(result, ShellBuiltinCommand)
        assert result.builtin == "echo"
        assert result.args == ["hello", ">", "output.txt"]

    def test_parse_command_with_quotes(self):
        """Test parsing commands with quoted arguments."""
        result = self.parser.parse('echo "hello world"')

        assert isinstance(result, ShellBuiltinCommand)
        assert result.builtin == "echo"
        assert result.args == ["hello world"]

    def test_parse_read_command_with_no_args(self):
        """Test parsing read command with no arguments raises ValueError."""
        with pytest.raises(ValueError, match="read command expects exactly 1 argument"):
            self.parser.parse("read")

    def test_parse_read_command_with_too_many_args(self):
        """Test parsing read command with too many arguments raises ValueError."""
        with pytest.raises(ValueError, match="read command expects exactly 1 argument"):
            self.parser.parse("read file1 file2")

    def test_parse_python_command_with_no_args(self):
        """Test parsing python command with no arguments raises ValueError."""
        with pytest.raises(
            ValueError, match="python command expects at least a script path"
        ):
            self.parser.parse("python")

    def test_is_system_tool(self):
        """Test system tool detection."""
        assert self.parser.is_system_tool("pdftotext") is True
        assert self.parser.is_system_tool("soffice") is True
        assert self.parser.is_system_tool("unknown-tool") is False
        assert self.parser.is_system_tool("ls") is True  # Also in shell builtins

    def test_is_shell_builtin(self):
        """Test shell builtin detection."""
        assert self.parser.is_shell_builtin("cd") is True
        assert self.parser.is_shell_builtin("pwd") is True
        assert self.parser.is_shell_builtin("unknown-builtin") is False
        assert (
            self.parser.is_shell_builtin("ls") is False
        )  # ls is in system tools, not shell builtins
        assert self.parser.is_shell_builtin("echo") is True  # echo is a shell builtin

    def test_extract_command_type(self):
        """Test command type extraction."""
        assert self.parser.extract_command_type("read file.txt") == CommandType.READ
        assert (
            self.parser.extract_command_type("python script.py") == CommandType.PYTHON
        )
        assert (
            self.parser.extract_command_type("pdftotext input.pdf")
            == CommandType.SYSTEM_TOOL
        )
        assert (
            self.parser.extract_command_type("echo hello") == CommandType.SHELL_BUILTIN
        )  # echo is a shell builtin
        assert (
            self.parser.extract_command_type("ls -la") == CommandType.SYSTEM_TOOL
        )  # ls is a system tool
        assert (
            self.parser.extract_command_type("unknown-command")
            == CommandType.SYSTEM_TOOL
        )

    def test_extract_command_type_empty(self):
        """Test command type extraction with empty command."""
        assert self.parser.extract_command_type("") == CommandType.UNKNOWN
        assert self.parser.extract_command_type("   ") == CommandType.UNKNOWN

    def test_validate_command_syntax_valid(self):
        """Test syntax validation with valid commands."""
        assert self.parser.validate_command_syntax("read file.txt") is True
        assert self.parser.validate_command_syntax("python script.py") is True
        assert self.parser.validate_command_syntax("ls -la") is True

    def test_validate_command_syntax_invalid(self):
        """Test syntax validation with invalid commands."""
        assert self.parser.validate_command_syntax("read") is False  # Missing argument
        assert self.parser.validate_command_syntax("python") is False  # Missing script
        assert self.parser.validate_command_syntax("") is False  # Empty command

    def test_parse_command_case_insensitive(self):
        """Test that command parsing is case-insensitive."""
        result1 = self.parser.parse("READ file.txt")
        result2 = self.parser.parse("read file.txt")
        result3 = self.parser.parse("Read file.txt")

        assert all(isinstance(r, ReadCommand) for r in [result1, result2, result3])
        assert all(r.target == "file.txt" for r in [result1, result2, result3])

    def test_parse_command_with_redirection_operators(self):
        """Test parsing commands with redirection operators."""
        result = self.parser.parse("echo hello > output.txt")

        assert isinstance(result, ShellBuiltinCommand)
        assert result.builtin == "echo"
        assert result.args == ["hello", ">", "output.txt"]

    def test_parse_command_with_append_redirection(self):
        """Test parsing commands with append redirection."""
        result = self.parser.parse("echo hello >> output.txt")

        assert isinstance(result, ShellBuiltinCommand)
        assert result.builtin == "echo"
        assert result.args == ["hello", ">>", "output.txt"]

    def test_parse_command_with_input_redirection(self):
        """Test parsing commands with input redirection."""
        result = self.parser.parse("cat < input.txt")

        assert isinstance(result, SystemToolCommand)
        assert result.tool == "cat"
        assert result.args == ["<", "input.txt"]

    def test_parse_command_with_complex_redirection(self):
        """Test parsing commands with complex redirection."""
        result = self.parser.parse("echo >file.txt")

        assert isinstance(result, ShellBuiltinCommand)
        assert result.builtin == "echo"
        assert result.args == [">file.txt"]


class TestParseCommandFunction:
    """Test cases for the parse_command convenience function."""

    def test_parse_command_function(self):
        """Test the convenience parse function."""
        result = parse_command("read test.md")

        assert isinstance(result, ReadCommand)
        assert result.target == "test.md"

    def test_parse_command_function_with_working_dir(self):
        """Test the convenience parse function with working directory."""
        result = parse_command("python script.py", working_dir="/tmp")

        assert isinstance(result, PythonCommand)
        assert result.script == "script.py"
        assert result.working_dir == "/tmp"


class TestCommandTypeEnum:
    """Test cases for CommandType enum."""

    def test_command_type_values(self):
        """Test CommandType enum values."""
        assert CommandType.READ.value == "read"
        assert CommandType.PYTHON.value == "python"
        assert CommandType.SYSTEM_TOOL.value == "system_tool"
        assert CommandType.SHELL_BUILTIN.value == "shell_builtin"
        assert CommandType.UNKNOWN.value == "unknown"

    def test_command_type_equality(self):
        """Test CommandType equality."""
        assert CommandType.READ == CommandType.READ
        assert CommandType.READ != CommandType.PYTHON


class TestParsedCommandClasses:
    """Test cases for parsed command dataclasses."""

    def test_read_command_creation(self):
        """Test ReadCommand creation."""
        cmd = ReadCommand(
            raw_command="read file.txt", target="file.txt", working_dir="/tmp"
        )

        assert cmd.raw_command == "read file.txt"
        assert cmd.target == "file.txt"
        assert cmd.working_dir == "/tmp"
        assert cmd.command_type == CommandType.READ

    def test_python_command_creation(self):
        """Test PythonCommand creation."""
        cmd = PythonCommand(
            raw_command="python script.py arg1 arg2",
            script="script.py",
            args=["arg1", "arg2"],
            working_dir="/tmp",
        )

        assert cmd.raw_command == "python script.py arg1 arg2"
        assert cmd.script == "script.py"
        assert cmd.args == ["arg1", "arg2"]
        assert cmd.working_dir == "/tmp"
        assert cmd.command_type == CommandType.PYTHON

    def test_system_tool_command_creation(self):
        """Test SystemToolCommand creation."""
        cmd = SystemToolCommand(
            raw_command="pdftotext input.pdf output.txt",
            tool="pdftotext",
            args=["input.pdf", "output.txt"],
            working_dir="/tmp",
        )

        assert cmd.raw_command == "pdftotext input.pdf output.txt"
        assert cmd.tool == "pdftotext"
        assert cmd.args == ["input.pdf", "output.txt"]
        assert cmd.working_dir == "/tmp"
        assert cmd.command_type == CommandType.SYSTEM_TOOL

    def test_shell_builtin_command_creation(self):
        """Test ShellBuiltinCommand creation."""
        cmd = ShellBuiltinCommand(
            raw_command="ls -la /tmp",
            builtin="ls",
            args=["-la", "/tmp"],
            working_dir="/tmp",
        )

        assert cmd.raw_command == "ls -la /tmp"
        assert cmd.builtin == "ls"
        assert cmd.args == ["-la", "/tmp"]
        assert cmd.working_dir == "/tmp"
        assert cmd.command_type == CommandType.SHELL_BUILTIN
