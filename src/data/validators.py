"""Schema validation, ISO normalization, and dataset merging."""

import pandas as pd

from src.config import ENERGY_SHARE_COLS, ISO_COL, YEAR_COL


def validate_energy_data(df: pd.DataFrame) -> list[str]:
    """Validate OWID energy DataFrame. Returns error list (empty = valid)."""
    errors = []
    if df.empty:
        errors.append("Energy data is empty")
        return errors

    required = [ISO_COL, YEAR_COL]
    for col in required:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    share_present = [c for c in ENERGY_SHARE_COLS if c in df.columns]
    if not share_present:
        errors.append("No energy share columns found")

    if ISO_COL in df.columns:
        non_iso = df[~df[ISO_COL].str.match(r"^[A-Z]{3}$", na=False)]
        if not non_iso.empty:
            bad_codes = non_iso[ISO_COL].unique().tolist()[:5]
            errors.append(f"Invalid ISO codes found: {bad_codes}")

    return errors


def validate_ndc_data(ndc: dict | None) -> list[str]:
    """Validate NDC data dict. Returns list of error messages (empty = valid)."""
    errors = []
    if ndc is None:
        errors.append("NDC data is None")
        return errors
    if not ndc.get("iso_code"):
        errors.append("NDC missing iso_code")
    if ndc.get("ghg_target") is None and ndc.get("ghg_target_type") is None:
        errors.append("NDC has no GHG target or target type")
    return errors


def merge_energy_and_ndc(
    energy_df: pd.DataFrame,
    ndc_data: dict[str, dict],
) -> pd.DataFrame:
    """Merge energy data with NDC info on iso_code.

    Adds columns: ghg_target, ghg_target_type, pledge_base_year, pledge_target_year.
    """
    ndc_df = pd.DataFrame.from_dict(ndc_data, orient="index")
    if ndc_df.empty:
        return energy_df

    ndc_cols = [
        "iso_code", "ghg_target", "ghg_target_type",
        "pledge_base_year", "pledge_target_year",
    ]
    existing = [c for c in ndc_cols if c in ndc_df.columns]
    ndc_df = ndc_df[existing].copy()

    merged = energy_df.merge(ndc_df, on="iso_code", how="left")
    return merged
