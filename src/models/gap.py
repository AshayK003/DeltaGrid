"""Gap analysis: actual green score vs expected NDC trajectory."""

import pandas as pd

from src.config import ISO_COL


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

    Args:
        df: DataFrame with 'green_score' column (from compute_green_score).
        ndc_data: Dict of iso3 → NDC info.
        current_year: Year to evaluate.

    Returns:
        DataFrame with added columns: expected_trajectory, gap.
    """
    result = df.copy()
    expected = []
    gaps = []

    for _, row in result.iterrows():
        iso = row[ISO_COL]
        actual = row.get("green_score", 0.0)
        ndc = ndc_data.get(iso, {})

        target_pct = ndc.get("ghg_target")
        base_year = ndc.get("pledge_base_year")
        target_year = ndc.get("pledge_target_year")

        actual_score = actual if pd.notna(actual) else 0.0

        if target_pct is not None and base_year and target_year:
            try:
                by = int(base_year)
                ty = int(target_year)
                # Assume base year green score ≈ 0
                # Target: achieve target_pct% green by target_year
                trajectory = _linear_trajectory(
                    0.0, float(target_pct), by, ty, current_year
                )
            except (ValueError, TypeError):
                trajectory = 0.0
        else:
            trajectory = 0.0

        gap = actual_score - trajectory
        expected.append(round(trajectory, 2))
        gaps.append(round(gap, 2))

    result["expected_trajectory"] = expected
    result["gap"] = gaps
    return result
