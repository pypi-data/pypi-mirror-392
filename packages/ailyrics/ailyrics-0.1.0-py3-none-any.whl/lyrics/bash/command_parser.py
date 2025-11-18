"""
Command Parser - Parses bash commands into structured representations.
"""

import shlex
from dataclasses import dataclass, field
from enum import Enum


class CommandType(Enum):
    """Types of commands that can be parsed."""

    READ = "read"
    PYTHON = "python"
    SYSTEM_TOOL = "system_tool"
    SHELL_BUILTIN = "shell_builtin"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """Base class for parsed commands."""

    raw_command: str
    command_type: CommandType
    working_dir: str | None = None


@dataclass
class ReadCommand:
    """Parsed read command."""

    raw_command: str
    target: str  # File path to read
    working_dir: str | None = None
    command_type: CommandType = field(default=CommandType.READ, init=False)


@dataclass
class PythonCommand:
    """Parsed python command."""

    raw_command: str
    script: str  # Path to Python script
    args: list[str]  # Arguments to pass to the script
    working_dir: str | None = None
    command_type: CommandType = field(default=CommandType.PYTHON, init=False)


@dataclass
class SystemToolCommand:
    """Parsed system tool command."""

    raw_command: str
    tool: str  # Tool name (e.g., pdftotext, soffice)
    args: list[str]  # Arguments to pass to the tool
    working_dir: str | None = None
    command_type: CommandType = field(default=CommandType.SYSTEM_TOOL, init=False)


@dataclass
class ShellBuiltinCommand:
    """Parsed shell builtin command."""

    raw_command: str
    builtin: str  # Builtin command (e.g., ls, cd, mkdir)
    args: list[str]  # Arguments to pass to the builtin
    working_dir: str | None = None
    command_type: CommandType = field(default=CommandType.SHELL_BUILTIN, init=False)


class CommandParser:
    """
    Parses bash commands into structured representations.

    This parser is designed to handle the specific command patterns
    used by Agent Skills, including:
    - read commands: read xlsx/SKILL.md
    - python scripts: python xlsx/recalc.py output.xlsx 30
    - system tools: pdftotext -layout input.pdf output.txt
    - shell builtins: ls, mkdir, cp, etc.
    """

    # System tools that are commonly used by Agent Skills
    SYSTEM_TOOLS = {
        "pdftotext",
        "soffice",
        "qpdf",
        "pdftoppm",
        "convert",
        "find",
        "grep",
        "ls",
        "mkdir",
        "rm",
        "cp",
        "mv",
        "cat",
        "head",
        "tail",
        "wc",
        "sort",
        "uniq",
        "awk",
        "sed",
    }

    # Shell builtin commands
    SHELL_BUILTINS = {
        "cd",
        "pwd",
        "echo",
        "export",
        "source",
        "test",
        "[",
        "true",
        "false",
        "exit",
        "return",
        "break",
        "continue",
    }

    def parse(self, command: str, working_dir: str | None = None) -> ParsedCommand:
        """
        Parse a bash command string into a structured representation.

        Args:
            command: The raw bash command string
            working_dir: Current working directory (optional)

        Returns:
            ParsedCommand object representing the parsed command

        Raises:
            ValueError: If the command cannot be parsed
        """
        if not command or not command.strip():
            raise ValueError("Empty command provided")

        # Clean up the command
        command = command.strip()

        # Try to split the command using shell-like syntax
        try:
            # First, check if command contains shell operators like >, >>, |
            if any(op in command for op in [">", ">>", "|", "&", "&", "||"]):
                # For commands with shell operators, use simple split to preserve them
                parts = command.split()
            else:
                # For simple commands, use shlex for better quote handling
                parts = shlex.split(command)
        except ValueError:
            # If shlex fails, fall back to simple split
            parts = command.split()

        if not parts:
            raise ValueError("Empty command after parsing")

        main_cmd = parts[0].lower()
        args = parts[1:]

        # Determine command type and create appropriate parsed command
        if main_cmd == "read":
            return self._parse_read_command(command, args, working_dir)
        elif main_cmd == "python":
            return self._parse_python_command(command, args, working_dir)
        elif main_cmd in self.SYSTEM_TOOLS:
            return self._parse_system_tool_command(command, main_cmd, args, working_dir)
        elif main_cmd in self.SHELL_BUILTINS:
            return self._parse_shell_builtin_command(
                command, main_cmd, args, working_dir
            )
        else:
            # Try to determine if it's a system tool by checking if it exists
            return self._parse_unknown_command(command, main_cmd, args, working_dir)

    def _parse_read_command(
        self, raw_command: str, args: list[str], working_dir: str | None
    ) -> ReadCommand:
        """Parse a read command."""
        if len(args) != 1:
            raise ValueError(
                f"read command expects exactly 1 argument, got {len(args)}"
            )

        return ReadCommand(
            raw_command=raw_command, working_dir=working_dir, target=args[0]
        )

    def _parse_python_command(
        self, raw_command: str, args: list[str], working_dir: str | None
    ) -> PythonCommand:
        """Parse a python command."""
        if len(args) < 1:
            raise ValueError("python command expects at least a script path")

        return PythonCommand(
            raw_command=raw_command,
            working_dir=working_dir,
            script=args[0],
            args=args[1:],
        )

    def _parse_system_tool_command(
        self, raw_command: str, tool: str, args: list[str], working_dir: str | None
    ) -> SystemToolCommand:
        """Parse a system tool command."""
        return SystemToolCommand(
            raw_command=raw_command, working_dir=working_dir, tool=tool, args=args
        )

    def _parse_shell_builtin_command(
        self, raw_command: str, builtin: str, args: list[str], working_dir: str | None
    ) -> ShellBuiltinCommand:
        """Parse a shell builtin command."""
        # Handle special shell constructs like redirection
        processed_args = []
        for arg in args:
            # Handle redirection operators
            if arg in [">", ">>", "<"]:
                processed_args.append(arg)
            elif arg.startswith(">") or arg.startswith(">>") or arg.startswith("<"):
                # Handle cases like >file or >>file
                processed_args.append(arg)
            else:
                processed_args.append(arg)

        return ShellBuiltinCommand(
            raw_command=raw_command,
            working_dir=working_dir,
            builtin=builtin,
            args=processed_args,
        )

    def _parse_unknown_command(
        self, raw_command: str, cmd: str, args: list[str], working_dir: str | None
    ) -> SystemToolCommand | ShellBuiltinCommand:
        """Parse an unknown command - try to categorize it."""
        # Default to system tool for unknown commands
        # This allows for flexibility in adding new tools
        return SystemToolCommand(
            raw_command=raw_command, working_dir=working_dir, tool=cmd, args=args
        )

    def is_system_tool(self, tool_name: str) -> bool:
        """Check if a tool name is a known system tool."""
        return tool_name.lower() in self.SYSTEM_TOOLS

    def is_shell_builtin(self, builtin_name: str) -> bool:
        """Check if a command is a shell builtin."""
        return builtin_name.lower() in self.SHELL_BUILTINS

    def extract_command_type(self, command: str) -> CommandType:
        """
        Extract just the command type without full parsing.

        This is a lightweight method for quick command type detection.
        """
        try:
            parts = command.strip().split()
            if not parts:
                return CommandType.UNKNOWN

            main_cmd = parts[0].lower()

            if main_cmd == "read":
                return CommandType.READ
            elif main_cmd == "python":
                return CommandType.PYTHON
            elif main_cmd in self.SYSTEM_TOOLS:
                return CommandType.SYSTEM_TOOL
            elif main_cmd in self.SHELL_BUILTINS:
                return CommandType.SHELL_BUILTIN
            else:
                return CommandType.SYSTEM_TOOL  # Default assumption

        except Exception:
            return CommandType.UNKNOWN

    def validate_command_syntax(self, command: str) -> bool:
        """
        Basic syntax validation for commands.

        Returns:
            True if the command appears syntactically valid
        """
        try:
            parsed = self.parse(command)
            return parsed is not None
        except ValueError:
            return False


# Convenience function for quick parsing
def parse_command(command: str, working_dir: str | None = None) -> ParsedCommand:
    """Quick parse function using the default parser."""
    parser = CommandParser()
    return parser.parse(command, working_dir)
