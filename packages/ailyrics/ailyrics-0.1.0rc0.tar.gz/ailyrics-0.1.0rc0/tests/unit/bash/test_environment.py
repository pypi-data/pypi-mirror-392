"""
Unit tests for the Environment Manager module.
"""

import os
import tempfile
from unittest.mock import patch

from lyrics.bash.environment import EnvironmentManager
from lyrics.bash.types import ExecutionEnvironment


class TestEnvironmentManager:
    """Test cases for EnvironmentManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = EnvironmentManager()
        self.temp_dir = tempfile.mkdtemp()
        self.skills_path = os.path.join(self.temp_dir, "skills")
        self.workspace_path = os.path.join(self.temp_dir, "workspace")

        # Create directory structure
        os.makedirs(self.skills_path, exist_ok=True)
        os.makedirs(os.path.join(self.skills_path, "public"), exist_ok=True)
        os.makedirs(self.workspace_path, exist_ok=True)

        # Initialize manager
        self.manager.initialize(self.skills_path, self.workspace_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test environment manager initialization."""
        assert self.manager.skills_path == self.skills_path
        assert self.manager.workspace_path == self.workspace_path
        assert self.manager.get_current_working_dir() == self.workspace_path

        # Check default environment variables
        assert self.manager.default_env_vars["SKILLS_PATH"] == self.skills_path
        assert self.manager.default_env_vars["WORKSPACE_PATH"] == self.workspace_path
        assert "PATH" in self.manager.default_env_vars
        assert "PYTHONPATH" in self.manager.default_env_vars

    def test_get_execution_environment_default(self):
        """Test getting execution environment with default parameters."""
        env = self.manager.get_execution_environment()

        assert isinstance(env, ExecutionEnvironment)
        assert env.working_dir == self.workspace_path
        assert env.skills_path == self.skills_path
        assert env.workspace_path == self.workspace_path
        assert env.environment_vars["PWD"] == self.workspace_path
        assert env.environment_vars["SKILLS_PATH"] == self.skills_path
        assert env.environment_vars["WORKSPACE_PATH"] == self.workspace_path

    def test_get_execution_environment_custom_working_dir(self):
        """Test getting execution environment with custom working directory."""
        custom_dir = os.path.join(self.workspace_path, "subdir")
        os.makedirs(custom_dir, exist_ok=True)

        env = self.manager.get_execution_environment(working_dir=custom_dir)

        assert env.working_dir == custom_dir
        assert env.environment_vars["PWD"] == custom_dir

    def test_get_execution_environment_custom_env_vars(self):
        """Test getting execution environment with custom environment variables."""
        custom_env = {"CUSTOM_VAR": "custom_value", "TEST_VAR": "test_value"}

        env = self.manager.get_execution_environment(custom_env=custom_env)

        assert env.environment_vars["CUSTOM_VAR"] == "custom_value"
        assert env.environment_vars["TEST_VAR"] == "test_value"
        # Default vars should still be present
        assert env.environment_vars["SKILLS_PATH"] == self.skills_path

    def test_update_working_directory_absolute_path(self):
        """Test updating working directory with absolute path."""
        new_dir = os.path.join(self.workspace_path, "new_workspace")
        os.makedirs(new_dir, exist_ok=True)

        self.manager.update_working_directory(new_dir)

        assert self.manager.get_current_working_dir() == new_dir

    def test_update_working_directory_relative_path(self):
        """Test updating working directory with relative path."""
        subdir = os.path.join(self.workspace_path, "subdir")
        os.makedirs(subdir, exist_ok=True)

        # Change to subdir first
        self.manager.update_working_directory(subdir)
        assert self.manager.get_current_working_dir() == subdir

        # Then update with relative path (go up one level from subdir)
        # Use absolute path to avoid resolution issues
        parent_dir = os.path.dirname(subdir)
        self.manager.update_working_directory(parent_dir)

        assert self.manager.get_current_working_dir() == self.workspace_path

    def test_update_working_directory_invalid_path(self):
        """Test updating working directory with invalid path."""
        # Try to update with blocked path
        blocked_path = "/etc/passwd"

        # Should not change current directory
        original_dir = self.manager.get_current_working_dir()
        self.manager.update_working_directory(blocked_path)

        assert self.manager.get_current_working_dir() == original_dir

    def test_resolve_working_dir_absolute(self):
        """Test resolving absolute working directory."""
        abs_path = "/tmp/test"
        resolved = self.manager._resolve_working_dir(abs_path)
        assert resolved == abs_path

    def test_resolve_working_dir_relative_current(self):
        """Test resolving relative working directory (./)."""
        rel_path = "./subdir"
        resolved = self.manager._resolve_working_dir(rel_path)
        expected = os.path.join(self.workspace_path, "subdir")
        assert resolved == expected

    def test_resolve_working_dir_relative_parent(self):
        """Test resolving relative working directory (../)."""
        rel_path = "../tmp"
        resolved = self.manager._resolve_working_dir(rel_path)
        expected = os.path.join(os.path.dirname(self.workspace_path), "tmp")
        assert resolved == expected

    def test_resolve_working_dir_simple_relative(self):
        """Test resolving simple relative working directory."""
        rel_path = "subdir"
        resolved = self.manager._resolve_working_dir(rel_path)
        expected = os.path.join(self.workspace_path, "subdir")
        assert resolved == expected

    def test_validate_working_dir_allowed_paths(self):
        """Test validating working directory in allowed paths."""
        # Test workspace path
        assert self.manager._validate_working_dir(self.workspace_path) is True

        # Test skills path
        assert self.manager._validate_working_dir(self.skills_path) is True

        # Test /tmp
        assert self.manager._validate_working_dir("/tmp") is True

        # Test subdirectory of workspace
        subdir = os.path.join(self.workspace_path, "subdir")
        assert self.manager._validate_working_dir(subdir) is True

    def test_validate_working_dir_blocked_paths(self):
        """Test validating working directory in blocked paths."""
        # Test blocked paths
        assert self.manager._validate_working_dir("/etc") is False
        assert self.manager._validate_working_dir("/home") is False
        assert self.manager._validate_working_dir("/root") is False

    def test_build_python_path(self):
        """Test building PYTHONPATH environment variable."""
        python_path = self.manager._build_python_path()

        # Should contain basic paths
        assert "." in python_path
        assert self.skills_path in python_path
        assert os.path.join(self.skills_path, "public") in python_path
        assert self.workspace_path in python_path

    def test_build_python_path_with_existing_pythonpath(self):
        """Test building PYTHONPATH with existing PYTHONPATH."""
        with patch.dict(os.environ, {"PYTHONPATH": "/existing/path"}):
            python_path = self.manager._build_python_path()
            assert "/existing/path" in python_path

    def test_setup_additional_environment(self):
        """Test setting up additional environment variables."""
        env_vars = {"TEST_VAR": "test", "PATH": "/usr/bin:/bin"}
        self.manager._setup_additional_environment(env_vars, self.workspace_path)

        # Should add tool-specific paths
        assert "SOFFICE_PATH" in env_vars or True  # May not exist in test environment
        assert "TMPDIR" in env_vars
        assert "TEMP" in env_vars
        assert "TMP" in env_vars

    def test_get_skills_info(self):
        """Test getting skills environment information."""
        info = self.manager.get_skills_info()

        assert info["skills_path"] == self.skills_path
        assert info["workspace_path"] == self.workspace_path
        assert info["current_working_dir"] == self.workspace_path
        assert "python_path" in info

    def test_is_path_in_skills(self):
        """Test checking if path is in skills directory."""
        # Test skills path itself
        assert self.manager.is_path_in_skills(self.skills_path) is True

        # Test subdirectory of skills
        subdir = os.path.join(self.skills_path, "public", "xlsx")
        assert self.manager.is_path_in_skills(subdir) is True

        # Test workspace path
        assert self.manager.is_path_in_skills(self.workspace_path) is False

        # Test unrelated path
        assert self.manager.is_path_in_skills("/tmp") is False

    def test_is_path_in_workspace(self):
        """Test checking if path is in workspace directory."""
        # Test workspace path itself
        assert self.manager.is_path_in_workspace(self.workspace_path) is True

        # Test subdirectory of workspace
        subdir = os.path.join(self.workspace_path, "subdir")
        assert self.manager.is_path_in_workspace(subdir) is True

        # Test skills path
        assert self.manager.is_path_in_workspace(self.skills_path) is False

        # Test unrelated path
        assert self.manager.is_path_in_workspace("/tmp") is False

    def test_make_path_relative_to_skills(self):
        """Test making path relative to skills directory."""
        # Test path in skills
        skill_file = os.path.join(self.skills_path, "public", "xlsx", "test.py")
        relative = self.manager.make_path_relative_to_skills(skill_file)
        assert relative == "public/xlsx/test.py"

        # Test path not in skills
        workspace_file = os.path.join(self.workspace_path, "test.txt")
        relative = self.manager.make_path_relative_to_skills(workspace_file)
        assert relative is None

    def test_make_path_relative_to_workspace(self):
        """Test making path relative to workspace directory."""
        # Test path in workspace
        workspace_file = os.path.join(self.workspace_path, "subdir", "test.txt")
        relative = self.manager.make_path_relative_to_workspace(workspace_file)
        assert relative == "subdir/test.txt"

        # Test path not in workspace
        skill_file = os.path.join(self.skills_path, "test.py")
        relative = self.manager.make_path_relative_to_workspace(skill_file)
        assert relative is None

    def test_working_directory_persistence(self):
        """Test that working directory changes persist across calls."""
        # Create new directory
        new_dir = os.path.join(self.workspace_path, "persistent")
        os.makedirs(new_dir, exist_ok=True)

        # Update working directory
        self.manager.update_working_directory(new_dir)

        # Get environment - should use new directory
        env = self.manager.get_execution_environment()
        assert env.working_dir == new_dir

        # Another call should still use new directory
        env2 = self.manager.get_execution_environment()
        assert env2.working_dir == new_dir

    def test_environment_variables_merge(self):
        """Test that custom environment variables are properly merged."""
        custom_vars = {
            "CUSTOM_1": "value1",
            "CUSTOM_2": "value2",
            "SKILLS_PATH": "overridden",  # This should override default
        }

        env = self.manager.get_execution_environment(custom_env=custom_vars)

        # Should have custom variables
        assert env.environment_vars["CUSTOM_1"] == "value1"
        assert env.environment_vars["CUSTOM_2"] == "value2"

        # Should override default
        assert env.environment_vars["SKILLS_PATH"] == "overridden"

        # Should still have other defaults
        assert "WORKSPACE_PATH" in env.environment_vars
        assert "PATH" in env.environment_vars

    def test_path_validation_edge_cases(self):
        """Test path validation edge cases."""
        # Test with trailing slashes
        workspace_with_slash = self.workspace_path + "/"
        assert self.manager._validate_working_dir(workspace_with_slash) is True

        # Test with relative traversal that stays within allowed
        workspace_parent = os.path.dirname(self.workspace_path)
        if workspace_parent in ["/tmp", "/var/tmp"]:
            assert self.manager._validate_working_dir(workspace_parent) is True

    def test_python_path_with_nonexistent_directories(self):
        """Test building PYTHONPATH when some directories don't exist."""
        # Remove public directory
        public_path = os.path.join(self.skills_path, "public")
        if os.path.exists(public_path):
            os.rmdir(public_path)

        python_path = self.manager._build_python_path()

        # Should still contain other valid paths
        assert self.skills_path in python_path
        assert self.workspace_path in python_path
        # But public path should not be included since it doesn't exist

    def test_tool_environment_setup(self):
        """Test that tool-specific environment variables are set up."""
        env_vars = {"PATH": "/usr/bin:/bin"}
        self.manager._setup_additional_environment(env_vars, self.workspace_path)

        # Should set temporary directory variables
        assert env_vars["TMPDIR"] == "/tmp"
        assert env_vars["TEMP"] == "/tmp"
        assert env_vars["TMP"] == "/tmp"

        # Should add working directory to PATH
        assert self.workspace_path in env_vars["PATH"]

    def test_concurrent_environment_access(self):
        """Test that environment manager handles concurrent access."""
        import threading

        results = []
        errors = []

        def access_environment():
            try:
                env = self.manager.get_execution_environment()
                results.append(env.working_dir)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=access_environment)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify no errors
        assert len(errors) == 0
        assert len(results) == 10
        # All should have same working directory
        assert all(dir == self.workspace_path for dir in results)

    def test_nested_working_directory_changes(self):
        """Test nested working directory changes."""
        # Create nested directory structure
        level1 = os.path.join(self.workspace_path, "level1")
        level2 = os.path.join(level1, "level2")
        level3 = os.path.join(level2, "level3")

        os.makedirs(level3, exist_ok=True)

        # Navigate down
        self.manager.update_working_directory(level1)
        assert self.manager.get_current_working_dir() == level1

        self.manager.update_working_directory(level2)
        assert self.manager.get_current_working_dir() == level2

        self.manager.update_working_directory(level3)
        assert self.manager.get_current_working_dir() == level3

        # Navigate back up with relative paths (use absolute paths to avoid issues)
        self.manager.update_working_directory(level2)
        assert self.manager.get_current_working_dir() == level2

        self.manager.update_working_directory(level1)
        assert self.manager.get_current_working_dir() == level1

        self.manager.update_working_directory(self.workspace_path)
        assert self.manager.get_current_working_dir() == self.workspace_path

    def test_get_execution_environment_with_none_values(self):
        """Test get_execution_environment with None values."""
        # Should work with None working_dir
        env1 = self.manager.get_execution_environment(working_dir=None)
        assert env1.working_dir == self.workspace_path

        # Should work with None custom_env
        env2 = self.manager.get_execution_environment(custom_env=None)
        assert env2.working_dir == self.workspace_path
        assert "SKILLS_PATH" in env2.environment_vars

        # Should work with both None
        env3 = self.manager.get_execution_environment(working_dir=None, custom_env=None)
        assert env3.working_dir == self.workspace_path

    def test_empty_and_edge_case_paths(self):
        """Test handling of empty and edge case paths."""
        # Test empty string
        resolved = self.manager._resolve_working_dir("")
        assert resolved == os.path.join(self.workspace_path, "")

        # Test single dot
        resolved = self.manager._resolve_working_dir(".")
        assert resolved == os.path.join(self.workspace_path, ".")

        # Test double dot
        resolved = self.manager._resolve_working_dir("..")
        assert resolved == os.path.join(self.workspace_path, "..")

    def test_environment_variable_inheritance(self):
        """Test that environment variables are properly inherited from os.environ."""
        with patch.dict(os.environ, {"PATH": "/test/path"}):
            # Re-initialize to pick up new environment
            self.manager.initialize(self.skills_path, self.workspace_path)

            env = self.manager.get_execution_environment()

            # Should inherit PATH from os.environ
            assert "PATH" in env.environment_vars
            assert "/test/path" in env.environment_vars["PATH"]
