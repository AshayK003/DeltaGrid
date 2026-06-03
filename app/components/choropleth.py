"""Choropleth world map component using Plotly."""

from __future__ import annotations

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.ui import (
    render_country_count,
    render_empty_state,
    render_error_state,
)
from src.config import ISO_COL

logger = logging.getLogger(__name__)

# Readable labels for color bars
_COLOR_BAR_LABELS = {
    "green_score": "Green Score",
    "gap": "Gap",
    "expected_trajectory": "Expected Trajectory",
}


def render_choropleth(
    df: pd.DataFrame,
    color_col: str,
    title: str,
    color_scale: str = "RdYlGn",
    vmin: float | None = None,
    vmax: float | None = None,
) -> None:
    """Render a choropleth world map.

    Args:
        df: DataFrame with iso_code, year, and color_col.
        color_col: Column to color by (e.g., 'green_score' or 'gap').
        title: Map title.
        color_scale: Plotly color scale name.
        vmin: Minimum color value.
        vmax: Maximum color value.
    """
    if df.empty:
        render_empty_state(
            title="No data to display",
            message="No country data available for the selected filters.",
        )
        return

    if ISO_COL not in df.columns:
        render_empty_state(
            title="Missing data",
            message=f"Required column '{ISO_COL}' not found in dataset.",
        )
        return

    try:
        plot_df = df.copy()

        fig = px.choropleth(
            plot_df,
            locations=ISO_COL,
            color=color_col,
            hover_name="country" if "country" in plot_df.columns else ISO_COL,
            color_continuous_scale=color_scale,
            range_color=[vmin, vmax] if vmin is not None and vmax is not None else None,
        )

        color_bar_label = _COLOR_BAR_LABELS.get(
            color_col, color_col.replace("_", " ").title()
        )

        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, color="#E0E0E0"),
                x=0.01,
                xanchor="left",
            ),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type="natural earth",
                bgcolor="#0E1117",
                landcolor="#1A1F2E",
                showlakes=False,
            ),
            margin=dict(l=0, r=0, t=44, b=0),
            coloraxis_colorbar=dict(title=color_bar_label),
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            height=500,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
            },
        )

        render_country_count(len(plot_df))

    except Exception as e:
        logger.error("Choropleth render error: %s", e)
        render_error_state(
            title="Map rendering failed",
            message=f"Could not render the map: {e}",
        )
