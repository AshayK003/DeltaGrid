"""Green score computation: weighted sum of energy shares, normalized 0-100."""

import logging

import numpy as np
import pandas as pd

from src.config import DEFAULT_WEIGHTS, ISO_COL, YEAR_COL

logger = logging.getLogger(__name__)


def compute_green_score(
    df: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Compute green score for each row in the DataFrame.

    Args:
        df: OWID energy data with share columns.
        weights: Mapping of column name → weight.

    Returns:
        DataFrame with added 'green_score' column (0-100 scale).
    """
    if weights is None:
        weights = dict(DEFAULT_WEIGHTS)

    result = df.copy()

    if result.empty:
        result["green_score"] = []
        return result

    # Fill NaN shares with 0 for scoring
    for col in weights:
        if col in result.columns:
            result[col] = result[col].fillna(0.0)

    # Weighted sum
    score = np.zeros(len(result))
    total_weight = 0.0
    for col, w in weights.items():
        if col in result.columns:
            score += result[col].values * w
            total_weight += w

    # Normalize to absolute 0-100 scale
    if total_weight > 0:
        score = score / total_weight

    result["green_score"] = np.round(score, 2)
    return result


def get_green_score_for_country(
    df: pd.DataFrame,
    iso3: str,
    year: int,
    weights: dict[str, float] | None = None,
) -> float | None:
    """Get green score for a specific country and year."""
    row = df[(df[ISO_COL] == iso3) & (df[YEAR_COL] == year)]
    if row.empty:
        return None
    scored = compute_green_score(row, weights)
    val = scored["green_score"].iloc[0]
    return float(val) if not np.isnan(val) else None
