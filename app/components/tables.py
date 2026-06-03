"""Ranking tables with conditional formatting."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.ui import render_empty_state
from src.config import CLASS_COLORS, CLASS_LABELS, COUNTRY_COL, ISO_COL, YEAR_COL


def _format_gap(val: float) -> str:
    """Format gap value with +/- sign."""
    if pd.isna(val):
        return ""
    return f"+{val:.1f}" if val >= 0 else f"{val:.1f}"


def _format_score(val: float) -> str:
    """Format green score to 1 decimal."""
    if pd.isna(val):
        return ""
    return f"{val:.1f}"


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
        render_empty_state(
            title="No countries match",
            message="Try adjusting your filters or weights.",
        )
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
    total = len(df)
    table_df = df[existing].head(max_rows).copy()

    # Map raw classification keys to readable labels
    if "classification" in table_df.columns:
        table_df["classification"] = (
            table_df["classification"]
            .map(CLASS_LABELS)
            .fillna(table_df["classification"])
        )

    # Format numbers
    if "gap" in table_df.columns:
        table_df["gap"] = table_df["gap"].map(_format_gap)
    if "green_score" in table_df.columns:
        table_df["green_score"] = table_df["green_score"].map(_format_score)

    # Rename columns for display
    rename_map = {
        ISO_COL: "ISO",
        COUNTRY_COL: "Country",
        YEAR_COL: "Year",
        "gap": "Gap",
        "green_score": "Green Score",
        "classification": "Status",
    }
    table_df = table_df.rename(columns=rename_map)

    # Row count indicator
    showing = min(max_rows, total)
    if total > max_rows:
        st.caption(f"Showing {showing} of {total} countries")
    else:
        st.caption(f"{total} countries")

    st.dataframe(table_df, use_container_width=True, hide_index=True)


def render_classification_summary(df: pd.DataFrame) -> None:
    """Render summary counts by classification with badges."""
    if "classification" not in df.columns:
        return

    counts = df["classification"].value_counts()
    # Only show classes that actually appear in the data
    present = [cls for cls in CLASS_COLORS if cls in counts.index]
    if not present:
        return

    cols = st.columns(len(present))
    for i, cls in enumerate(present):
        with cols[i]:
            count = counts[cls]
            label = CLASS_LABELS.get(cls, cls.replace("_", " ").title())
            st.metric(label=label, value=count)
