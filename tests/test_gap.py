"""Tests for gap analysis."""

import pandas as pd

from src.models.gap import compute_gap


def test_compute_gap_adds_columns():
    df = pd.DataFrame({
        "iso_code": ["IND"],
        "year": [2022],
        "country": ["India"],
        "green_score": [25.0],
    })
    ndc = {
        "IND": {
            "ghg_target": 47.0,
            "pledge_base_year": "2005",
            "pledge_target_year": "2035",
        }
    }
    result = compute_gap(df, ndc, 2022)
    assert "expected_trajectory" in result.columns
    assert "gap" in result.columns


def test_compute_gap_positive_gap():
    df = pd.DataFrame({
        "iso_code": ["A"],
        "year": [2022],
        "country": ["A"],
        "green_score": [50.0],
    })
    ndc = {
        "A": {
            "ghg_target": 40.0,
            "pledge_base_year": "2005",
            "pledge_target_year": "2035",
        }
    }
    result = compute_gap(df, ndc, 2022)
    assert result["gap"].iloc[0] > 0  # Ahead of trajectory


def test_compute_gap_no_ndc():
    df = pd.DataFrame({
        "iso_code": ["X"],
        "year": [2022],
        "country": ["X"],
        "green_score": [10.0],
    })
    result = compute_gap(df, {}, 2022)
    assert result["expected_trajectory"].iloc[0] == 0.0
    assert result["gap"].iloc[0] == 10.0


def test_compute_gap_empty_df():
    df = pd.DataFrame(columns=["iso_code", "year", "country", "green_score"])
    result = compute_gap(df, {}, 2022)
    assert len(result) == 0
    assert "gap" in result.columns


def test_compute_gap_nan_green_score():
    df = pd.DataFrame({
        "iso_code": ["X"],
        "year": [2022],
        "country": ["X"],
        "green_score": [float("nan")],
    })
    result = compute_gap(df, {}, 2022)
    assert result["gap"].iloc[0] == 0.0


def test_compute_gap_invalid_base_year():
    df = pd.DataFrame({
        "iso_code": ["A"],
        "year": [2022],
        "country": ["A"],
        "green_score": [30.0],
    })
    ndc = {
        "A": {
            "ghg_target": 40.0,
            "pledge_base_year": "abc",
            "pledge_target_year": "2035",
        }
    }
    result = compute_gap(df, ndc, 2022)
    assert result["expected_trajectory"].iloc[0] == 0.0
