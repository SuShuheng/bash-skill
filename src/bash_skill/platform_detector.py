"""Platform detection module for cross-platform shell command execution."""

import platform
import shutil
import subprocess
from typing import Literal
from dataclasses import dataclass


@dataclass
class PlatformInfo:
    """Platform information data class."""

    system: Literal["Windows", "Linux", "Darwin", "Unknown"]
    shell: Literal["cmd", "powershell", "bash", "sh", "pwsh"]
    shell_available: bool


class PlatformDetector:
    """Detects the current platform and available shells."""

    @staticmethod
    def detect() -> PlatformInfo:
        """Detect the current platform and return platform information.

        Returns:
            PlatformInfo: Information about the detected platform and shell.
        """
        system = platform.system()

        if system == "Windows":
            return PlatformDetector._detect_windows()
        elif system in ("Linux", "Darwin"):
            return PlatformDetector._detect_unix(system)
        else:
            return PlatformInfo(
                system="Unknown",
                shell="sh",
                shell_available=False
            )

    @staticmethod
    def _detect_windows() -> PlatformInfo:
        """Detect shell on Windows systems.

        Returns:
            PlatformInfo: Windows platform information with available shell.
        """
        # Try PowerShell Core (pwsh) first, then Windows PowerShell
        if shutil.which("pwsh"):
            return PlatformInfo(
                system="Windows",
                shell="pwsh",
                shell_available=True
            )
        elif shutil.which("powershell"):
            return PlatformInfo(
                system="Windows",
                shell="powershell",
                shell_available=True
            )
        # Fall back to cmd (always available on Windows)
        return PlatformInfo(
            system="Windows",
            shell="cmd",
            shell_available=True
        )

    @staticmethod
    def _detect_unix(system: str) -> PlatformInfo:
        """Detect shell on Unix-like systems.

        Args:
            system: The system name (Linux or Darwin).

        Returns:
            PlatformInfo: Unix platform information with available shell.
        """
        # Try bash first, then fall back to sh
        if shutil.which("bash"):
            return PlatformInfo(
                system=system,
                shell="bash",
                shell_available=True
            )
        elif shutil.which("sh"):
            return PlatformInfo(
                system=system,
                shell="sh",
                shell_available=True
            )
        else:
            return PlatformInfo(
                system=system,
                shell="sh",
                shell_available=False
            )

    @staticmethod
    def get_command_prefix(shell: str) -> list[str]:
        """Get the command prefix for a specific shell.

        Args:
            shell: The shell type.

        Returns:
            List of command prefix arguments for subprocess execution.

        Raises:
            ValueError: If the shell type is unknown.
        """
        shell_commands = {
            "cmd": ["cmd", "/c"],
            "powershell": ["powershell", "-Command"],
            "pwsh": ["pwsh", "-Command"],
            "bash": ["bash", "-c"],
            "sh": ["sh", "-c"],
        }

        if shell not in shell_commands:
            raise ValueError(f"Unknown shell type: {shell}")

        return shell_commands[shell]

    @staticmethod
    def get_available_shells() -> dict[str, bool]:
        """Get all available shells on the current system.

        Returns:
            Dictionary mapping shell names to availability status.
        """
        shells = ["cmd", "powershell", "pwsh", "bash", "sh"]
        return {shell: shutil.which(shell) is not None for shell in shells}
