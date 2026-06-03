"""Methodology page: scoring explanation and weight preview."""

import streamlit as st

from src.config import DEFAULT_WEIGHTS, ENERGY_SHARE_COLS

st.set_page_config(page_title="Methodology — DeltaGrid", page_icon="📐", layout="wide")
st.title("📐 Methodology")

st.header("Green Score")
st.markdown("""
The **Green Score** (0–100) measures how clean a country's energy mix is.
It is computed as a weighted sum of energy share columns, normalized to 0–100:

```
green_score = Σ(weight_i × share_i) / max(Σ(weight_i × share_i)) × 100
```

**Energy Sources:**
- Solar share of total energy
- Wind share of total energy
- Hydro share of total energy
- Nuclear share of total energy
- Gas share of total energy
- Coal share of total energy
""")

st.header("Default Weights")
col1, col2 = st.columns(2)
with col1:
    for col in ENERGY_SHARE_COLS:
        label = col.replace("_share_energy", "").title()
        st.write(f"**{label}**: {DEFAULT_WEIGHTS[col]}")
with col2:
    st.info("Adjust weights in the sidebar to explore different scenarios.")

st.header("Gap Analysis")
st.markdown("""
The **Gap** is the difference between a country's actual Green Score
and the expected trajectory toward its NDC pledge:

```
gap = actual_green_score - expected_trajectory
```

The expected trajectory is a linear interpolation from the base year
to the target year, based on the NDC GHG reduction target.
""")

st.header("Classification")
st.markdown("""
| Category | Gap Range |
|---|---|
| 🟢 Hidden Champion | gap > 5 |
| 🟢 On Track | 0 ≤ gap ≤ 5 |
| 🟡 Slightly Behind | -5 ≤ gap < 0 |
| 🔴 Laggard | gap < -5 |
""")

st.header("Data Sources")
st.markdown("""
- **Energy Data**:
  [Our World in Data](https://github.com/owid/energy-data) (OWID Energy Dataset)
- **NDC Pledges**:
  [Climate Watch Data](https://www.climatewatchdata.org/) (NDC API)
""")
