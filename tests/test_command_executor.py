"""Tests for the command executor module."""

import pytest
from bash_skill.platform_detector import PlatformInfo, PlatformDetector
from bash_skill.command_executor import CommandExecutor, ExecutionResult


class TestCommandExecutor:
    """Test cases for CommandExecutor."""

    @pytest.fixture
    def platform_info(self):
        """Provide a test PlatformInfo."""
        return PlatformDetector.detect()

    @pytest.fixture
    def executor(self, platform_info):
        """Provide a test CommandExecutor."""
        return CommandExecutor(platform_info)

    @pytest.mark.asyncio
    async def test_executor_initialization(self):
        """Test executor initialization."""
        info = PlatformDetector.detect()
        executor = CommandExecutor(info)

        assert executor.platform_info == info

    @pytest.mark.asyncio
    async def test_executor_auto_detect(self):
        """Test executor auto-detects platform if not provided."""
        executor = CommandExecutor()

        assert executor.platform_info is not None
        assert isinstance(executor.platform_info, PlatformInfo)

    @pytest.mark.asyncio
    async def test_execute_simple_command(self, executor):
        """Test executing a simple command."""
        if executor.platform_info.system == "Windows":
            command = "echo hello"
        else:
            command = "echo 'hello'"

        result = await executor.execute(command)

        assert isinstance(result, ExecutionResult)
        assert isinstance(result.exit_code, int)
        assert isinstance(result.stdout, str)
        assert isinstance(result.stderr, str)
        assert isinstance(result.success, bool)
        assert result.timed_out is False
        assert "hello" in result.stdout.lower()

    @pytest.mark.asyncio
    async def test_execute_invalid_command(self, executor):
        """Test executing an invalid command."""
        result = await executor.execute("invalid_command_that_does_not_exist_12345")

        assert result.success is False
        assert len(result.stderr) > 0 or result.exit_code != 0

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self, executor):
        """Test command execution with timeout."""
        # Create a command that will timeout
        if executor.platform_info.system == "Windows":
            command = "timeout 100"
        else:
            command = "sleep 100"

        result = await executor.execute(command, timeout=1)

        assert result.timed_out is True
        assert result.success is False
        assert "timeout" in result.stderr.lower()

    @pytest.mark.asyncio
    async def test_execute_batch(self, executor):
        """Test batch execution of commands."""
        if executor.platform_info.system == "Windows":
            commands = ["echo hello", "echo world"]
        else:
            commands = ["echo 'hello'", "echo 'world'"]

        results = await executor.execute_batch(commands)

        assert len(results) == 2
        assert all(isinstance(r, ExecutionResult) for r in results)
        assert "hello" in results[0].stdout.lower()
        assert "world" in results[1].stdout.lower()

    @pytest.mark.asyncio
    async def test_execute_batch_stops_on_failure(self, executor):
        """Test that batch execution stops on first failure."""
        commands = ["echo hello", "invalid_command_xyz", "echo world"]

        results = await executor.execute_batch(commands)

        assert len(results) == 2  # Stops after invalid_command
        assert results[0].success is True
        assert results[1].success is False
