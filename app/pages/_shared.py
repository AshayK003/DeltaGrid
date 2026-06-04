"""Shared page utilities for Streamlit pages."""

import pandas as pd
import streamlit as st

from src.data.owid import load_owid_data
from src.pipeline import AnalysisResult, run_analysis


def load_energy_data() -> pd.DataFrame:
    """Load energy data from uploaded file or OWID default."""
    if "uploaded_df" in st.session_state:
        return st.session_state["uploaded_df"]
    return load_owid_data()


def cached_analysis(
    weights: dict[str, float],
    selected_year: int,
    energy_df,
) -> AnalysisResult:
    """Run analysis with Streamlit memoization.

    Weights dict is converted to a sorted tuple for hashing.
    """
    weights_key = tuple(sorted(weights.items()))
    return _run(weights_key, selected_year, energy_df)


@st.cache_data(show_spinner="Running analysis...", hash_funcs={tuple: lambda x: x})
def _run(weights_key, selected_year: int, energy_df) -> AnalysisResult:
    weights = dict(weights_key)
    return run_analysis(weights, selected_year, energy_df=energy_df)
