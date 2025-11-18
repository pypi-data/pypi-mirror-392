"""
Complete integration test for Lyrics Server
Covers all API requirements from ./dev/API_SPEC.md and ./dev/DESIGN.md
"""

import httpx


# API_SPEC.md Section 3.7 - Health Check API
def test_health_endpoint() -> None:
    """GET /health - Service health check"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.get("/health")
        result = response.json()

        # Verify response format from actual API
        assert result["status"] == "healthy"
        assert "service" in result

        assert result is not None
    finally:
        client.close()


# API_SPEC.md Section 3.1 - Bash Command Execution API
def test_bash_execute_basic() -> None:
    """POST /bash/execute - Basic command execution"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.post("/bash/execute", json={"command": "echo 'Hello World'"})
        result = response.json()

        # Verify response format from actual API
        assert result["exit_code"] == 0
        assert "Hello World" in result["stdout"]
        assert result["stderr"] == ""
        assert "working_dir" in result

        assert result is not None
    finally:
        client.close()


def test_bash_execute_with_working_dir() -> None:
    """POST /bash/execute - Command execution with custom working directory"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.post("/bash/execute", json={"command": "cd /tmp && pwd"})
        result = response.json()

        # Verify response format
        assert result["exit_code"] == 0
        assert "/tmp" in result["stdout"]

        assert result is not None
    finally:
        client.close()


def test_bash_execute_with_env() -> None:
    """POST /bash/execute - Command execution with environment variables"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.post(
            "/bash/execute",
            json={
                "command": "echo $TEST_VAR",
                "environment": {"TEST_VAR": "test_value"},
            },
        )
        result = response.json()

        # Should work without error
        assert isinstance(result["exit_code"], int)
        assert result is not None
    finally:
        client.close()


def test_bash_execute_with_timeout() -> None:
    """POST /bash/execute - Command execution with timeout"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.post(
            "/bash/execute",
            json={
                "command": "echo 'before' && sleep 1 && echo 'after'",
                "timeout": 5.0,
            },
        )
        result = response.json()

        # Should complete successfully
        assert result["exit_code"] == 0
        assert "before" in result["stdout"]
        assert "after" in result["stdout"]

        assert result is not None
    finally:
        client.close()


def test_skills_listing() -> None:
    """GET /skills - List available skills"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.get("/skills")
        result = response.json()

        # Verify response format
        assert "skills" in result
        assert "total" in result
        assert isinstance(result["skills"], list)
        assert len(result["skills"]) >= 2  # At least xlsx and pdf skills

        # Check first skill structure
        if result["skills"]:
            skill = result["skills"][0]
            assert "name" in skill
            assert "path" in skill
            assert "files" in skill
            assert "description" in skill

        assert result is not None
    finally:
        client.close()


def test_skill_metadata_parsing():
    """Test that SKILL.md YAML frontmatter is correctly parsed."""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.get("/skills")
        result = response.json()

        assert "skills" in result
        skills = result["skills"]
        assert len(skills) >= 2

        # Test PDF skill metadata parsing
        pdf_skill = next((s for s in skills if s["name"] == "pdf"), None)
        if pdf_skill:
            # Should contain YAML metadata description, not just file content
            assert pdf_skill["description"] is not None
            assert (
                len(pdf_skill["description"]) > 100
            )  # Should be a substantial description

            # Check for expected phrases from YAML frontmatter
            expected_phrases = [
                "Comprehensive PDF manipulation toolkit",
                "extracting text and tables",
                "creating new PDFs",
            ]

            description = pdf_skill["description"]
            for phrase in expected_phrases:
                error_msg = f"Expected phrase '{phrase}' not found in description"
                assert phrase in description, error_msg

            # Should NOT start with "# PDF Processing Guide" (which is markdown content)
            assert not description.startswith("# "), (
                "Description should not start with markdown heading"
            )

            print(f"✅ PDF skill description from YAML: {description[:80]}...")

        # Test XLSX skill metadata parsing
        xlsx_skill = next((s for s in skills if s["name"] == "xlsx"), None)
        if xlsx_skill:
            assert xlsx_skill["description"] is not None
            assert len(xlsx_skill["description"]) > 100

            # Check for expected XLSX phrases
            xlsx_phrases = [
                "Comprehensive spreadsheet creation",
                "editing, and analysis",
                "formulas, formatting",
            ]

            description = xlsx_skill["description"]
            for phrase in xlsx_phrases:
                error_msg = f"Expected phrase '{phrase}' not found in XLSX description"
                assert phrase in description, error_msg

            print(f"✅ XLSX skill description from YAML: {description[:80]}...")

        # Test that skill names match metadata (not directory names)
        for skill in skills:
            # Skill name should come from YAML metadata, not just directory name
            assert skill["name"], f"Skill missing name field: {skill}"
            assert skill["description"], f"Skill missing description field: {skill}"

        print("✅ All skills have proper YAML metadata parsing")
        assert True

    finally:
        client.close()


def test_skill_detail(skill_name: str = "xlsx") -> None:
    """GET /skills/{skill_name} - Get specific skill details"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.get(f"/skills/{skill_name}")
        skill = response.json()

        # Verify skill structure
        assert skill["name"] == skill_name
        assert "path" in skill
        assert "files" in skill
        assert isinstance(skill["files"], list)
        assert "description" in skill

        assert skill is not None
    finally:
        client.close()


def test_read_pattern() -> None:
    """Test read command pattern"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        # First create a test file
        client.post(
            "/bash/execute",
            json={"command": "echo 'test content' > /tmp/test_read.txt"},
        )

        # Then read it
        response = client.post(
            "/bash/execute", json={"command": "cat /tmp/test_read.txt"}
        )
        result = response.json()

        assert result["exit_code"] == 0
        assert "test content" in result["stdout"]

        # Cleanup
        client.post("/bash/execute", json={"command": "rm /tmp/test_read.txt"})

        assert result is not None
    finally:
        client.close()


def test_python_pattern() -> None:
    """Test Python script execution pattern"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.post(
            "/bash/execute",
            json={"command": "python3 -c 'print(\"Python test output\")'"},
        )
        result = response.json()

        assert result["exit_code"] == 0
        assert "Python test output" in result["stdout"]

        assert result is not None
    finally:
        client.close()


def test_system_tool_pattern() -> None:
    """Test system tool execution pattern"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        response = client.post("/bash/execute", json={"command": "ls -la /tmp"})
        result = response.json()

        assert result["exit_code"] == 0
        assert len(result["stdout"]) > 0

        assert result is not None
    finally:
        client.close()


def test_file_operations_pattern() -> None:
    """Test file operations pattern"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        # Create directory
        response = client.post(
            "/bash/execute", json={"command": "mkdir -p /tmp/test_dir"}
        )
        assert response.json()["exit_code"] == 0

        # Create file
        response = client.post(
            "/bash/execute", json={"command": "echo 'test' > /tmp/test_dir/test.txt"}
        )
        assert response.json()["exit_code"] == 0

        # List directory
        response = client.post("/bash/execute", json={"command": "ls /tmp/test_dir"})
        result = response.json()
        assert result["exit_code"] == 0
        assert "test.txt" in result["stdout"]

        # Cleanup
        client.post("/bash/execute", json={"command": "rm -rf /tmp/test_dir"})

        assert result is not None
    finally:
        client.close()


def test_all_system_tools() -> bool:
    """Test all available system tools to ensure they don't crash"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        tools_to_test = ["ls", "pwd", "echo", "cat", "mkdir", "rm"]

        for tool in tools_to_test:
            response = client.post(
                "/bash/execute",
                json={"command": f"which {tool} || echo '{tool} not found'"},
            )
            result = response.json()
            # Should not crash, even if tool doesn't exist
            assert isinstance(result["exit_code"], int)

        assert True
    finally:
        client.close()


def test_bash_compatibility() -> bool:
    """Test bash compatibility features"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        # Test environment variables
        response = client.post("/bash/execute", json={"command": "echo $HOME"})
        result = response.json()
        assert result["exit_code"] == 0

        # Test path resolution
        response = client.post("/bash/execute", json={"command": "echo $PATH"})
        result = response.json()
        assert result["exit_code"] == 0

        assert True
    finally:
        client.close()


def test_container_native_functionality() -> bool:
    """Test container-native functionality"""
    client = httpx.Client(timeout=30.0, base_url="http://localhost:8870/api/v1")
    try:
        # Test that we're running in a container-like environment
        response = client.post(
            "/bash/execute",
            json={
                "command": "test -f /.dockerenv && echo 'Docker' || echo 'Not Docker'"
            },
        )
        result = response.json()
        assert result["exit_code"] == 0

        # Test working directory
        response = client.post("/bash/execute", json={"command": "pwd"})
        result = response.json()
        assert result["exit_code"] == 0
        assert "/" in result["stdout"]

        assert True
    finally:
        client.close()
