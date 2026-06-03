"""Gap analysis: actual green score vs expected NDC trajectory."""

import logging

import pandas as pd

from src.config import ISO_COL

logger = logging.getLogger(__name__)


def _linear_trajectory(
    base_value: float,
    target_value: float,
    base_year: int,
    target_year: int,
    current_year: int,
) -> float:
    """Linear interpolation between base and target year values."""
    if target_year == base_year:
        return target_value
    progress = (current_year - base_year) / (target_year - base_year)
    progress = max(0.0, min(1.0, progress))
    return base_value + (target_value - base_value) * progress


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

    # Build NDC lookup arrays
    has_gap = result[ISO_COL].isin(ndc_data)
    result["expected_trajectory"] = 0.0

    for idx in result.index[has_gap]:
        iso = result.at[idx, ISO_COL]
        ndc = ndc_data[iso]
        target_pct = ndc.get("ghg_target")
        base_year = ndc.get("pledge_base_year")
        target_year = ndc.get("pledge_target_year")

        if target_pct is None or not base_year or not target_year:
            continue

        try:
            by = int(base_year)
            ty = int(target_year)
            trajectory = _linear_trajectory(
                0.0, float(target_pct), by, ty, current_year
            )
            result.at[idx, "expected_trajectory"] = trajectory
        except (ValueError, TypeError) as e:
            logger.warning(
                "Invalid NDC years for %s: base=%s target=%s: %s",
                iso, base_year, target_year, e,
            )

    # Handle NaN green scores
    actual = result["green_score"].fillna(0.0)
    result["gap"] = (actual - result["expected_trajectory"]).round(2)
    result["expected_trajectory"] = result["expected_trajectory"].round(2)

    return result
