"""Sidebar: weight sliders and year selector with grouped controls."""

from __future__ import annotations

import streamlit as st

from src.config import DEFAULT_WEIGHTS, ENERGY_SHARE_COLS, YEAR_MAX, YEAR_MIN

# Readable labels for energy sources
WEIGHT_LABELS = {
    "solar_share_energy": "Solar",
    "wind_share_energy": "Wind",
    "hydro_share_energy": "Hydro",
    "nuclear_share_energy": "Nuclear",
    "gas_share_energy": "Gas",
    "coal_share_energy": "Coal",
}

# Grouping for visual hierarchy
_CLEAN_SOURCES = ["solar_share_energy", "wind_share_energy", "hydro_share_energy"]
_TRANSITION_SOURCES = ["nuclear_share_energy", "gas_share_energy", "coal_share_energy"]


def render_sidebar(year_range: tuple[int, int]) -> tuple[dict[str, float], int]:
    """Render sidebar with weight sliders and year selector.

    Returns:
        (weights dict, selected year)
    """
    st.sidebar.header("Configuration")

    # Year selector — prominent display
    selected_year = st.sidebar.slider(
        "Year",
        min_value=YEAR_MIN,
        max_value=YEAR_MAX,
        value=min(YEAR_MAX, 2022),
        step=1,
    )
    st.sidebar.caption(
        f"Selected: **{selected_year}** — Year for gap analysis"
    )

    st.sidebar.divider()

    # Weight controls
    st.sidebar.subheader("Green Score Weights")
    st.sidebar.caption(
        "Adjust how each energy source contributes to the score. "
        "Higher weight = more influence."
    )

    # Clean sources group
    st.sidebar.markdown("**Clean Sources**")
    weights: dict[str, float] = {}
    for col in _CLEAN_SOURCES:
        label = WEIGHT_LABELS.get(col, col)
        weights[col] = st.sidebar.slider(
            label,
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_WEIGHTS.get(col, 1.0),
            step=0.1,
            key=f"weight_{col}",
        )

    st.sidebar.divider()

    # Transition sources group
    st.sidebar.markdown("**Transition Sources**")
    for col in _TRANSITION_SOURCES:
        label = WEIGHT_LABELS.get(col, col)
        weights[col] = st.sidebar.slider(
            label,
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_WEIGHTS.get(col, 1.0),
            step=0.1,
            key=f"weight_{col}",
        )

    st.sidebar.divider()

    # Reset button
    if st.sidebar.button("Reset to Defaults", use_container_width=True):
        for col in ENERGY_SHARE_COLS:
            st.session_state[f"weight_{col}"] = DEFAULT_WEIGHTS.get(col, 1.0)
        st.rerun()

    return weights, selected_year
