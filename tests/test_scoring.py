"""Tests for green score computation."""

import pandas as pd
import pytest

from src.config import DEFAULT_WEIGHTS
from src.models.scoring import compute_green_score, get_green_score_for_country


@pytest.fixture
def sample_energy_df():
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
    })


def test_compute_green_score_returns_column(sample_energy_df):
    result = compute_green_score(sample_energy_df)
    assert "green_score" in result.columns


def test_compute_green_score_range(sample_energy_df):
    result = compute_green_score(sample_energy_df)
    assert result["green_score"].between(0, 100).all()


def test_compute_green_score_respects_weights(sample_energy_df):
    result = compute_green_score(sample_energy_df, weights=DEFAULT_WEIGHTS)
    assert "green_score" in result.columns
    assert len(result) == 4


def test_compute_green_score_zero_weights():
    df = pd.DataFrame({
        "iso_code": ["X"],
        "year": [2020],
        "country": ["X"],
        "solar_share_energy": [10.0],
    })
    weights = {"solar_share_energy": 0.0}
    result = compute_green_score(df, weights=weights)
    assert result["green_score"].iloc[0] == 0.0


def test_get_green_score_for_country(sample_energy_df):
    score = get_green_score_for_country(sample_energy_df, "IND", 2020)
    assert score is not None
    assert 0 <= score <= 100


def test_get_green_score_missing_country():
    df = pd.DataFrame({
        "iso_code": ["IND"],
        "year": [2020],
        "country": ["India"],
        "solar_share_energy": [1.0],
    })
    score = get_green_score_for_country(df, "ZZZ", 2020)
    assert score is None


def test_compute_green_score_empty_df():
    df = pd.DataFrame(columns=["iso_code", "year", "country", "solar_share_energy"])
    result = compute_green_score(df)
    assert "green_score" in result.columns
    assert len(result) == 0


def test_compute_green_score_nan_shares():
    df = pd.DataFrame({
        "iso_code": ["X"],
        "year": [2020],
        "country": ["X"],
        "solar_share_energy": [float("nan")],
        "wind_share_energy": [float("nan")],
    })
    w = {"solar_share_energy": 1.0, "wind_share_energy": 1.0}
    result = compute_green_score(df, weights=w)
    assert result["green_score"].iloc[0] == 0.0


def test_compute_green_score_single_row():
    df = pd.DataFrame({
        "iso_code": ["X"],
        "year": [2020],
        "country": ["X"],
        "solar_share_energy": [5.0],
    })
    result = compute_green_score(df, weights={"solar_share_energy": 1.0})
    assert result["green_score"].iloc[0] == 100.0


def test_compute_green_score_does_not_mutate_input():
    df = pd.DataFrame({
        "iso_code": ["IND"],
        "year": [2020],
        "country": ["India"],
        "solar_share_energy": [1.0],
    })
    original_cols = list(df.columns)
    compute_green_score(df)
    assert list(df.columns) == original_cols


def test_get_green_score_missing_year():
    df = pd.DataFrame({
        "iso_code": ["IND", "IND"],
        "year": [2020, 2021],
        "country": ["India", "India"],
        "solar_share_energy": [1.0, 2.0],
    })
    score = get_green_score_for_country(df, "IND", 2099)
    assert score is None


def test_compute_green_score_all_zero_shares():
    df = pd.DataFrame({
        "iso_code": ["X"],
        "year": [2020],
        "country": ["X"],
        "solar_share_energy": [0.0],
        "wind_share_energy": [0.0],
    })
    w = {"solar_share_energy": 1.0, "wind_share_energy": 1.0}
    result = compute_green_score(df, weights=w)
    assert result["green_score"].iloc[0] == 0.0
