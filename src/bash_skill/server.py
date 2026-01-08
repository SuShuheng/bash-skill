"""MCP Server for cross-platform shell command execution."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Literal, Optional

from .platform_detector import PlatformDetector, PlatformInfo
from .command_executor import CommandExecutor
from .output_parser import OutputParser, ErrorType


# Create MCP server
mcp = FastMCP(
    "Bash Skill",
    instructions="Cross-platform shell command execution server for LLM agents",
)


# Data models
class CommandInput(BaseModel):
    """Input schema for command execution."""

    command: str = Field(description="Shell command to execute")
    working_dir: Optional[str] = Field(None, description="Working directory")
    timeout: int = Field(30, description="Timeout in seconds")


class CommandResult(BaseModel):
    """Result schema for command execution."""

    exit_code: int
    stdout: str
    stderr: str
    success: bool
    platform: str
    shell: str
    error_type: Literal[
        "none",
        "command_not_found",
        "permission_denied",
        "syntax_error",
        "runtime_error",
        "timeout"
    ]


class ShellInfo(BaseModel):
    """Information about the current shell and platform."""

    platform: str = Field(description="Operating system (Windows, Linux, Darwin)")
    shell: str = Field(description="Current shell (cmd, powershell, pwsh, bash, sh)")
    available_shells: dict[str, bool] = Field(description="Available shells and their status")


# Global state
_platform_info: Optional[PlatformInfo] = None
_executor: Optional[CommandExecutor] = None


def _get_executor() -> CommandExecutor:
    """Get or create the command executor instance."""
    global _platform_info, _executor

    if _executor is None:
        _platform_info = PlatformDetector.detect()
        _executor = CommandExecutor(_platform_info)

    return _executor


@mcp.tool()
async def execute_command(
    command: str,
    working_dir: Optional[str] = None,
    timeout: int = 30,
) -> CommandResult:
    """Execute a shell command with structured output.

    This tool runs shell commands on the host system and provides
    structured, parsed output with error classification.

    Args:
        command: Shell command to execute
        working_dir: Working directory (optional)
        timeout: Timeout in seconds (default: 30)

    Returns:
        CommandResult: Structured execution result with error classification

    Examples:
        Windows:
            execute_command(command="dir C:\\\\")

        Linux/macOS:
            execute_command(command="ls -la /tmp")
    """
    executor = _get_executor()

    # Execute the command
    result = await executor.execute(
        command=command,
        working_dir=working_dir,
        timeout=timeout,
    )

    # Parse the result
    parsed = OutputParser.parse(result, executor.platform_info)

    return CommandResult(
        exit_code=parsed.exit_code,
        stdout=parsed.stdout,
        stderr=parsed.stderr,
        success=parsed.success,
        platform=parsed.platform,
        shell=parsed.shell,
        error_type=parsed.error_type.value,
    )


@mcp.tool()
async def get_shell_info() -> ShellInfo:
    """Get information about the current platform and available shells.

    Returns detailed information about the operating system, current shell,
    and all available shells on the system.

    Returns:
        ShellInfo: Platform and shell information
    """
    platform_info = PlatformDetector.detect()
    available_shells = PlatformDetector.get_available_shells()

    return ShellInfo(
        platform=platform_info.system,
        shell=platform_info.shell,
        available_shells=available_shells,
    )


@mcp.tool()
async def execute_batch(
    commands: list[str],
    working_dir: Optional[str] = None,
    timeout: int = 30,
) -> list[CommandResult]:
    """Execute multiple commands in sequence.

    Executes a list of commands one after another. Stops if a command fails.

    Args:
        commands: List of shell commands to execute
        working_dir: Working directory (optional)
        timeout: Timeout in seconds per command (default: 30)

    Returns:
        List[CommandResult]: Results for each executed command
    """
    executor = _get_executor()

    results = await executor.execute_batch(
        commands=commands,
        working_dir=working_dir,
        timeout=timeout,
    )

    return [
        CommandResult(
            exit_code=r.exit_code,
            stdout=r.stdout,
            stderr=r.stderr,
            success=r.success,
            platform=executor.platform_info.system,
            shell=executor.platform_info.shell,
            error_type=OutputParser.detect_error_type(
                r.stderr,
                r.exit_code,
                r.timed_out
            ).value,
        )
        for r in results
    ]


# Main entry point
if __name__ == "__main__":
    mcp.run()
