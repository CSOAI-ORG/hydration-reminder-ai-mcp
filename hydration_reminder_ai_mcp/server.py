from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hydration-reminder")

WATER_LOG = []

@mcp.tool()
def log_water(amount: float, unit: str = "ml") -> dict:
    """Log water intake. Converts oz to ml internally."""
    ml = amount * 29.5735 if unit.lower() == "oz" else amount
    WATER_LOG.append({"amount_ml": round(ml, 1), "unit": unit.lower()})
    total = sum(e["amount_ml"] for e in WATER_LOG)
    return {"logged_ml": round(ml, 1), "total_ml": round(total, 1), "entries": len(WATER_LOG)}

@mcp.tool()
def calculate_daily_goal(weight_kg: float, activity_minutes: int = 0) -> dict:
    """Calculate recommended daily water intake in ml."""
    base = weight_kg * 35
    activity_add = (activity_minutes / 30) * 350
    goal = base + activity_add
    return {"daily_goal_ml": round(goal, 1), "daily_goal_oz": round(goal / 29.5735, 1)}

@mcp.tool()
def get_hydration_status(goal_ml: float = 2500) -> dict:
    """Get hydration progress."""
    total = sum(e["amount_ml"] for e in WATER_LOG)
    remaining = max(0, goal_ml - total)
    percent = min(100, round((total / goal_ml) * 100, 1)) if goal_ml > 0 else 0
    return {
        "consumed_ml": round(total, 1),
        "goal_ml": goal_ml,
        "remaining_ml": round(remaining, 1),
        "percent_complete": percent,
        "reminder": "Drink a glass of water now!" if remaining > 0 else "Goal reached! Great job!",
    }

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
