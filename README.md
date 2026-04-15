# Hydration Reminder AI

> By [MEOK AI Labs](https://meok.ai) — Hydration tracking and reminders

## Installation

```bash
pip install hydration-reminder-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install hydration-reminder-ai-mcp
```

## Tools

### `log_water_intake`
Log water/beverage intake. Specify ml directly or use container type (glass, bottle, cup, etc.).

**Parameters:**
- `user_id` (str): User identifier
- `amount_ml` (float): Amount in millilitres (optional, defaults to container size or 250ml)
- `drink_type` (str): Type of beverage — affects effective hydration calculation (default: "water")
- `container` (str): Container type: glass, cup, bottle, small_bottle, large_bottle, mug, shot, sip, gulp

### `get_daily_hydration`
Get today's hydration summary with progress toward target.

**Parameters:**
- `user_id` (str): User identifier
- `target_ml` (float): Daily hydration target in ml (default: 2500)

### `calculate_target`
Calculate personalized daily hydration target based on weight, activity, and climate.

**Parameters:**
- `weight_kg` (float): Body weight in kilograms
- `activity_level` (str): One of: sedentary, light, moderate, active, very_active, athlete (default: "moderate")
- `climate` (str): One of: cold, temperate, warm, hot, humid, tropical (default: "temperate")

### `get_hydration_tips`
Get hydration tips and advice for specific situations.

**Parameters:**
- `situation` (str): One of: general, exercise, hot_weather, office, morning (default: "general")

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
