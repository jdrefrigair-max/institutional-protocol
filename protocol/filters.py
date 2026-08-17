"""Core three-filter engine + action decision."""

from config.settings import LAY_PRICE_THRESHOLD, MAX_QUALIFIERS, LIGHTLY_RACED_STARTS


def apply_filters(
    recent_form_ok: bool,
    wfa_ok: bool,
    bm_ok: bool,
    career_starts: int = 10,
    has_going_form: bool = True,
):
    rec = "Pass" if recent_form_ok else "Bord"
    wfa = "Pass" if wfa_ok else "Bord"
    bm = "Pass" if bm_ok else "Bord"
    is_clean = (rec == "Pass" and wfa == "Pass" and bm == "Pass")
    return rec, wfa, bm, is_clean


def decide_action(
    is_clean: bool,
    assessed: float,
    market: float,
    is_maiden: bool = False,
) -> str:
    if is_maiden:
        return "TRACK"
    if market < LAY_PRICE_THRESHOLD and not is_clean:
        return "LAY"
    if is_clean and assessed <= market:
        return "BACK"
    return "NO BET"


def apply_max_qualifiers_rule(actions: list) -> list:
    back_idxs = [i for i, a in enumerate(actions) if a == "BACK"]
    if len(back_idxs) > MAX_QUALIFIERS:
        for i in back_idxs:
            actions[i] = "NO BET"
    return actions