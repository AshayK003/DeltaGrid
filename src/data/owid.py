"""OWID energy data ingestion with filtering and caching."""

from pathlib import Path

import pandas as pd
import requests

from src.config import (
    CACHE_TTL_CSV,
    COUNTRY_COL,
    ENERGY_ABSOLUTE_COLS,
    ENERGY_SHARE_COLS,
    ISO_COL,
    OWID_CSV,
    OWID_URL,
    YEAR_COL,
)
from src.data.cache import read_cache, write_cache
from src.data.country_codes import is_aggregate, normalize_iso3


def download_owid_csv() -> Path:
    """Download OWID energy CSV if not cached locally."""
    if OWID_CSV.exists():
        return OWID_CSV
    OWID_CSV.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(OWID_URL, timeout=60)
    resp.raise_for_status()
    OWID_CSV.write_bytes(resp.content)
    return OWID_CSV


def load_owid_data() -> pd.DataFrame:
    """Load OWID CSV, filter aggregates, normalize ISO codes.

    Returns DataFrame with columns: iso_code, year, country, + all share/absolute cols.
    """
    cache_key = "owid_raw"
    cached = read_cache(cache_key, CACHE_TTL_CSV)
    if cached is not None:
        return pd.DataFrame(cached)

    csv_path = download_owid_csv()
    df = pd.read_csv(csv_path, low_memory=False)

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
            df[col] = pd.to_numeric(df[col], errors="coerce")

    write_cache(cache_key, df.to_dict(orient="records"))
    return df


def get_owid_latest_year(df: pd.DataFrame) -> int:
    """Return the most recent year in the dataset."""
    return int(df[YEAR_COL].max())


def get_owid_year_range(df: pd.DataFrame) -> tuple[int, int]:
    """Return (min_year, max_year) of available data."""
    return int(df[YEAR_COL].min()), int(df[YEAR_COL].max())


def filter_owid_by_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Return data for a single year."""
    return df[df[YEAR_COL] == year].copy()


def filter_owid_by_iso(df: pd.DataFrame, iso3: str) -> pd.DataFrame:
    """Return data for a single country."""
    return df[df[ISO_COL] == normalize_iso3(iso3)].copy()
