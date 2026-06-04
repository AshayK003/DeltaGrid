"""Tests for OWID energy data ingestion."""

from pathlib import Path

import pandas as pd
import pytest

from src.config import ISO_COL
from src.data.owid import get_owid_year_range, load_owid_data


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "iso_code": ["IND", "IND", "USA", "USA"],
        "year": [2020, 2021, 2020, 2021],
        "country": ["India", "India", "United States", "United States"],
        "solar_share_energy": [1.0, 1.5, 2.0, 3.0],
        "wind_share_energy": [0.5, 0.7, 3.5, 4.0],
        "hydro_share_energy": [10.0, 10.5, 6.0, 6.5],
        "nuclear_share_energy": [1.2, 1.3, 8.0, 8.5],
        "gas_share_energy": [5.0, 5.2, 32.0, 33.0],
        "coal_share_energy": [44.0, 43.0, 19.0, 18.0],
        "primary_energy_consumption": [100, 110, 200, 210],
    })


class TestGetOwidYearRange:
    def test_returns_tuple(self, sample_df):
        result = get_owid_year_range(sample_df)
        assert result == (2020, 2021)

    def test_type(self, sample_df):
        result = get_owid_year_range(sample_df)
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)


class TestLoadOwidData:
    def test_loads_from_csv(self):
        csv_path = Path(
            "D:/Personal projects/DeltaGrid/data/raw/"
            "owid-energy-data-2010-2025.csv"
        )
        if not csv_path.exists():
            pytest.skip("OWID CSV not available locally")
        result = load_owid_data()
        assert len(result) > 0
        assert ISO_COL in result.columns
        assert "year" in result.columns

    def test_filters_aggregates(self):
        csv_path = Path(
            "D:/Personal projects/DeltaGrid/data/raw/"
            "owid-energy-data-2010-2025.csv"
        )
        if not csv_path.exists():
            pytest.skip("OWID CSV not available locally")
        result = load_owid_data()
        assert "World" not in result["country"].values
