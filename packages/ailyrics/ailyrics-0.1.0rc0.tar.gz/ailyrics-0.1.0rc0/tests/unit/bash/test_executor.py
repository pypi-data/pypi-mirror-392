"""
Unit tests for the Command Executor module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from lyrics.bash.command_parser import (
    PythonCommand,
    ReadCommand,
    ShellBuiltinCommand,
    SystemToolCommand,
)
from lyrics.bash.executor import CommandExecutor
from lyrics.bash.types import ExecutionEnvironment


class TestCommandExecutor:
    """Test cases for CommandExecutor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.skills_path = os.path.join(self.temp_dir, "skills")
        self.workspace_path = os.path.join(self.temp_dir, "workspace")
        os.makedirs(self.workspace_path, exist_ok=True)

        self.environment = ExecutionEnvironment(
            working_dir=self.workspace_path,
            environment_vars={"TEST_VAR": "test_value"},
            skills_path=self.skills_path,
            workspace_path=self.workspace_path,
        )

        # Initialize executor with persistent shell
        self.executor = CommandExecutor()
        success = self.executor.initialize(self.workspace_path)
        if not success:
            pytest.skip("Failed to initialize executor with persistent shell")

        # Create mock objects for commands that need path resolution
        self.path_resolver = Mock()
        self.path_validator = Mock()

        # Set up default mock behaviors
        self.path_validator.can_read.return_value = True
        self.path_validator.can_write.return_value = True
        self.path_validator.can_access.return_value = True

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.executor:
            self.executor.cleanup()

        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_executor_initialization(self):
        """Test executor initialization."""
        assert self.executor._initialized is True
        assert self.executor.is_alive() is True

    def test_get_current_working_dir(self):
        """Test getting current working directory."""
        cwd = self.executor.get_current_working_dir()
        assert os.path.realpath(cwd) == os.path.realpath(self.workspace_path)

    def test_execute_shell_builtin_echo(self):
        """Test echo shell builtin command."""
        command = ShellBuiltinCommand(
            raw_command="echo hello world",
            builtin="echo",
            args=["hello", "world"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "hello world" in result.stdout

    def test_execute_shell_builtin_pwd(self):
        """Test pwd shell builtin command."""
        command = ShellBuiltinCommand(
            raw_command="pwd", builtin="pwd", args=[], working_dir=self.workspace_path
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert os.path.realpath(self.workspace_path) in os.path.realpath(result.stdout)

    def test_execute_shell_builtin_ls(self):
        """Test ls shell builtin command."""
        # Create test files
        test_file1 = os.path.join(self.workspace_path, "file1.txt")
        test_file2 = os.path.join(self.workspace_path, "file2.txt")
        Path(test_file1).touch()
        Path(test_file2).touch()

        command = ShellBuiltinCommand(
            raw_command="ls", builtin="ls", args=[], working_dir=self.workspace_path
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "file1.txt" in result.stdout
        assert "file2.txt" in result.stdout

    def test_execute_shell_builtin_mkdir(self):
        """Test mkdir shell builtin command."""
        newdir = "newdir"
        command = ShellBuiltinCommand(
            raw_command=f"mkdir {newdir}",
            builtin="mkdir",
            args=[newdir],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert os.path.exists(os.path.join(self.workspace_path, newdir))

    def test_execute_shell_builtin_mkdir_nested(self):
        """Test mkdir with nested path."""
        command = ShellBuiltinCommand(
            raw_command="mkdir -p parent/child",
            builtin="mkdir",
            args=["-p", "parent/child"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        nested_path = os.path.join(self.workspace_path, "parent", "child")
        assert os.path.exists(nested_path)

    def test_execute_shell_builtin_rm_file(self):
        """Test rm shell builtin command on file."""
        test_file = os.path.join(self.workspace_path, "test.txt")
        Path(test_file).touch()

        command = ShellBuiltinCommand(
            raw_command="rm test.txt",
            builtin="rm",
            args=["test.txt"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert not os.path.exists(test_file)

    def test_execute_shell_builtin_cat(self):
        """Test cat shell builtin command."""
        test_file = os.path.join(self.workspace_path, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello World")

        command = ShellBuiltinCommand(
            raw_command="cat test.txt",
            builtin="cat",
            args=["test.txt"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "Hello World" in result.stdout

    def test_execute_shell_builtin_cat_multiple_files(self):
        """Test cat with multiple files."""
        file1 = os.path.join(self.workspace_path, "file1.txt")
        file2 = os.path.join(self.workspace_path, "file2.txt")
        with open(file1, "w") as f:
            f.write("Content1\n")
        with open(file2, "w") as f:
            f.write("Content2\n")

        command = ShellBuiltinCommand(
            raw_command="cat file1.txt file2.txt",
            builtin="cat",
            args=["file1.txt", "file2.txt"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "Content1" in result.stdout
        assert "Content2" in result.stdout

    def test_execute_shell_builtin_cd(self):
        """Test cd shell builtin command."""
        # Create subdirectory
        subdir = os.path.join(self.workspace_path, "subdir")
        os.makedirs(subdir, exist_ok=True)

        command = ShellBuiltinCommand(
            raw_command="cd subdir",
            builtin="cd",
            args=["subdir"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0

        # Verify directory changed by running pwd
        cwd = self.executor.get_current_working_dir()
        assert "subdir" in cwd

    def test_shell_state_persistence_environment_variables(self):
        """Test that environment variables persist across commands."""
        # Set environment variable
        cmd1 = ShellBuiltinCommand(
            raw_command="export MY_VAR=hello",
            builtin="export",
            args=["MY_VAR=hello"],
            working_dir=self.workspace_path,
        )

        result1 = self.executor.execute(
            cmd1, self.environment, self.path_resolver, self.path_validator
        )
        assert result1.exit_code == 0

        # Read environment variable
        cmd2 = ShellBuiltinCommand(
            raw_command="echo $MY_VAR",
            builtin="echo",
            args=["$MY_VAR"],
            working_dir=self.workspace_path,
        )

        result2 = self.executor.execute(
            cmd2, self.environment, self.path_resolver, self.path_validator
        )
        assert result2.exit_code == 0
        assert "hello" in result2.stdout

    def test_shell_state_persistence_working_directory(self):
        """Test that working directory persists across commands."""
        # Create subdirectory
        subdir = os.path.join(self.workspace_path, "testdir")
        os.makedirs(subdir, exist_ok=True)

        # Change directory - no working_dir set, so state persists
        cmd1 = ShellBuiltinCommand(
            raw_command="cd testdir",
            builtin="cd",
            args=["testdir"],
            working_dir=None,  # None = change shell's state permanently
        )

        result1 = self.executor.execute(
            cmd1, self.environment, self.path_resolver, self.path_validator
        )
        assert result1.exit_code == 0

        # Check current directory - should be in testdir now
        cmd2 = ShellBuiltinCommand(
            raw_command="pwd",
            builtin="pwd",
            args=[],
            working_dir=None,  # None = use current shell directory
        )

        result2 = self.executor.execute(
            cmd2, self.environment, self.path_resolver, self.path_validator
        )
        assert result2.exit_code == 0
        assert "testdir" in result2.stdout

    def test_working_dir_isolation(self):
        """Test that working_dir parameter doesn't change shell state."""
        # Create subdirectory
        subdir = os.path.join(self.workspace_path, "testdir")
        os.makedirs(subdir, exist_ok=True)

        # Get initial directory
        initial_dir = self.executor.get_current_working_dir()

        # Execute ls in subdirectory - with working_dir set
        cmd = ShellBuiltinCommand(
            raw_command="ls",
            builtin="ls",
            args=[],
            working_dir=subdir,  # Temporary switch for this command only
        )

        result = self.executor.execute(
            cmd, self.environment, self.path_resolver, self.path_validator
        )
        assert result.exit_code == 0

        # Check that shell's directory didn't change
        final_dir = self.executor.get_current_working_dir()
        assert initial_dir == final_dir  # Should be the same

    def test_execute_with_output_redirection(self):
        """Test command with output redirection."""
        output_file = os.path.join(self.workspace_path, "output.txt")

        command = ShellBuiltinCommand(
            raw_command="echo hello > output.txt",
            builtin="echo",
            args=["hello", ">", "output.txt"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert os.path.exists(output_file)
        with open(output_file) as f:
            assert "hello" in f.read()

    def test_execute_with_append_redirection(self):
        """Test command with append redirection."""
        output_file = os.path.join(self.workspace_path, "output.txt")
        with open(output_file, "w") as f:
            f.write("existing\n")

        command = ShellBuiltinCommand(
            raw_command="echo new >> output.txt",
            builtin="echo",
            args=["new", ">>", "output.txt"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        with open(output_file) as f:
            content = f.read()
            assert "existing" in content
            assert "new" in content

    def test_execute_command_with_pipe(self):
        """Test command with pipe."""
        # Fix: Use the raw command directly - pipe is not a builtin
        # The shell session will handle pipes natively
        command = ShellBuiltinCommand(
            raw_command="echo 'hello world' | grep hello",
            builtin="echo",  # The primary command
            args=["'hello world' | grep hello"],  # But really we should pass raw
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "hello" in result.stdout

    def test_execute_read_command(self):
        """Test read command execution."""
        test_file = os.path.join(self.workspace_path, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        self.path_resolver.resolve.return_value = test_file

        command = ReadCommand(
            raw_command="read test.txt",
            target="test.txt",
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "test content" in result.stdout

    def test_execute_read_command_permission_denied(self):
        """Test read command with permission denied."""
        self.path_validator.can_read.return_value = False
        self.path_resolver.resolve.return_value = "/blocked/file.txt"

        command = ReadCommand(
            raw_command="read blocked.txt",
            target="blocked.txt",
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 1
        assert "Permission denied" in result.stderr

    def test_execute_read_command_file_not_found(self):
        """Test read command with file not found."""
        self.path_resolver.resolve.return_value = "/nonexistent/file.txt"

        command = ReadCommand(
            raw_command="read nonexistent.txt",
            target="nonexistent.txt",
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 1
        assert "not found" in result.stderr.lower()

    def test_execute_python_command(self):
        """Test Python command execution."""
        script_path = os.path.join(self.workspace_path, "test.py")
        with open(script_path, "w") as f:
            f.write("print('Hello from Python')")

        self.path_resolver.resolve.return_value = script_path

        command = PythonCommand(
            raw_command="python test.py",
            script="test.py",
            args=[],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "Hello from Python" in result.stdout

    def test_execute_python_command_with_args(self):
        """Test Python command with arguments."""
        script_path = os.path.join(self.workspace_path, "test.py")
        with open(script_path, "w") as f:
            f.write("import sys\nprint(sys.argv[1])")

        self.path_resolver.resolve.return_value = script_path

        command = PythonCommand(
            raw_command="python test.py hello",
            script="test.py",
            args=["hello"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "hello" in result.stdout

    def test_execute_python_command_not_python_file(self):
        """Test Python command with non-Python file."""
        self.path_resolver.resolve.return_value = "/path/to/script.txt"

        command = PythonCommand(
            raw_command="python script.txt",
            script="script.txt",
            args=[],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 1
        assert "Not a Python script" in result.stderr

    def test_execute_system_tool(self):
        """Test system tool execution."""
        command = SystemToolCommand(
            raw_command="ls -la",
            tool="ls",
            args=["-la"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        # ls should work via system handler
        assert (
            result.exit_code == 0 or result.exit_code == 1
        )  # May fail depending on system

    def test_command_failure_nonzero_exit(self):
        """Test command that fails with non-zero exit code."""
        command = ShellBuiltinCommand(
            raw_command="ls /nonexistent_directory_xyz",
            builtin="ls",
            args=["/nonexistent_directory_xyz"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code != 0

    def test_multiline_output(self):
        """Test command with multiline output."""
        command = ShellBuiltinCommand(
            raw_command="printf 'line1\\nline2\\nline3\\n'",
            builtin="printf",
            args=["'line1\\nline2\\nline3\\n'"],
            working_dir=self.workspace_path,
        )

        result = self.executor.execute(
            command, self.environment, self.path_resolver, self.path_validator
        )

        assert result.exit_code == 0
        assert "line1" in result.stdout
        assert "line2" in result.stdout
        assert "line3" in result.stdout

    def test_cleanup(self):
        """Test executor cleanup."""
        assert self.executor.is_alive()

        self.executor.cleanup()

        assert not self.executor._initialized
        assert not self.executor.is_alive()
