"""Choropleth world map component using Plotly."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import ISO_COL


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
        st.warning(f"No data available for {title}")
        return

    plot_df = df.copy()
    if ISO_COL not in plot_df.columns:
        st.error(f"Missing {ISO_COL} column")
        return

    fig = px.choropleth(
        plot_df,
        locations=ISO_COL,
        color=color_col,
        hover_name="country" if "country" in plot_df.columns else ISO_COL,
        color_continuous_scale=color_scale,
        range_color=[vmin, vmax] if vmin is not None and vmax is not None else None,
        title=title,
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title=color_col.replace("_", " ").title()),
    )
    st.plotly_chart(fig, use_container_width=True)
