"""Output parsing module for structured command result interpretation."""

import json
import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional

from .command_executor import ExecutionResult
from .platform_detector import PlatformInfo


class ErrorType(Enum):
    """Classification of error types."""

    NONE = "none"
    COMMAND_NOT_FOUND = "command_not_found"
    PERMISSION_DENIED = "permission_denied"
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"


@dataclass
class ParsedResult:
    """Parsed and structured command execution result."""

    exit_code: int
    stdout: str
    stderr: str
    success: bool
    platform: str
    shell: str
    error_type: ErrorType
    parsed_data: Optional[dict] = None


class OutputParser:
    """Parses and structures command execution results."""

    # Common error patterns for different shells
    ERROR_PATTERNS = {
        "command_not_found": [
            r"command not found",
            r"not recognized as an internal or external command",
            r"is not recognized",
            r"no such file or directory",
            r"cannot find",
        ],
        "permission_denied": [
            r"permission denied",
            r"access denied",
            r"unauthorized",
            r"insufficient privileges",
        ],
        "syntax_error": [
            r"syntax error",
            r"invalid syntax",
            r"unexpected token",
            r"parse error",
        ],
    }

    @staticmethod
    def parse(
        result: ExecutionResult,
        platform_info: PlatformInfo,
    ) -> ParsedResult:
        """Parse a command execution result into a structured format.

        Args:
            result: The raw execution result.
            platform_info: Platform information for context.

        Returns:
            ParsedResult: Structured and parsed result.
        """
        # Detect error type
        error_type = OutputParser.detect_error_type(
            result.stderr,
            result.exit_code,
            result.timed_out
        )

        # Try to parse structured output (JSON)
        parsed_data = None
        if result.stdout.strip():
            parsed_data = OutputParser.try_parse_json(result.stdout)

        return ParsedResult(
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            success=result.success,
            platform=platform_info.system,
            shell=platform_info.shell,
            error_type=error_type,
            parsed_data=parsed_data,
        )

    @staticmethod
    def detect_error_type(
        stderr: str,
        exit_code: int,
        timed_out: bool
    ) -> ErrorType:
        """Detect and classify the error type from stderr and exit code.

        Args:
            stderr: Standard error output.
            exit_code: Process exit code.
            timed_out: Whether the command timed out.

        Returns:
            ErrorType: The detected error type.
        """
        # Check for timeout first
        if timed_out:
            return ErrorType.TIMEOUT

        # No error if exit code is 0 and stderr is empty
        if exit_code == 0 and not stderr.strip():
            return ErrorType.NONE

        # Check stderr against error patterns
        stderr_lower = stderr.lower()

        for error_type, patterns in OutputParser.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern.lower(), stderr_lower):
                    return ErrorType[error_type.upper()]

        # Default to runtime error
        return ErrorType.RUNTIME_ERROR

    @staticmethod
    def try_parse_json(output: str) -> Optional[dict]:
        """Attempt to parse JSON output.

        Args:
            output: The output string to parse.

        Returns:
            Parsed JSON dictionary or None if parsing fails.
        """
        output = output.strip()

        # Try direct JSON parsing
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from output (handles cases with surrounding text)
        # Match complete JSON objects
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, output, re.DOTALL)

        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        # Try to extract JSON arrays
        array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
        matches = re.findall(array_pattern, output, re.DOTALL)

        for match in matches:
            try:
                return {"data": json.loads(match)}
            except json.JSONDecodeError:
                continue

        return None

    @staticmethod
    def format_summary(result: ParsedResult) -> str:
        """Format a parsed result as a human-readable summary.

        Args:
            result: The parsed result to format.

        Returns:
            A formatted summary string.
        """
        lines = [
            f"Exit Code: {result.exit_code}",
            f"Platform: {result.platform}",
            f"Shell: {result.shell}",
            f"Success: {result.success}",
        ]

        if result.error_type != ErrorType.NONE:
            lines.append(f"Error Type: {result.error_type.value}")

        if result.stdout.strip():
            stdout_preview = result.stdout.strip()[:200]
            if len(result.stdout) > 200:
                stdout_preview += "..."
            lines.append(f"\nStdout:\n{stdout_preview}")

        if result.stderr.strip():
            stderr_preview = result.stderr.strip()[:200]
            if len(result.stderr) > 200:
                stderr_preview += "..."
            lines.append(f"\nStderr:\n{stderr_preview}")

        if result.parsed_data:
            lines.append(f"\nParsed Data:\n{json.dumps(result.parsed_data, indent=2)}")

        return "\n".join(lines)

    @staticmethod
    def extract_key_value_pairs(output: str) -> dict[str, str]:
        """Extract key-value pairs from command output.

        Handles formats like:
        - KEY=value
        - KEY: value
        - KEY = value

        Args:
            output: The output string to parse.

        Returns:
            Dictionary of extracted key-value pairs.
        """
        pairs = {}

        # Pattern for KEY=value, KEY: value, KEY = value
        patterns = [
            r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$',
            r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$',
        ]

        for line in output.splitlines():
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    key, value = match.groups()
                    pairs[key] = value.strip()
                    break

        return pairs

    @staticmethod
    def extract_table(output: str) -> list[dict[str, str]]:
        """Extract tabular data from command output.

        Handles simple tabular formats with column headers.

        Args:
            output: The output string to parse.

        Returns:
            List of dictionaries representing table rows.
        """
        lines = [line.strip() for line in output.splitlines() if line.strip()]

        if len(lines) < 2:
            return []

        # Try to detect the separator line
        separator_idx = -1
        for i, line in enumerate(lines):
            if re.match(r'^[\s\-\+\|]+$', line):
                separator_idx = i
                break

        if separator_idx == -1 or separator_idx == 0 or separator_idx >= len(lines) - 1:
            return []

        # Extract headers (before separator)
        headers_line = lines[separator_idx - 1]
        rows_lines = lines[separator_idx + 1 :]

        # Try different parsing strategies
        # Strategy 1: Pipe-separated
        if '|' in headers_line:
            headers = [h.strip() for h in headers_line.split('|') if h.strip()]
            result = []
            for row in rows_lines:
                if '|' not in row:
                    continue
                values = [v.strip() for v in row.split('|') if v.strip()]
                if len(values) == len(headers):
                    result.append(dict(zip(headers, values)))
            return result

        # Strategy 2: Whitespace-separated
        headers = headers_line.split()
        result = []
        for row in rows_lines:
            values = row.split()
            if len(values) >= len(headers):
                # Take only the number of values that match headers
                values = values[:len(headers)]
                result.append(dict(zip(headers, values)))
        return result
