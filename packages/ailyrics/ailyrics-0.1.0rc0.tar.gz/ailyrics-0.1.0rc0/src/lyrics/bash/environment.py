"""
Environment Manager - Manages execution environment for bash commands.
"""

import logging
import os

from .types import ExecutionEnvironment

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """
    Manages execution environment for bash commands.

    This includes:
    - Working directory management
    - Environment variables
    - Skills and workspace paths
    - State persistence across commands
    """

    def __init__(self):
        self.skills_path: str = "/skills"
        self.workspace_path: str = "/workspace"
        self.default_env_vars: dict[str, str] = {}
        self._current_working_dir: str = "/workspace"

    def initialize(self, skills_path: str, workspace_path: str):
        """
        Initialize the environment manager with paths.

        Args:
            skills_path: Path to the skills directory
            workspace_path: Path to the workspace directory
        """
        self.skills_path = skills_path
        self.workspace_path = workspace_path
        self._current_working_dir = workspace_path

        # Set up default environment variables
        self.default_env_vars = {
            "SKILLS_PATH": skills_path,
            "WORKSPACE_PATH": workspace_path,
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": self._build_python_path(),
            "HOME": "/tmp",
            "TMPDIR": "/tmp",
        }

        logger.info("Environment manager initialized")
        logger.info(f"Skills path: {skills_path}")
        logger.info(f"Workspace path: {workspace_path}")

    def get_execution_environment(
        self, working_dir: str | None = None, custom_env: dict[str, str] | None = None
    ) -> ExecutionEnvironment:
        """
        Get the execution environment for a command.

        Args:
            working_dir: Working directory for the command (optional)
            custom_env: Custom environment variables (optional)

        Returns:
            ExecutionEnvironment configured for the command
        """
        # Determine working directory
        if working_dir:
            # Validate and resolve the working directory
            resolved_working_dir = self._resolve_working_dir(working_dir)
        else:
            resolved_working_dir = self._current_working_dir

        # Build environment variables
        env_vars = self.default_env_vars.copy()

        # Add current working directory to environment
        env_vars["PWD"] = resolved_working_dir

        # Merge custom environment variables
        if custom_env:
            env_vars.update(custom_env)

        # Add any additional environment setup
        self._setup_additional_environment(env_vars, resolved_working_dir)

        return ExecutionEnvironment(
            working_dir=resolved_working_dir,
            environment_vars=env_vars,
            skills_path=self.skills_path,
            workspace_path=self.workspace_path,
        )

    def update_working_directory(self, new_dir: str):
        """
        Update the current working directory.

        Args:
            new_dir: New working directory path
        """
        resolved_dir = self._resolve_working_dir(new_dir)
        if self._validate_working_dir(resolved_dir):
            self._current_working_dir = resolved_dir
            logger.debug(f"Updated working directory to: {resolved_dir}")
        else:
            logger.warning(f"Invalid working directory: {new_dir}")

    def get_current_working_dir(self) -> str:
        """Get the current working directory."""
        return self._current_working_dir

    def _resolve_working_dir(self, working_dir: str) -> str:
        """
        Resolve and validate a working directory path.

        Args:
            working_dir: Working directory path (relative or absolute)

        Returns:
            Resolved absolute path
        """
        # Handle absolute paths
        if working_dir.startswith("/"):
            return working_dir

        # Handle relative paths
        if working_dir.startswith("./"):
            # Relative to current working directory
            relative_path = working_dir[2:]
            return os.path.join(self._current_working_dir, relative_path)
        elif working_dir.startswith("../"):
            # Parent directory
            parent_dir = os.path.dirname(self._current_working_dir)
            return os.path.join(parent_dir, working_dir[3:])
        else:
            # Simple relative path
            return os.path.join(self._current_working_dir, working_dir)

    def _validate_working_dir(self, working_dir: str) -> bool:
        """
        Validate that a working directory is safe to use.

        Args:
            working_dir: Working directory path to validate

        Returns:
            True if the directory is valid and safe
        """
        # Check that the directory is within allowed paths
        allowed_paths = [self.workspace_path, "/tmp", "/var/tmp"]

        # Also allow subdirectories of skills path for reading
        allowed_paths.append(self.skills_path)

        for allowed_path in allowed_paths:
            if working_dir.startswith(allowed_path):
                return True

        logger.warning(f"Working directory '{working_dir}' is not in allowed paths")
        return False

    def _build_python_path(self) -> str:
        """Build the PYTHONPATH environment variable."""
        python_paths = []

        # Add current directory
        python_paths.append(".")

        # Add skills path (for importing skill modules)
        if os.path.exists(self.skills_path):
            python_paths.append(self.skills_path)
            # Add public subdirectory
            public_path = os.path.join(self.skills_path, "public")
            if os.path.exists(public_path):
                python_paths.append(public_path)

        # Add workspace path
        python_paths.append(self.workspace_path)

        # Add existing PYTHONPATH
        existing_pythonpath = os.environ.get("PYTHONPATH", "")
        if existing_pythonpath:
            python_paths.append(existing_pythonpath)

        return ":".join(python_paths)

    def _setup_additional_environment(self, env_vars: dict[str, str], working_dir: str):
        """
        Set up additional environment variables based on context.

        Args:
            env_vars: Environment variables dictionary to modify
            working_dir: Current working directory
        """
        # Set up tool-specific environment variables

        # LibreOffice configuration
        libreoffice_paths = [
            "/usr/bin/soffice",
            "/usr/lib/libreoffice/program/soffice",
            "/opt/libreoffice/program/soffice",
        ]

        for lo_path in libreoffice_paths:
            if os.path.exists(lo_path):
                env_vars["SOFFICE_PATH"] = lo_path
                break

        # Poppler tools (pdftotext, pdftoppm, etc.)
        poppler_paths = ["/usr/bin", "/usr/local/bin"]

        for poppler_path in poppler_paths:
            pdftotext_path = os.path.join(poppler_path, "pdftotext")
            if os.path.exists(pdftotext_path):
                env_vars["POPPLER_PATH"] = poppler_path
                break

        # ImageMagick
        convert_paths = ["/usr/bin/convert", "/usr/local/bin/convert"]

        for convert_path in convert_paths:
            if os.path.exists(convert_path):
                env_vars["IMAGEMAGICK_PATH"] = os.path.dirname(convert_path)
                break

        # QPDF
        qpdf_paths = ["/usr/bin/qpdf", "/usr/local/bin/qpdf"]

        for qpdf_path in qpdf_paths:
            if os.path.exists(qpdf_path):
                env_vars["QPDF_PATH"] = qpdf_path
                break

        # Set temporary directory
        env_vars["TMPDIR"] = "/tmp"
        env_vars["TEMP"] = "/tmp"
        env_vars["TMP"] = "/tmp"

        # Add working directory to PATH for local executables
        if working_dir not in env_vars["PATH"]:
            env_vars["PATH"] = f"{working_dir}:{env_vars['PATH']}"

    def get_skills_info(self) -> dict[str, str]:
        """Get information about the skills environment."""
        return {
            "skills_path": self.skills_path,
            "workspace_path": self.workspace_path,
            "current_working_dir": self._current_working_dir,
            "python_path": self.default_env_vars.get("PYTHONPATH", ""),
        }

    def is_path_in_skills(self, path: str) -> bool:
        """
        Check if a path is within the skills directory.

        Args:
            path: Path to check

        Returns:
            True if the path is within skills directory
        """
        return path.startswith(self.skills_path)

    def is_path_in_workspace(self, path: str) -> bool:
        """
        Check if a path is within the workspace directory.

        Args:
            path: Path to check

        Returns:
            True if the path is within workspace directory
        """
        return path.startswith(self.workspace_path)

    def make_path_relative_to_skills(self, path: str) -> str | None:
        """
        Make a path relative to the skills directory.

        Args:
            path: Absolute path to make relative

        Returns:
            Relative path if path is within skills directory, None otherwise
        """
        if self.is_path_in_skills(path):
            return os.path.relpath(path, self.skills_path)
        return None

    def make_path_relative_to_workspace(self, path: str) -> str | None:
        """
        Make a path relative to the workspace directory.

        Args:
            path: Absolute path to make relative

        Returns:
            Relative path if path is within workspace directory, None otherwise
        """
        if self.is_path_in_workspace(path):
            return os.path.relpath(path, self.workspace_path)
        return None
