"""
Assessed Price calculation.

Placeholder for now – will evolve into a proper model using:
- Form strength
- BM fit
- Going evidence
- Market shape
"""

from typing import Dict, Any
from config.settings import NO_GOING_EVIDENCE_MULTIPLIER


def calculate_assessed_price(runner: Dict[str, Any], base_price: float) -> float:
    """
    Returns an assessed fair price.

    Higher price = more conservative (needs bigger overlay to BACK).
    """
    price = base_price

    if not runner.get("has_runs_on_going", False):
        price *= NO_GOING_EVIDENCE_MULTIPLIER

    if not runner.get("distance_proven", False):
        price *= 1.08

    return round(price, 2)
