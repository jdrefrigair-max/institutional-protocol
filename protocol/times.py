"""Predicted time and vs-par calculations."""

TRACK_DATABASE = {
    "Scone": {"Pars": {1000: (57.5, 58.5), 1100: (64.0, 65.2), 1200: (70.5, 71.8), 1300: (76.8, 78.2), 1400: (83.5, 85.0), 1600: (96.5, 98.5), 1700: (103.0, 105.0)}},
    "Emerald": {"Pars": {1000: (57.0, 58.2), 1200: (70.0, 71.5), 1280: (75.5, 77.0), 1630: (99.0, 101.5)}},
    "Wyong": {"Pars": {1000: (56.8, 57.5), 1100: (63.0, 64.2), 1200: (69.5, 70.5), 1350: (79.0, 80.2), 1600: (96.5, 97.8)}},
    "Pakenham": {"Pars": {1000: (57.2, 58.0), 1100: (63.5, 64.5), 1200: (70.0, 71.2), 1400: (83.0, 84.5), 1600: (96.0, 97.8)}},
    "Newcastle": {"Pars": {900: (51.0, 51.8), 1200: (70.2, 71.0), 1300: (76.2, 77.2), 1400: (83.0, 84.1), 1600: (96.2, 97.4)}},
    "Kembla Grange": {"Pars": {1000: (56.4, 57.2), 1200: (69.5, 70.4), 1300: (76.0, 77.1), 1400: (82.3, 83.4), 1600: (95.0, 96.2)}},
    "Rosehill": {"Pars": {1100: (64.5, 65.5), 1200: (70.5, 71.5), 1400: (83.0, 84.2), 1500: (89.5, 90.8), 2000: (121.5, 123.5)}},
}

MOISTURE_OFFSETS = {
    "Good 3": 0.0, "Good 4": 0.2, "Soft 5": 0.80, "Soft 6": 1.10,
    "Soft 7": 1.50, "Heavy 8": 2.20, "Heavy 9": 2.90, "Heavy 10": 3.50, "Synthetic": 0.0,
}


def get_par(track: str, distance: int, going: str = "Good 4") -> float:
    track_data = TRACK_DATABASE.get(track, {})
    pars = track_data.get("Pars", {})
    if distance not in pars:
        available = sorted(pars.keys())
        if not available:
            return 0.0
        nearest = min(available, key=lambda x: abs(x - distance))
        base = sum(pars[nearest]) / 2
    else:
        base = sum(pars[distance]) / 2
    return round(base + MOISTURE_OFFSETS.get(going, 0.0), 2)


def calculate_vs_par(career_best_time, weight_delta, track, distance, going="Good 4", weight_factor=0.03):
    if career_best_time is None or career_best_time <= 0:
        return None
    par = get_par(track, distance, going)
    if par <= 0:
        return None
    adj = career_best_time + (weight_delta * weight_factor)
    return round(adj - par, 2)


def format_time(seconds: float) -> str:
    if seconds is None or seconds <= 0:
        return "—"
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:05.2f}"