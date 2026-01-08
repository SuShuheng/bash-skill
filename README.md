# Bash Skill

A cross-platform shell command execution skill for LLM agents, providing structured output parsing and intelligent error classification.

## Features

- **Cross-platform support**: Windows (cmd/PowerShell), Linux, and macOS (bash/sh)
- **Structured output**: JSON, key-value pairs, and tabular data parsing
- **Error classification**: Intelligent error type detection
- **Timeout control**: Configurable execution timeouts
- **Working directory management**: Execute commands in specific directories
- **Batch execution**: Run multiple commands in sequence
- **MCP Server**: Model Context Protocol server integration
- **Agent Skill**: Claude Desktop/Claude Code skill definition

## Installation

### From source

```bash
cd Path\To\bash-skill
pip install -e .
```

### Development dependencies

```bash
pip install -e ".[dev]"
```

## MCP Server Setup

### Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "bash-skill": {
      "command": "python",
      "args": ["-m", "bash_skill.server"]
    }
  }
}
```

### Claude Code

```bash
cd Path\To\bash-skill
mcp install src/bash_skill/server.py --name bash-skill
```

## Usage

### As an MCP Server

The MCP server provides three tools:

1. **`execute_command`** - Execute a shell command
2. **`get_shell_info`** - Get platform and shell information
3. **`execute_batch`** - Execute multiple commands in sequence

### As an Agent Skill

The skill is automatically activated when you need to execute terminal commands. It:

1. Checks the current environment using `get_shell_info`
2. Executes commands using `execute_command`
3. Parses and structures the output

## API Reference

### `execute_command`

Execute a shell command with structured output.

**Parameters:**

- `command` (str): Shell command to execute
- `working_dir` (str, optional): Working directory
- `timeout` (int, optional): Timeout in seconds (default: 30)

**Returns:**

```typescript
{
  exit_code: number
  stdout: string
  stderr: string
  success: boolean
  platform: string
  shell: string
  error_type: "none" | "command_not_found" | "permission_denied" | "syntax_error" | "runtime_error" | "timeout"
}
```

### `get_shell_info`

Get information about the current platform and available shells.

**Returns:**

```typescript
{
  platform: "Windows" | "Linux" | "Darwin"
  shell: "cmd" | "powershell" | "pwsh" | "bash" | "sh"
  available_shells: { [shell: string]: boolean }
}
```

### `execute_batch`

Execute multiple commands in sequence.

**Parameters:**

- `commands` (str[]): List of shell commands to execute
- `working_dir` (str, optional): Working directory
- `timeout` (int, optional): Timeout in seconds per command (default: 30)

**Returns:**
Array of `CommandResult` objects.

## Examples

### Windows

```python
# Check environment
get_shell_info()
# => {platform: "Windows", shell: "cmd", available_shells: {...}}

# Execute command
execute_command(command="dir C:\\")
# => {exit_code: 0, stdout: "...", success: true, ...}
```

### Linux/macOS

```python
# Check environment
get_shell_info()
# => {platform: "Linux", shell: "bash", available_shells: {...}}

# Execute command
execute_command(command="ls -la /tmp")
# => {exit_code: 0, stdout: "...", success: true, ...}
```

## Development

### Running tests

```bash
pytest
```

### Running specific test file

```bash
pytest tests/test_platform_detector.py
```

### Running with coverage

```bash
pytest --cov=bash_skill --cov-report=html
```

## Project Structure

```
bash-skill/
├── .claude/
│   └── skills/
│       └── bash-skill/
│           └── SKILL.md              # Agent Skill definition
├── src/bash_skill/
│   ├── __init__.py
│   ├── server.py                     # MCP server
│   ├── command_executor.py           # Command execution
│   ├── output_parser.py              # Output parsing
│   └── platform_detector.py          # Platform detection
├── tests/                            # Test suite
├── docs/plan.md                      # Project plan
├── pyproject.toml                    # Project configuration
└── README.md
```

## Requirements

- Python 3.11+
- mcp>=0.9.0

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
