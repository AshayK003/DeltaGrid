"""Preprocessing pipeline for user-uploaded energy data files."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from src.config import (
    COUNTRY_COL,
    ENERGY_ABSOLUTE_COLS,
    ENERGY_SHARE_COLS,
    ISO_COL,
    YEAR_COL,
)
from src.data.country_codes import is_aggregate, normalize_iso3

logger = logging.getLogger(__name__)

# Columns the app needs at minimum to function
_REQUIRED_COLS = {ISO_COL, YEAR_COL}
# Columns needed for green score computation (at least some share cols)
_MIN_SHARE_COLS = 1


@dataclass
class PreprocessResult:
    """Result of preprocessing an uploaded file."""

    df: pd.DataFrame
    errors: list[str]
    warnings: list[str]


def _read_file(uploaded_file) -> pd.DataFrame | None:
    """Read a CSV or XLSX file into a DataFrame.

    Handles the file stream position correctly for Streamlit's
    UploadedFile objects which may be re-read on reruns.
    """
    uploaded_file.seek(0)
    name = uploaded_file.name.lower()

    try:
        if name.endswith(".csv"):
            # Try common encodings
            for encoding in ("utf-8", "latin-1", "cp1252"):
                try:
                    uploaded_file.seek(0)
                    return pd.read_csv(
                        io.BytesIO(uploaded_file.read()),
                        encoding=encoding,
                        low_memory=False,
                    )
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            return None
        elif name.endswith((".xlsx", ".xls")):
            uploaded_file.seek(0)
            return pd.read_excel(io.BytesIO(uploaded_file.read()))
    except Exception as e:
        logger.error("Failed to read uploaded file: %s", e)
        return None

    return None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: strip whitespace, lowercase, snake_case."""
    import re

    result = df.copy()
    new_cols = {}
    for col in result.columns:
        normalized = col.strip().lower()
        normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
        normalized = normalized.strip("_")
        new_cols[col] = normalized
    result = result.rename(columns=new_cols)
    return result


def _coerce_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Convert columns to numeric, coercing errors to NaN."""
    result = df.copy()
    for col in cols:
        if col in result.columns:
            before_nan = result[col].isna().sum()
            result[col] = pd.to_numeric(result[col], errors="coerce")
            new_nan = result[col].isna().sum() - before_nan
            if new_nan > 0:
                logger.warning(
                    "Column %s: %d values coerced to NaN", col, new_nan
                )
    return result


def preprocess_upload(uploaded_file) -> PreprocessResult:
    """Full preprocessing pipeline for an uploaded energy data file.

    Steps:
    1. Read file (CSV/XLSX) with encoding detection
    2. Normalize column names
    3. Validate required columns exist
    4. Normalize ISO codes
    5. Remove aggregate regions
    6. Coerce numeric columns
    7. Filter to valid year range
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Step 1: Read file
    df = _read_file(uploaded_file)
    if df is None or df.empty:
        errors.append("Could not read file or file is empty.")
        return PreprocessResult(df=pd.DataFrame(), errors=errors, warnings=warnings)

    logger.info(
        "Read uploaded file %s: %d rows, %d columns",
        uploaded_file.name, len(df), len(df.columns),
    )

    # Step 2: Normalize column names
    df = _normalize_columns(df)

    # Step 3: Validate required columns
    missing_required = _REQUIRED_COLS - set(df.columns)
    if missing_required:
        errors.append(
            f"Missing required columns: {', '.join(sorted(missing_required))}. "
            f"Found columns: {', '.join(sorted(df.columns))}"
        )
        return PreprocessResult(df=df, errors=errors, warnings=warnings)

    # Check for energy share columns
    share_present = [c for c in ENERGY_SHARE_COLS if c in df.columns]
    if len(share_present) < _MIN_SHARE_COLS:
        # Try to find alternative column names (common variations)
        alt_mapping = _detect_alternative_columns(df)
        if alt_mapping:
            df = df.rename(columns=alt_mapping)
            share_present = [
                c for c in ENERGY_SHARE_COLS if c in df.columns
            ]
            warnings.append(f"Renamed columns: {alt_mapping}")

        if len(share_present) < _MIN_SHARE_COLS:
            warnings.append(
                "No energy share columns found. "
                "Green scores will default to 0. "
                f"Expected columns like: {', '.join(ENERGY_SHARE_COLS[:3])}"
            )

    # Step 4: Normalize ISO codes
    df[ISO_COL] = df[ISO_COL].fillna("").apply(normalize_iso3)

    # Remove rows with empty ISO
    before = len(df)
    df = df[df[ISO_COL] != ""]
    removed = before - len(df)
    if removed > 0:
        warnings.append(f"Removed {removed} rows with invalid/missing ISO codes.")

    # Step 5: Remove aggregates
    before = len(df)
    df = df[~df[COUNTRY_COL].apply(is_aggregate)] if COUNTRY_COL in df.columns else df
    removed = before - len(df)
    if removed > 0:
        warnings.append(f"Removed {removed} aggregate region rows.")

    # Step 6: Coerce numeric columns
    numeric_cols = ENERGY_SHARE_COLS + ENERGY_ABSOLUTE_COLS
    df = _coerce_numeric(df, [c for c in numeric_cols if c in df.columns])

    # Ensure year is int
    if YEAR_COL in df.columns:
        df[YEAR_COL] = pd.to_numeric(df[YEAR_COL], errors="coerce")
        df = df.dropna(subset=[YEAR_COL])
        df[YEAR_COL] = df[YEAR_COL].astype(int)

    # Step 7: Filter to reasonable year range
    if YEAR_COL in df.columns and not df.empty:
        min_year = df[YEAR_COL].min()
        max_year = df[YEAR_COL].max()
        if min_year < 1960 or max_year > 2030:
            df = df[(df[YEAR_COL] >= 1960) & (df[YEAR_COL] <= 2030)]
            warnings.append("Filtered years to 1960-2030 range.")

    # Select available columns (keep extra columns for potential future use)
    idx_cols = [ISO_COL, YEAR_COL]
    if COUNTRY_COL in df.columns:
        idx_cols.append(COUNTRY_COL)
    all_numeric = ENERGY_SHARE_COLS + ENERGY_ABSOLUTE_COLS
    keep_cols = idx_cols + [
        c for c in all_numeric if c in df.columns
    ]
    df = df[[c for c in keep_cols if c in df.columns]].copy()

    if df.empty:
        errors.append("No valid data rows after preprocessing.")
    else:
        logger.info(
            "Preprocessed upload: %d rows, years %s-%s, %d countries",
            len(df),
            df[YEAR_COL].min() if YEAR_COL in df.columns else "?",
            df[YEAR_COL].max() if YEAR_COL in df.columns else "?",
            df[ISO_COL].nunique() if ISO_COL in df.columns else 0,
        )

    return PreprocessResult(df=df, errors=errors, warnings=warnings)


def _detect_alternative_columns(df: pd.DataFrame) -> dict[str, str]:
    """Try to match common alternative column names to expected names."""
    mapping = {}
    alternatives = {
        "solar_share_energy": [
            "solar", "solar_share", "solar_pct", "solar_percent",
            "renewable_solar", "solar_share_of_energy",
        ],
        "wind_share_energy": [
            "wind", "wind_share", "wind_pct", "wind_percent",
            "renewable_wind", "wind_share_of_energy",
        ],
        "hydro_share_energy": [
            "hydro", "hydro_share", "hydro_pct", "hydro_percent",
            "renewable_hydro", "hydro_share_of_energy",
        ],
        "nuclear_share_energy": [
            "nuclear", "nuclear_share", "nuclear_pct", "nuclear_percent",
        ],
        "gas_share_energy": [
            "gas", "gas_share", "gas_pct", "gas_percent", "natural_gas",
        ],
        "coal_share_energy": [
            "coal", "coal_share", "coal_pct", "coal_percent",
        ],
        "primary_energy_consumption": [
            "primary_energy", "energy_consumption", "total_energy",
        ],
    }

    existing_lower = {col.lower().strip(): col for col in df.columns}

    for target, alts in alternatives.items():
        if target in df.columns:
            continue
        for alt in alts:
            if alt in existing_lower:
                mapping[existing_lower[alt]] = target
                break

    return mapping


# Need io for file reading
import io  # noqa: E402
