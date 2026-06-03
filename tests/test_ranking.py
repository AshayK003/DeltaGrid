"""Tests for country classification and ranking."""

import pandas as pd

from src.models.ranking import (
    classify_countries,
    classify_gap,
    get_hidden_champions,
    get_laggards,
    get_rankings,
)


def test_classify_gap_champion():
    assert classify_gap(10) == "hidden_champion"


def test_classify_gap_on_track():
    assert classify_gap(2) == "on_track"


def test_classify_gap_behind():
    assert classify_gap(-3) == "slightly_behind"


def test_classify_gap_laggard():
    assert classify_gap(-10) == "laggard"


def test_classify_countries_adds_column():
    df = pd.DataFrame({
        "iso_code": ["A", "B"],
        "year": [2022, 2022],
        "country": ["A", "B"],
        "gap": [10.0, -10.0],
    })
    result = classify_countries(df)
    assert "classification" in result.columns
    assert result["classification"].tolist() == ["hidden_champion", "laggard"]


def test_get_laggards():
    df = pd.DataFrame({
        "iso_code": ["A", "B", "C"],
        "year": [2022, 2022, 2022],
        "country": ["A", "B", "C"],
        "gap": [10.0, -10.0, -20.0],
        "classification": ["hidden_champion", "laggard", "laggard"],
    })
    result = get_laggards(df)
    assert len(result) == 2
    assert result.iloc[0]["iso_code"] == "C"


def test_get_hidden_champions():
    df = pd.DataFrame({
        "iso_code": ["A", "B"],
        "year": [2022, 2022],
        "country": ["A", "B"],
        "gap": [15.0, 5.0],
        "classification": ["hidden_champion", "hidden_champion"],
    })
    result = get_hidden_champions(df)
    assert len(result) == 2
    assert result.iloc[0]["iso_code"] == "A"


def test_get_rankings_sorted():
    df = pd.DataFrame({
        "iso_code": ["A", "B", "C"],
        "year": [2022, 2022, 2022],
        "country": ["A", "B", "C"],
        "gap": [-5.0, 10.0, 0.0],
    })
    result = get_rankings(df)
    assert result.iloc[0]["iso_code"] == "B"
    assert result.iloc[-1]["iso_code"] == "A"


def test_classify_gap_boundary_exactly_five():
    assert classify_gap(5) == "on_track"


def test_classify_gap_boundary_exactly_zero():
    assert classify_gap(0) == "on_track"


def test_classify_gap_boundary_exactly_negative_five():
    assert classify_gap(-5) == "slightly_behind"


def test_classify_gap_boundary_six():
    assert classify_gap(6) == "hidden_champion"


def test_classify_gap_boundary_negative_six():
    assert classify_gap(-6) == "laggard"


def test_classify_countries_no_gap_column():
    df = pd.DataFrame({
        "iso_code": ["A"],
        "year": [2022],
        "country": ["A"],
    })
    result = classify_countries(df)
    assert all(result["classification"] == "no_data")


def test_get_laggards_empty():
    df = pd.DataFrame({
        "iso_code": ["A"],
        "year": [2022],
        "country": ["A"],
        "gap": [10.0],
        "classification": ["hidden_champion"],
    })
    result = get_laggards(df)
    assert len(result) == 0


def test_get_hidden_champions_empty():
    df = pd.DataFrame({
        "iso_code": ["A"],
        "year": [2022],
        "country": ["A"],
        "gap": [-10.0],
        "classification": ["laggard"],
    })
    result = get_hidden_champions(df)
    assert len(result) == 0


def test_get_rankings_empty():
    df = pd.DataFrame(columns=["iso_code", "year", "country", "gap"])
    result = get_rankings(df)
    assert len(result) == 0
