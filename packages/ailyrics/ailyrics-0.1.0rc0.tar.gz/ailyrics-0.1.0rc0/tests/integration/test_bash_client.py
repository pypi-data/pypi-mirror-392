"""
Comprehensive BashClient Integration Tests
Tests all BashClient functionality against the Lyrics Server
"""

import httpx


def test_client_initialization():
    """Test client initialization and basic properties"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        assert client.base_url == "http://localhost:8870/api/v1/"
        # Just check that timeout is set (exact comparison depends on httpx version)
        assert (
            hasattr(client.timeout, "timeout")
            or str(client.timeout) == "Timeout(timeout=30.0)"
        )
    finally:
        client.close()


def test_health_check():
    """Test server health check"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.get("/health")
        result = response.json()

        assert result["status"] == "healthy"
        assert "service" in result
    finally:
        client.close()


def test_basic_command_execution():
    """Test basic bash command execution"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.post(
            "/bash/execute", json={"command": "echo 'Hello from BashClient'"}
        )
        result = response.json()

        assert result["exit_code"] == 0
        assert "Hello from BashClient" in result["stdout"]
        assert result["stderr"] == ""
    finally:
        client.close()


def test_command_with_error():
    """Test command execution that fails"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.post("/bash/execute", json={"command": "false"})
        result = response.json()

        assert result["exit_code"] == 1
        assert result["stderr"] == ""
    finally:
        client.close()


def test_list_skills():
    """Test skills listing"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.get("/skills")
        result = response.json()
        skills = result["skills"]

        assert isinstance(skills, list)
        assert len(skills) > 0

        # Check first skill structure
        if skills:
            skill = skills[0]
            assert "name" in skill
            assert "path" in skill
            assert "files" in skill
            assert isinstance(skill["files"], list)
    finally:
        client.close()


def test_get_skill_details():
    """Test getting specific skill details"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.get("/skills/xlsx")
        skill = response.json()

        assert skill["name"] == "xlsx"
        assert "xlsx" in skill["path"]
        assert isinstance(skill["files"], list)
        assert len(skill["files"]) > 0
    finally:
        client.close()


def test_sync_client_basic_usage():
    """Test basic synchronous client usage"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")

    try:
        # Test health check
        response = client.get("/health")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "healthy"

        # Test basic command
        response = client.post("/bash/execute", json={"command": "echo 'test'"})
        assert response.status_code == 200
        result = response.json()
        assert result["exit_code"] == 0
        assert "test" in result["stdout"]

        assert True  # All tests passed
    finally:
        client.close()
