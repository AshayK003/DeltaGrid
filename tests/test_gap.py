"""Tests for gap analysis."""

import numpy as np
import pandas as pd

from src.models.gap import _vectorized_trajectory, compute_gap


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


def test_vectorized_trajectory_normal_case():
    target_values = np.array([50.0])
    base_years = np.array([2000])
    target_years = np.array([2030])
    current_year = 2015
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert result[0] == 25.0  # Halfway through trajectory


def test_vectorized_trajectory_before_base_year():
    target_values = np.array([50.0])
    base_years = np.array([2000])
    target_years = np.array([2030])
    current_year = 1995
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert result[0] == 0.0  # Clipped to 0.0


def test_vectorized_trajectory_after_target_year():
    target_values = np.array([50.0])
    base_years = np.array([2000])
    target_years = np.array([2030])
    current_year = 2040
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert result[0] == 50.0  # Clipped to target value


def test_vectorized_trajectory_same_year():
    target_values = np.array([50.0])
    base_years = np.array([2000])
    target_years = np.array([2000])
    current_year = 2000
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert result[0] == 50.0  # Returns target value directly


def test_vectorized_trajectory_zero_years():
    target_values = np.array([50.0, 30.0])
    base_years = np.array([0, 2000])
    target_years = np.array([2030, 0])
    current_year = 2015
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert result[0] == 0.0  # Base year 0 excluded
    assert result[1] == 0.0  # Target year 0 excluded


def test_vectorized_trajectory_mixed_array():
    target_values = np.array([50.0, 30.0, 20.0])
    base_years = np.array([2000, 0, 2010])
    target_years = np.array([2030, 2030, 2020])
    current_year = 2025
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert round(result[0], 2) == 41.67  # Valid entry computed
    assert result[1] == 0.0  # Invalid base year excluded
    assert result[2] == 20.0  # After target year, clipped to target


def test_vectorized_trajectory_empty_array():
    target_values = np.array([])
    base_years = np.array([])
    target_years = np.array([])
    current_year = 2015
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert len(result) == 0


def test_vectorized_trajectory_zero_target_value():
    target_values = np.array([0.0])
    base_years = np.array([2000])
    target_years = np.array([2030])
    current_year = 2015
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert result[0] == 0.0


def test_vectorized_trajectory_negative_years():
    target_values = np.array([50.0, 30.0])
    base_years = np.array([-5, 2000])
    target_years = np.array([2030, -10])
    current_year = 2015
    result = _vectorized_trajectory(target_values, base_years, target_years, current_year)
    assert result[0] == 0.0  # Negative base year excluded
    assert result[1] == 0.0  # Negative target year excluded
