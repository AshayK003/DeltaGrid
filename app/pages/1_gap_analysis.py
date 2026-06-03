"""Gap Analysis page: dual choropleth (green score + gap) + stats."""

import streamlit as st

from app.components.choropleth import render_choropleth
from app.components.sidebar import render_sidebar
from app.components.tables import render_classification_summary
from app.pages.shared import cached_analysis
from src.data.owid import get_owid_year_range, load_owid_data
from src.models.ranking import get_laggards

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

result = cached_analysis(weights, selected_year, energy_df)

st.success(f"Loaded NDC data for {result.ndc_count} countries")

col1, col2 = st.columns(2)
with col1:
    render_choropleth(
        result.classified, "green_score",
        f"Green Score ({selected_year})",
        vmin=0, vmax=100,
    )
with col2:
    render_choropleth(
        result.classified, "gap",
        f"Gap ({selected_year})",
        color_scale="RdBu", vmin=-50, vmax=50,
    )

render_classification_summary(result.classified)

laggards = get_laggards(result.classified)
if not laggards.empty:
    st.subheader("Top Laggards")
    cols = ["iso_code", "country", "green_score", "gap", "classification"]
    st.dataframe(
        laggards[cols].head(10),
        use_container_width=True,
    )
