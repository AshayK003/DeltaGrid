"""Rankings page: tabs for laggards, hidden champions, all countries."""

import streamlit as st

from app.components.sidebar import render_sidebar
from app.components.tables import render_ranking_table
from src.data.climate_watch import fetch_all_ndcs
from src.data.owid import get_owid_year_range, load_owid_data
from src.models.gap import compute_gap
from src.models.ranking import (
    classify_countries,
    get_hidden_champions,
    get_laggards,
    get_rankings,
)
from src.models.scoring import compute_green_score

st.set_page_config(page_title="Rankings — DeltaGrid", page_icon="🏆", layout="wide")
st.title("🏆 Country Rankings")

with st.spinner("Loading energy data..."):
    energy_df = load_owid_data()
year_range = get_owid_year_range(energy_df)
weights, selected_year = render_sidebar(year_range)

scored_df = compute_green_score(energy_df, weights)

# Fetch all NDCs in one call
with st.spinner("Fetching NDC pledges... this may take a moment on first load"):
    ndc_data = fetch_all_ndcs()

st.success(f"Loaded NDC data for {len(ndc_data)} countries")

gap_df = compute_gap(scored_df, ndc_data, selected_year)
year_df = gap_df[gap_df["year"] == selected_year].copy()
classified = classify_countries(year_df)

# Tabs
tab1, tab2, tab3 = st.tabs(["All Countries", "Laggards", "Hidden Champions"])

with tab1:
    rankings = get_rankings(classified)
    render_ranking_table(rankings, f"All Countries ({selected_year})", max_rows=50)

with tab2:
    laggards = get_laggards(classified)
    render_ranking_table(laggards, f"Laggards ({selected_year})", max_rows=20)

with tab3:
    champions = get_hidden_champions(classified)
    render_ranking_table(champions, f"Hidden Champions ({selected_year})", max_rows=20)
