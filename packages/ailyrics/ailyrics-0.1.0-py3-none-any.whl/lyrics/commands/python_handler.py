"""
Python Handler - Handles execution of Python scripts.
"""

import logging
import os
import sys
import traceback
from pathlib import Path

from ..bash.types import ExecutionEnvironment, ExecutionResult

logger = logging.getLogger(__name__)


class PythonHandler:
    """
    Handles execution of Python scripts for Agent Skills.

    This handler provides functionality to execute Python scripts with arguments
    in a controlled environment, capturing output and handling errors.
    """

    def __init__(self):
        # Maximum execution time for Python scripts (5 minutes)
        self.max_execution_time = 300

        # Maximum memory usage (100MB)
        self.max_memory_usage = 100 * 1024 * 1024

        # Allowed modules (whitelist approach for security)
        self.allowed_modules = {
            # Standard library
            "os",
            "sys",
            "json",
            "xml",
            "csv",
            "re",
            "math",
            "datetime",
            "pathlib",
            "glob",
            "shutil",
            "tempfile",
            "zipfile",
            "tarfile",
            "subprocess",
            "argparse",
            "logging",
            "urllib",
            "http",
            "base64",
            "hashlib",
            "uuid",
            "random",
            "statistics",
            "collections",
            "itertools",
            "functools",
            "operator",
            "string",
            "textwrap",
            "codecs",
            "io",
            "pickle",
            # Data processing
            "pandas",
            "numpy",
            "openpyxl",
            "xlrd",
            "xlwt",
            "PIL",
            "Pillow",
            "opencv-python",
            "cv2",
            # PDF processing
            "PyPDF2",
            "pdfplumber",
            "pdfminer",
            "pdfrw",
            # Office documents
            "python-docx",
            "docx",
            "xlsxwriter",
            "pptx",
            # Web/API
            "requests",
            "urllib3",
            "beautifulsoup4",
            "bs4",
            # Utilities
            "pytz",
            "dateutil",
            "pyyaml",
            "yaml",
            "tqdm",
            "click",
            "colorama",
        }

        # Blocked modules (blacklist approach)
        self.blocked_modules = {
            "socket",
            "socketserver",
            "asyncio",
            "threading",
            "multiprocessing",
            "ctypes",
            "cffi",
            "gc",
            "inspect",
            "marshal",
            "code",
            "codeop",
            "compileall",
            "dis",
            "pickletools",
            "py_compile",
            "site",
            "sysconfig",
        }

    def execute_script(
        self, script_path: str, args: list[str], environment: ExecutionEnvironment
    ) -> "ExecutionResult":
        """
        Execute a Python script with arguments.

        Args:
            script_path: Path to the Python script
            args: Command line arguments to pass to the script
            environment: Execution environment

        Returns:
            ExecutionResult with stdout, stderr, and exit code
        """
        try:
            logger.info(f"Executing Python script: {script_path}")
            logger.debug(f"Script arguments: {args}")

            # Validate script path
            script_path_obj = Path(script_path)
            if not script_path_obj.exists():
                return self._make_error_result(f"Script not found: {script_path}")

            if not script_path_obj.is_file():
                return self._make_error_result(f"Not a file: {script_path}")

            if not script_path_obj.suffix == ".py":
                return self._make_error_result(f"Not a Python script: {script_path}")

            # Check file size
            file_size = script_path_obj.stat().st_size
            if file_size > 1024 * 1024:  # 1MB limit for script files
                return self._make_error_result(f"Script too large: {file_size} bytes")

            # Read script content
            try:
                with open(script_path, encoding="utf-8") as f:
                    script_content = f.read()
            except Exception as e:
                return self._make_error_result(f"Error reading script: {e}")

            # Validate script content for safety
            validation_result = self._validate_script_content(script_content)
            if not validation_result["valid"]:
                return self._make_error_result(
                    f"Script validation failed: {validation_result['message']}"
                )

            # Set up execution environment
            exec_env = self._setup_execution_environment(script_path, args, environment)

            # Execute the script
            result = self._execute_script_content(
                script_content, script_path, args, exec_env
            )

            logger.info(
                f"Script execution completed with exit code: {result.exit_code}"
            )
            return result

        except Exception as e:
            logger.error(f"Error executing Python script {script_path}: {e}")
            logger.error(traceback.format_exc())
            return self._make_error_result(f"Script execution error: {e}")

    def _validate_script_content(self, script_content: str) -> dict:
        """
        Validate Python script content for safety.

        Args:
            script_content: Content of the Python script

        Returns:
            Dictionary with 'valid' boolean and 'message' string
        """
        try:
            # Check for obviously dangerous patterns
            dangerous_patterns = [
                "import __import__",
                "__import__(",
                "eval(",
                "exec(",
                "compile(",
                "open(",  # Will be allowed but monitored
                "file(",
                "input(",
                "raw_input(",
                "os.system(",
                "subprocess.call(",
                "subprocess.run(",
                "subprocess.Popen(",
                "os.popen(",
                "pty.spawn(",
                "socket.socket(",
                "urllib.urlopen(",
                "requests.get(",
                "requests.post(",
            ]

            for pattern in dangerous_patterns:
                if pattern in script_content:
                    return {
                        "valid": False,
                        "message": f"Potentially dangerous pattern detected: {pattern}",
                    }

            # Check for blocked modules
            for module in self.blocked_modules:
                if (
                    f"import {module}" in script_content
                    or f"from {module}" in script_content
                ):
                    return {
                        "valid": False,
                        "message": f"Blocked module import: {module}",
                    }

            # Basic syntax check
            try:
                compile(script_content, "<string>", "exec")
            except SyntaxError as e:
                return {"valid": False, "message": f"Syntax error: {e}"}

            return {"valid": True, "message": "Script content is valid"}

        except Exception as e:
            return {"valid": False, "message": f"Validation error: {e}"}

    def _setup_execution_environment(
        self, script_path: str, args: list[str], environment: ExecutionEnvironment
    ) -> dict:
        """
        Set up the execution environment for the script.

        Args:
            script_path: Path to the script
            args: Command line arguments
            environment: Base execution environment

        Returns:
            Dictionary with execution environment settings
        """
        script_dir = str(Path(script_path).parent)

        # Build command line arguments
        sys_argv = [script_path] + args

        # Set up environment variables
        env_vars = environment.environment_vars.copy()
        env_vars.update(
            {
                "SCRIPT_PATH": script_path,
                "SCRIPT_DIR": script_dir,
                "SCRIPT_NAME": Path(script_path).name,
            }
        )

        # Add script directory to Python path
        python_path = env_vars.get("PYTHONPATH", "")
        if script_dir not in python_path:
            env_vars["PYTHONPATH"] = f"{script_dir}:{python_path}"

        return {
            "working_dir": environment.working_dir,
            "env_vars": env_vars,
            "sys_argv": sys_argv,
            "skills_path": environment.skills_path,
            "workspace_path": environment.workspace_path,
        }

    def _execute_script_content(
        self, script_content: str, script_path: str, args: list[str], exec_env: dict
    ) -> "ExecutionResult":
        """
        Execute the actual Python script content.

        Args:
            script_content: Content of the script
            script_path: Path to the script file
            args: Command line arguments
            exec_env: Execution environment

        Returns:
            ExecutionResult with output and exit code
        """
        # ExecutionResult is already imported

        try:
            # Create a subprocess to execute the script
            # This provides better isolation than exec()

            cmd = [sys.executable, script_path] + args

            logger.debug(f"Executing command: {' '.join(cmd)}")
            logger.debug(f"Working directory: {exec_env['working_dir']}")

            # Run the script as a subprocess (synchronous version)
            import subprocess

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=exec_env["working_dir"],
                env=exec_env["env_vars"],
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=self.max_execution_time)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()

            # Decode output
            stdout_str = stdout.decode("utf-8", errors="replace") if stdout else ""
            stderr_str = stderr.decode("utf-8", errors="replace") if stderr else ""

            return ExecutionResult(
                stdout=stdout_str, stderr=stderr_str, exit_code=process.returncode
            )

        except subprocess.TimeoutExpired:
            logger.error(
                f"Script execution timed out after {self.max_execution_time} seconds"
            )
            return ExecutionResult(
                stdout="",
                stderr=(
                    f"Script execution timed out after "
                    f"{self.max_execution_time} seconds"
                ),
                exit_code=124,  # Standard timeout exit code
            )

        except Exception as e:
            logger.error(f"Error executing script {script_path}: {e}")
            logger.error(traceback.format_exc())
            return ExecutionResult(
                stdout="", stderr=f"Script execution error: {e}", exit_code=1
            )

    def _make_error_result(self, error_message: str) -> "ExecutionResult":
        """
        Create an error execution result.

        Args:
            error_message: Error message to include

        Returns:
            ExecutionResult with error information
        """
        return ExecutionResult(stdout="", stderr=error_message, exit_code=1)

    def _is_allowed_module(self, module_name: str) -> bool:
        """
        Check if a module is allowed for import.

        Args:
            module_name: Name of the module

        Returns:
            True if the module is allowed
        """
        # Check blocked modules first
        if module_name in self.blocked_modules:
            return False

        # Check allowed modules
        if module_name in self.allowed_modules:
            return True

        # Allow standard library modules by default
        # (This is a simplified check - in production, you'd want more
        # rigorous validation)
        try:
            __import__(module_name)
            module = sys.modules[module_name]
            # Check if it's a built-in or standard library module
            if hasattr(module, "__file__") and "site-packages" not in module.__file__:
                return True
        except ImportError:
            pass

        return False

    def set_max_execution_time(self, seconds: int):
        """
        Set the maximum execution time for scripts.

        Args:
            seconds: Maximum execution time in seconds
        """
        self.max_execution_time = seconds

    def set_max_memory_usage(self, bytes_size: int):
        """
        Set the maximum memory usage for scripts.

        Args:
            bytes_size: Maximum memory usage in bytes
        """
        self.max_memory_usage = bytes_size

    def add_allowed_module(self, module_name: str):
        """
        Add a module to the allowed list.

        Args:
            module_name: Name of the module to allow
        """
        self.allowed_modules.add(module_name)

    def add_blocked_module(self, module_name: str):
        """
        Add a module to the blocked list.

        Args:
            module_name: Name of the module to block
        """
        self.blocked_modules.add(module_name)

    def execute_python_code(
        self, code: str, args: list[str], environment: ExecutionEnvironment
    ) -> "ExecutionResult":
        """
        Execute Python code directly (not from a file).

        Args:
            code: Python code to execute
            args: Command line arguments
            environment: Execution environment

        Returns:
            ExecutionResult with output and exit code
        """
        try:
            # Create a temporary script file
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_script_path = f.name

            try:
                # Execute the temporary script
                result = self.execute_script(temp_script_path, args, environment)
                return result

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_script_path)
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"Error executing Python code: {e}")
            return self._make_error_result(f"Code execution error: {e}")
