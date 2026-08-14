"""
Institutional Protocol Engine

Takes a race (list of runners + market prices) and applies the full protocol.
"""

from typing import Dict, Any
from .filters import evaluate_runner
from config.settings import MAX_QUALIFIERS_PER_RACE, LAY_PRICE_THRESHOLD, MIN_OVERLAY_PCT


def determine_action(runner_result: Dict[str, Any], market_price: float, assessed_price: float) -> str:
    """
    Decide BACK / LAY / Value Lay / Veto for a single runner.
    """
    is_qualifier = runner_result["is_qualifier"]
    under_threshold = market_price < LAY_PRICE_THRESHOLD

    if under_threshold and not is_qualifier:
        return "LAY"
    if under_threshold and is_qualifier:
        return "Value Lay"
    if is_qualifier:
        if market_price >= assessed_price * (1 + MIN_OVERLAY_PCT):
            return "BACK"
        return "Veto"  # Qualifier but insufficient overlay
    return "Veto"


def run_protocol(race: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point.

    race = {
        "track": str,
        "race_number": int,
        "distance": int,
        "condition": str,          # e.g. "Good 4", "Soft 5"
        "runners": [ {name, market_price, ...form fields...}, ... ]
    }
    """
    condition = race.get("condition", "Good")
    results = []
    qualifiers = []

    for runner in race.get("runners", []):
        evaluation = evaluate_runner(runner, track_condition=condition)

        base_assessed = runner.get("raw_assessed", runner.get("market_price", 10.0) * 1.2)
        assessed_price = base_assessed * evaluation["assessed_multiplier"]

        action = determine_action(evaluation, runner.get("market_price", 99.0), assessed_price)

        row = {
            **runner,
            **evaluation,
            "assessed_price": round(assessed_price, 2),
            "action": action,
        }
        results.append(row)

        if evaluation["is_qualifier"]:
            qualifiers.append(runner.get("name"))

    if len(qualifiers) > MAX_QUALIFIERS_PER_RACE:
        race_status = "SKIP"
        for r in results:
            if r["action"] in ("BACK", "Value Lay"):
                r["action"] = "Veto (Race Skipped)"
    else:
        race_status = "LIVE"

    return {
        "track": race.get("track"),
        "race_number": race.get("race_number"),
        "status": race_status,
        "qualifier_count": len(qualifiers),
        "qualifiers": qualifiers,
        "runners": results,
    }
