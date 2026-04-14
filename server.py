#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
import json
mcp = FastMCP("hydration-reminder-ai-mcp")
@mcp.tool(name="hydration_plan")
async def hydration_plan(weight_kg: float, activity_level: str) -> str:
    base = weight_kg * 0.033
    mult = {"low": 1.0, "moderate": 1.2, "high": 1.5}.get(activity_level.lower(), 1.0)
    return json.dumps({"daily_litres": round(base * mult, 2), "glasses": round(base * mult / 0.25)})
@mcp.tool(name="reminder_schedule")
async def reminder_schedule(wake_time: str, sleep_time: str) -> str:
    return json.dumps({"reminders": ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]})
if __name__ == "__main__":
    mcp.run()
