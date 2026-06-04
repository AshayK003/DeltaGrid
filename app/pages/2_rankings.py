"""Rankings page: tabs for laggards, hidden champions, all countries."""

import streamlit as st

from app.components.sidebar import render_sidebar
from app.components.tables import render_ranking_table
from app.components.ui import render_error_state, render_page_header
from app.pages._shared import cached_analysis, load_energy_data
from src.data.owid import get_owid_year_range
from src.models.ranking import (
    get_hidden_champions,
    get_laggards,
    get_rankings,
)

st.set_page_config(
    page_title="Rankings — DeltaGrid",
    page_icon="⚡",
    layout="wide",
)
render_page_header(
    "Country Rankings",
    "Explore country performance sorted by gap analysis results.",
)

with st.spinner("Loading energy data..."):
    energy_df = load_energy_data()
year_range = get_owid_year_range(energy_df)
weights, selected_year = render_sidebar(year_range)

try:
    result = cached_analysis(weights, selected_year, energy_df)
except Exception as e:
    render_error_state(
        title="Analysis failed",
        message=f"Could not complete analysis: {e}",
    )
    st.stop()

tab1, tab2, tab3 = st.tabs(
    ["All Countries", "Laggards", "Hidden Champions"]
)

with tab1:
    rankings = get_rankings(result.classified)
    render_ranking_table(
        rankings, f"All Countries ({selected_year})", max_rows=50
    )

with tab2:
    laggards = get_laggards(result.classified)
    render_ranking_table(
        laggards, f"Laggards ({selected_year})", max_rows=20
    )

with tab3:
    champions = get_hidden_champions(result.classified)
    render_ranking_table(
        champions,
        f"Hidden Champions ({selected_year})",
        max_rows=20,
    )
