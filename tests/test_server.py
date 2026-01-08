"""Tests for the MCP server module."""

import pytest
from bash_skill.server import mcp, execute_command, get_shell_info, execute_batch, _get_executor


class TestMCPServer:
    """Test cases for MCP server."""

    @pytest.mark.asyncio
    async def test_get_executor(self):
        """Test executor initialization."""
        executor = _get_executor()
        assert executor is not None

    @pytest.mark.asyncio
    async def test_get_shell_info(self):
        """Test getting shell info."""
        info = await get_shell_info()

        assert hasattr(info, "platform")
        assert hasattr(info, "shell")
        assert hasattr(info, "available_shells")
        assert isinstance(info.available_shells, dict)

    @pytest.mark.asyncio
    async def test_execute_simple_command(self):
        """Test executing a simple command."""
        result = await execute_command(command="echo test")

        assert hasattr(result, "exit_code")
        assert hasattr(result, "stdout")
        assert hasattr(result, "stderr")
        assert hasattr(result, "success")
        assert hasattr(result, "platform")
        assert hasattr(result, "shell")
        assert hasattr(result, "error_type")
        assert "test" in result.stdout.lower()

    @pytest.mark.asyncio
    async def test_execute_batch(self):
        """Test batch execution."""
        results = await execute_batch(commands=["echo hello", "echo world"])

        assert len(results) == 2
        assert all("hello" in r.stdout.lower() or "world" in r.stdout.lower() for r in results)

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self):
        """Test command with timeout."""
        result = await execute_command(command="echo test", timeout=5)
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_execute_invalid_command(self):
        """Test executing invalid command."""
        result = await execute_command(command="invalid_command_xyz_12345")

        assert result.success is False
        assert result.error_type in (
            "command_not_found",
            "runtime_error",
            "syntax_error"
        )
