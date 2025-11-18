"""
Unit tests for ShellSessionManager.

Tests cover initialization, command execution, state persistence,
error handling, and edge cases.
"""

import os
import tempfile
import time

import pytest

from lyrics.bash.session_manager import ShellSessionManager
from lyrics.bash.types import ExecutionResult

# 添加全局超时，防止测试卡死
pytestmark = pytest.mark.timeout(5)  # 每个测试最多5秒


class TestShellSessionManagerInitialization:
    """Test shell session initialization."""

    def test_init_default_shell(self):
        """Test initialization with default shell path."""
        manager = ShellSessionManager()
        assert manager.shell_path == "/bin/bash"
        assert manager.process is None
        assert not manager._initialized

    def test_init_custom_shell(self):
        """Test initialization with custom shell path."""
        manager = ShellSessionManager(shell_path="/bin/sh")
        assert manager.shell_path == "/bin/sh"

    def test_initialize_success(self):
        """Test successful initialization."""
        manager = ShellSessionManager()
        try:
            result = manager.initialize()
            assert result is True
            assert manager._initialized
            assert manager.process is not None
            # Fix: pexpect.spawn uses isalive() instead of poll()
            assert manager.process.isalive()
        finally:
            manager.cleanup()

    def test_initialize_with_custom_directory(self):
        """Test initialization with custom working directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ShellSessionManager()
            try:
                result = manager.initialize(initial_working_dir=tmpdir)
                assert result is True

                # Verify we're in the correct directory
                pwd_result = manager.execute_command("pwd", timeout=2.0)
                assert pwd_result.exit_code == 0
                assert tmpdir in pwd_result.stdout
            finally:
                manager.cleanup()

    def test_initialize_creates_directory_if_not_exists(self):
        """Test that initialize creates the working directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "new_workspace")
            manager = ShellSessionManager()
            try:
                result = manager.initialize(initial_working_dir=new_dir)
                assert result is True
                assert os.path.exists(new_dir)
            finally:
                manager.cleanup()

    def test_initialize_with_invalid_shell(self):
        """Test initialization with non-existent shell."""
        manager = ShellSessionManager(shell_path="/nonexistent/shell")
        try:
            result = manager.initialize()
            assert result is False
            assert not manager._initialized
        finally:
            # 确保清理
            manager.cleanup()


class TestBasicCommandExecution:
    """Test basic command execution functionality."""

    @pytest.fixture
    def manager(self):
        """Fixture to provide initialized manager."""
        mgr = ShellSessionManager()
        success = mgr.initialize()
        if not success:
            pytest.skip("Failed to initialize manager")
        yield mgr
        mgr.cleanup()
        # 给清理一点时间
        time.sleep(0.1)

    def test_simple_command_success(self, manager):
        """Test executing a simple successful command."""
        result = manager.execute_command("echo hello", timeout=2.0)
        assert isinstance(result, ExecutionResult)
        assert result.exit_code == 0
        assert "hello" in result.stdout

    def test_simple_command_failure(self, manager):
        """Test executing a command that fails."""
        result = manager.execute_command(
            "ls /nonexistent_directory_12345_xyz", timeout=2.0
        )
        assert result.exit_code != 0
        # Fix: stderr contains the error message now
        assert len(result.stderr) > 0 or "No such file" in result.stdout

    def test_command_with_exit_code(self, manager):
        """Test that exit codes are correctly captured."""
        result = manager.execute_command("bash -c 'exit 42'", timeout=2.0)
        assert result.exit_code == 42

    def test_multiline_output(self, manager):
        """Test command with multiple lines of output."""
        result = manager.execute_command(
            "printf 'line1\\nline2\\nline3\\n'", timeout=2.0
        )
        assert result.exit_code == 0
        assert "line1" in result.stdout
        assert "line2" in result.stdout
        assert "line3" in result.stdout

    def test_empty_command(self, manager):
        """Test executing empty command."""
        result = manager.execute_command("", timeout=2.0)
        assert result.exit_code == 0

    def test_command_with_stderr(self, manager):
        """Test command that produces stderr output."""
        result = manager.execute_command("echo 'error message' >&2", timeout=2.0)
        assert result.exit_code == 0
        # Fix: With exec 2>&1, stderr is merged into stdout
        assert "error message" in result.stdout or "error message" in result.stderr


class TestStatePersistence:
    """Test that shell state persists across commands."""

    @pytest.fixture
    def manager(self):
        """Fixture to provide initialized manager."""
        mgr = ShellSessionManager()
        success = mgr.initialize()
        if not success:
            pytest.skip("Failed to initialize manager")
        yield mgr
        mgr.cleanup()
        time.sleep(0.1)

    def test_working_directory_persistence(self, manager):
        """Test that working directory changes persist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result1 = manager.execute_command(f"cd {tmpdir}", timeout=2.0)
            assert result1.exit_code == 0

            result2 = manager.execute_command("pwd", timeout=2.0)
            assert result2.exit_code == 0
            assert os.path.realpath(tmpdir) in os.path.realpath(result2.stdout)

    def test_environment_variable_persistence(self, manager):
        """Test that environment variables persist."""
        result1 = manager.execute_command("export TEST_VAR=hello_world", timeout=2.0)
        assert result1.exit_code == 0

        result2 = manager.execute_command("echo $TEST_VAR", timeout=2.0)
        assert result2.exit_code == 0
        assert "hello_world" in result2.stdout

    def test_multiple_environment_variables(self, manager):
        """Test multiple environment variables."""
        manager.execute_command("export VAR1=value1", timeout=2.0)
        manager.execute_command("export VAR2=value2", timeout=2.0)
        manager.execute_command("export VAR3=value3", timeout=2.0)

        result = manager.execute_command("echo $VAR1 $VAR2 $VAR3", timeout=2.0)
        assert "value1" in result.stdout
        assert "value2" in result.stdout
        assert "value3" in result.stdout

    def test_shell_function_persistence(self, manager):
        """Test that shell functions persist."""
        result1 = manager.execute_command(
            "myfunc() { echo 'function works'; }", timeout=2.0
        )
        assert result1.exit_code == 0

        result2 = manager.execute_command("myfunc", timeout=2.0)
        assert result2.exit_code == 0
        assert "function works" in result2.stdout

    def test_file_creation_persistence(self, manager):
        """Test that file operations persist."""
        result1 = manager.execute_command("echo 'test content' > test.txt", timeout=2.0)
        assert result1.exit_code == 0

        result2 = manager.execute_command("cat test.txt", timeout=2.0)
        assert result2.exit_code == 0
        assert "test content" in result2.stdout


class TestGetCurrentWorkingDir:
    """Test getting current working directory."""

    @pytest.fixture
    def manager(self):
        """Fixture to provide initialized manager."""
        mgr = ShellSessionManager()
        success = mgr.initialize()
        if not success:
            pytest.skip("Failed to initialize manager")
        yield mgr
        mgr.cleanup()
        time.sleep(0.1)

    def test_get_initial_working_dir(self, manager):
        """Test getting initial working directory."""
        cwd = manager.get_current_working_dir()
        assert os.path.exists(cwd)

    def test_get_working_dir_after_cd(self, manager):
        """Test getting working directory after changing it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager.execute_command(f"cd {tmpdir}", timeout=2.0)
            cwd = manager.get_current_working_dir()
            assert os.path.realpath(tmpdir) == os.path.realpath(cwd)

    def test_get_working_dir_uninitialized(self):
        """Test getting working directory from uninitialized manager."""
        manager = ShellSessionManager()
        cwd = manager.get_current_working_dir()
        assert os.path.exists(cwd)


class TestCommandTimeout:
    """Test command timeout functionality."""

    @pytest.fixture
    def manager(self):
        """Fixture to provide initialized manager."""
        mgr = ShellSessionManager()
        success = mgr.initialize()
        if not success:
            pytest.skip("Failed to initialize manager")
        yield mgr
        mgr.cleanup()
        time.sleep(0.1)

    def test_command_timeout(self, manager):
        """Test that long-running commands timeout."""
        start_time = time.time()
        result = manager.execute_command("sleep 10", timeout=0.5)
        elapsed = time.time() - start_time

        assert elapsed < 2.0
        assert result.exit_code == 124
        # Fix: check for "timed out" not just "timeout"
        assert "timed out" in result.stderr.lower()

    def test_fast_command_no_timeout(self, manager):
        """Test that fast commands don't timeout."""
        result = manager.execute_command("echo hello", timeout=2.0)
        assert result.exit_code == 0


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_execute_without_initialization(self):
        """Test executing command without initialization."""
        manager = ShellSessionManager()
        result = manager.execute_command("echo hello", timeout=2.0)
        assert result.exit_code == 1
        assert "not initialized" in result.stderr.lower()

    def test_execute_after_cleanup(self):
        """Test executing command after cleanup."""
        manager = ShellSessionManager()
        manager.initialize()
        manager.cleanup()
        time.sleep(0.1)

        result = manager.execute_command("echo hello", timeout=2.0)
        assert result.exit_code == 1
        assert "not initialized" in result.stderr.lower()


class TestCleanup:
    """Test cleanup functionality."""

    def test_cleanup_running_process(self):
        """Test cleanup with running process."""
        manager = ShellSessionManager()
        manager.initialize()

        result = manager.execute_command("echo test", timeout=2.0)
        assert result.exit_code == 0

        assert manager.is_alive()
        manager.cleanup()
        time.sleep(0.1)

        assert not manager._initialized

    def test_cleanup_already_cleaned(self):
        """Test cleanup when already cleaned."""
        manager = ShellSessionManager()
        manager.initialize()
        manager.cleanup()
        time.sleep(0.1)

        # Should not raise error
        manager.cleanup()

    def test_cleanup_never_initialized(self):
        """Test cleanup without initialization."""
        manager = ShellSessionManager()
        # Should not raise error
        manager.cleanup()


class TestIsAlive:
    """Test is_alive functionality."""

    def test_is_alive_after_init(self):
        """Test is_alive returns True after initialization."""
        manager = ShellSessionManager()
        manager.initialize()
        try:
            assert manager.is_alive()
        finally:
            manager.cleanup()
            time.sleep(0.1)

    def test_is_alive_before_init(self):
        """Test is_alive returns False before initialization."""
        manager = ShellSessionManager()
        assert not manager.is_alive()

    def test_is_alive_after_cleanup(self):
        """Test is_alive returns False after cleanup."""
        manager = ShellSessionManager()
        manager.initialize()
        manager.cleanup()
        time.sleep(0.1)
        assert not manager.is_alive()


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.fixture
    def manager(self):
        """Fixture to provide initialized manager."""
        mgr = ShellSessionManager()
        success = mgr.initialize()
        if not success:
            pytest.skip("Failed to initialize manager")
        yield mgr
        mgr.cleanup()
        time.sleep(0.1)

    def test_very_long_output(self, manager):
        """Test command with very long output."""
        result = manager.execute_command("seq 1 100", timeout=2.0)
        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 100

    def test_command_with_pipes(self, manager):
        """Test command with pipes."""
        result = manager.execute_command("echo 'hello world' | grep hello", timeout=2.0)
        assert result.exit_code == 0
        assert "hello" in result.stdout

    def test_unicode_output(self, manager):
        """Test command with Unicode output."""
        result = manager.execute_command("echo '你好世界'", timeout=2.0)
        assert result.exit_code == 0


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    @pytest.fixture
    def manager(self):
        """Fixture to provide initialized manager."""
        mgr = ShellSessionManager()
        success = mgr.initialize()
        if not success:
            pytest.skip("Failed to initialize manager")
        yield mgr
        mgr.cleanup()
        time.sleep(0.1)

    def test_python_script_execution(self, manager):
        """Test executing a Python script."""
        script_content = "print('Hello from Python')"
        manager.execute_command(f'echo "{script_content}" > script.py', timeout=2.0)

        result = manager.execute_command("python3 script.py", timeout=2.0)
        assert result.exit_code == 0
        assert "Hello from Python" in result.stdout

    def test_file_operations(self, manager):
        """Test various file operations."""
        manager.execute_command("mkdir -p a/b/c", timeout=2.0)
        manager.execute_command("touch a/file1.txt", timeout=2.0)
        manager.execute_command("touch a/b/file2.txt", timeout=2.0)

        result = manager.execute_command("find . -name '*.txt'", timeout=2.0)
        assert result.exit_code == 0
        assert "file1.txt" in result.stdout
        assert "file2.txt" in result.stdout
