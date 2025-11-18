#!/usr/bin/env python3
"""
Lyrics Server - FastAPI server that provides bash command proxy functionality
for Agent Skills in containerized environments.
"""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import uvicorn
import yaml
from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel

from .bash.command_parser import CommandParser
from .bash.environment import EnvironmentManager
from .bash.executor import CommandExecutor
from .filesystem.resolver import PathResolver
from .filesystem.validator import PathValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ==================== SERVICE LAYER ====================
# Unified service class for business logic abstraction


class LyricsService:
    """Unified service for all Lyrics Server business logic"""

    def __init__(
        self, command_parser: CommandParser, command_executor: CommandExecutor
    ):
        self.command_parser = command_parser
        self.command_executor = command_executor
        self.env_manager: EnvironmentManager | None = None
        self.path_resolver: PathResolver | None = None
        self.path_validator: PathValidator | None = None
        self.skills_path: str = "/skills"  # Default, will be updated in initialize
        self.thread_pool = ThreadPoolExecutor(
            max_workers=10
        )  # Thread pool for sync operations

    def shutdown(self):
        """Shutdown the service and clean up resources"""
        # Shutdown command executor (this will clean up the shell session)
        if hasattr(self, "command_executor"):
            self.command_executor.cleanup()
            logger.info("CommandExecutor cleanup complete")

        # Shutdown the thread pool
        if hasattr(self, "thread_pool"):
            self.thread_pool.shutdown(wait=True)
            logger.info("Thread pool shutdown complete")

    def initialize(
        self,
        skills_path: str,
        workspace_path: str,
        env_manager: EnvironmentManager,
        path_resolver: PathResolver,
        path_validator: PathValidator,
    ) -> None:
        self.env_manager = env_manager
        self.path_resolver = path_resolver
        self.path_validator = path_validator
        self.skills_path = skills_path

        # Initialize the persistent shell session
        if not self.command_executor.initialize(workspace_path):
            raise RuntimeError("Failed to initialize persistent shell session")

        logger.info(f"LyricsService initialized with skills path: {skills_path}")
        logger.info(
            "CommandExecutor initialized with persistent shell session "
            "for natural state management"
        )

    async def execute_command(
        self,
        command: str,
        working_dir: str = "/workspace",
        environment: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Execute a bash command and return results using thread pool
        for sync operations"""
        logger.info(f"Executing command: {command}")

        # Use thread pool to execute the synchronous command
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.thread_pool,
            self._execute_command_sync,
            command,
            working_dir,
            environment,
        )

    def _execute_command_sync(
        self,
        command: str,
        working_dir: str = "/workspace",
        environment: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Synchronous version of command execution"""
        logger.info(f"Executing command (sync): {command}")

        # Parse the command
        parsed_command = self.command_parser.parse(command)
        logger.debug(f"Parsed command: {parsed_command}")

        # Set up environment for execution
        execution_env = self.env_manager.get_execution_environment(
            working_dir, environment
        )

        # Execute the command synchronously
        result = self.command_executor.execute(
            parsed_command, execution_env, self.path_resolver, self.path_validator
        )

        logger.info(f"Command executed with exit code: {result.exit_code}")

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "working_dir": execution_env.working_dir,
        }

    async def list_skills(self) -> dict[str, any]:
        """List all available skills using thread pool for file operations"""
        try:
            # Use thread pool to execute the synchronous file operations
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.thread_pool, self._list_skills_sync)
        except Exception as e:
            logger.error(f"Error listing skills: {e}")
            raise RuntimeError(f"Failed to list skills: {str(e)}")

    def _list_skills_sync(self) -> dict[str, any]:
        """Synchronous version of list_skills"""
        public_skills_path = Path(self.skills_path) / "public"

        if not public_skills_path.exists():
            logger.warning(f"Public skills path does not exist: {public_skills_path}")
            return {"skills": [], "total": 0}

        skills = []
        for skill_dir in public_skills_path.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                skill_info = self._get_skill_info_sync(skill_dir)
                if skill_info:
                    skills.append(skill_info)

        logger.info(f"Found {len(skills)} skills: {[s['name'] for s in skills]}")
        return {"skills": skills, "total": len(skills)}

    async def get_skill(self, skill_name: str) -> dict[str, any]:
        """Get detailed information about a specific skill using thread pool"""
        try:
            # Use thread pool to execute the synchronous file operations
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.thread_pool, self._get_skill_sync, skill_name
            )
        except RuntimeError as e:
            if "not found" in str(e).lower():
                raise
            raise RuntimeError(f"Failed to get skill: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting skill '{skill_name}': {e}")
            raise

    def _get_skill_sync(self, skill_name: str) -> dict[str, any]:
        """Synchronous version of get_skill"""
        skill_path = Path(self.skills_path) / "public" / skill_name

        if not skill_path.exists() or not skill_path.is_dir():
            raise RuntimeError(f"Skill '{skill_name}' not found")

        skill_info = self._get_skill_info_sync(skill_path)
        if not skill_info:
            raise RuntimeError(f"Skill '{skill_name}' not found")

        return skill_info

    def _get_skill_info_sync(self, skill_path: Path) -> dict[str, any] | None:
        """Get information about a skill directory"""
        try:
            # Look for description files
            description = None
            desc_files = ["SKILL.md", "README.md", "DESCRIPTION.md"]

            for desc_file in desc_files:
                desc_path = skill_path / desc_file
                if desc_path.exists():
                    try:
                        with open(desc_path, encoding="utf-8") as f:
                            lines = f.readlines()[:5]
                            description = "".join(lines).strip()
                            break
                    except Exception:
                        continue

            # List all files in the skill directory
            files = []
            for file_path in skill_path.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(skill_path)
                    files.append(str(relative_path))

            return {
                "name": skill_path.name,
                "path": str(skill_path),
                "description": description,
                "files": sorted(files),
            }
        except Exception as e:
            logger.error(f"Error getting skill info for {skill_path}: {e}")
            return None


# ==================== ROUTE HANDLERS ====================
# Clean route handlers that delegate to service layer


# Pydantic models for API requests/responses
class BashExecuteRequest(BaseModel):
    command: str
    working_dir: str | None = "/workspace"
    environment: dict[str, str] | None = None


class BashExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    working_dir: str


class SkillInfo(BaseModel):
    name: str
    path: str
    description: str | None = None
    files: list[str]


class SkillsListResponse(BaseModel):
    skills: list[SkillInfo]
    total: int


# Initialize FastAPI app
app = FastAPI(
    title="Lyrics Server",
    description="Bash command proxy for Agent Skills",
    version="0.1.0",
)

# Create API v1 router
api_v1_router = APIRouter(prefix="/api/v1", tags=["API v1"])

# Initialize core components
command_parser = CommandParser()
command_executor = CommandExecutor()
env_manager = EnvironmentManager()
path_resolver = PathResolver()
path_validator = PathValidator()

# Initialize service layer
lyrics_service = LyricsService(command_parser, command_executor)


@app.on_event("startup")
async def startup_event():
    """Initialize server components on startup."""
    logger.info("Starting Lyrics Server with refactored architecture...")

    # Set up skills path
    skills_path = os.environ.get("SKILLS_PATH", "/skills")
    workspace_path = os.environ.get("WORKSPACE_PATH", "/workspace")

    # Initialize core components
    env_manager.initialize(skills_path, workspace_path)
    path_resolver.initialize(skills_path)
    path_validator.initialize(skills_path, workspace_path)

    # Initialize unified service layer
    lyrics_service.initialize(
        skills_path, workspace_path, env_manager, path_resolver, path_validator
    )

    logger.info(f"Skills path: {skills_path}")
    logger.info(f"Workspace path: {workspace_path}")

    # Scan available skills
    await scan_skills()

    logger.info("Lyrics Server started successfully with layered architecture")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown."""
    logger.info("Shutting down Lyrics Server...")
    # Shutdown thread pool to prevent resource leaks
    lyrics_service.shutdown()


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "service": "Lyrics Server",
        "version": "0.1.0",
        "status": "running",
        "api_versions": {"v1": "/api/v1"},
        "endpoints": {
            "execute": "/api/v1/bash/execute",
            "skills": "/api/v1/skills",
            "health": "/api/v1/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lyrics"}


@api_v1_router.get("/health", response_model=dict)
async def api_health_check():
    """API v1 health check endpoint."""
    return {"status": "healthy", "service": "lyrics", "api_version": "v1"}


@api_v1_router.post("/bash/execute", response_model=BashExecuteResponse)
async def execute_bash(request: BashExecuteRequest):
    """
    Execute a bash command and return results.

    This is the main endpoint that simulates bash command execution
    for Agent Skills in a containerized environment.
    """
    try:
        # Use service layer for business logic
        result = await lyrics_service.execute_command(
            command=request.command,
            working_dir=request.working_dir,
            environment=request.environment,
        )

        return BashExecuteResponse(**result)

    except Exception as e:
        logger.error(f"Error executing command '{request.command}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute command: {str(e)}",
        )


@api_v1_router.get("/skills", response_model=SkillsListResponse)
async def list_skills():
    """
    List all available skills in the skills directory.
    Equivalent to: ls /skills/public/
    """
    try:
        # Use service layer for business logic
        result = await lyrics_service.list_skills()

        # Convert to Pydantic models
        skill_models = []
        for skill_data in result["skills"]:
            skill_models.append(SkillInfo(**skill_data))

        return SkillsListResponse(skills=skill_models, total=result["total"])

    except Exception as e:
        logger.error(f"Error listing skills: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list skills: {str(e)}",
        )


@api_v1_router.get("/skills/{skill_name}", response_model=SkillInfo)
async def get_skill(skill_name: str):
    """
    Get detailed information about a specific skill.
    """
    try:
        # Use service layer for business logic
        skill_data = await lyrics_service.get_skill(skill_name)

        # Convert to Pydantic model
        return SkillInfo(**skill_data)

    except RuntimeError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill '{skill_name}' not found",
            )
        raise
    except Exception as e:
        logger.error(f"Error getting skill '{skill_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get skill: {str(e)}",
        )


def parse_skill_metadata(skill_path: Path) -> dict[str, Any] | None:
    """
    Parse YAML frontmatter from SKILL.md file.
    Returns metadata dictionary or None if not found.
    """
    try:
        skill_md_path = skill_path / "SKILL.md"
        if not skill_md_path.exists():
            return None

        with open(skill_md_path, encoding="utf-8") as f:
            content = f.read()

        # Check if file has YAML frontmatter (starts and ends with ---)
        if content.startswith("---"):
            # Find the end of frontmatter
            end_index = content.find("\n---", 3)
            if end_index != -1:
                # Extract content between the two --- markers
                frontmatter = content[4:end_index]  # Skip first "---\n"
                try:
                    metadata = yaml.safe_load(frontmatter)
                    return metadata
                except yaml.YAMLError as e:
                    logger.warning(
                        f"Failed to parse YAML frontmatter in {skill_md_path}: {e}"
                    )

        return None
    except Exception as e:
        logger.warning(f"Error reading skill metadata from {skill_path}: {e}")
        return None


async def get_skill_info(skill_path: Path) -> SkillInfo | None:
    """
    Get information about a skill directory.
    """
    try:
        # First, try to get metadata from SKILL.md YAML frontmatter
        metadata = parse_skill_metadata(skill_path)

        # Extract description from metadata or fallback to file content
        description = None
        if metadata and "description" in metadata:
            description = metadata["description"]
        else:
            # Fallback: Look for description in files
            desc_files = ["SKILL.md", "README.md", "DESCRIPTION.md"]
            for desc_file in desc_files:
                desc_path = skill_path / desc_file
                if desc_path.exists():
                    try:
                        with open(desc_path, encoding="utf-8") as f:
                            # Read first few lines as description
                            lines = f.readlines()[:5]
                            description = "".join(lines).strip()
                            break
                    except Exception:
                        continue

        # List all files in the skill directory
        files = []
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                # Store relative path from skill directory
                relative_path = file_path.relative_to(skill_path)
                files.append(str(relative_path))

        # Get skill name from metadata or fallback to directory name
        skill_name = metadata.get("name") if metadata else skill_path.name

        return SkillInfo(
            name=skill_name,
            path=str(skill_path),
            description=description,
            files=sorted(files),
        )

    except Exception as e:
        logger.error(f"Error getting skill info for {skill_path}: {e}")
        return None


async def scan_skills():
    """Scan and log available skills."""
    try:
        skills_response = await list_skills()
        skill_names = [skill.name for skill in skills_response.skills]

        logger.info(f"Found {skills_response.total} skills: {', '.join(skill_names)}")

        # Log detailed skill information
        for skill in skills_response.skills:
            logger.debug(f"Skill '{skill.name}': {len(skill.files)} files")

    except Exception as e:
        logger.error(f"Error scanning skills: {e}")


# Include the API v1 router in the main app
app.include_router(api_v1_router)


def main():
    """Main entry point for the server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Lyrics Server - Bash command proxy for Agent Skills"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8870, help="Port to bind to")
    parser.add_argument(
        "--skills-path", default="/skills", help="Path to skills directory"
    )
    parser.add_argument(
        "--workspace-path", default="/workspace", help="Path to workspace directory"
    )
    parser.add_argument("--log-level", default="INFO", help="Log level")

    args = parser.parse_args()

    # Set environment variables
    os.environ["SKILLS_PATH"] = args.skills_path
    os.environ["WORKSPACE_PATH"] = args.workspace_path

    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"Skills path: {args.skills_path}")
    logger.info(f"Workspace path: {args.workspace_path}")

    # Run the server
    uvicorn.run(
        "lyrics.server:app",
        host=args.host,
        port=args.port,
        reload=False,
        log_level=args.log_level.lower(),
    )


if __name__ == "__main__":
    main()
