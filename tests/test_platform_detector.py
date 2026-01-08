"""Tests for the platform detector module."""

import pytest
from bash_skill.platform_detector import PlatformDetector, PlatformInfo


class TestPlatformDetector:
    """Test cases for PlatformDetector."""

    def test_detect_returns_platform_info(self):
        """Test that detect returns a valid PlatformInfo object."""
        info = PlatformDetector.detect()

        assert isinstance(info, PlatformInfo)
        assert isinstance(info.system, str)
        assert isinstance(info.shell, str)
        assert isinstance(info.shell_available, bool)

    def test_detect_windows(self, monkeypatch):
        """Test detection of Windows platform."""
        monkeypatch.setattr("platform.system", lambda: "Windows")

        info = PlatformDetector.detect()

        assert info.system == "Windows"
        assert info.shell in ("cmd", "powershell", "pwsh")
        assert info.shell_available is True

    def test_detect_linux(self, monkeypatch):
        """Test detection of Linux platform."""
        monkeypatch.setattr("platform.system", lambda: "Linux")
        monkeypatch.setattr("shutil.which", lambda x: "bash" if x == "bash" else None)

        info = PlatformDetector.detect()

        assert info.system == "Linux"
        assert info.shell == "bash"
        assert info.shell_available is True

    def test_detect_darwin(self, monkeypatch):
        """Test detection of macOS (Darwin) platform."""
        monkeypatch.setattr("platform.system", lambda: "Darwin")
        monkeypatch.setattr("shutil.which", lambda x: "zsh" if x == "zsh" else ("bash" if x == "bash" else None))

        info = PlatformDetector.detect()

        assert info.system == "Darwin"
        assert info.shell in ("bash", "sh")

    def test_get_command_prefix_cmd(self):
        """Test command prefix for cmd."""
        prefix = PlatformDetector.get_command_prefix("cmd")
        assert prefix == ["cmd", "/c"]

    def test_get_command_prefix_powershell(self):
        """Test command prefix for PowerShell."""
        prefix = PlatformDetector.get_command_prefix("powershell")
        assert prefix == ["powershell", "-Command"]

    def test_get_command_prefix_pwsh(self):
        """Test command prefix for PowerShell Core."""
        prefix = PlatformDetector.get_command_prefix("pwsh")
        assert prefix == ["pwsh", "-Command"]

    def test_get_command_prefix_bash(self):
        """Test command prefix for bash."""
        prefix = PlatformDetector.get_command_prefix("bash")
        assert prefix == ["bash", "-c"]

    def test_get_command_prefix_sh(self):
        """Test command prefix for sh."""
        prefix = PlatformDetector.get_command_prefix("sh")
        assert prefix == ["sh", "-c"]

    def test_get_command_prefix_invalid(self):
        """Test command prefix for invalid shell."""
        with pytest.raises(ValueError, match="Unknown shell type"):
            PlatformDetector.get_command_prefix("invalid_shell")

    def test_get_available_shells(self):
        """Test getting available shells."""
        shells = PlatformDetector.get_available_shells()

        assert isinstance(shells, dict)
        assert "cmd" in shells
        assert "powershell" in shells
        assert "bash" in shells
        assert "sh" in shells
        assert "pwsh" in shells

        for shell, available in shells.items():
            assert isinstance(shell, str)
            assert isinstance(available, bool)
