"""OWID energy data ingestion with filtering and caching."""

import logging
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from src.config import (
    COUNTRY_COL,
    ENERGY_ABSOLUTE_COLS,
    ENERGY_SHARE_COLS,
    ISO_COL,
    OWID_CSV,
    OWID_URL,
    YEAR_COL,
)
from src.data.country_codes import is_aggregate, normalize_iso3

logger = logging.getLogger(__name__)


def download_owid_csv() -> Path:
    """Download OWID energy CSV if not cached locally."""
    if OWID_CSV.exists():
        return OWID_CSV
    OWID_CSV.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading OWID CSV from %s", OWID_URL)
    try:
        resp = requests.get(OWID_URL, timeout=60)
        resp.raise_for_status()
        OWID_CSV.write_bytes(resp.content)
        logger.info("Downloaded OWID CSV: %d bytes", len(resp.content))
    except requests.RequestException as e:
        logger.error("Failed to download OWID CSV: %s", e)
        raise
    return OWID_CSV


@st.cache_data(show_spinner=False, ttl=3600)
def load_owid_data() -> pd.DataFrame:
    """Load OWID CSV, filter aggregates, normalize ISO codes."""
    csv_path = download_owid_csv()
    df = pd.read_csv(csv_path, low_memory=False)
    logger.info("Read OWID CSV: %d rows", len(df))

    # Normalize ISO codes
    df[ISO_COL] = df[ISO_COL].fillna("").apply(normalize_iso3)

    # Remove rows with empty ISO code
    df = df[df[ISO_COL] != ""]

    # Remove aggregates
    df = df[~df[COUNTRY_COL].apply(is_aggregate)]

    # Select relevant columns
    idx_cols = [ISO_COL, YEAR_COL, COUNTRY_COL]
    keep_cols = idx_cols + ENERGY_SHARE_COLS + ENERGY_ABSOLUTE_COLS
    existing = [c for c in keep_cols if c in df.columns]
    df = df[existing].copy()

    # Convert to numeric
    for col in ENERGY_SHARE_COLS + ENERGY_ABSOLUTE_COLS:
        if col in df.columns:
            before_nan = df[col].isna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            new_nan = df[col].isna().sum() - before_nan
            if new_nan > 0:
                logger.warning(
                    "Column %s: %d values coerced to NaN", col, new_nan
                )

    logger.info(
        "Filtered OWID data: %d rows, years %s-%s",
        len(df),
        df[YEAR_COL].min(),
        df[YEAR_COL].max(),
    )

    return df


def get_owid_year_range(df: pd.DataFrame) -> tuple[int, int]:
    """Return (min_year, max_year) of available data."""
    if df.empty:
        return (0, 0)
    return int(df[YEAR_COL].min()), int(df[YEAR_COL].max())



