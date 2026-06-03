"""Gap Analysis page: dual choropleth (green score + gap) + stats."""

import streamlit as st

from app.components.choropleth import render_choropleth
from app.components.sidebar import render_sidebar
from app.components.tables import render_classification_summary
from src.data.climate_watch import fetch_all_ndcs
from src.data.owid import get_owid_year_range, load_owid_data
from src.models.gap import compute_gap
from src.models.ranking import classify_countries, get_laggards
from src.models.scoring import compute_green_score

st.set_page_config(
    page_title="Gap Analysis — DeltaGrid",
    page_icon="📊",
    layout="wide",
)
st.title("📊 Gap Analysis")

with st.spinner("Loading energy data..."):
    energy_df = load_owid_data()
year_range = get_owid_year_range(energy_df)
weights, selected_year = render_sidebar(year_range)

# Compute scores
scored_df = compute_green_score(energy_df, weights)

# Fetch all NDCs in one call
with st.spinner("Fetching NDC pledges... this may take a moment on first load"):
    ndc_data = fetch_all_ndcs()

st.success(f"Loaded NDC data for {len(ndc_data)} countries")

# Compute gap
gap_df = compute_gap(scored_df, ndc_data, selected_year)
year_gap = gap_df[gap_df["year"] == selected_year].copy()
classified = classify_countries(year_gap)

# Display
col1, col2 = st.columns(2)
with col1:
    render_choropleth(
        year_gap, "green_score",
        f"Green Score ({selected_year})",
        vmin=0, vmax=100,
    )
with col2:
    render_choropleth(
        year_gap, "gap",
        f"Gap ({selected_year})",
        color_scale="RdBu", vmin=-50, vmax=50,
    )

render_classification_summary(classified)

# Top laggards
laggards = get_laggards(classified)
if not laggards.empty:
    st.subheader("Top Laggards")
    cols = ["iso_code", "country", "green_score", "gap", "classification"]
    st.dataframe(
        laggards[cols].head(10),
        use_container_width=True,
    )
