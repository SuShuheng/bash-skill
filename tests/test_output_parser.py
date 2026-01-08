"""Tests for the output parser module."""

import pytest
from bash_skill.output_parser import OutputParser, ErrorType, ParsedResult
from bash_skill.command_executor import ExecutionResult
from bash_skill.platform_detector import PlatformInfo


class TestOutputParser:
    """Test cases for OutputParser."""

    @pytest.fixture
    def platform_info(self):
        """Provide a test PlatformInfo."""
        return PlatformInfo(system="Linux", shell="bash", shell_available=True)

    @pytest.fixture
    def success_result(self):
        """Provide a successful execution result."""
        return ExecutionResult(
            exit_code=0,
            stdout="hello world",
            stderr="",
            success=True,
            timed_out=False
        )

    @pytest.fixture
    def error_result(self):
        """Provide an error execution result."""
        return ExecutionResult(
            exit_code=1,
            stdout="",
            stderr="command not found: test",
            success=False,
            timed_out=False
        )

    def test_parse_success_result(self, success_result, platform_info):
        """Test parsing a successful result."""
        parsed = OutputParser.parse(success_result, platform_info)

        assert isinstance(parsed, ParsedResult)
        assert parsed.exit_code == 0
        assert parsed.stdout == "hello world"
        assert parsed.stderr == ""
        assert parsed.success is True
        assert parsed.platform == "Linux"
        assert parsed.shell == "bash"
        assert parsed.error_type == ErrorType.NONE

    def test_detect_error_type_none(self):
        """Test error type detection for no error."""
        error_type = OutputParser.detect_error_type("", 0, False)
        assert error_type == ErrorType.NONE

    def test_detect_error_type_timeout(self):
        """Test error type detection for timeout."""
        error_type = OutputParser.detect_error_type("", -1, True)
        assert error_type == ErrorType.TIMEOUT

    def test_detect_error_type_command_not_found(self):
        """Test error type detection for command not found."""
        error_type = OutputParser.detect_error_type("bash: test: command not found", 127, False)
        assert error_type == ErrorType.COMMAND_NOT_FOUND

    def test_detect_error_type_permission_denied(self):
        """Test error type detection for permission denied."""
        error_type = OutputParser.detect_error_type("bash: /bin/test: Permission denied", 126, False)
        assert error_type == ErrorType.PERMISSION_DENIED

    def test_detect_error_type_syntax_error(self):
        """Test error type detection for syntax error."""
        error_type = OutputParser.detect_error_type("bash: syntax error near unexpected token", 2, False)
        assert error_type == ErrorType.SYNTAX_ERROR

    def test_try_parse_json_valid(self):
        """Test JSON parsing with valid JSON."""
        json_str = '{"key": "value", "number": 42}'
        result = OutputParser.try_parse_json(json_str)

        assert result is not None
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_try_parse_json_invalid(self):
        """Test JSON parsing with invalid JSON."""
        result = OutputParser.try_parse_json("not json")
        assert result is None

    def test_try_parse_json_extract_from_output(self):
        """Test extracting JSON from mixed output."""
        output = "Some text before\n{\"key\": \"value\"}\nSome text after"
        result = OutputParser.try_parse_json(output)

        assert result is not None
        assert result["key"] == "value"

    def test_extract_key_value_pairs(self):
        """Test extracting key-value pairs."""
        output = """
KEY1=value1
KEY2: value2
KEY3 = value3
"""
        pairs = OutputParser.extract_key_value_pairs(output)

        assert pairs.get("KEY1") == "value1"
        assert pairs.get("KEY2") == "value2"
        assert pairs.get("KEY3") == "value3"

    def test_extract_table_pipe_separated(self):
        """Test extracting pipe-separated table data."""
        output = """
| Name | Age | City |
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |
"""
        tables = OutputParser.extract_table(output)

        assert len(tables) == 2
        assert tables[0]["Name"] == "John"
        assert tables[0]["Age"] == "30"
        assert tables[1]["Name"] == "Jane"

    def test_format_summary(self, success_result, platform_info):
        """Test formatting a result summary."""
        parsed = OutputParser.parse(success_result, platform_info)
        summary = OutputParser.format_summary(parsed)

        assert "Exit Code: 0" in summary
        assert "Platform: Linux" in summary
        assert "Shell: bash" in summary
        assert "Success: True" in summary
        assert "hello world" in summary
