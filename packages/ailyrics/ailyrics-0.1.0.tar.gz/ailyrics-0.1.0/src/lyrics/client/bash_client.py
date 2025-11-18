"""
Bash Client - Client library for interacting with the Lyrics Server.

This client provides a convenient interface for executing bash commands
on the Lyrics Server, mimicking the behavior of a local bash environment.
"""

import asyncio
import logging
import os
from urllib.parse import urljoin

import httpx

logger = logging.getLogger(__name__)


class BashResult:
    """
    Result of a bash command execution.

    This class provides the same interface as subprocess.CompletedProcess
    to maintain compatibility with existing bash-based workflows.
    """

    def __init__(self, stdout: str, stderr: str, exit_code: int, working_dir: str):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.returncode = exit_code  # Alias for compatibility
        self.working_dir = working_dir

    def __str__(self):
        return (
            f"BashResult(exit_code={self.exit_code}, working_dir='{self.working_dir}')"
        )

    def __repr__(self):
        return self.__str__()

    @property
    def success(self) -> bool:
        """Check if the command succeeded (exit code 0)."""
        return self.exit_code == 0

    @property
    def failed(self) -> bool:
        """Check if the command failed (exit code != 0)."""
        return self.exit_code != 0

    def check_returncode(self):
        """Raise an exception if the command failed."""
        if self.exit_code != 0:
            raise BashExecutionError(
                f"Command failed with exit code {self.exit_code}", result=self
            )


class BashExecutionError(Exception):
    """Exception raised when a bash command fails."""

    def __init__(self, message: str, result: BashResult | None = None):
        super().__init__(message)
        self.result = result
        self.message = message

    def __str__(self):
        if self.result:
            return (
                f"{self.message}\nstdout: {self.result.stdout}\n"
                f"stderr: {self.result.stderr}"
            )
        return self.message


class SkillInfo:
    """Information about an available skill."""

    def __init__(
        self,
        name: str,
        path: str,
        description: str | None = None,
        files: list[str] | None = None,
    ):
        self.name = name
        self.path = path
        self.description = description
        self.files = files or []

    def __str__(self):
        return f"SkillInfo(name='{self.name}', files={len(self.files)})"

    def __repr__(self):
        return self.__str__()


class BashClient:
    """
    Client for interacting with the Lyrics Server.

    This client provides methods to execute bash commands and work with
    Agent Skills in a way that mimics local bash execution.
    """

    def __init__(
        self,
        server_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        working_dir: str = "/workspace",
    ):
        """
        Initialize the BashClient.

        Args:
            server_url: URL of the Lyrics Server (e.g., "http://localhost:8870")
            timeout: Timeout for requests in seconds
            max_retries: Maximum number of retries for failed requests
            working_dir: Default working directory for commands
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.working_dir = working_dir

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

        logger.info(f"BashClient initialized for {server_url}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.debug("BashClient closed")

    async def execute_bash(
        self,
        command: str,
        working_dir: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> BashResult:
        """
        Execute a bash command on the server.

        Args:
            command: Bash command to execute
            working_dir: Working directory for the command (optional)
            environment: Environment variables (optional)

        Returns:
            BashResult with command output and exit code

        Raises:
            BashExecutionError: If there's an error executing the command
            httpx.HTTPError: If there's a network error
        """
        working_dir = working_dir or self.working_dir

        logger.debug(f"Executing command: {command}")
        logger.debug(f"Working directory: {working_dir}")

        url = urljoin(self.server_url, "/api/v1/bash/execute")
        payload = {
            "command": command,
            "working_dir": working_dir,
            "environment": environment or {},
        }

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()

                data = response.json()
                result = BashResult(
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    exit_code=data.get("exit_code", 1),
                    working_dir=data.get("working_dir", working_dir),
                )

                logger.debug(f"Command completed with exit code: {result.exit_code}")
                return result

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 500 and attempt < self.max_retries:
                    logger.warning(
                        f"Server error on attempt {attempt + 1}, retrying..."
                    )
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.error(f"HTTP error executing command: {e}")
                    raise BashExecutionError(f"HTTP error: {e}")

            except httpx.RequestError as e:
                if attempt < self.max_retries:
                    logger.warning(
                        f"Request error on attempt {attempt + 1}, retrying..."
                    )
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.error(f"Request error executing command: {e}")
                    raise BashExecutionError(f"Request error: {e}")

            except Exception as e:
                logger.error(f"Unexpected error executing command: {e}")
                raise BashExecutionError(f"Unexpected error: {e}")

        # This should not be reached, but just in case
        raise BashExecutionError("Max retries exceeded")

    async def read_file(self, file_path: str, working_dir: str | None = None) -> str:
        """
        Read a file using the 'read' command.

        Args:
            file_path: Path to the file to read
            working_dir: Working directory (optional)

        Returns:
            File contents as string

        Raises:
            BashExecutionError: If the file cannot be read
        """
        result = await self.execute_bash(f"read {file_path}", working_dir=working_dir)
        if result.exit_code != 0:
            raise BashExecutionError(
                f"Failed to read file {file_path}: {result.stderr}", result=result
            )
        return result.stdout

    async def execute_python(
        self, script_path: str, *args, working_dir: str | None = None
    ) -> BashResult:
        """
        Execute a Python script with arguments.

        Args:
            script_path: Path to the Python script
            *args: Arguments to pass to the script
            working_dir: Working directory (optional)

        Returns:
            BashResult with script output and exit code
        """
        args_str = " ".join(str(arg) for arg in args)
        command = f"python {script_path} {args_str}".strip()
        return await self.execute_bash(command, working_dir=working_dir)

    async def execute_tool(
        self, tool_name: str, *args, working_dir: str | None = None
    ) -> BashResult:
        """
        Execute a system tool with arguments.

        Args:
            tool_name: Name of the system tool (e.g., 'pdftotext', 'soffice')
            *args: Arguments to pass to the tool
            working_dir: Working directory (optional)

        Returns:
            BashResult with tool output and exit code
        """
        args_str = " ".join(str(arg) for arg in args)
        command = f"{tool_name} {args_str}".strip()
        return await self.execute_bash(command, working_dir=working_dir)

    async def list_skills(self) -> list[SkillInfo]:
        """
        List all available skills.

        Returns:
            List of SkillInfo objects

        Raises:
            BashExecutionError: If there's an error listing skills
        """
        url = urljoin(self.server_url, "/api/v1/skills")

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            skills = []

            for skill_data in data.get("skills", []):
                skill = SkillInfo(
                    name=skill_data["name"],
                    path=skill_data["path"],
                    description=skill_data.get("description"),
                    files=skill_data.get("files", []),
                )
                skills.append(skill)

            return skills

        except httpx.HTTPError as e:
            logger.error(f"HTTP error listing skills: {e}")
            raise BashExecutionError(f"Failed to list skills: {e}")

    async def get_skill(self, skill_name: str) -> SkillInfo:
        """
        Get detailed information about a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            SkillInfo object

        Raises:
            BashExecutionError: If the skill is not found
        """
        url = urljoin(self.server_url, f"/api/v1/skills/{skill_name}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            return SkillInfo(
                name=data["name"],
                path=data["path"],
                description=data.get("description"),
                files=data.get("files", []),
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise BashExecutionError(f"Skill '{skill_name}' not found")
            else:
                logger.error(f"HTTP error getting skill {skill_name}: {e}")
                raise BashExecutionError(f"Failed to get skill {skill_name}: {e}")

    async def health_check(self) -> dict:
        """
        Check the health of the Lyrics Server.

        Returns:
            Dictionary with server health information

        Raises:
            BashExecutionError: If the server is not healthy
        """
        url = urljoin(self.server_url, "/api/v1/health")

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Health check failed: {e}")
            raise BashExecutionError(f"Server health check failed: {e}")

    async def execute_workflow(
        self,
        commands: list[str],
        working_dir: str | None = None,
        stop_on_error: bool = True,
    ) -> list[BashResult]:
        """
        Execute a sequence of bash commands.

        Args:
            commands: List of bash commands to execute
            working_dir: Working directory for all commands (optional)
            stop_on_error: Whether to stop execution on first error

        Returns:
            List of BashResult objects, one for each command

        Raises:
            BashExecutionError: If a command fails and stop_on_error is True
        """
        results = []
        current_dir = working_dir or self.working_dir

        for i, command in enumerate(commands):
            logger.info(f"Executing workflow step {i + 1}/{len(commands)}: {command}")

            result = await self.execute_bash(command, working_dir=current_dir)
            results.append(result)

            # Update working directory for next command
            current_dir = result.working_dir

            # Check for errors
            if result.exit_code != 0 and stop_on_error:
                logger.error(f"Workflow failed at step {i + 1}: {command}")
                raise BashExecutionError(
                    f"Workflow failed at step {i + 1}: {command}\n{result.stderr}",
                    result=result,
                )

        logger.info(f"Workflow completed: {len(commands)} commands executed")
        return results

    def set_working_directory(self, working_dir: str):
        """
        Set the default working directory.

        Args:
            working_dir: New default working directory
        """
        self.working_dir = working_dir
        logger.debug(f"Default working directory set to: {working_dir}")

    async def upload_file(self, local_path: str, remote_path: str) -> BashResult:
        """
        Upload a file to the server workspace.

        Args:
            local_path: Path to the local file
            remote_path: Path where to save the file on the server

        Returns:
            BashResult of the upload operation

        Note:
            This is a convenience method that reads the local file and
            writes it to the server using echo commands.
        """
        try:
            with open(local_path, "rb") as f:
                content = f.read()

            # Convert to base64 to handle binary data safely
            import base64

            encoded_content = base64.b64encode(content).decode("utf-8")

            # Create the remote directory if needed
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                await self.execute_bash(f"mkdir -p {remote_dir}")

            # Write the file in chunks to avoid command line length limits
            chunk_size = 1000  # Safe chunk size
            await self.execute_bash(f"echo -n '' > {remote_path}")  # Create empty file

            for i in range(0, len(encoded_content), chunk_size):
                chunk = encoded_content[i : i + chunk_size]
                await self.execute_bash(f"echo -n '{chunk}' >> {remote_path}")

            # Decode the base64 content back to binary
            return await self.execute_bash(
                f"base64 -d {remote_path} > {remote_path}.decoded && "
                f"mv {remote_path}.decoded {remote_path}"
            )

        except Exception as e:
            return BashResult(
                stdout="",
                stderr=f"Upload error: {e}",
                exit_code=1,
                working_dir=self.working_dir,
            )

    async def download_file(self, remote_path: str, local_path: str) -> bytes:
        """
        Download a file from the server.

        Args:
            remote_path: Path to the file on the server
            local_path: Path where to save the local file

        Returns:
            File contents as bytes

        Raises:
            BashExecutionError: If the file cannot be read
        """
        # Use base64 encoding to safely transfer binary data
        result = await self.execute_bash(f"base64 {remote_path}")

        if result.exit_code != 0:
            raise BashExecutionError(
                f"Failed to download file {remote_path}: {result.stderr}", result=result
            )

        try:
            import base64

            content = base64.b64decode(result.stdout.strip())

            # Save to local file if path provided
            if local_path:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(content)

            return content

        except Exception as e:
            raise BashExecutionError(f"Failed to decode downloaded file: {e}")

    # Convenience methods for common operations

    async def ls(self, path: str = ".", working_dir: str | None = None) -> list[str]:
        """
        List directory contents.

        Args:
            path: Path to list (default: current directory)
            working_dir: Working directory (optional)

        Returns:
            List of directory entries
        """
        result = await self.execute_bash(f"ls {path}", working_dir=working_dir)
        if result.exit_code != 0:
            raise BashExecutionError(
                f"Failed to list directory {path}: {result.stderr}", result=result
            )
        return [line for line in result.stdout.split("\n") if line.strip()]

    async def mkdir(self, path: str, working_dir: str | None = None) -> BashResult:
        """
        Create a directory.

        Args:
            path: Path to create
            working_dir: Working directory (optional)

        Returns:
            BashResult of the operation
        """
        return await self.execute_bash(f"mkdir -p {path}", working_dir=working_dir)

    async def rm(self, path: str, working_dir: str | None = None) -> BashResult:
        """
        Remove a file or directory.

        Args:
            path: Path to remove
            working_dir: Working directory (optional)

        Returns:
            BashResult of the operation
        """
        return await self.execute_bash(f"rm -rf {path}", working_dir=working_dir)

    async def cp(
        self, src: str, dst: str, working_dir: str | None = None
    ) -> BashResult:
        """
        Copy a file or directory.

        Args:
            src: Source path
            dst: Destination path
            working_dir: Working directory (optional)

        Returns:
            BashResult of the operation
        """
        return await self.execute_bash(f"cp -r {src} {dst}", working_dir=working_dir)

    async def mv(
        self, src: str, dst: str, working_dir: str | None = None
    ) -> BashResult:
        """
        Move/rename a file or directory.

        Args:
            src: Source path
            dst: Destination path
            working_dir: Working directory (optional)

        Returns:
            BashResult of the operation
        """
        return await self.execute_bash(f"mv {src} {dst}", working_dir=working_dir)

    async def cat(self, path: str, working_dir: str | None = None) -> str:
        """
        Read file contents.

        Args:
            path: Path to the file
            working_dir: Working directory (optional)

        Returns:
            File contents as string
        """
        result = await self.execute_bash(f"cat {path}", working_dir=working_dir)
        if result.exit_code != 0:
            raise BashExecutionError(
                f"Failed to read file {path}: {result.stderr}", result=result
            )
        return result.stdout

    async def pwd(self, working_dir: str | None = None) -> str:
        """
        Get current working directory.

        Args:
            working_dir: Working directory (optional)

        Returns:
            Current working directory path
        """
        result = await self.execute_bash("pwd", working_dir=working_dir)
        if result.exit_code != 0:
            raise BashExecutionError(
                f"Failed to get working directory: {result.stderr}", result=result
            )
        return result.stdout.strip()

    async def cd(self, path: str, working_dir: str | None = None) -> str:
        """
        Change directory and return the new working directory.

        Args:
            path: Path to change to
            working_dir: Current working directory (optional)

        Returns:
            New working directory path
        """
        result = await self.execute_bash(f"cd {path} && pwd", working_dir=working_dir)
        if result.exit_code != 0:
            raise BashExecutionError(
                f"Failed to change directory to {path}: {result.stderr}", result=result
            )
        return result.stdout.strip()
