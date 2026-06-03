"""Tests for data validation and merging."""

import pandas as pd

from src.data.validators import (
    merge_energy_and_ndc,
    validate_energy_data,
    validate_ndc_data,
)


def test_validate_energy_data_valid():
    df = pd.DataFrame({
        "iso_code": ["IND", "USA"],
        "year": [2020, 2020],
        "country": ["India", "United States"],
        "solar_share_energy": [1.0, 2.0],
    })
    errors = validate_energy_data(df)
    assert errors == []


def test_validate_energy_data_empty():
    errors = validate_energy_data(pd.DataFrame())
    assert len(errors) == 1


def test_validate_energy_data_missing_column():
    df = pd.DataFrame({
        "iso_code": ["IND"],
        "year": [2020],
        "country": ["India"],
    })
    errors = validate_energy_data(df)
    assert any("share" in e.lower() for e in errors)


def test_validate_ndc_data_valid():
    ndc = {"iso_code": "IND", "ghg_target": 47.0}
    errors = validate_ndc_data(ndc)
    assert errors == []


def test_validate_ndc_data_none():
    errors = validate_ndc_data(None)
    assert len(errors) == 1


def test_merge_energy_and_ndc():
    energy = pd.DataFrame({
        "iso_code": ["IND", "USA"],
        "year": [2020, 2020],
        "country": ["India", "United States"],
        "solar_share_energy": [1.0, 2.0],
    })
    ndc = {
        "IND": {"iso_code": "IND", "ghg_target": 47.0, "pledge_base_year": "2005"},
        "USA": {"iso_code": "USA", "ghg_target": 50.0, "pledge_base_year": "2005"},
    }
    result = merge_energy_and_ndc(energy, ndc)
    assert "ghg_target" in result.columns
    assert result[result["iso_code"] == "IND"]["ghg_target"].iloc[0] == 47.0


def test_validate_energy_data_missing_iso():
    df = pd.DataFrame({
        "year": [2020],
        "country": ["India"],
        "solar_share_energy": [1.0],
    })
    errors = validate_energy_data(df)
    assert any("iso_code" in e for e in errors)


def test_validate_energy_data_missing_year():
    df = pd.DataFrame({
        "iso_code": ["IND"],
        "country": ["India"],
        "solar_share_energy": [1.0],
    })
    errors = validate_energy_data(df)
    assert any("year" in e for e in errors)


def test_validate_ndc_data_empty_dict():
    errors = validate_ndc_data({})
    assert any("iso_code" in e for e in errors)


def test_validate_ndc_data_missing_both_ghg_fields():
    errors = validate_ndc_data({"iso_code": "IND"})
    assert any("GHG" in e for e in errors)


def test_merge_energy_and_ndc_empty_ndc():
    energy = pd.DataFrame({
        "iso_code": ["IND"],
        "year": [2020],
        "country": ["India"],
        "solar_share_energy": [1.0],
    })
    result = merge_energy_and_ndc(energy, {})
    assert "ghg_target" not in result.columns


def test_merge_energy_and_ndc_partial_overlap():
    energy = pd.DataFrame({
        "iso_code": ["IND", "USA"],
        "year": [2020, 2020],
        "country": ["India", "United States"],
        "solar_share_energy": [1.0, 2.0],
    })
    ndc = {"IND": {"iso_code": "IND", "ghg_target": 47.0}}
    result = merge_energy_and_ndc(energy, ndc)
    assert result[result["iso_code"] == "IND"]["ghg_target"].iloc[0] == 47.0
    assert pd.isna(result[result["iso_code"] == "USA"]["ghg_target"].iloc[0])
