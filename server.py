#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

from mcp.server.fastmcp import FastMCP
import json
mcp = FastMCP("hydration-reminder-ai-mcp")
@mcp.tool(name="hydration_plan")
async def hydration_plan(weight_kg: float, activity_level: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    base = weight_kg * 0.033
    mult = {"low": 1.0, "moderate": 1.2, "high": 1.5}.get(activity_level.lower(), 1.0)
    return {"daily_litres": round(base * mult, 2), "glasses": round(base * mult / 0.25)}
@mcp.tool(name="reminder_schedule")
async def reminder_schedule(wake_time: str, sleep_time: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    return {"reminders": ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]}
    return {"reminders": ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]}
if __name__ == "__main__":
    mcp.run()
