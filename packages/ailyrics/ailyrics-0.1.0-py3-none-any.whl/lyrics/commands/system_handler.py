"""
System Handler - Handles execution of system tools and commands.
"""

import logging
import os
import sys

from ..bash.types import ExecutionEnvironment, ExecutionResult

logger = logging.getLogger(__name__)


class SystemHandler:
    """
    Handles execution of system tools for Agent Skills.

    This handler provides functionality to execute system commands like:
    - pdftotext, pdftoppm (PDF processing)
    - soffice (LibreOffice)
    - qpdf (PDF manipulation)
    - convert (ImageMagick)
    - Standard Unix tools (ls, grep, find, etc.)
    """

    def __init__(self):
        # System tools and their common paths
        self.system_tools = {
            "pdftotext": self._find_tool(
                ["/usr/bin/pdftotext", "/usr/local/bin/pdftotext"]
            ),
            "pdftoppm": self._find_tool(
                ["/usr/bin/pdftoppm", "/usr/local/bin/pdftoppm"]
            ),
            "soffice": self._find_tool(
                [
                    "/usr/bin/soffice",
                    "/usr/lib/libreoffice/program/soffice",
                    "/opt/libreoffice/program/soffice",
                ]
            ),
            "qpdf": self._find_tool(["/usr/bin/qpdf", "/usr/local/bin/qpdf"]),
            "convert": self._find_tool(["/usr/bin/convert", "/usr/local/bin/convert"]),
            "find": self._find_tool(["/usr/bin/find", "/bin/find"]),
            "grep": self._find_tool(["/bin/grep", "/usr/bin/grep"]),
            "ls": self._find_tool(["/bin/ls", "/usr/bin/ls"]),
            "mkdir": self._find_tool(["/bin/mkdir", "/usr/bin/mkdir"]),
            "rm": self._find_tool(["/bin/rm", "/usr/bin/rm"]),
            "cp": self._find_tool(["/bin/cp", "/usr/bin/cp"]),
            "mv": self._find_tool(["/bin/mv", "/usr/bin/mv"]),
            "cat": self._find_tool(["/bin/cat", "/usr/bin/cat"]),
            "head": self._find_tool(["/usr/bin/head", "/bin/head"]),
            "tail": self._find_tool(["/usr/bin/tail", "/bin/tail"]),
            "wc": self._find_tool(["/usr/bin/wc", "/usr/bin/wc"]),
            "sort": self._find_tool(["/usr/bin/sort", "/bin/sort"]),
            "uniq": self._find_tool(["/usr/bin/uniq", "/bin/uniq"]),
            "awk": self._find_tool(["/usr/bin/awk", "/bin/awk"]),
            "sed": self._find_tool(["/bin/sed", "/usr/bin/sed"]),
            "which": self._find_tool(["/usr/bin/which", "/bin/which"]),
            "python": self._find_tool(
                ["/usr/bin/python3", "/usr/bin/python", sys.executable]
            ),
            "python3": self._find_tool(["/usr/bin/python3", sys.executable]),
            "true": self._find_tool(["/usr/bin/true", "/bin/true"]),
            "false": self._find_tool(["/usr/bin/false", "/bin/false"]),
        }

        # Remove None values (tools that weren't found)
        self.system_tools = {
            k: v for k, v in self.system_tools.items() if v is not None
        }

        # Maximum execution time for system tools (5 minutes)
        self.max_execution_time = 300

        # Tools that require special handling
        self.special_tools = {"soffice", "convert", "qpdf"}

        logger.info(f"System handler initialized with {len(self.system_tools)} tools")
        logger.debug(f"Available tools: {list(self.system_tools.keys())}")

    def _find_tool(self, possible_paths: list[str]) -> str | None:
        """
        Find a system tool in possible paths.

        Args:
            possible_paths: List of possible paths to check

        Returns:
            Path to the tool if found, None otherwise
        """
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        return None

    def execute_tool(
        self, tool_name: str, args: list[str], environment: ExecutionEnvironment
    ) -> "ExecutionResult":
        """
        Execute a system tool with arguments.

        Args:
            tool_name: Name of the tool to execute
            args: Arguments to pass to the tool
            environment: Execution environment

        Returns:
            ExecutionResult with stdout, stderr, and exit code
        """
        try:
            logger.info(f"Executing system tool: {tool_name}")
            logger.debug(f"Tool arguments: {args}")

            # Find the tool executable
            tool_path = self.system_tools.get(tool_name)
            if not tool_path:
                return self._make_error_result(f"System tool not found: {tool_name}")

            # Validate tool arguments
            validation_result = self._validate_tool_args(tool_name, args, environment)
            if not validation_result["valid"]:
                return self._make_error_result(
                    f"Invalid arguments: {validation_result['message']}"
                )

            # Handle special tools
            if tool_name in self.special_tools:
                return self._execute_special_tool(tool_name, args, environment)

            # Execute the tool
            return self._execute_generic_tool(tool_path, args, environment)

        except Exception as e:
            logger.error(f"Error executing system tool {tool_name}: {e}")
            return self._make_error_result(f"Tool execution error: {e}")

    def _validate_tool_args(
        self, tool_name: str, args: list[str], environment: ExecutionEnvironment
    ) -> dict:
        """
        Validate arguments for a system tool.

        Args:
            tool_name: Name of the tool
            args: Arguments to validate
            environment: Execution environment

        Returns:
            Dictionary with 'valid' boolean and 'message' string
        """
        try:
            # Check for dangerous patterns in arguments
            dangerous_patterns = [";", "&&", "||", "|", "$", "`", ">", "<", "&", "\n"]

            for arg in args:
                for pattern in dangerous_patterns:
                    if pattern in arg:
                        return {
                            "valid": False,
                            "message": (
                                f"Dangerous pattern detected in argument: {pattern}"
                            ),
                        }

            # Validate file paths exist and are accessible
            for arg in args:
                if "/" in arg and not arg.startswith("-"):
                    # This looks like a file path
                    file_path = (
                        os.path.join(environment.working_dir, arg)
                        if not arg.startswith("/")
                        else arg
                    )

                    # Special handling for creation tools that don't require input files
                    creation_tools = {"mkdir", "touch", "mkfifo"}
                    if tool_name in creation_tools:
                        # For creation tools, we don't require input files to exist
                        # But we should ensure the parent directory is accessible
                        parent_dir = os.path.dirname(file_path)
                        if parent_dir and not os.path.exists(parent_dir):
                            return {
                                "valid": False,
                                "message": f"Parent directory missing: {parent_dir}",
                            }
                    elif tool_name not in {"pdftotext", "soffice", "qpdf", "convert"}:
                        # For other tools, check if input file exists
                        if not os.path.exists(file_path):
                            return {
                                "valid": False,
                                "message": f"Input file not found: {arg}",
                            }

                    # Check file access permissions
                    if os.path.exists(file_path):
                        if not os.access(file_path, os.R_OK):
                            return {
                                "valid": False,
                                "message": f"Cannot read file: {arg}",
                            }

            return {"valid": True, "message": "Arguments are valid"}

        except Exception as e:
            return {"valid": False, "message": f"Validation error: {e}"}

    def _execute_generic_tool(
        self, tool_path: str, args: list[str], environment: ExecutionEnvironment
    ) -> "ExecutionResult":
        """
        Execute a generic system tool.

        Args:
            tool_path: Path to the tool executable
            args: Arguments for the tool
            environment: Execution environment

        Returns:
            ExecutionResult with output and exit code
        """
        try:
            # Build command
            cmd = [tool_path] + args

            logger.debug(f"Executing command: {' '.join(cmd)}")
            logger.debug(f"Working directory: {environment.working_dir}")

            # Run the tool as a subprocess (synchronous version)
            import subprocess

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=environment.working_dir,
                env=environment.environment_vars,
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
                f"Tool execution timed out after {self.max_execution_time} seconds"
            )
            return ExecutionResult(
                stdout="",
                stderr=(
                    f"Tool execution timed out after {self.max_execution_time} seconds"
                ),
                exit_code=124,  # Standard timeout exit code
            )

        except Exception as e:
            logger.error(f"Error executing tool {tool_path}: {e}")
            return ExecutionResult(
                stdout="", stderr=f"Tool execution error: {e}", exit_code=1
            )

    def _execute_special_tool(
        self, tool_name: str, args: list[str], environment: ExecutionEnvironment
    ) -> "ExecutionResult":
        """
        Execute special tools that require custom handling.

        Args:
            tool_name: Name of the tool
            args: Arguments for the tool
            environment: Execution environment

        Returns:
            ExecutionResult with output and exit code
        """
        if tool_name == "soffice":
            return self._execute_soffice(args, environment)
        elif tool_name == "convert":
            return self._execute_convert(args, environment)
        elif tool_name == "qpdf":
            return self._execute_qpdf(args, environment)
        else:
            # Fallback to generic execution
            tool_path = self.system_tools.get(tool_name)
            return self._execute_generic_tool(tool_path, args, environment)

    def _execute_soffice(
        self, args: list[str], environment: ExecutionEnvironment
    ) -> "ExecutionResult":
        """
        Execute LibreOffice with special handling.

        Args:
            args: Arguments for soffice
            environment: Execution environment

        Returns:
            ExecutionResult with output and exit code
        """
        try:
            tool_path = self.system_tools.get("soffice")
            if not tool_path:
                return self._make_error_result("LibreOffice not found")

            # Add headless mode for server environments
            if "--headless" not in args:
                args = ["--headless"] + args

            # Add conversion timeout
            if "--convert-to" in args:
                # Increase timeout for conversions
                original_timeout = self.max_execution_time
                self.max_execution_time = 600  # 10 minutes for conversions

                try:
                    result = self._execute_generic_tool(tool_path, args, environment)
                finally:
                    self.max_execution_time = original_timeout

                return result

            return self._execute_generic_tool(tool_path, args, environment)

        except Exception as e:
            return self._make_error_result(f"LibreOffice execution error: {e}")

    def _execute_convert(
        self, args: list[str], environment: ExecutionEnvironment
    ) -> "ExecutionResult":
        """
        Execute ImageMagick convert with special handling.

        Args:
            args: Arguments for convert
            environment: Execution environment

        Returns:
            ExecutionResult with output and exit code
        """
        try:
            tool_path = self.system_tools.get("convert")
            if not tool_path:
                return self._make_error_result("ImageMagick convert not found")

            # Validate image processing arguments
            for arg in args:
                if arg.startswith("-") and len(arg) > 10:
                    # Very long argument might be suspicious
                    return self._make_error_result(f"Suspicious argument: {arg}")

            return self._execute_generic_tool(tool_path, args, environment)

        except Exception as e:
            return self._make_error_result(f"ImageMagick execution error: {e}")

    def _execute_qpdf(
        self, args: list[str], environment: ExecutionEnvironment
    ) -> "ExecutionResult":
        """
        Execute QPDF with special handling.

        Args:
            args: Arguments for qpdf
            environment: Execution environment

        Returns:
            ExecutionResult with output and exit code
        """
        try:
            tool_path = self.system_tools.get("qpdf")
            if not tool_path:
                return self._make_error_result("QPDF not found")

            # QPDF often works with encrypted PDFs, so we might need to handle passwords
            # For now, just execute normally
            return self._execute_generic_tool(tool_path, args, environment)

        except Exception as e:
            return self._make_error_result(f"QPDF execution error: {e}")

    def _make_error_result(self, error_message: str) -> "ExecutionResult":
        """
        Create an error execution result.

        Args:
            error_message: Error message to include

        Returns:
            ExecutionResult with error information
        """
        from ..bash.executor import ExecutionResult

        return ExecutionResult(stdout="", stderr=error_message, exit_code=1)

    def get_available_tools(self) -> list[str]:
        """
        Get list of available system tools.

        Returns:
            List of tool names that are available
        """
        return list(self.system_tools.keys())

    def is_tool_available(self, tool_name: str) -> bool:
        """
        Check if a system tool is available.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if the tool is available
        """
        return tool_name in self.system_tools

    def get_tool_path(self, tool_name: str) -> str | None:
        """
        Get the path to a system tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Path to the tool if available, None otherwise
        """
        return self.system_tools.get(tool_name)

    def add_tool(self, tool_name: str, tool_path: str):
        """
        Add a system tool to the handler.

        Args:
            tool_name: Name of the tool
            tool_path: Path to the tool executable
        """
        if os.path.exists(tool_path) and os.access(tool_path, os.X_OK):
            self.system_tools[tool_name] = tool_path
            logger.info(f"Added system tool: {tool_name} at {tool_path}")
        else:
            logger.warning(
                f"Cannot add tool {tool_name}: {tool_path} not found or not executable"
            )

    def remove_tool(self, tool_name: str):
        """
        Remove a system tool from the handler.

        Args:
            tool_name: Name of the tool to remove
        """
        if tool_name in self.system_tools:
            del self.system_tools[tool_name]
            logger.info(f"Removed system tool: {tool_name}")

    def set_max_execution_time(self, seconds: int):
        """
        Set the maximum execution time for system tools.

        Args:
            seconds: Maximum execution time in seconds
        """
        self.max_execution_time = seconds

    def scan_for_tools(self):
        """
        Scan common paths for available system tools.
        """
        common_paths = ["/usr/bin", "/usr/local/bin", "/bin", "/opt/bin"]
        common_tools = [
            "pdftotext",
            "pdftoppm",
            "pdfinfo",
            "pdfseparate",
            "pdfunite",
            "soffice",
            "libreoffice",
            "oowriter",
            "oocalc",
            "ooimpress",
            "qpdf",
            "pdfjam",
            "pdfjoin",
            "convert",
            "identify",
            "mogrify",
            "montage",
            "ffmpeg",
            "ffprobe",
            "ffplay",
            "unzip",
            "zip",
            "tar",
            "gzip",
            "bzip2",
            "xz",
            "git",
            "svn",
            "hg",
            "curl",
            "wget",
            "http",
            "aria2c",
            "rsync",
            "scp",
            "sftp",
        ]

        added_tools = []
        for tool_name in common_tools:
            if tool_name not in self.system_tools:
                for path in common_paths:
                    tool_path = os.path.join(path, tool_name)
                    if os.path.exists(tool_path) and os.access(tool_path, os.X_OK):
                        self.system_tools[tool_name] = tool_path
                        added_tools.append(tool_name)
                        break

        if added_tools:
            logger.info(
                f"Scanned and added {len(added_tools)} new tools: {added_tools}"
            )

        return added_tools
