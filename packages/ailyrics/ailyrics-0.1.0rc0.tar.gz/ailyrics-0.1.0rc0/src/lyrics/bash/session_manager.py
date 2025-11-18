"""
Shell Session Manager - True persistent bash subprocess session.

Maintains a real bash process that preserves all shell state including
working directory, environment variables, shell functions, etc.

Uses pexpect for reliable process management.
"""

import logging
import os
import tempfile
import time
from threading import RLock

import pexpect

from ..bash.types import ExecutionResult

logger = logging.getLogger(__name__)


class ShellSessionManager:
    """
    Manages a truly persistent bash subprocess session.

    Uses pexpect to maintain an interactive bash session with full state persistence.
    """

    def __init__(self, shell_path: str = "/bin/bash"):
        """
        Initialize the shell session manager.

        Args:
            shell_path: Path to the shell executable (default: /bin/bash)
        """
        self.shell_path = shell_path
        self.process: pexpect.spawn | None = None
        self.session_lock = RLock()
        self._initialized = False
        self._command_counter = 0
        self._prompt = "__SHELL_PROMPT__"

    def initialize(self, initial_working_dir: str | None = None) -> bool:
        """
        Initialize the persistent bash subprocess.

        Args:
            initial_working_dir: Initial working directory for the shell.
                               If None, uses a temporary directory.

        Returns:
            True if initialization successful, False otherwise
        """
        with self.session_lock:
            try:
                # Use temp directory if not specified or if specified dir not writable
                if initial_working_dir is None:
                    initial_working_dir = tempfile.mkdtemp(prefix="shell_session_")
                else:
                    try:
                        os.makedirs(initial_working_dir, exist_ok=True)
                        test_file = os.path.join(initial_working_dir, ".write_test")
                        with open(test_file, "w") as f:
                            f.write("test")
                        os.remove(test_file)
                    except (OSError, PermissionError) as e:
                        logger.warning(
                            f"Cannot use {initial_working_dir}: {e}, using temp dir"
                        )
                        initial_working_dir = tempfile.mkdtemp(prefix="shell_session_")

                logger.info(
                    f"Initializing persistent bash subprocess in: {initial_working_dir}"
                )

                # Start bash with pexpect
                self.process = pexpect.spawn(
                    self.shell_path,
                    ["--norc", "--noprofile"],
                    cwd=initial_working_dir,
                    encoding="utf-8",
                    echo=False,
                    timeout=30,
                )

                # Set a custom prompt for reliable command termination detection
                self.process.sendline(f'PS1="{self._prompt}"')
                self.process.expect(self._prompt, timeout=5)

                # Set BASH to combine stderr with stdout for simpler handling
                # This makes pexpect capture both streams
                self.process.sendline("exec 2>&1")
                self.process.expect(self._prompt, timeout=5)

                # Clear any initial output
                time.sleep(0.1)

                self._initialized = True
                logger.info("Persistent bash subprocess initialized successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to initialize persistent bash subprocess: {e}")
                self.cleanup()
                return False

    def execute_command(self, command: str, timeout: float = 30.0) -> ExecutionResult:
        """
        Execute a command in the persistent bash session.

        Args:
            command: Command to execute
            timeout: Command timeout in seconds

        Returns:
            ExecutionResult with stdout, stderr, and exit code
        """
        if not self._initialized or not self.process:
            return ExecutionResult(
                stdout="", stderr="Shell session not initialized", exit_code=1
            )

        with self.session_lock:
            try:
                logger.debug(f"Executing command in persistent bash: {command}")

                # Handle empty command
                if not command.strip():
                    return ExecutionResult(stdout="", stderr="", exit_code=0)

                # Send command
                self.process.sendline(command)

                # Wait for command to complete (prompt appears)
                try:
                    self.process.expect(self._prompt, timeout=timeout)
                except pexpect.TIMEOUT:
                    return ExecutionResult(
                        stdout=self.process.before if self.process.before else "",
                        stderr="command timed out",
                        exit_code=124,
                    )
                except pexpect.EOF:
                    return ExecutionResult(
                        stdout="",
                        stderr="Bash process terminated unexpectedly",
                        exit_code=1,
                    )

                # Get output (everything before the prompt)
                output = self.process.before if self.process.before else ""

                # Remove the echoed command from output (first line)
                # pexpect might echo the command even with echo=False
                lines = output.split("\n")
                if lines and command.strip() in lines[0]:
                    lines = lines[1:]

                stdout = "\n".join(lines).strip()

                # Clean escape sequences more carefully
                import re

                # Only remove specific problematic sequences
                stdout = re.sub(r"\x1b\[\?2004[hl]", "", stdout)
                stdout = re.sub(r"\r", "", stdout)  # Remove carriage returns
                stdout = stdout.strip()

                # Get exit code
                self.process.sendline("echo $?")
                self.process.expect(self._prompt, timeout=5)
                exit_code_output = self.process.before if self.process.before else "1"

                # Parse exit code (the last line should contain the exit code)
                try:
                    exit_code_lines = exit_code_output.strip().split("\n")
                    # Find the line that contains just the exit code number
                    exit_code = 0
                    for line in exit_code_lines:
                        line = line.strip()
                        if line.isdigit():
                            exit_code = int(line)
                            break
                except (ValueError, IndexError):
                    exit_code = 1  # Default to error if we can't parse

                # Since we redirected stderr to stdout, we don't have separate stderr
                # But we can simulate it by checking if the command failed
                stderr = ""
                if exit_code != 0:
                    # For failed commands, put the output in stderr
                    stderr = stdout
                    stdout = ""

                return ExecutionResult(
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                )

            except Exception as e:
                logger.error(f"Error executing command in persistent bash: {e}")
                return ExecutionResult(
                    stdout="", stderr=f"Command execution error: {e}", exit_code=1
                )

    def get_current_working_dir(self) -> str:
        """
        Get the current working directory from the persistent bash session.

        Returns:
            Current working directory path
        """
        try:
            # Use a more reliable method to get pwd
            result = self.execute_command("pwd", timeout=5.0)
            if result.exit_code == 0 and result.stdout.strip():
                path = result.stdout.strip()
                try:
                    return os.path.realpath(path)
                except (OSError, ValueError):
                    return path
            return tempfile.gettempdir()
        except Exception as e:
            logger.error(f"Error getting current working directory: {e}")
            return tempfile.gettempdir()

    def cleanup(self):
        """Clean up the persistent bash subprocess."""
        with self.session_lock:
            try:
                if self.process:
                    try:
                        if self.process.isalive():
                            self.process.sendline("exit")
                            self.process.expect(pexpect.EOF, timeout=1)
                    except (pexpect.ExceptionPexpect, OSError):
                        pass

                    try:
                        self.process.close(force=True)
                    except (pexpect.ExceptionPexpect, OSError):
                        pass

                    self.process = None

                self._initialized = False
                logger.info("Persistent bash subprocess cleaned up")

            except Exception as e:
                logger.error(f"Error cleaning up persistent bash subprocess: {e}")

    def is_alive(self) -> bool:
        """
        Check if the persistent bash subprocess is alive.

        Returns:
            True if the process is running, False otherwise
        """
        try:
            return (
                self._initialized
                and self.process is not None
                and self.process.isalive()
            )
        except (pexpect.ExceptionPexpect, OSError, AttributeError):
            return False

    def __del__(self):
        """Destructor - ensure cleanup on object deletion."""
        try:
            self.cleanup()
        except Exception:
            pass
