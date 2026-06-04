"""Gap analysis: actual green score vs expected NDC trajectory."""

import logging

import numpy as np
import pandas as pd

from src.config import ISO_COL

logger = logging.getLogger(__name__)


def _vectorized_trajectory(
    base_values: np.ndarray,
    target_values: np.ndarray,
    base_years: np.ndarray,
    target_years: np.ndarray,
    current_year: int,
) -> np.ndarray:
    """Vectorized linear interpolation for arrays of trajectories."""
    result = np.zeros_like(target_values, dtype=float)

    # Avoid division by zero; also treat year 0 as invalid
    valid = (
        (target_years != base_years)
        & (target_years > 0)
        & (base_years > 0)
    )

    progress = np.zeros_like(target_values, dtype=float)
    progress[valid] = (
        (current_year - base_years[valid])
        / (target_years[valid] - base_years[valid])
    )
    progress = np.clip(progress, 0.0, 1.0)

    result[valid] = base_values[valid] + (
        target_values[valid] - base_values[valid]
    ) * progress[valid]

    # Same-year case: use target value directly
    same_year = (target_years == base_years) & (target_years > 0)
    result[same_year] = target_values[same_year]

    return result


def compute_gap(
    df: pd.DataFrame,
    ndc_data: dict[str, dict],
    current_year: int,
) -> pd.DataFrame:
    """Compute gap between actual green score and expected NDC trajectory.

    Vectorized implementation for performance.
    """
    result = df.copy()

    if "green_score" not in result.columns:
        logger.warning("Missing 'green_score' column, defaulting to 0")
        result["green_score"] = 0.0

    # Build NDC lookup arrays for vectorized computation
    iso_array = result[ISO_COL].values
    n = len(iso_array)

    target_values = np.zeros(n)
    base_years = np.zeros(n, dtype=int)
    target_years = np.zeros(n, dtype=int)

    for i, iso in enumerate(iso_array):
        ndc = ndc_data.get(iso)
        if ndc is None:
            continue

        target_pct = ndc.get("ghg_target")
        base_year = ndc.get("pledge_base_year")
        target_year = ndc.get("pledge_target_year")

        if target_pct is None or not base_year or not target_year:
            continue

        try:
            target_values[i] = float(target_pct)
            base_years[i] = int(base_year)
            target_years[i] = int(target_year)
        except (ValueError, TypeError) as e:
            logger.warning(
                "Invalid NDC years for %s: base=%s target=%s: %s",
                iso, base_year, target_year, e,
            )

    # Vectorized trajectory computation
    result["expected_trajectory"] = _vectorized_trajectory(
        np.zeros(n), target_values, base_years, target_years, current_year
    )

    # Handle NaN green scores
    actual = result["green_score"].fillna(0.0)
    result["gap"] = (actual - result["expected_trajectory"]).round(2)
    result["expected_trajectory"] = result["expected_trajectory"].round(2)

    return result
