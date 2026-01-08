# Bash-Skill 项目方案

## 项目概述

创建一个功能完整的 `bash-skill`，供大模型（LLM）Agent 使用，实现跨平台的终端命令执行功能，具备输出解析能力。

**架构模式**: 混合架构（Agent Skill + MCP Server）
- **Agent Skill**: 为 Claude 提供命令执行的最佳实践和指导
- **MCP Server**: 提供实际的命令执行工具
- **跨平台支持**: Windows (cmd/PowerShell) + Unix-like (bash/sh)

## 项目结构

```
bash-skill/
├── .claude/
│   └── skills/
│       └── bash-skill/
│           └── SKILL.md                 # Agent Skill 定义
├── src/
│   ├── __init__.py
│   ├── server.py                        # MCP 服务器主入口
│   ├── command_executor.py              # 命令执行逻辑
│   ├── output_parser.py                 # 输出解析和格式化
│   └── platform_detector.py             # 操作系统检测和 Shell 选择
├── scripts/
│   └── install.sh                       # 安装脚本（可选）
├── tests/
│   ├── __init__.py
│   ├── test_command_executor.py
│   ├── test_output_parser.py
│   └── test_server.py
├── docs/
│   └── plan.md                          # 本方案文档
├── pyproject.toml                       # 项目配置
├── requirements.txt
├── README.md
└── .env.example                         # 环境变量模板
```

## 实施计划

### 阶段 1: 项目初始化

**目标**: 创建项目基础结构

**任务清单**:
1. 创建项目目录结构
2. 使用 `pyproject.toml` 初始化 Python 项目
3. 添加 MCP SDK 依赖
4. 创建基础配置文件

**核心文件**:
- `E:\文档\PROJECT\bash-skill\pyproject.toml`

**配置内容**:
```toml
[project]
name = "bash-skill"
version = "0.1.0"
description = "Cross-platform shell command execution skill for LLM agents"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp>=0.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pyright>=1.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.mcp]
command = "python"
args = ["-m", "bash_skill.server"]
```

---

### 阶段 2: 平台检测模块

**目标**: 自动检测操作系统并选择合适的 Shell

**核心文件**:
- `E:\文档\PROJECT\bash-skill\src\platform_detector.py`

**功能特性**:
- 检测 Windows vs Unix-like 系统
- 返回适当的 Shell 命令（cmd, powershell, bash, sh）
- 处理平台特定的特殊情况

**接口设计**:
```python
import platform
from typing import Literal
from dataclasses import dataclass

@dataclass
class PlatformInfo:
    """平台信息"""
    system: Literal["Windows", "Linux", "Darwin", "Unknown"]
    shell: Literal["cmd", "powershell", "bash", "sh", "pwsh"]
    shell_available: bool

class PlatformDetector:
    """平台检测器"""

    @staticmethod
    def detect() -> PlatformInfo:
        """检测当前平台并返回平台信息"""

    @staticmethod
    def get_command_prefix(shell: str) -> list[str]:
        """获取特定 Shell 的命令前缀"""
        # Windows cmd: ["cmd", "/c"]
        # PowerShell: ["pwsh", "-Command"] or ["powershell", "-Command"]
        # Unix bash: ["bash", "-c"]
        # Unix sh: ["sh", "-c"]
```

---

### 阶段 3: 命令执行模块

**目标**: 实现异步命令执行功能

**核心文件**:
- `E:\文档\PROJECT\bash-skill\src\command_executor.py`

**功能特性**:
- 异步执行命令
- 支持 stdin、stdout、stderr 处理
- 超时控制
- 工作目录管理
- 环境变量支持

**接口设计**:
```python
import asyncio
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    """命令执行结果"""
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    timed_out: bool = False

class CommandExecutor:
    """命令执行器"""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info

    async def execute(
        self,
        command: str,
        working_dir: str | None = None,
        timeout: int = 30,
        env: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """执行命令并返回结果"""
```

---

### 阶段 4: 输出解析模块

**目标**: 实现结构化输出解析

**核心文件**:
- `E:\文档\PROJECT\bash-skill\src\output_parser.py`

**功能特性**:
- 解析命令输出（stdout、stderr、退出码）
- 错误检测和分类
- 结果格式化
- 支持常见输出格式（JSON、键值对、表格）

**接口设计**:
```python
from enum import Enum
from dataclasses import dataclass

class ErrorType(Enum):
    """错误类型"""
    NONE = "none"
    COMMAND_NOT_FOUND = "command_not_found"
    PERMISSION_DENIED = "permission_denied"
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"

@dataclass
class ParsedResult:
    """解析后的结果"""
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    platform: str
    shell: str
    error_type: ErrorType
    parsed_data: dict | None = None

class OutputParser:
    """输出解析器"""

    @staticmethod
    def parse(
        result: ExecutionResult,
        platform_info: PlatformInfo,
    ) -> ParsedResult:
        """解析命令执行结果"""

    @staticmethod
    def detect_error_type(stderr: str, exit_code: int) -> ErrorType:
        """检测错误类型"""

    @staticmethod
    def try_parse_json(output: str) -> dict | None:
        """尝试解析 JSON 输出"""
```

---

### 阶段 5: MCP 服务器实现

**目标**: 使用 FastMCP 框架实现 MCP 服务器

**核心文件**:
- `E:\文档\PROJECT\bash-skill\src\server.py`

**提供的工具**:

1. **`execute_command`** - 执行单个 Shell 命令
   - 输入: command, working_dir (可选), timeout (可选)
   - 输出: 结构化的执行结果

2. **`get_shell_info`** - 获取当前 Shell 和平台信息
   - 输入: 无
   - 输出: 平台信息、可用 Shell 列表

**服务器代码框架**:
```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Literal

# 创建 MCP 服务器
mcp = FastMCP(
    "Bash Skill",
    instructions="Cross-platform shell command execution server for LLM agents",
)

# 数据模型
class CommandInput(BaseModel):
    command: str = Field(description="Shell command to execute")
    working_dir: str | None = Field(None, description="Working directory")
    timeout: int = Field(30, description="Timeout in seconds")

class CommandResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    platform: str
    shell: str
    error_type: Literal["none", "command_not_found", "permission_denied",
                        "syntax_error", "runtime_error", "timeout"]

# 工具 1: 执行命令
@mcp.tool()
async def execute_command(
    command: str,
    working_dir: str | None = None,
    timeout: int = 30,
) -> CommandResult:
    """Execute a shell command with structured output"""

# 工具 2: 获取 Shell 信息
@mcp.tool()
async def get_shell_info() -> dict:
    """Get information about the current platform and available shells"""

# 主入口
if __name__ == "__main__":
    mcp.run()
```

---

### 阶段 6: Agent Skill 定义

**目标**: 创建 `.claude/skills/bash-skill/SKILL.md`

**核心文件**:
- `E:\文档\PROJECT\bash-skill\.claude\skills\bash-skill\SKILL.md`

**内容结构**:
```yaml
---
name: bash-skill
description: Execute terminal commands across platforms with structured output parsing. Use when you need to run shell commands, scripts, or system operations on Windows (cmd/PowerShell) or Unix-like systems (bash/sh).
allowed-tools:
  - Bash
  - execute_command
  - get_shell_info
---

# Bash Skill

## Overview

This skill enables cross-platform shell command execution with intelligent output parsing. It automatically detects the operating system and uses the appropriate shell (cmd/PowerShell on Windows, bash/sh on Unix-like systems).

## Quick Start

1. **Check the environment first**:
   ```
   Call get_shell_info to understand the current platform and available shells.
   ```

2. **Execute commands**:
   ```
   Use execute_command for running shell commands with structured output.
   ```

## Best Practices

- **Always check the environment** before executing commands
- **Use absolute paths** when specifying working directories
- **Handle errors gracefully** using the structured error_type field
- **Set appropriate timeouts** for long-running commands

## Examples

### Windows Example
```
get_shell_info → {platform: "Windows", shell: "cmd"}
execute_command(command="dir C:\\") → {exit_code: 0, stdout: "...", success: true}
```

### Unix Example
```
get_shell_info → {platform: "Linux", shell: "bash"}
execute_command(command="ls -la /tmp") → {exit_code: 0, stdout: "...", success: true}
```

## Error Types

- `none`: No error
- `command_not_found`: Command does not exist
- `permission_denied`: Insufficient permissions
- `syntax_error`: Invalid command syntax
- `runtime_error`: Command execution failed
- `timeout`: Command exceeded timeout limit
```

---

### 阶段 7: 测试

**目标**: 创建全面的测试套件

**核心文件**:
- `E:\文档\PROJECT\bash-skill\tests\`

**测试内容**:
- 平台检测测试
- 命令执行测试（使用 mock）
- 输出解析测试
- MCP 服务器集成测试
- 跨平台兼容性测试

**测试框架**:
```python
import pytest
from bash_skill.platform_detector import PlatformDetector
from bash_skill.command_executor import CommandExecutor
from bash_skill.output_parser import OutputParser

class TestPlatformDetector:
    def test_detect_windows(self):
        ...

    def test_detect_linux(self):
        ...

class TestCommandExecutor:
    @pytest.mark.asyncio
    async def test_execute_simple_command(self):
        ...

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self):
        ...

class TestOutputParser:
    def test_parse_success_result(self):
        ...

    def test_detect_error_types(self):
        ...
```

---

### 阶段 8: 文档

**目标**: 创建 README 和使用文档

**核心文件**:
- `E:\文档\PROJECT\bash-skill\README.md`

**文档内容**:
- 项目介绍
- 安装说明
- MCP 服务器设置（Claude Desktop/Claude Code 集成）
- Skill 使用示例
- API 参考
- 开发指南

---

## MCP 服务器工具规范

### 工具 1: `execute_command`

执行单个 Shell 命令，返回结构化结果。

**输入参数**:
```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "Shell command to execute"
    },
    "working_dir": {
      "type": "string",
      "description": "Working directory (optional)"
    },
    "timeout": {
      "type": "number",
      "description": "Timeout in seconds (default: 30)"
    }
  },
  "required": ["command"]
}
```

**输出格式**:
```json
{
  "type": "object",
  "properties": {
    "exit_code": {"type": "integer"},
    "stdout": {"type": "string"},
    "stderr": {"type": "string"},
    "success": {"type": "boolean"},
    "platform": {"type": "string"},
    "shell": {"type": "string"},
    "error_type": {
      "type": "string",
      "enum": ["none", "command_not_found", "permission_denied",
              "syntax_error", "runtime_error", "timeout"]
    }
  }
}
```

### 工具 2: `get_shell_info`

获取当前平台和 Shell 信息。

**输出格式**:
```json
{
  "type": "object",
  "properties": {
    "platform": {
      "type": "string",
      "description": "Operating system (Windows, Linux, Darwin)"
    },
    "shell": {
      "type": "string",
      "description": "Current shell (cmd, powershell, bash, sh)"
    },
    "available_shells": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of available shells on this system"
    }
  }
}
```

---

## Agent Skill 元数据

```yaml
---
name: bash-skill
description: Execute terminal commands across platforms with structured output parsing. Use when you need to run shell commands, scripts, or system operations on Windows (cmd/PowerShell) or Unix-like systems (bash/sh).
allowed-tools:
  - Bash
  - execute_command
  - get_shell_info
---
```

---

## 依赖项

```toml
[project]
name = "bash-skill"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp>=0.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]
```

---

## 使用流程

1. **在 Claude Desktop/Claude Code 中安装 MCP 服务器**:
   ```bash
   cd E:\文档\PROJECT\bash-skill
   uv run mcp install src/server.py --name bash-skill
   ```

2. **Skill 激活**: Claude 在需要执行终端命令时自动调用此 Skill

3. **命令执行流程**:
   - Claude 调用 `get_shell_info` 了解当前环境
   - Claude 使用 `execute_command` 执行实际命令
   - 结果被解析和格式化以便更好地理解

---

## 下一步行动

1. [ ] 创建项目目录结构
2. [ ] 实现平台检测模块
3. [ ] 构建命令执行器
4. [ ] 创建输出解析器
5. [ ] 使用 FastMCP 实现 MCP 服务器
6. [ ] 编写 Agent Skill 定义
7. [ ] 添加测试
8. [ ] 创建文档

---

## 参考资源

- [Agent Skills 文档](https://code.claude.com/docs/en/skills)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP 指南](https://modelcontextprotocol.github.io/python-sdk/)
