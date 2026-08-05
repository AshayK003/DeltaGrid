"""Sidebar: weight sliders, year selector, and file upload."""

from __future__ import annotations

import streamlit as st

from src.config import (
    DEFAULT_SELECTED_YEAR_OFFSET,
    DEFAULT_WEIGHTS,
    ENERGY_SHARE_COLS,
    YEAR_MAX,
    YEAR_MIN,
)
from src.data.upload_preprocessor import preprocess_upload

# Readable labels for energy sources
WEIGHT_LABELS = {
    "solar_share_energy": "Solar",
    "wind_share_energy": "Wind",
    "hydro_share_energy": "Hydro",
    "nuclear_share_energy": "Nuclear",
    "gas_share_energy": "Gas",
    "coal_share_energy": "Coal",
}

# Grouping for visual hierarchy
_CLEAN_SOURCES = ["solar_share_energy", "wind_share_energy", "hydro_share_energy"]
_TRANSITION_SOURCES = ["nuclear_share_energy", "gas_share_energy", "coal_share_energy"]


def render_sidebar(year_range: tuple[int, int]) -> tuple[dict[str, float], int]:
    """Render sidebar with weight sliders and year selector.

    Returns:
        (weights dict, selected year)
    """
    st.sidebar.header("Configuration")

    # --- File upload with preprocessing ---
    st.sidebar.subheader("Upload Data")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your own energy dataset",
        type=["csv", "xlsx", "xls"],
        help="CSV or Excel file. Required: iso_code, year. "
             "Optional: country, solar_share_energy, etc.",
    )

    if uploaded_file is not None:
        # Only preprocess if this is a new file (different name/size)
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("_upload_key") != file_key:
            result = preprocess_upload(uploaded_file)
            st.session_state["_upload_key"] = file_key

            if result.errors:
                for err in result.errors:
                    st.sidebar.error(err)
                st.session_state.pop("uploaded_df", None)
            else:
                st.session_state["uploaded_df"] = result.df
                for warn in result.warnings:
                    st.sidebar.warning(warn)
                st.sidebar.success(
                    f"Loaded {uploaded_file.name} "
                    f"({len(result.df)} rows, "
                    f"{result.df['iso_code'].nunique()} countries)"
                )
        else:
            st.sidebar.success(
                f"Using {uploaded_file.name} "
                f"({len(st.session_state.get('uploaded_df', []))} rows)"
            )
    elif "uploaded_df" in st.session_state:
        st.sidebar.info("Using uploaded data.")
        if st.sidebar.button("Clear uploaded data", use_container_width=True):
            st.session_state.pop("uploaded_df", None)
            st.session_state.pop("_upload_key", None)
            st.rerun()

    st.sidebar.divider()

    # --- Year selector — uses actual data year range ---
    data_min_year, data_max_year = year_range
    min_year = max(YEAR_MIN, data_min_year)
    max_year = min(YEAR_MAX, data_max_year)
    default_year = max_year - DEFAULT_SELECTED_YEAR_OFFSET

    selected_year = st.sidebar.slider(
        "Year",
        min_value=min_year,
        max_value=max_year,
        value=default_year,
        step=1,
    )
    st.sidebar.caption(
        f"Year: **{selected_year}** (data range: {min_year}–{max_year})"
    )

    st.sidebar.divider()

    # Weight controls
    st.sidebar.subheader("Green Score Weights")
    st.sidebar.caption(
        "Adjust how each energy source contributes to the score. "
        "Higher weight = more influence."
    )

    # Clean sources group
    st.sidebar.markdown("**Clean Sources**")
    weights: dict[str, float] = {}
    for col in _CLEAN_SOURCES:
        label = WEIGHT_LABELS.get(col, col)
        weights[col] = st.sidebar.slider(
            label,
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_WEIGHTS.get(col, 1.0),
            step=0.1,
            key=f"weight_{col}",
        )

    st.sidebar.divider()

    # Transition sources group
    st.sidebar.markdown("**Transition Sources**")
    for col in _TRANSITION_SOURCES:
        label = WEIGHT_LABELS.get(col, col)
        weights[col] = st.sidebar.slider(
            label,
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_WEIGHTS.get(col, 1.0),
            step=0.1,
            key=f"weight_{col}",
        )

    # Weight summary
    active = {WEIGHT_LABELS.get(k, k): v for k, v in weights.items() if v > 0}
    if active:
        st.sidebar.caption(
            "Active weights: "
            + ", ".join(f"{k}={v:.1f}" for k, v in sorted(active.items()))
        )

    st.sidebar.divider()

    # Reset button — delete widget keys so sliders fall back to value= param
    if st.sidebar.button("Reset to Defaults", use_container_width=True):
        for col in ENERGY_SHARE_COLS:
            key = f"weight_{col}"
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.sidebar.markdown(
        """
        <div style="text-align:center;margin-top:24px;">
            <a href="https://chai4.me/ashaykushwaha003" target="_blank"
               title="Support on Chai4Me"
               style="display:inline-flex;flex-direction:column;align-items:center;
                      justify-content:center;background:#ffffff;padding:8px 32px;
                      border-radius:16px;text-decoration:none;border:1px solid #e5e7eb;
                      box-shadow:0 4px 6px -1px rgba(0,0,0,0.05),
                      0 2px 4px -2px rgba(0,0,0,0.05);">
                <img src="https://chai4.me/icons/wordmark.png" alt="Chai4Me"
                     style="height:32px;object-fit:contain;"/>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return weights, selected_year
