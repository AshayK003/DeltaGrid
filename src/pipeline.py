"""Analysis pipeline: orchestrates data loading, scoring, gap, classification."""

import logging
from dataclasses import dataclass

import pandas as pd

from src.data.climate_watch import fetch_all_ndcs
from src.data.owid import load_owid_data
from src.models.gap import compute_gap
from src.models.ranking import classify_countries
from src.models.scoring import compute_green_score

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Container for analysis pipeline output."""

    classified: pd.DataFrame
    selected_year: int


def run_analysis(
    weights: dict[str, float],
    selected_year: int,
    energy_df: pd.DataFrame | None = None,
) -> AnalysisResult:
    """Run the full analysis pipeline.

    Steps: load OWID → score → fetch NDCs → gap → classify.

    Optionally accepts a pre-loaded energy_df to avoid redundant CSV reads.
    """
    logger.info(
        "Running analysis for year=%d with %d weights",
        selected_year, len(weights),
    )

    if energy_df is None:
        energy_df = load_owid_data()

    scored_df = compute_green_score(energy_df, weights)
    year_df = scored_df[scored_df["year"] == selected_year].copy()

    ndc_data = fetch_all_ndcs()
    classified = classify_countries(
        compute_gap(year_df, ndc_data, selected_year)
    )

    logger.info(
        "Analysis complete: %d countries, %d with NDCs",
        len(year_df), len(ndc_data),
    )

    return AnalysisResult(
        classified=classified,
        selected_year=selected_year,
    )
