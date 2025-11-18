"""
Path Resolver - Resolves relative paths to absolute paths.
"""

import logging
import os

logger = logging.getLogger(__name__)


class PathResolver:
    """
    Resolves relative paths to absolute paths for Agent Skills.

    This resolver handles the specific path resolution rules for the
    Lyrics system, including:
    - Skill-relative paths (e.g., "xlsx/recalc.py")
    - Workspace-relative paths (e.g., "./file.txt")
    - Absolute paths (e.g., "/workspace/file.txt")
    """

    def __init__(self):
        self.skills_path: str = "/skills"
        self.workspace_path: str = "/workspace"
        self.public_skills_path: str = "/skills/public"

    def initialize(self, skills_path: str, workspace_path: str = "/workspace"):
        """
        Initialize the path resolver with base paths.

        Args:
            skills_path: Base path to skills directory
            workspace_path: Base path to workspace directory
        """
        self.skills_path = skills_path
        self.workspace_path = workspace_path
        self.public_skills_path = os.path.join(skills_path, "public")

        logger.info("Path resolver initialized")
        logger.info(f"Skills path: {skills_path}")
        logger.info(f"Workspace path: {workspace_path}")
        logger.info(f"Public skills path: {self.public_skills_path}")

    def resolve(self, path: str, working_dir: str) -> str:
        """
        Resolve a path to its absolute form.

        Args:
            path: The path to resolve (can be relative or absolute)
            working_dir: Current working directory

        Returns:
            Absolute path

        Raises:
            ValueError: If the path is invalid or unsafe
        """
        if not path:
            raise ValueError("Empty path provided")

        # Handle absolute paths
        if path.startswith("/"):
            return self._resolve_absolute_path(path)

        # Handle special relative paths
        if path.startswith("./"):
            return self._resolve_current_dir_path(path, working_dir)

        if path.startswith("../"):
            return self._resolve_parent_dir_path(path, working_dir)

        # Handle skill-relative paths (e.g., "xlsx/recalc.py")
        if self._is_skill_relative_path(path):
            return self._resolve_skill_path(path)

        # Handle workspace-relative paths (simple relative paths)
        return self._resolve_workspace_path(path, working_dir)

    def _resolve_absolute_path(self, path: str) -> str:
        """
        Resolve an absolute path.

        Args:
            path: Absolute path starting with '/'

        Returns:
            Resolved absolute path

        Raises:
            ValueError: If the path is invalid or unsafe
        """
        # Normalize the path
        normalized_path = os.path.normpath(path)

        # Ensure it's still absolute after normalization
        if not normalized_path.startswith("/"):
            raise ValueError(f"Path normalization resulted in relative path: {path}")

        # Validate that the path is within allowed directories
        if not self._is_path_allowed(normalized_path):
            raise ValueError(f"Path not in allowed directories: {path}")

        return normalized_path

    def _resolve_current_dir_path(self, path: str, working_dir: str) -> str:
        """
        Resolve a path starting with './'.

        Args:
            path: Path starting with './'
            working_dir: Current working directory

        Returns:
            Resolved absolute path
        """
        # Remove the './' prefix
        relative_path = path[2:]

        # Join with working directory
        absolute_path = os.path.join(working_dir, relative_path)

        # Normalize and validate
        normalized_path = os.path.normpath(absolute_path)

        if not self._is_path_allowed(normalized_path):
            raise ValueError(f"Path not in allowed directories: {path}")

        return normalized_path

    def _resolve_parent_dir_path(self, path: str, working_dir: str) -> str:
        """
        Resolve a path starting with '../'.

        Args:
            path: Path starting with '../'
            working_dir: Current working directory

        Returns:
            Resolved absolute path

        Raises:
            ValueError: If the path goes outside allowed directories
        """
        # Count the number of parent directory references
        parent_count = 0
        remaining_path = path

        while remaining_path.startswith("../"):
            parent_count += 1
            remaining_path = remaining_path[3:]

        # Build the base path by going up parent_count directories
        current_dir = working_dir
        for _ in range(parent_count):
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached root
                break
            current_dir = parent_dir

        # Join with remaining path
        if remaining_path:
            absolute_path = os.path.join(current_dir, remaining_path)
        else:
            absolute_path = current_dir

        # Normalize and validate
        normalized_path = os.path.normpath(absolute_path)

        if not self._is_path_allowed(normalized_path):
            raise ValueError(f"Path goes outside allowed directories: {path}")

        return normalized_path

    def _resolve_skill_path(self, path: str) -> str:
        """
        Resolve a skill-relative path.

        Args:
            path: Path like "xlsx/recalc.py"

        Returns:
            Absolute path in the skills directory
        """
        # Join with public skills path
        absolute_path = os.path.join(self.public_skills_path, path)

        # Normalize
        normalized_path = os.path.normpath(absolute_path)

        # Validate it's within skills directory
        if not normalized_path.startswith(self.skills_path):
            raise ValueError(f"Path resolved outside skills directory: {path}")

        return normalized_path

    def _resolve_workspace_path(self, path: str, working_dir: str) -> str:
        """
        Resolve a workspace-relative path.

        Args:
            path: Relative path
            working_dir: Current working directory

        Returns:
            Resolved absolute path
        """
        # Join with working directory
        absolute_path = os.path.join(working_dir, path)

        # Normalize
        normalized_path = os.path.normpath(absolute_path)

        # Validate it's within allowed directories
        if not self._is_path_allowed(normalized_path):
            raise ValueError(f"Path not in allowed directories: {path}")

        return normalized_path

    def _is_skill_relative_path(self, path: str) -> bool:
        """
        Check if a path looks like a skill-relative path.

        Args:
            path: Path to check

        Returns:
            True if it looks like a skill-relative path
        """
        # Skill-relative paths typically look like "skillname/file.txt"
        if "/" not in path:
            return False

        # Get the first component (skill name)
        skill_name = path.split("/")[0]

        # Check if it looks like a skill name (not a path component)
        if skill_name in [".", "..", ""]:
            return False

        # Check if it's a known skill directory
        skill_path = os.path.join(self.public_skills_path, skill_name)
        if os.path.exists(skill_path) and os.path.isdir(skill_path):
            return True

        # If we don't know, make a heuristic decision
        # Skill names are typically alphanumeric with hyphens/underscores
        if skill_name.replace("-", "").replace("_", "").isalnum():
            return True

        return False

    def _is_path_allowed(self, path: str) -> bool:
        """
        Check if a path is within allowed directories.

        Args:
            path: Absolute path to check

        Returns:
            True if the path is allowed
        """
        # List of allowed base directories
        allowed_bases = [
            self.skills_path,
            self.workspace_path,
            "/tmp",
            "/var/tmp",
            "/dev/shm",
        ]

        # Check if path starts with any allowed base
        for allowed_base in allowed_bases:
            if path.startswith(allowed_base):
                return True

        return False

    def is_skill_path(self, path: str) -> bool:
        """
        Check if a path is within the skills directory.

        Args:
            path: Path to check

        Returns:
            True if the path is within skills directory
        """
        try:
            resolved_path = self.resolve(path, self.workspace_path)
            return resolved_path.startswith(self.skills_path)
        except Exception:
            return False

    def is_workspace_path(self, path: str) -> bool:
        """
        Check if a path is within the workspace directory.

        Args:
            path: Path to check

        Returns:
            True if the path is within workspace directory
        """
        try:
            resolved_path = self.resolve(path, self.workspace_path)
            return resolved_path.startswith(self.workspace_path)
        except Exception:
            return False

    def make_relative_to_skills(self, path: str) -> str | None:
        """
        Make a path relative to the skills directory.

        Args:
            path: Absolute path to make relative

        Returns:
            Relative path if possible, None otherwise
        """
        try:
            resolved_path = self.resolve(path, self.workspace_path)
            if resolved_path.startswith(self.skills_path):
                return os.path.relpath(resolved_path, self.skills_path)
        except Exception:
            pass
        return None

    def make_relative_to_workspace(self, path: str) -> str | None:
        """
        Make a path relative to the workspace directory.

        Args:
            path: Absolute path to make relative

        Returns:
            Relative path if possible, None otherwise
        """
        try:
            resolved_path = self.resolve(path, self.workspace_path)
            if resolved_path.startswith(self.workspace_path):
                return os.path.relpath(resolved_path, self.workspace_path)
        except Exception:
            pass
        return None

    def get_skill_name_from_path(self, path: str) -> str | None:
        """
        Extract the skill name from a skill-relative path.

        Args:
            path: Path that might be skill-relative

        Returns:
            Skill name if path is skill-relative, None otherwise
        """
        if not self._is_skill_relative_path(path):
            return None

        return path.split("/")[0]

    def list_skills(self) -> list:
        """
        List available skills in the skills directory.

        Returns:
            List of skill names
        """
        skills = []

        try:
            if os.path.exists(self.public_skills_path):
                for entry in os.listdir(self.public_skills_path):
                    entry_path = os.path.join(self.public_skills_path, entry)
                    if os.path.isdir(entry_path) and not entry.startswith("."):
                        skills.append(entry)
        except Exception as e:
            logger.error(f"Error listing skills: {e}")

        return sorted(skills)

    def get_skill_info(self, skill_name: str) -> dict | None:
        """
        Get information about a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Dictionary with skill information or None
        """
        skill_path = os.path.join(self.public_skills_path, skill_name)

        if not os.path.exists(skill_path) or not os.path.isdir(skill_path):
            return None

        try:
            # Count files in the skill directory
            file_count = 0
            for root, dirs, files in os.walk(skill_path):
                file_count += len(files)

            return {
                "name": skill_name,
                "path": skill_path,
                "file_count": file_count,
                "exists": True,
            }
        except Exception as e:
            logger.error(f"Error getting skill info for {skill_name}: {e}")
            return None

    def validate_path_string(self, path: str) -> bool:
        """
        Validate that a path string is syntactically valid.

        Args:
            path: Path string to validate

        Returns:
            True if the path string is valid
        """
        if not path:
            return False

        # Check for null bytes and other dangerous characters
        dangerous_chars = ["\x00", "\n", "\r"]
        for char in dangerous_chars:
            if char in path:
                return False

        # Check for path traversal patterns
        if ".." in path and not path.startswith("../"):
            # Only allow .. at the beginning (parent directory references)
            return False

        # Basic length check
        if len(path) > 4096:  # Reasonable maximum path length
            return False

        return True

    def is_safe_path(self, path: str, working_dir: str) -> bool:
        """
        Check if a path is safe to resolve.

        Args:
            path: Path to check
            working_dir: Current working directory

        Returns:
            True if the path is safe
        """
        try:
            resolved_path = self.resolve(path, working_dir)
            return self._is_path_allowed(resolved_path)
        except Exception:
            return False
