#!/usr/bin/env python3
"""Hydration tracking, reminders, and daily water intake analysis — MEOK AI Labs."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
import math
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)


def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now - t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT:
        return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now)
    return None


# In-memory hydration log keyed by user
_hydration_log = defaultdict(list)

# Common drink volumes in ml
_DRINK_VOLUMES = {
    "glass": 250,
    "cup": 240,
    "bottle": 500,
    "small_bottle": 330,
    "large_bottle": 750,
    "mug": 350,
    "shot": 30,
    "sip": 30,
    "gulp": 60,
}

# Hydration multipliers for beverages (how much counts as water)
_BEVERAGE_FACTORS = {
    "water": 1.0,
    "sparkling water": 1.0,
    "herbal tea": 0.95,
    "green tea": 0.90,
    "black tea": 0.85,
    "coffee": 0.80,
    "juice": 0.85,
    "milk": 0.87,
    "sports drink": 0.90,
    "soda": 0.70,
    "beer": 0.40,
    "wine": 0.30,
    "energy drink": 0.60,
    "smoothie": 0.80,
    "coconut water": 0.95,
}


mcp = FastMCP("hydration-reminder-ai-mcp", instructions="Hydration tracking and reminders by MEOK AI Labs.")


@mcp.tool(name="log_water_intake")
async def log_water_intake(user_id: str, amount_ml: float = None, drink_type: str = "water", container: str = "", api_key: str = "") -> dict:
    """Log water/beverage intake. Specify ml directly or use container type (glass, bottle, cup, etc.)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    # Determine amount
    if amount_ml is None:
        if container.lower().strip() in _DRINK_VOLUMES:
            amount_ml = _DRINK_VOLUMES[container.lower().strip()]
        else:
            amount_ml = 250  # Default glass

    if amount_ml <= 0 or amount_ml > 5000:
        return {"error": "Amount must be between 1 and 5000 ml."}

    # Calculate effective hydration
    drink_key = drink_type.lower().strip()
    factor = _BEVERAGE_FACTORS.get(drink_key, 0.85)
    effective_ml = round(amount_ml * factor, 1)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "amount_ml": amount_ml,
        "drink_type": drink_type,
        "effective_hydration_ml": effective_ml,
        "hydration_factor": factor,
    }
    _hydration_log[user_id].append(entry)

    # Today's running total
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_entries = [e for e in _hydration_log[user_id] if e["timestamp"].startswith(today)]
    daily_total = round(sum(e["effective_hydration_ml"] for e in today_entries), 1)
    daily_raw = round(sum(e["amount_ml"] for e in today_entries), 1)

    return {
        "status": "logged",
        "amount_ml": amount_ml,
        "drink_type": drink_type,
        "effective_hydration_ml": effective_ml,
        "hydration_factor": factor,
        "daily_total_ml": daily_raw,
        "daily_effective_ml": daily_total,
        "entries_today": len(today_entries),
        "timestamp": entry["timestamp"],
    }


@mcp.tool(name="get_daily_hydration")
async def get_daily_hydration(user_id: str, target_ml: float = 2500, api_key: str = "") -> dict:
    """Get today's hydration summary with progress toward target."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries = [e for e in _hydration_log.get(user_id, []) if e["timestamp"].startswith(today)]

    total_ml = round(sum(e["amount_ml"] for e in entries), 1)
    effective_ml = round(sum(e["effective_hydration_ml"] for e in entries), 1)

    # Breakdown by drink type
    by_type = defaultdict(lambda: {"amount_ml": 0, "effective_ml": 0, "count": 0})
    for e in entries:
        dt = e["drink_type"]
        by_type[dt]["amount_ml"] += e["amount_ml"]
        by_type[dt]["effective_ml"] += e["effective_hydration_ml"]
        by_type[dt]["count"] += 1

    for v in by_type.values():
        v["amount_ml"] = round(v["amount_ml"], 1)
        v["effective_ml"] = round(v["effective_ml"], 1)

    progress_pct = round(effective_ml / max(target_ml, 1) * 100, 1)
    remaining = max(0, round(target_ml - effective_ml, 1))
    glasses_remaining = math.ceil(remaining / 250) if remaining > 0 else 0

    # Hourly distribution
    hourly = defaultdict(float)
    for e in entries:
        hour = e["timestamp"][11:13]
        hourly[hour] += e["effective_hydration_ml"]

    if progress_pct >= 100:
        status = "target_reached"
        message = "Great job! You've reached your hydration target."
    elif progress_pct >= 75:
        status = "almost_there"
        message = f"Almost there! {glasses_remaining} more glasses to go."
    elif progress_pct >= 50:
        status = "on_track"
        message = f"Halfway there. Drink {glasses_remaining} more glasses."
    elif progress_pct >= 25:
        status = "behind"
        message = f"You're behind on hydration. Try to drink {glasses_remaining} more glasses."
    else:
        status = "low"
        message = f"Hydration is low. You need about {glasses_remaining} glasses to reach your target."

    return {
        "user_id": user_id,
        "date": today,
        "total_intake_ml": total_ml,
        "effective_hydration_ml": effective_ml,
        "target_ml": target_ml,
        "progress_percent": progress_pct,
        "remaining_ml": remaining,
        "glasses_remaining": glasses_remaining,
        "status": status,
        "message": message,
        "entries": len(entries),
        "by_drink_type": dict(by_type),
        "hourly_distribution": {k: round(v, 1) for k, v in sorted(hourly.items())},
    }


@mcp.tool(name="calculate_target")
async def calculate_target(weight_kg: float, activity_level: str = "moderate", climate: str = "temperate", api_key: str = "") -> dict:
    """Calculate personalized daily hydration target based on weight, activity, and climate."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    if weight_kg <= 0 or weight_kg > 500:
        return {"error": "Weight must be between 1 and 500 kg."}

    # Base: 33ml per kg
    base_ml = weight_kg * 33

    activity_mult = {
        "sedentary": 0.9,
        "light": 1.0,
        "moderate": 1.15,
        "active": 1.3,
        "very_active": 1.5,
        "athlete": 1.7,
    }
    climate_mult = {
        "cold": 0.9,
        "temperate": 1.0,
        "warm": 1.15,
        "hot": 1.3,
        "humid": 1.35,
        "tropical": 1.4,
    }

    act_m = activity_mult.get(activity_level.lower().strip(), 1.15)
    clm_m = climate_mult.get(climate.lower().strip(), 1.0)

    target_ml = round(base_ml * act_m * clm_m)
    target_litres = round(target_ml / 1000, 2)
    glasses = math.ceil(target_ml / 250)

    # Build schedule (assuming 16-hour waking period)
    interval_mins = round(16 * 60 / glasses)
    per_glass_ml = round(target_ml / glasses)
    schedule = []
    start_hour = 7
    for i in range(glasses):
        total_mins = start_hour * 60 + i * interval_mins
        h = (total_mins // 60) % 24
        m = total_mins % 60
        schedule.append({"time": f"{h:02d}:{m:02d}", "amount_ml": per_glass_ml, "glass_number": i + 1})

    return {
        "weight_kg": weight_kg,
        "activity_level": activity_level,
        "climate": climate,
        "daily_target_ml": target_ml,
        "daily_target_litres": target_litres,
        "glasses_of_250ml": glasses,
        "base_ml": round(base_ml),
        "activity_multiplier": act_m,
        "climate_multiplier": clm_m,
        "suggested_schedule": schedule,
        "tip": "Drink before you feel thirsty. Spread intake evenly throughout the day.",
    }


@mcp.tool(name="get_hydration_tips")
async def get_hydration_tips(situation: str = "general", api_key: str = "") -> dict:
    """Get hydration tips and advice for specific situations."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    tips_db = {
        "general": {
            "tips": ["Carry a reusable water bottle everywhere.", "Set reminders every 30-60 minutes.", "Drink water first thing in the morning.", "Eat water-rich foods like cucumbers and watermelon.", "Track intake to build awareness.", "Drink a glass before each meal."],
            "quick_facts": ["The body is approximately 60% water.", "Even mild dehydration (1-2%) impairs cognition.", "Thirst is already a sign of dehydration."],
        },
        "exercise": {
            "tips": ["Drink 500ml 2 hours before exercise.", "During exercise, 150-250ml every 15-20 min.", "After: 500-700ml per 0.5kg lost in sweat.", "Sessions over 60 min: consider electrolytes.", "Pale yellow urine = good hydration."],
            "quick_facts": ["Sweat rates: 0.5-2.5 litres/hour.", "2% body weight loss from dehydration cuts performance 25%."],
        },
        "hot_weather": {
            "tips": ["Increase intake 500-1000ml on hot days.", "Drink before going out in heat.", "Avoid alcohol and caffeine in extreme heat.", "Eat cold fruits for hydration boost.", "Watch for heat exhaustion: headache, dizziness, nausea."],
            "quick_facts": ["In extreme heat, body can lose 2L sweat/hour.", "Heat stroke is a medical emergency."],
        },
        "office": {
            "tips": ["Keep a water bottle on your desk.", "Drink water every break.", "Use a marked bottle to track progress.", "AC increases dehydration.", "Replace afternoon coffee with herbal tea."],
            "quick_facts": ["Office workers often mistake thirst for hunger.", "Dehydration causes fatigue and poor concentration."],
        },
        "morning": {
            "tips": ["Drink 500ml within 30 min of waking.", "Add lemon for flavor and vitamin C.", "Drink water before coffee.", "Body loses 200-400ml during sleep."],
            "quick_facts": ["Morning hydration kickstarts metabolism.", "Most people wake mildly dehydrated."],
        },
    }

    situation_key = situation.lower().strip()
    if situation_key not in tips_db:
        closest = "general"
        for key in tips_db:
            if key in situation_key or situation_key in key:
                closest = key
                break
        situation_key = closest

    data = tips_db[situation_key]
    available_containers = [{"name": name, "ml": vol} for name, vol in sorted(_DRINK_VOLUMES.items(), key=lambda x: x[1])]

    return {
        "situation": situation_key,
        "tips": data["tips"],
        "quick_facts": data["quick_facts"],
        "available_situations": list(tips_db.keys()),
        "common_containers": available_containers,
        "beverage_hydration_factors": _BEVERAGE_FACTORS,
    }


if __name__ == "__main__":
    mcp.run()
