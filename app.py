"""
Institutional AI Form Analyst & Edge Protocol
Streamlit MVP – 110% assessed book + strict 3-filter gate + Betfair
"""

import streamlit as st
import pandas as pd
from protocol.filters import apply_filters, decide_action, apply_max_qualifiers_rule
from protocol.pricing import build_assessed_book, edge_pct
from protocol.times import get_par, calculate_vs_par, format_time
from config.settings import ASSESSED_BOOK_PCT, MAX_QUALIFIERS

st.set_page_config(
    page_title="Institutional Protocol",
    page_icon="🏇",
    layout="wide",
)

st.title("🏇 Institutional AI Form Analyst & Edge Protocol")
st.caption(f"Assessed book target: {int(ASSESSED_BOOK_PCT*100)}%  |  Must pass all 3 filters to BACK  |  Max {MAX_QUALIFIERS} qualifiers")

with st.sidebar:
    st.header("Race Setup")
    track = st.selectbox("Track", ["Scone", "Emerald", "Wyong", "Pakenham", "Newcastle", "Kembla Grange", "Rosehill"])
    distance = st.number_input("Distance (m)", min_value=900, max_value=3200, value=1300, step=50)
    going = st.selectbox("Going", ["Good 3", "Good 4", "Soft 5", "Soft 6", "Soft 7", "Heavy 8", "Synthetic"])
    race_class = st.selectbox("Class", ["Maiden", "BM50", "BM55", "BM58", "BM60", "BM64", "BM66", "BM72", "CL1", "CL2", "CL3", "CL4", "Open"])
    is_maiden = race_class == "Maiden"
    par = get_par(track, distance, going)
    st.metric("Race Par", format_time(par) if par else "—")

    st.markdown("---")
    st.subheader("Betfair")
    if st.button("Load AU Horse Markets"):
        try:
            from protocol.betfair_client import get_client, get_aus_horse_markets
            client = get_client()
            markets = get_aus_horse_markets(client)
            st.session_state["bf_markets"] = markets
            st.success(f"Loaded {len(markets)} markets")
        except Exception as e:
            st.error(f"Betfair error: {e}")

    if "bf_markets" in st.session_state:
        market_options = {
            f"{m['venue']} | {m['market_name']} | {m['start_time'][:16]}": m
            for m in st.session_state["bf_markets"]
        }
        chosen = st.selectbox("Select market", list(market_options.keys()))
        if chosen:
            st.session_state["selected_market"] = market_options[chosen]

st.subheader(f"{track} | {distance}m | {going} | {race_class}")
st.markdown(f"**Par: {format_time(par)}**")

demo = pd.DataFrame({
    "No": [1, 2, 3, 4, 5],
    "Horse": ["Pride Of Savabella", "Bitof theblarney", "Varune", "Ready And Lucky", "Ellibaby"],
    "Weight": [58.0, 57.5, 59.0, 58.0, 56.5],
    "Career Starts": [12, 8, 15, 6, 9],
    "Recent Form OK": [True, True, True, True, True],
    "WFA OK": [True, True, True, True, True],
    "BM OK": [True, True, False, True, False],
    "Career Best (s)": [78.2, 78.5, 79.4, 77.9, 79.1],
    "Weight Delta": [0.0, -1.0, 1.5, 0.0, -0.5],
    "Market": [3.80, 4.20, 2.80, 3.40, 1.85],
    "Raw Prob": [0.22, 0.19, 0.28, 0.24, 0.35],
})

edited = st.data_editor(demo, num_rows="dynamic", use_container_width=True, key="field")

if st.button("▶ Run Institutional Protocol", type="primary"):
    raw = dict(zip(edited["Horse"], edited["Raw Prob"]))
    assessed_map = build_assessed_book(raw)

    rows = []
    actions = []
    for _, r in edited.iterrows():
        rec, wfa, bm, is_clean = apply_filters(
            r["Recent Form OK"], r["WFA OK"], r["BM OK"], int(r["Career Starts"])
        )
        assessed = assessed_map.get(r["Horse"], 99.0)
        market = float(r["Market"])
        vs = calculate_vs_par(r["Career Best (s)"], r["Weight Delta"], track, distance, going)
        action = decide_action(is_clean, assessed, market, is_maiden)
        actions.append(action)

        rows.append({
            "No": r["No"],
            "Horse": r["Horse"],
            "Wgt": r["Weight"],
            "vs Par": vs if vs is not None else "—",
            "Assessed": assessed,
            "Market": market,
            "Edge %": edge_pct(assessed, market),
            "Filters": f"{rec}/{wfa}/{bm}",
            "Action": action,
        })

    actions = apply_max_qualifiers_rule(actions)
    for i, a in enumerate(actions):
        rows[i]["Action"] = a

    result = pd.DataFrame(rows)

    def colour_vs(val):
        if isinstance(val, (int, float)):
            if val < 0: return "color: #0a7a0a; font-weight: 600"
            if val > 0: return "color: #b00000; font-weight: 600"
        return ""

    def colour_action(val):
        if val == "BACK": return "background-color: #d4edda; font-weight: 700"
        if val == "LAY": return "background-color: #f8d7da; font-weight: 700"
        if val == "TRACK": return "background-color: #fff3cd"
        return ""

    st.markdown("---")
    st.subheader("Protocol Output")
    styled = (
        result.style
        .map(colour_vs, subset=["vs Par"])
        .map(colour_action, subset=["Action"])
        .format({"Assessed": "{:.2f}", "Market": "{:.2f}", "Edge %": "{:+.1f}"})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    backs = result[result["Action"] == "BACK"]
    lays = result[result["Action"] == "LAY"]

    st.markdown("### Plays Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**BACKS**")
        if backs.empty: st.write("None")
        else:
            for _, b in backs.iterrows():
                st.success(f"{b['Horse']} @ {b['Market']:.2f} (Assessed {b['Assessed']:.2f})")
    with col2:
        st.markdown("**LAYS**")
        if lays.empty: st.write("None")
        else:
            for _, l in lays.iterrows():
                st.error(f"{l['Horse']} @ {l['Market']:.2f}")

st.markdown("---")
st.caption("Institutional Protocol • 110% assessed book • Strict 3-filter gate • Max 2 qualifiers")