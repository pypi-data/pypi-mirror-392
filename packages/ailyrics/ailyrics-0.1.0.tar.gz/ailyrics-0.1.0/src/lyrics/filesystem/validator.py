"""
Path Validator - Validates file system access permissions.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class PathValidator:
    """
    Validates file system access permissions for Agent Skills.

    This validator ensures that:
    - Skills can only be read from (not modified)
    - Workspace files can be read and written
    - No access outside allowed directories
    - No symbolic link traversal attacks
    """

    def __init__(self):
        self.skills_path: str = "/skills"
        self.workspace_path: str = "/workspace"
        self.read_only_paths: set = set()
        self.read_write_paths: set = set()
        self.blocked_paths: set = set()

    def initialize(self, skills_path: str, workspace_path: str):
        """
        Initialize the path validator with base paths.

        Args:
            skills_path: Path to skills directory
            workspace_path: Path to workspace directory
        """
        self.skills_path = os.path.abspath(skills_path)
        self.workspace_path = os.path.abspath(workspace_path)

        # Set up default permissions
        self.read_only_paths = {
            self.skills_path,
            os.path.join(self.skills_path, "public"),
        }

        self.read_write_paths = {self.workspace_path}

        # Block dangerous paths
        self.blocked_paths = {
            "/etc",
            "/home",
            "/root",
            "/boot",
            "/dev",
            "/proc",
            "/sys",
            "/usr",
            "/bin",
            "/sbin",
            "/lib",
            "/lib64",
            "/opt",
            "/var/log",
            "/var/run",
            "/var/lib",
        }

        logger.info("Path validator initialized")
        logger.info(f"Skills path (read-only): {self.skills_path}")
        logger.info(f"Workspace path (read-write): {self.workspace_path}")

    def can_read(self, path: str) -> bool:
        """
        Check if a path can be read.

        Args:
            path: Path to check

        Returns:
            True if the path can be read
        """
        try:
            normalized_path = os.path.abspath(path)

            # Check if path is blocked
            if self._is_path_blocked(normalized_path):
                return False

            # Check if path exists
            if not os.path.exists(normalized_path):
                return False

            # Check if it's in a read-only path (takes precedence)
            if self._is_path_in_read_only(normalized_path):
                return True

            # Check if it's in a read-write path
            if self._is_path_in_read_write(normalized_path):
                return os.access(normalized_path, os.R_OK)

            # Path is not in any allowed area
            return False

        except Exception as e:
            logger.error(f"Error checking read permission for {path}: {e}")
            return False

    def can_write(self, path: str) -> bool:
        """
        Check if a path can be written to.

        Args:
            path: Path to check

        Returns:
            True if the path can be written
        """
        try:
            normalized_path = os.path.abspath(path)

            # Check if path is blocked
            if self._is_path_blocked(normalized_path):
                return False

            # Check if it's in a read-only path (read-only takes precedence)
            if self._is_path_in_read_only(normalized_path):
                return False

            # Check if it's in a read-write path
            if self._is_path_in_read_write(normalized_path):
                # For existing files, check write permission
                if os.path.exists(normalized_path):
                    return os.access(normalized_path, os.W_OK)

                # For new files, check parent directory write permission
                parent_dir = os.path.dirname(normalized_path)
                if os.path.exists(parent_dir):
                    return os.access(parent_dir, os.W_OK)

                # Allow creating new files in read-write directories
                return True

            # Path is not in any read-write area
            return False

        except Exception as e:
            logger.error(f"Error checking write permission for {path}: {e}")
            return False

    def can_execute(self, path: str) -> bool:
        """
        Check if a path can be executed.

        Args:
            path: Path to check

        Returns:
            True if the path can be executed
        """
        try:
            normalized_path = os.path.abspath(path)

            # Check if path is blocked
            if self._is_path_blocked(normalized_path):
                return False

            # Check if path exists
            if not os.path.exists(normalized_path):
                return False

            # Check if it's in a read-only or read-write path
            if self._is_path_in_read_only(normalized_path):
                return os.access(normalized_path, os.X_OK)

            if self._is_path_in_read_write(normalized_path):
                return os.access(normalized_path, os.X_OK)

            # Path is not in any allowed area
            return False

        except Exception as e:
            logger.error(f"Error checking execute permission for {path}: {e}")
            return False

    def can_access(self, path: str) -> bool:
        """
        Check if a path can be accessed (read, write, or execute).

        Args:
            path: Path to check

        Returns:
            True if the path can be accessed in any way
        """
        return self.can_read(path) or self.can_write(path) or self.can_execute(path)

    def can_delete(self, path: str) -> bool:
        """
        Check if a path can be deleted.

        Args:
            path: Path to check

        Returns:
            True if the path can be deleted
        """
        # Deletion follows the same rules as writing
        return self.can_write(path)

    def can_create(self, path: str) -> bool:
        """
        Check if a file or directory can be created at the given path.

        Args:
            path: Path where the file/directory would be created

        Returns:
            True if creation is allowed
        """
        try:
            normalized_path = os.path.abspath(path)

            # Check if path is blocked
            if self._is_path_blocked(normalized_path):
                return False

            # Check if it's in a read-only path (read-only takes precedence)
            if self._is_path_in_read_only(normalized_path):
                return False

            # Check if it's in a read-write path
            if self._is_path_in_read_write(normalized_path):
                # Check parent directory permissions
                parent_dir = os.path.dirname(normalized_path)
                if os.path.exists(parent_dir):
                    return os.access(parent_dir, os.W_OK)
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking create permission for {path}: {e}")
            return False

    def _is_path_blocked(self, path: str) -> bool:
        """
        Check if a path is in the blocked paths list.

        Args:
            path: Path to check

        Returns:
            True if the path is blocked
        """
        # Check exact matches
        if path in self.blocked_paths:
            return True

        # Check if path is a subdirectory of any blocked path
        for blocked_path in self.blocked_paths:
            if path.startswith(blocked_path + os.sep):
                return True

        return False

    def _is_path_in_read_only(self, path: str) -> bool:
        """
        Check if a path is in a read-only area.

        Args:
            path: Path to check

        Returns:
            True if the path is in a read-only area
        """
        # Check exact matches
        if path in self.read_only_paths:
            return True

        # Check if path is a subdirectory of any read-only path
        for read_only_path in self.read_only_paths:
            if path.startswith(read_only_path + os.sep):
                return True

        return False

    def _is_path_in_read_write(self, path: str) -> bool:
        """
        Check if a path is in a read-write area.

        Args:
            path: Path to check

        Returns:
            True if the path is in a read-write area
        """
        # First check if it's a read-only path (read-only takes precedence)
        if self._is_path_in_read_only(path):
            return False

        # Check exact matches
        if path in self.read_write_paths:
            return True

        # Check if path is a subdirectory of any read-write path
        for read_write_path in self.read_write_paths:
            if path.startswith(read_write_path + os.sep):
                return True

        return False

    def validate_path_traversal(self, path: str, base_path: str) -> bool:
        """
        Validate that a path doesn't traverse outside a base path.

        Args:
            path: Path to validate
            base_path: Base path that the path should stay within

        Returns:
            True if the path doesn't traverse outside the base path
        """
        try:
            # Get absolute paths
            abs_path = os.path.abspath(path)
            abs_base_path = os.path.abspath(base_path)

            # Check if path is within base path
            return (
                abs_path.startswith(abs_base_path + os.sep) or abs_path == abs_base_path
            )

        except Exception as e:
            logger.error(f"Error validating path traversal for {path}: {e}")
            return False

    def validate_symlink(self, path: str) -> bool:
        """
        Validate that a path doesn't contain dangerous symbolic links.

        Args:
            path: Path to validate

        Returns:
            True if the path is safe (no dangerous symlinks)
        """
        try:
            path_obj = Path(path)

            # Check if the path itself is a symlink
            if path_obj.is_symlink():
                # Resolve the symlink
                resolved_path = path_obj.resolve()

                # Check if the resolved path is allowed
                if not self._is_path_allowed(str(resolved_path)):
                    return False

            # Check parent directories for symlinks
            for parent in path_obj.parents:
                if parent.is_symlink():
                    resolved_parent = parent.resolve()

                    # Check if the resolved parent is allowed
                    if not self._is_path_allowed(str(resolved_parent)):
                        return False

            return True

        except Exception as e:
            logger.error(f"Error validating symlink for {path}: {e}")
            return False

    def _is_path_allowed(self, path: str) -> bool:
        """
        Check if a path is generally allowed (not blocked).

        Args:
            path: Path to check

        Returns:
            True if the path is allowed
        """
        # Check if path is blocked
        if self._is_path_blocked(path):
            return False

        # Check if path is in read-only or read-write areas
        if self._is_path_in_read_only(path) or self._is_path_in_read_write(path):
            return True

        return False

    def add_read_only_path(self, path: str):
        """
        Add a path to the read-only list.

        Args:
            path: Path to add
        """
        normalized_path = os.path.abspath(path)
        self.read_only_paths.add(normalized_path)
        logger.info(f"Added read-only path: {normalized_path}")

    def add_read_write_path(self, path: str):
        """
        Add a path to the read-write list.

        Args:
            path: Path to add
        """
        normalized_path = os.path.abspath(path)
        self.read_write_paths.add(normalized_path)
        logger.info(f"Added read-write path: {normalized_path}")

    def add_blocked_path(self, path: str):
        """
        Add a path to the blocked list.

        Args:
            path: Path to block
        """
        normalized_path = os.path.abspath(path)
        self.blocked_paths.add(normalized_path)
        logger.info(f"Added blocked path: {normalized_path}")

    def remove_path(self, path: str):
        """
        Remove a path from all permission lists.

        Args:
            path: Path to remove
        """
        normalized_path = os.path.abspath(path)
        self.read_only_paths.discard(normalized_path)
        self.read_write_paths.discard(normalized_path)
        self.blocked_paths.discard(normalized_path)
        logger.info(f"Removed path: {normalized_path}")

    def get_permissions_info(self, path: str) -> dict:
        """
        Get detailed permission information for a path.

        Args:
            path: Path to check

        Returns:
            Dictionary with permission information
        """
        try:
            normalized_path = os.path.abspath(path)

            info = {
                "path": normalized_path,
                "exists": os.path.exists(normalized_path),
                "is_read_only": self._is_path_in_read_only(normalized_path),
                "is_read_write": self._is_path_in_read_write(normalized_path),
                "is_blocked": self._is_path_blocked(normalized_path),
                "can_read": self.can_read(normalized_path),
                "can_write": self.can_write(normalized_path),
                "can_execute": self.can_execute(normalized_path),
                "can_delete": self.can_delete(normalized_path),
                "can_create": self.can_create(normalized_path),
            }

            if info["exists"]:
                stat = os.stat(normalized_path)
                info.update(
                    {
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "is_file": os.path.isfile(normalized_path),
                        "is_directory": os.path.isdir(normalized_path),
                        "is_symlink": os.path.islink(normalized_path),
                    }
                )

            return info

        except Exception as e:
            logger.error(f"Error getting permissions info for {path}: {e}")
            return {
                "path": path,
                "error": str(e),
                "can_read": False,
                "can_write": False,
                "can_execute": False,
                "can_delete": False,
                "can_create": False,
            }

    def validate_path_safety(self, path: str) -> dict:
        """
        Perform comprehensive safety validation on a path.

        Args:
            path: Path to validate

        Returns:
            Dictionary with validation results
        """
        try:
            normalized_path = os.path.abspath(path)

            validation = {
                "path": normalized_path,
                "is_valid": True,
                "errors": [],
                "warnings": [],
            }

            # Check if path exists
            if not os.path.exists(normalized_path):
                validation["warnings"].append("Path does not exist")

            # Check path traversal
            if not self.validate_path_traversal(normalized_path, self.workspace_path):
                if not self.validate_path_traversal(normalized_path, self.skills_path):
                    validation["errors"].append(
                        "Path traversal outside allowed directories"
                    )
                    validation["is_valid"] = False

            # Check symlink safety
            if not self.validate_symlink(normalized_path):
                validation["errors"].append("Dangerous symbolic link detected")
                validation["is_valid"] = False

            # Check blocked paths
            if self._is_path_blocked(normalized_path):
                validation["errors"].append("Path is in blocked list")
                validation["is_valid"] = False

            # Check permissions
            permissions = self.get_permissions_info(normalized_path)
            if not permissions["can_access"]:
                validation["warnings"].append("No access permissions for path")

            return validation

        except Exception as e:
            logger.error(f"Error validating path safety for {path}: {e}")
            return {
                "path": path,
                "is_valid": False,
                "errors": [f"Validation error: {e}"],
                "warnings": [],
            }
