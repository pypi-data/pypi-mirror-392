"""
Unit tests for the Lyrics Server API endpoints.
"""

import os
import tempfile
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

# Import the server components
try:
    from lyrics.server import (
        BashExecuteRequest,
        BashExecuteResponse,
        LyricsService,
        SkillInfo,
        SkillsListResponse,
        app,
    )
except ImportError:
    # Skip if server module is not available
    app = None
    LyricsService = None
    BashExecuteRequest = None
    BashExecuteResponse = None
    SkillInfo = None
    SkillsListResponse = None
from lyrics.bash.types import ExecutionEnvironment, ExecutionResult

# Skip tests if server components are not available
if app is None:
    pytest.skip("Server module not available", allow_module_level=True)


class TestLyricsService:
    """Test cases for LyricsService class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock components
        self.mock_command_parser = Mock()
        self.mock_command_executor = Mock()

        # Create service
        self.service = LyricsService(
            self.mock_command_parser, self.mock_command_executor
        )

        # Create temp directories
        self.temp_dir = tempfile.mkdtemp()
        self.skills_path = os.path.join(self.temp_dir, "skills")
        self.workspace_path = os.path.join(self.temp_dir, "workspace")

        # Create directory structure
        os.makedirs(os.path.join(self.skills_path, "public", "xlsx"), exist_ok=True)
        os.makedirs(self.workspace_path, exist_ok=True)

        # Create mock environment components
        self.mock_env_manager = Mock()
        self.mock_path_resolver = Mock()
        self.mock_path_validator = Mock()

        # Initialize service
        self.service.initialize(
            self.skills_path,
            self.workspace_path,
            self.mock_env_manager,
            self.mock_path_resolver,
            self.mock_path_validator,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.service.shutdown()

    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Test successful command execution."""
        # Set up mocks
        mock_parsed_command = Mock()
        self.mock_command_parser.parse.return_value = mock_parsed_command

        mock_execution_result = ExecutionResult(
            stdout="command output", stderr="", exit_code=0
        )
        self.mock_command_executor.execute.return_value = mock_execution_result

        mock_env = ExecutionEnvironment(
            working_dir=self.workspace_path,
            environment_vars={},
            skills_path=self.skills_path,
            workspace_path=self.workspace_path,
        )
        self.mock_env_manager.get_execution_environment.return_value = mock_env

        # Execute command
        result = await self.service.execute_command("ls -la", "/workspace")

        # Verify
        assert result["stdout"] == "command output"
        assert result["stderr"] == ""
        assert result["exit_code"] == 0
        assert result["working_dir"] == self.workspace_path

        self.mock_command_parser.parse.assert_called_once_with("ls -la")
        self.mock_command_executor.execute.assert_called_once_with(
            mock_parsed_command,
            mock_env,
            self.mock_path_resolver,
            self.mock_path_validator,
        )

    @pytest.mark.asyncio
    async def test_execute_command_with_error(self):
        """Test command execution with error."""
        # Set up mocks
        mock_parsed_command = Mock()
        self.mock_command_parser.parse.return_value = mock_parsed_command

        mock_execution_result = ExecutionResult(
            stdout="", stderr="error message", exit_code=1
        )
        self.mock_command_executor.execute.return_value = mock_execution_result

        mock_env = ExecutionEnvironment(
            working_dir=self.workspace_path,
            environment_vars={},
            skills_path=self.skills_path,
            workspace_path=self.workspace_path,
        )
        self.mock_env_manager.get_execution_environment.return_value = mock_env

        # Execute command
        result = await self.service.execute_command("invalid_command", "/workspace")

        # Verify
        assert result["stdout"] == ""
        assert result["stderr"] == "error message"
        assert result["exit_code"] == 1
        assert result["working_dir"] == self.workspace_path

    @pytest.mark.asyncio
    async def test_execute_command_with_custom_env(self):
        """Test command execution with custom environment variables."""
        # Set up mocks
        mock_parsed_command = Mock()
        self.mock_command_parser.parse.return_value = mock_parsed_command

        mock_execution_result = ExecutionResult(stdout="output", stderr="", exit_code=0)
        self.mock_command_executor.execute.return_value = mock_execution_result

        custom_env = {"CUSTOM_VAR": "custom_value"}
        mock_env = ExecutionEnvironment(
            working_dir=self.workspace_path,
            environment_vars=custom_env,
            skills_path=self.skills_path,
            workspace_path=self.workspace_path,
        )
        self.mock_env_manager.get_execution_environment.return_value = mock_env

        # Execute command
        result = await self.service.execute_command(
            "echo $CUSTOM_VAR", "/workspace", custom_env
        )

        # Verify
        assert result["stdout"] == "output"
        assert result["exit_code"] == 0

        self.mock_env_manager.get_execution_environment.assert_called_once_with(
            "/workspace", custom_env
        )

    @pytest.mark.asyncio
    async def test_list_skills_success(self):
        """Test successful skills listing."""
        # Create test skills
        xlsx_path = os.path.join(self.skills_path, "public", "xlsx")
        os.makedirs(xlsx_path, exist_ok=True)

        # Create skill description file
        skill_md = os.path.join(xlsx_path, "SKILL.md")
        with open(skill_md, "w") as f:
            f.write("# XLSX Skill\nExcel processing functionality")

        # Create a Python file in the skill
        test_py = os.path.join(xlsx_path, "test.py")
        with open(test_py, "w") as f:
            f.write("print('test')")

        # Execute
        result = await self.service.list_skills()

        # Verify
        assert result["total"] == 1
        assert len(result["skills"]) == 1

        skill = result["skills"][0]
        assert skill["name"] == "xlsx"
        assert "xlsx" in skill["path"]
        assert "Excel processing functionality" in skill["description"]
        assert "test.py" in skill["files"]

    @pytest.mark.asyncio
    async def test_list_skills_empty(self):
        """Test skills listing when no skills exist."""
        # Remove all skills
        public_path = os.path.join(self.skills_path, "public")
        if os.path.exists(public_path):
            import shutil

            shutil.rmtree(public_path)

        # Execute
        result = await self.service.list_skills()

        # Verify
        assert result["total"] == 0
        assert result["skills"] == []

    @pytest.mark.asyncio
    async def test_get_skill_success(self):
        """Test getting specific skill information."""
        # Create test skill
        xlsx_path = os.path.join(self.skills_path, "public", "xlsx")
        os.makedirs(xlsx_path, exist_ok=True)

        # Create skill description file
        skill_md = os.path.join(xlsx_path, "SKILL.md")
        with open(skill_md, "w") as f:
            f.write("# XLSX Skill\nExcel processing functionality")

        # Create Python files in the skill
        test_py = os.path.join(xlsx_path, "test.py")
        with open(test_py, "w") as f:
            f.write("print('test')")

        helper_py = os.path.join(xlsx_path, "helper.py")
        with open(helper_py, "w") as f:
            f.write("def helper(): pass")

        # Execute
        result = await self.service.get_skill("xlsx")

        # Verify
        assert result["name"] == "xlsx"
        assert "xlsx" in result["path"]
        assert "Excel processing functionality" in result["description"]
        assert "test.py" in result["files"]
        assert "helper.py" in result["files"]

    @pytest.mark.asyncio
    async def test_get_skill_not_found(self):
        """Test getting non-existent skill."""
        with pytest.raises(RuntimeError) as exc_info:
            await self.service.get_skill("nonexistent")

        assert "not found" in str(exc_info.value).lower()

    def test_shutdown(self):
        """Test service shutdown."""
        # Create a mock thread pool
        mock_thread_pool = Mock()
        self.service.thread_pool = mock_thread_pool

        # Shutdown
        self.service.shutdown()

        # Verify thread pool was shut down
        mock_thread_pool.shutdown.assert_called_once_with(wait=True)


class TestServerAPI:
    """Test cases for FastAPI server endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temp directories
        self.temp_dir = tempfile.mkdtemp()
        self.skills_path = os.path.join(self.temp_dir, "skills")
        self.workspace_path = os.path.join(self.temp_dir, "workspace")

        # Set environment variables
        os.environ["SKILLS_PATH"] = self.skills_path
        os.environ["WORKSPACE_PATH"] = self.workspace_path

        # Create directory structure
        os.makedirs(os.path.join(self.skills_path, "public", "xlsx"), exist_ok=True)
        os.makedirs(self.workspace_path, exist_ok=True)

        # Create test files
        xlsx_path = os.path.join(self.skills_path, "public", "xlsx")
        skill_md = os.path.join(xlsx_path, "SKILL.md")
        with open(skill_md, "w") as f:
            f.write("# XLSX Skill\nExcel processing functionality")

        test_py = os.path.join(xlsx_path, "test.py")
        with open(test_py, "w") as f:
            f.write("print('test')")

        # Initialize client after environment is set up with API v1 prefix
        self.client = TestClient(app, base_url="http://testserver/api/v1")

        # Manually initialize the service components for testing
        from lyrics.server import (
            env_manager,
            lyrics_service,
            path_resolver,
            path_validator,
        )

        # Initialize core components
        env_manager.initialize(self.skills_path, self.workspace_path)
        path_resolver.initialize(self.skills_path)
        path_validator.initialize(self.skills_path, self.workspace_path)

        # Initialize service
        lyrics_service.initialize(
            self.skills_path,
            self.workspace_path,
            env_manager,
            path_resolver,
            path_validator,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Clean up environment variables
        os.environ.pop("SKILLS_PATH", None)
        os.environ.pop("WORKSPACE_PATH", None)

    def test_root_endpoint(self):
        """Test root endpoint."""
        # Create a separate client without base_url for root endpoint
        root_client = TestClient(app)
        response = root_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Lyrics Server"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
        assert "/api/v1/bash/execute" in data["endpoints"]["execute"]
        assert "/api/v1/skills" in data["endpoints"]["skills"]
        assert "/health" in data["endpoints"]["health"]

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "lyrics"

    def test_execute_bash_success(self):
        """Test successful bash command execution."""
        request_data = {
            "command": "echo 'Hello World'",
            "working_dir": "/workspace",
            "environment": {},
        }

        response = self.client.post("/bash/execute", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "stdout" in data
        assert "stderr" in data
        assert "exit_code" in data
        assert "working_dir" in data

    def test_execute_bash_invalid_request(self):
        """Test bash command execution with invalid request."""
        # Missing required command field
        request_data = {"working_dir": "/workspace"}

        response = self.client.post("/bash/execute", json=request_data)

        # Should return validation error
        assert response.status_code == 422

    def test_list_skills_endpoint(self):
        """Test skills listing endpoint."""
        response = self.client.get("/skills")

        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert "total" in data
        assert isinstance(data["skills"], list)
        assert isinstance(data["total"], int)

        # Should find our test skill
        if data["total"] > 0:
            skill = data["skills"][0]
            assert "name" in skill
            assert "path" in skill
            assert "files" in skill

    def test_get_skill_endpoint_success(self):
        """Test getting specific skill endpoint."""
        response = self.client.get("/skills/xlsx")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "xlsx"
        assert "path" in data
        assert "files" in data
        assert "test.py" in data["files"]

    def test_get_skill_endpoint_not_found(self):
        """Test getting non-existent skill endpoint."""
        response = self.client.get("/skills/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_skill_endpoint_invalid_name(self):
        """Test getting skill with invalid name."""
        response = self.client.get("/skills/../../etc/passwd")

        # Should handle path traversal attempts
        assert response.status_code in [400, 404, 422]


class TestServerModels:
    """Test cases for Pydantic models."""

    def test_bash_execute_request_valid(self):
        """Test valid BashExecuteRequest creation."""
        request = BashExecuteRequest(
            command="ls -la", working_dir="/workspace", environment={"TEST": "value"}
        )

        assert request.command == "ls -la"
        assert request.working_dir == "/workspace"
        assert request.environment == {"TEST": "value"}

    def test_bash_execute_request_defaults(self):
        """Test BashExecuteRequest with default values."""
        request = BashExecuteRequest(command="echo test")

        assert request.command == "echo test"
        assert request.working_dir == "/workspace"
        assert request.environment is None

    def test_bash_execute_response_valid(self):
        """Test valid BashExecuteResponse creation."""
        response = BashExecuteResponse(
            stdout="output", stderr="error", exit_code=0, working_dir="/workspace"
        )

        assert response.stdout == "output"
        assert response.stderr == "error"
        assert response.exit_code == 0
        assert response.working_dir == "/workspace"

    def test_skill_info_valid(self):
        """Test valid SkillInfo creation."""
        skill = SkillInfo(
            name="xlsx",
            path="/skills/public/xlsx",
            description="Excel processing",
            files=["test.py", "helper.py"],
        )

        assert skill.name == "xlsx"
        assert skill.path == "/skills/public/xlsx"
        assert skill.description == "Excel processing"
        assert skill.files == ["test.py", "helper.py"]

    def test_skill_info_optional_fields(self):
        """Test SkillInfo with optional fields."""
        skill = SkillInfo(name="test", path="/skills/public/test", files=["file1.py"])

        assert skill.name == "test"
        assert skill.path == "/skills/public/test"
        assert skill.files == ["file1.py"]
        assert skill.description is None

    def test_skills_list_response_valid(self):
        """Test valid SkillsListResponse creation."""
        skills = [
            SkillInfo(name="xlsx", path="/skills/xlsx", files=["test.py"]),
            SkillInfo(name="pdf", path="/skills/pdf", files=["extract.py"]),
        ]

        response = SkillsListResponse(skills=skills, total=2)

        assert response.skills == skills
        assert response.total == 2
        assert len(response.skills) == 2


class TestServerIntegration:
    """Integration tests for the complete server."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app, base_url="http://testserver/api/v1")

        # Create temp directories
        self.temp_dir = tempfile.mkdtemp()
        self.skills_path = os.path.join(self.temp_dir, "skills")
        self.workspace_path = os.path.join(self.temp_dir, "workspace")

        # Set environment variables
        os.environ["SKILLS_PATH"] = self.skills_path
        os.environ["WORKSPACE_PATH"] = self.workspace_path

        # Create directory structure
        os.makedirs(os.path.join(self.skills_path, "public", "xlsx"), exist_ok=True)
        os.makedirs(os.path.join(self.skills_path, "public", "pdf"), exist_ok=True)
        os.makedirs(self.workspace_path, exist_ok=True)

        # Create test files
        for skill_name in ["xlsx", "pdf"]:
            skill_path = os.path.join(self.skills_path, "public", skill_name)

            # Create skill description
            skill_md = os.path.join(skill_path, "SKILL.md")
            with open(skill_md, "w") as f:
                f.write(
                    f"# {skill_name.upper()} Skill\n"
                    f"{skill_name} processing functionality"
                )

            # Create test script
            test_py = os.path.join(skill_path, "test.py")
            with open(test_py, "w") as f:
                f.write(f"print('{skill_name} test')")

        # Manually initialize the service components for testing
        from lyrics.server import (
            env_manager,
            lyrics_service,
            path_resolver,
            path_validator,
        )

        # Initialize core components
        env_manager.initialize(self.skills_path, self.workspace_path)
        path_resolver.initialize(self.skills_path)
        path_validator.initialize(self.skills_path, self.workspace_path)

        # Initialize service
        lyrics_service.initialize(
            self.skills_path,
            self.workspace_path,
            env_manager,
            path_resolver,
            path_validator,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Clean up environment variables
        os.environ.pop("SKILLS_PATH", None)
        os.environ.pop("WORKSPACE_PATH", None)

    def test_complete_workflow(self):
        """Test complete workflow: list skills, get skill, execute command."""
        # 1. List skills
        response = self.client.get("/skills")
        assert response.status_code == 200
        skills_data = response.json()
        assert skills_data["total"] >= 2
        assert len(skills_data["skills"]) >= 2

        # 2. Get specific skill
        skill_name = skills_data["skills"][0]["name"]
        response = self.client.get(f"/skills/{skill_name}")
        assert response.status_code == 200
        skill_data = response.json()
        assert skill_data["name"] == skill_name
        assert len(skill_data["files"]) > 0

        # 3. Execute a command
        response = self.client.post(
            "/bash/execute",
            json={
                "command": f"echo 'Testing {skill_name} skill'",
                "working_dir": "/workspace",
            },
        )
        assert response.status_code == 200
        exec_data = response.json()
        assert exec_data["exit_code"] == 0
        assert "Testing" in exec_data["stdout"]

    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        import threading

        results = []
        errors = []

        def make_request():
            try:
                response = self.client.post(
                    "/bash/execute",
                    json={
                        "command": "echo 'concurrent test'",
                        "working_dir": "/workspace",
                    },
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0
        assert len(results) == 5
        assert all(status == 200 for status in results)

    def test_error_handling_workflow(self):
        """Test error handling in various scenarios."""
        # Test invalid command
        response = self.client.post(
            "/bash/execute",
            json={
                "command": "",  # Empty command
                "working_dir": "/workspace",
            },
        )
        assert response.status_code == 500  # Empty command should return server error

        # Test non-existent skill
        response = self.client.get("/skills/nonexistent_skill_12345")
        assert response.status_code == 404

        # Test invalid skill name
        response = self.client.get("/skills/invalid@skill#name")
        # Should handle gracefully
        assert response.status_code in [400, 404, 422]

    def test_health_endpoint_during_load(self):
        """Test health endpoint remains responsive during load."""
        # Make multiple requests to stress the system
        for _ in range(10):
            self.client.post(
                "/bash/execute",
                json={"command": "echo 'load test'", "working_dir": "/workspace"},
            )

        # Health should still work
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_async_service_operations():
    """Test async operations in service."""
    # Create service with mocked components
    mock_parser = Mock()
    mock_executor = Mock()
    service = LyricsService(mock_parser, mock_executor)

    # Mock execution result
    mock_result = ExecutionResult(stdout="async output", stderr="", exit_code=0)
    mock_executor.execute.return_value = mock_result

    # Mock other components
    mock_env_manager = Mock()
    mock_path_resolver = Mock()
    mock_path_validator = Mock()

    temp_dir = tempfile.mkdtemp()
    try:
        service.initialize(
            os.path.join(temp_dir, "skills"),
            os.path.join(temp_dir, "workspace"),
            mock_env_manager,
            mock_path_resolver,
            mock_path_validator,
        )

        # Test async execution
        result = await service.execute_command("test command", "/workspace")
        assert result["stdout"] == "async output"

    finally:
        service.shutdown()
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run a simple test
    pytest.main([__file__, "-v"])
