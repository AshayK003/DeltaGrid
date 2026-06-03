"""DeltaGrid — Paris Agreement NDC vs energy trajectory gap analysis."""

import streamlit as st

from app.components.choropleth import render_choropleth
from app.components.sidebar import render_sidebar
from app.components.tables import render_classification_summary
from src.data.owid import get_owid_year_range, load_owid_data
from src.data.validators import validate_energy_data
from src.models.scoring import compute_green_score

st.set_page_config(
    page_title="DeltaGrid",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 DeltaGrid")
st.caption("Paris Agreement NDC pledges vs actual energy trajectory gap analysis")

# Load data
with st.spinner("Loading energy data..."):
    energy_df = load_owid_data()

year_range = get_owid_year_range(energy_df)
weights, selected_year = render_sidebar(year_range)

# Validate
errors = validate_energy_data(energy_df)
if errors:
    st.error("Data validation errors: " + "; ".join(errors))
    st.stop()

# Compute green scores
progress = st.progress(0, text="Computing green scores...")
scored_df = compute_green_score(energy_df, weights)
progress.progress(50, text="Filtering by year...")
year_df = scored_df[scored_df["year"] == selected_year].copy()
progress.progress(100, text="Done!")
progress.empty()

# Fetch NDCs for visible countries
st.subheader(f"Green Score — {selected_year}")
render_choropleth(
    year_df, "green_score",
    f"Green Score ({selected_year})",
    vmin=0, vmax=100,
)

# Summary stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Countries", len(year_df))
with col2:
    avg_score = year_df["green_score"].mean()
    st.metric("Avg Green Score", f"{avg_score:.1f}")
with col3:
    st.metric("Year", selected_year)

# Classification summary
render_classification_summary(year_df)

# Footer
st.divider()
st.caption("Data: OWID Energy + Climate Watch NDC | Built with Streamlit")
