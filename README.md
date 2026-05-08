<div align="center">

# Hydration Reminder Ai MCP

**MCP server for hydration reminder ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-hydration-reminder-ai-mcp)](https://pypi.org/project/meok-hydration-reminder-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Hydration Reminder Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `log_water_intake` | Log water/beverage intake. Specify ml directly or use container type (glass, bot |
| `get_daily_hydration` | Get today's hydration summary with progress toward target. |
| `calculate_target` | Calculate personalized daily hydration target based on weight, activity, and cli |
| `get_hydration_tips` | Get hydration tips and advice for specific situations. |

## Installation

```bash
pip install meok-hydration-reminder-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "hydration-reminder-ai": {
      "command": "python",
      "args": ["-m", "meok_hydration_reminder_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
