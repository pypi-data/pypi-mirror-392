"""
Common types for the bash module.
"""

from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of command execution."""

    stdout: str
    stderr: str
    exit_code: int
    execution_time: float | None = None


@dataclass
class ExecutionEnvironment:
    """Environment for command execution."""

    working_dir: str
    environment_vars: dict
    skills_path: str
    workspace_path: str
