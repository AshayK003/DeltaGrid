"""Methodology page: scoring explanation and weight preview."""

import streamlit as st

from app.components.ui import render_page_header
from src.config import CLASS_COLORS, CLASS_LABELS, DEFAULT_WEIGHTS, ENERGY_SHARE_COLS

st.set_page_config(
    page_title="Methodology — DeltaGrid",
    page_icon="⚡",
    layout="wide",
)
render_page_header(
    "Methodology",
    "How the Green Score, Gap, and Classification are calculated.",
)

# --- Green Score ---
st.header("Green Score", anchor="green-score")
st.markdown("""
The **Green Score** (0-100) measures how clean a country's energy mix is.
It is computed as a weighted sum of energy share columns, normalized to 0-100:
""")

st.code(
    "green_score = (weight_i * share_i) / max(weight_i * share_i) * 100",
    language=None,
)

st.subheader("Energy Sources")
st.markdown("""
- **Solar** share of total energy
- **Wind** share of total energy
- **Hydro** share of total energy
- **Nuclear** share of total energy
- **Gas** share of total energy
- **Coal** share of total energy
""")

# --- Default Weights ---
st.header("Default Weights", anchor="default-weights")
col1, col2 = st.columns(2)
with col1:
    for col in ENERGY_SHARE_COLS:
        label = col.replace("_share_energy", "").title()
        weight = DEFAULT_WEIGHTS[col]
        st.markdown(f"**{label}**: {weight}")
with col2:
    st.info("Adjust weights in the sidebar to explore different scenarios.")

# --- Gap Analysis ---
st.header("Gap Analysis", anchor="gap-analysis")
st.markdown("""
The **Gap** is the difference between a country's actual Green Score
and the expected trajectory toward its NDC pledge:
""")

st.code("gap = actual_green_score - expected_trajectory", language=None)

st.markdown("""
The expected trajectory is a linear interpolation from the base year
to the target year, based on the NDC GHG reduction target.
""")

# --- Classification ---
st.header("Classification", anchor="classification")

# Render classification as badges instead of emoji dots
badge_html = ""
for cls_key, label in CLASS_LABELS.items():
    color = CLASS_COLORS[cls_key]
    badge_html += (
        f'<span style="display:inline-block;padding:4px 12px;'
        f'border-radius:16px;font-size:13px;font-weight:600;'
        f'margin:4px 8px 4px 0;'
        f'background:rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15);'
        f'color:{color};">{label}</span>'
    )

st.markdown(badge_html, unsafe_allow_html=True)

st.markdown("""
| Category | Gap Range |
|---|---|
| Hidden Champion | gap > 5 |
| On Track | 0 <= gap <= 5 |
| Slightly Behind | -5 <= gap < 0 |
| Laggard | gap < -5 |
""")

# --- Data Sources ---
st.header("Data Sources", anchor="data-sources")
st.markdown("""
- **Energy Data**:
  [Our World in Data](https://github.com/owid/energy-data) (OWID Energy Dataset)
- **NDC Pledges**:
  [Climate Watch Data](https://www.climatewatchdata.org/) (NDC API)
""")
