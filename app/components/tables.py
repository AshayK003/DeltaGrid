"""Ranking tables with conditional formatting."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import COUNTRY_COL, ISO_COL, YEAR_COL

CLASS_COLORS = {
    "hidden_champion": "#00C853",
    "on_track": "#4CAF50",
    "slightly_behind": "#FFC107",
    "laggard": "#F44336",
    "no_data": "#9E9E9E",
}


def render_ranking_table(
    df: pd.DataFrame,
    title: str,
    max_rows: int = 20,
    show_gap: bool = True,
) -> None:
    """Render a styled ranking table.

    Args:
        df: DataFrame with iso_code, country, gap, classification.
        title: Table title.
        max_rows: Maximum rows to display.
        show_gap: Whether to show the gap column.
    """
    st.subheader(title)

    if df.empty:
        st.info("No data available")
        return

    display_cols = [ISO_COL, COUNTRY_COL]
    if YEAR_COL in df.columns:
        display_cols.append(YEAR_COL)
    if show_gap and "gap" in df.columns:
        display_cols.append("gap")
    if "green_score" in df.columns:
        display_cols.append("green_score")
    if "classification" in df.columns:
        display_cols.append("classification")

    existing = [c for c in display_cols if c in df.columns]
    table_df = df[existing].head(max_rows).copy()

    # Style the gap column
    if "gap" in table_df.columns:
        def color_gap(val):
            if val > 5:
                return f"color: {CLASS_COLORS['hidden_champion']}; font-weight: bold"
            elif val > 0:
                return f"color: {CLASS_COLORS['on_track']}"
            elif val > -5:
                return f"color: {CLASS_COLORS['slightly_behind']}"
            else:
                return f"color: {CLASS_COLORS['laggard']}; font-weight: bold"

        styled = table_df.style.applymap(color_gap, subset=["gap"])
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.dataframe(table_df, use_container_width=True, hide_index=True)


def render_classification_summary(df: pd.DataFrame) -> None:
    """Render summary counts by classification."""
    if "classification" not in df.columns:
        return

    counts = df["classification"].value_counts()
    cols = st.columns(len(CLASS_COLORS))

    for i, (cls, color) in enumerate(CLASS_COLORS.items()):
        with cols[i]:
            count = counts.get(cls, 0)
            st.metric(label=cls.replace("_", " ").title(), value=count)
