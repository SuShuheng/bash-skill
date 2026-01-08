"""Command execution module for running shell commands asynchronously."""

import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from .platform_detector import PlatformInfo, PlatformDetector


@dataclass
class ExecutionResult:
    """Result of a command execution."""

    exit_code: int
    stdout: str
    stderr: str
    success: bool
    timed_out: bool = False


class CommandExecutor:
    """Executes shell commands asynchronously."""

    def __init__(self, platform_info: Optional[PlatformInfo] = None):
        """Initialize the command executor.

        Args:
            platform_info: Platform information. If None, will auto-detect.
        """
        self.platform_info = platform_info or PlatformDetector.detect()

    async def execute(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: int = 30,
        env: Optional[dict[str, str]] = None,
    ) -> ExecutionResult:
        """Execute a shell command and return the result.

        Args:
            command: The shell command to execute.
            working_dir: The working directory for the command (optional).
            timeout: Maximum execution time in seconds (default: 30).
            env: Environment variables to set for the command (optional).

        Returns:
            ExecutionResult: The result of the command execution.
        """
        # Get the command prefix for the current shell
        cmd_prefix = PlatformDetector.get_command_prefix(self.platform_info.shell)
        full_command = cmd_prefix + [command]

        # Prepare the working directory
        cwd = Path(working_dir) if working_dir else None

        # Prepare environment variables
        process_env = None
        if env:
            import os
            process_env = os.environ.copy()
            process_env.update(env)

        try:
            # Create the subprocess
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=process_env,
            )

            # Wait for completion with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                timed_out = False
            except asyncio.TimeoutError:
                # Kill the process on timeout
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Command timed out after {timeout} seconds",
                    success=False,
                    timed_out=True
                )

            # Decode output
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")

            return ExecutionResult(
                exit_code=process.returncode or 0,
                stdout=stdout,
                stderr=stderr,
                success=process.returncode == 0,
                timed_out=False
            )

        except FileNotFoundError:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Shell '{self.platform_info.shell}' not found",
                success=False,
                timed_out=False
            )
        except PermissionError:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Permission denied when trying to execute command",
                success=False,
                timed_out=False
            )
        except Exception as e:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Unexpected error: {str(e)}",
                success=False,
                timed_out=False
            )

    async def execute_batch(
        self,
        commands: list[str],
        working_dir: Optional[str] = None,
        timeout: int = 30,
        env: Optional[dict[str, str]] = None,
    ) -> list[ExecutionResult]:
        """Execute multiple commands in sequence.

        Args:
            commands: List of shell commands to execute.
            working_dir: The working directory for the commands (optional).
            timeout: Maximum execution time per command in seconds (default: 30).
            env: Environment variables to set for the commands (optional).

        Returns:
            List[ExecutionResult]: Results of each command execution.
        """
        results = []
        for command in commands:
            result = await self.execute(command, working_dir, timeout, env)
            results.append(result)

            # Stop execution if a command fails
            if not result.success:
                break

        return results
