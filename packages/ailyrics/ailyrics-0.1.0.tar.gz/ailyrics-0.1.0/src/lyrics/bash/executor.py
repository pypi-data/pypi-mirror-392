"""
Command Executor - Executes parsed bash commands.

Simplified executor that uses a persistent shell subprocess for
maintaining state across commands. This eliminates the need for
manual state management and provides a true shell experience.
"""

import logging

from ..bash.command_parser import (
    CommandType,
    ParsedCommand,
    PythonCommand,
    ReadCommand,
    ShellBuiltinCommand,
    SystemToolCommand,
)
from ..bash.session_manager import ShellSessionManager
from ..bash.types import ExecutionEnvironment, ExecutionResult
from ..commands.python_handler import PythonHandler
from ..commands.read_handler import ReadHandler
from ..commands.system_handler import SystemHandler
from ..filesystem.resolver import PathResolver
from ..filesystem.validator import PathValidator

logger = logging.getLogger(__name__)


class CommandExecutor:
    """
    Executes parsed bash commands using a persistent shell subprocess.

    This executor maintains a single shell session that preserves state
    across commands, eliminating the need for manual state management.
    """

    def __init__(self, env_manager=None):
        """Initialize the command executor."""
        self.system_handler = SystemHandler()
        self.read_handler = ReadHandler()
        self.python_handler = PythonHandler()
        self.env_manager = env_manager
        self.shell_session: ShellSessionManager | None = None
        self._initialized = False

    def initialize(self, working_dir: str = "/workspace") -> bool:
        """
        Initialize the persistent shell session.

        Args:
            working_dir: Initial working directory for the shell

        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing CommandExecutor with persistent shell session")
            self.shell_session = ShellSessionManager()

            if self.shell_session.initialize(working_dir):
                self._initialized = True
                logger.info(
                    "CommandExecutor initialized successfully with persistent shell"
                )
                return True
            else:
                logger.error("Failed to initialize persistent shell session")
                return False

        except Exception as e:
            logger.error(f"Error initializing CommandExecutor: {e}")
            return False

    def execute(
        self,
        command: ParsedCommand,
        environment: ExecutionEnvironment,
        path_resolver: PathResolver,
        path_validator: PathValidator,
    ) -> ExecutionResult:
        """
        Execute a parsed command.

        Args:
            command: The parsed command to execute
            environment: Execution environment
            path_resolver: Path resolver for file operations
            path_validator: Path validator for security checks

        Returns:
            ExecutionResult with output and exit code
        """
        # Initialize if not already done (for testing compatibility)
        if not self._initialized:
            self.initialize(environment.working_dir)

        try:
            logger.debug(f"Executing command: {command}")

            # Route command based on type
            if command.command_type == CommandType.READ:
                return self._execute_read(
                    command, environment, path_resolver, path_validator
                )
            elif command.command_type == CommandType.PYTHON:
                return self._execute_python(
                    command, environment, path_resolver, path_validator
                )
            elif command.command_type == CommandType.SYSTEM_TOOL:
                return self._execute_system_tool(
                    command, environment, path_resolver, path_validator
                )
            elif command.command_type == CommandType.SHELL_BUILTIN:
                return self._execute_shell_builtin(
                    command, environment, path_resolver, path_validator
                )
            else:
                return self._execute_unknown(
                    command, environment, path_resolver, path_validator
                )

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return ExecutionResult(
                stdout="", stderr=f"Command execution error: {e}", exit_code=1
            )

    def _execute_read(
        self,
        command: ReadCommand,
        environment: ExecutionEnvironment,
        path_resolver: PathResolver,
        path_validator: PathValidator,
    ) -> ExecutionResult:
        """Execute a read command using the read handler."""
        try:
            # Resolve the file path
            file_path = path_resolver.resolve(command.target, environment.working_dir)

            # Check if we can read the file
            if not path_validator.can_read(file_path):
                return ExecutionResult(
                    stdout="", stderr=f"Permission denied: {file_path}", exit_code=1
                )

            # Use the read handler to read the file
            content = self.read_handler.read_file(file_path)

            return ExecutionResult(stdout=content, stderr="", exit_code=0)

        except FileNotFoundError:
            return ExecutionResult(
                stdout="", stderr=f"File not found: {command.target}", exit_code=1
            )
        except PermissionError:
            return ExecutionResult(
                stdout="", stderr=f"Permission denied: {file_path}", exit_code=1
            )
        except Exception as e:
            return ExecutionResult(
                stdout="", stderr=f"Error reading file: {str(e)}", exit_code=1
            )

    def _execute_python(
        self,
        command: PythonCommand,
        environment: ExecutionEnvironment,
        path_resolver: PathResolver,
        path_validator: PathValidator,
    ) -> ExecutionResult:
        """Execute a Python command using the python handler."""
        try:
            # Resolve the script path
            script_path = path_resolver.resolve(command.script, environment.working_dir)

            # Check if it's a Python file
            if not script_path.endswith(".py"):
                return ExecutionResult(
                    stdout="",
                    stderr=f"Not a Python script: {command.script}",
                    exit_code=1,
                )

            # Use the python handler to execute the script
            return self.python_handler.execute_script(
                script_path, command.args, environment
            )

        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=f"Error executing Python script: {str(e)}",
                exit_code=1,
            )

    def _execute_system_tool(
        self,
        command: SystemToolCommand,
        environment: ExecutionEnvironment,
        path_resolver: PathResolver,
        path_validator: PathValidator,
    ) -> ExecutionResult:
        """Execute a system tool using the system handler."""
        # Use the system handler to execute the tool
        return self.system_handler.execute_tool(command.tool, command.args, environment)

    def _execute_shell_builtin(
        self,
        command: ShellBuiltinCommand,
        environment: ExecutionEnvironment,
        path_resolver: PathResolver,
        path_validator: PathValidator,
    ) -> ExecutionResult:
        """Execute a shell builtin - delegate to persistent shell."""

        # For state-changing commands (cd, export, etc.), always use raw command
        STATE_CHANGING_BUILTINS = {"cd", "export", "unset", "alias", "unalias"}

        if command.builtin in STATE_CHANGING_BUILTINS:
            # These commands should change the shell's state
            return self.shell_session.execute_command(command.raw_command)

        # For other commands, if working_dir is set, execute in that context
        if command.working_dir:
            # Use subshell for isolation
            cmd = f"(cd '{command.working_dir}' && {command.raw_command})"
        else:
            # Execute in current directory
            cmd = command.raw_command

        return self.shell_session.execute_command(cmd)

    def _execute_unknown(
        self,
        command: ParsedCommand,
        environment: ExecutionEnvironment,
        path_resolver: PathResolver,
        path_validator: PathValidator,
    ) -> ExecutionResult:
        """Execute an unknown command - let the shell figure it out."""
        # Just pass the raw command to the shell
        cmd = command.raw_command
        if command.working_dir:
            cmd = f"cd {command.working_dir} && {cmd}"
        return self.shell_session.execute_command(cmd)

    def get_current_working_dir(self) -> str:
        """Get the current working directory from the shell session."""
        if self._initialized and self.shell_session:
            return self.shell_session.get_current_working_dir()
        return "/workspace"

    def is_alive(self) -> bool:
        """Check if the shell session is alive."""
        return (
            self._initialized and self.shell_session and self.shell_session.is_alive()
        )

    def cleanup(self):
        """Clean up the command executor."""
        if self.shell_session:
            self.shell_session.cleanup()
            self.shell_session = None
        self._initialized = False

    def __del__(self):
        """Destructor - ensure cleanup."""
        self.cleanup()
