"""110% assessed book construction."""

from config.settings import ASSESSED_BOOK_PCT


def build_assessed_book(raw_probs: dict) -> dict:
    total = sum(raw_probs.values())
    if total <= 0:
        return {h: 99.0 for h in raw_probs}

    scale = ASSESSED_BOOK_PCT / total
    assessed = {}
    for horse, p in raw_probs.items():
        adj_p = max(p * scale, 0.01)
        assessed[horse] = round(1.0 / adj_p, 2)
    return assessed


def edge_pct(assessed: float, market: float) -> float:
    if assessed <= 0 or market <= 0:
        return 0.0
    return round(((market / assessed) - 1.0) * 100, 1)