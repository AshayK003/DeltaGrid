"""Country classification and ranking based on gap analysis."""

import pandas as pd

from src.config import CLASS_THRESHOLDS


def classify_gap(gap: float) -> str:
    """Classify a single gap value into a category."""
    if gap > CLASS_THRESHOLDS["hidden_champion"]:
        return "hidden_champion"
    elif gap >= CLASS_THRESHOLDS["on_track"]:
        return "on_track"
    elif gap >= CLASS_THRESHOLDS["slightly_behind"]:
        return "slightly_behind"
    else:
        return "laggard"


def classify_countries(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'classification' column based on gap values.

    Expects DataFrame with 'gap' column from compute_gap().
    """
    result = df.copy()
    if "gap" not in result.columns:
        result["classification"] = "no_data"
        return result

    result["classification"] = result["gap"].apply(classify_gap)

    # Mark rows with missing gap as no_data
    result.loc[result["gap"].isna(), "classification"] = "no_data"

    return result


def get_laggards(df: pd.DataFrame, min_gap: float = -100) -> pd.DataFrame:
    """Return laggard countries sorted by gap (worst first)."""
    lag = df[df["classification"] == "laggard"].copy()
    lag = lag[lag["gap"] >= min_gap]
    return lag.sort_values("gap", ascending=True)


def get_hidden_champions(df: pd.DataFrame) -> pd.DataFrame:
    """Return hidden champion countries sorted by gap (best first)."""
    champ = df[df["classification"] == "hidden_champion"].copy()
    return champ.sort_values("gap", ascending=False)


def get_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Return full country ranking sorted by gap (best to worst)."""
    return df.sort_values("gap", ascending=False).reset_index(drop=True)
