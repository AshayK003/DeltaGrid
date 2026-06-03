"""Sidebar: weight sliders and year selector."""

import streamlit as st

from src.config import DEFAULT_WEIGHTS, ENERGY_SHARE_COLS

WEIGHT_LABELS = {
    "solar_share_energy": "Solar",
    "wind_share_energy": "Wind",
    "hydro_share_energy": "Hydro",
    "nuclear_share_energy": "Nuclear",
    "gas_share_energy": "Gas",
    "coal_share_energy": "Coal",
}


def render_sidebar(year_range: tuple[int, int]) -> tuple[dict[str, float], int]:
    """Render sidebar with weight sliders and year selector.

    Returns:
        (weights dict, selected year)
    """
    st.sidebar.header("Configuration")

    # Year selector (fixed 2010–2025 range)
    selected_year = st.sidebar.slider(
        "Year",
        min_value=2010,
        max_value=2025,
        value=2022,
        step=1,
    )

    st.sidebar.divider()
    st.sidebar.subheader("Green Score Weights")

    weights: dict[str, float] = {}
    for col in ENERGY_SHARE_COLS:
        label = WEIGHT_LABELS.get(col, col)
        weights[col] = st.sidebar.slider(
            label,
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_WEIGHTS.get(col, 1.0),
            step=0.1,
            key=f"weight_{col}",
        )

    return weights, selected_year
