---
name: bash-skill
description: Execute terminal commands across platforms with structured output parsing. Use when user let you use bash-skill to run shell commands, scripts, or system operations on Windows (cmd/PowerShell) or Unix-like systems (bash/sh).
allowed-tools:
  - Bash
  - execute_command
  - get_shell_info
  - execute_batch
---

# Bash Skill

## Overview

This skill enables cross-platform shell command execution with intelligent output parsing. It automatically detects the operating system and uses the appropriate shell (cmd/PowerShell on Windows, bash/sh on Unix-like systems).

## Quick Start

1. **Check the environment first**:
   Call `get_shell_info` to understand the current platform and available shells.

2. **Execute commands**:
   Use `execute_command` for running shell commands with structured output.

3. **Batch execution**:
   Use `execute_batch` for running multiple commands in sequence.

## Best Practices

- **Always check the environment** before executing commands
- **Use absolute paths** when specifying working directories
- **Handle errors gracefully** using the structured `error_type` field
- **Set appropriate timeouts** for long-running commands
- **Parse output intelligently** - the skill automatically detects JSON, key-value pairs, and tabular data

## Error Types

- `none`: No error
- `command_not_found`: Command does not exist
- `permission_denied`: Insufficient permissions
- `syntax_error`: Invalid command syntax
- `runtime_error`: Command execution failed
- `timeout`: Command exceeded timeout limit

## Platform-Specific Notes

### Windows
- Default shell: `cmd` (falls back to PowerShell if available)
- Path separator: backslash `\`
- Example: `dir C:\` or `Get-ChildItem C:\` (PowerShell)

### Linux/macOS
- Default shell: `bash` (falls back to `sh` if needed)
- Path separator: forward slash `/`
- Example: `ls -la /tmp`

## Examples

### Basic Usage

#### Check Environment
```
get_shell_info()
```
Returns:
```json
{
  "platform": "Windows",
  "shell": "cmd",
  "available_shells": {
    "cmd": true,
    "powershell": true,
    "pwsh": false,
    "bash": false,
    "sh": false
  }
}
```

#### Execute Command
```
execute_command(command="ls -la /tmp")
```
Returns:
```json
{
  "exit_code": 0,
  "stdout": "total 8...",
  "stderr": "",
  "success": true,
  "platform": "Linux",
  "shell": "bash",
  "error_type": "none"
}
```

### Advanced Usage

#### Working Directory
```
execute_command(
  command="npm test",
  working_dir="/home/user/project"
)
```

#### Custom Timeout
```
execute_command(
  command="pytest",
  timeout=120
)
```

#### Batch Execution
```
execute_batch(
  commands=[
    "mkdir -p build",
    "cd build",
    "cmake ..",
    "make"
  ],
  working_dir="/home/user/project"
)
```

## Integration with Claude Code

This skill works seamlessly with Claude Code's built-in Bash tool:

1. **Prefer Bash tool** for simple operations
2. **Use this skill** when you need:
   - Cross-platform compatibility
   - Structured error classification
   - Output parsing (JSON, tables, key-value pairs)
   - Timeout control
   - Working directory management

## Output Features

The skill automatically parses command output to extract:
- JSON data
- Key-value pairs (e.g., `KEY=value` or `KEY: value`)
- Tabular data (column headers with separators)

This makes it easier to work with command output programmatically.
