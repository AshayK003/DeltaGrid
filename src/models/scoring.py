"""Green score computation: weighted sum of energy shares divided by max weight."""

import numpy as np
import pandas as pd


def compute_green_score(
    df: pd.DataFrame,
    weights: dict[str, float],
) -> pd.DataFrame:
    """Compute green score for each row in the DataFrame.

    Args:
        df: OWID energy data with share columns.
        weights: Mapping of column name → weight.

    Returns:
        DataFrame with added 'green_score' column
        (0-100 scale: 100 = 100% from the most-valued source).
    """
    result = df.copy()

    if result.empty:
        result["green_score"] = []
        return result

    # Weighted sum — operate on numpy arrays, never mutate the DataFrame
    score = np.zeros(len(result))
    for col, w in weights.items():
        if col in result.columns:
            score += result[col].fillna(0.0).values * w

    # Normalize by max weight so 100% from the most-valued source = 100
    max_weight = max(weights.values()) if weights else 0.0
    if max_weight > 0:
        score = score / max_weight

    result["green_score"] = np.round(score, 2)
    return result



