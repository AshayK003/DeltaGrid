"""Integration tests: full data flows across modules."""

import pandas as pd
import pytest

from src.config import DEFAULT_WEIGHTS
from src.data.validators import merge_energy_and_ndc, validate_energy_data
from src.models.gap import compute_gap
from src.models.ranking import (
    classify_countries,
    get_hidden_champions,
    get_laggards,
    get_rankings,
)
from src.models.scoring import compute_green_score


@pytest.fixture
def energy_df():
    return pd.DataFrame({
        "iso_code": ["IND", "IND", "USA", "USA", "CHN", "CHN"],
        "year": [2020, 2021, 2020, 2021, 2020, 2021],
        "country": [
            "India", "India", "United States",
            "United States", "China", "China",
        ],
        "solar_share_energy": [1.0, 1.5, 2.0, 3.0, 1.5, 2.0],
        "wind_share_energy": [0.5, 0.7, 3.5, 4.0, 1.0, 1.5],
        "hydro_share_energy": [10.0, 10.5, 6.0, 6.5, 8.0, 8.5],
        "nuclear_share_energy": [1.2, 1.3, 8.0, 8.5, 3.0, 3.2],
        "gas_share_energy": [5.0, 5.2, 32.0, 33.0, 8.0, 8.5],
        "coal_share_energy": [44.0, 43.0, 19.0, 18.0, 55.0, 54.0],
    })


@pytest.fixture
def ndc_data():
    return {
        "IND": {
            "iso_code": "IND",
            "ghg_target": 47.0,
            "ghg_target_type": "Intensity",
            "pledge_base_year": "2005",
            "pledge_target_year": "2035",
        },
        "USA": {
            "iso_code": "USA",
            "ghg_target": 50.0,
            "ghg_target_type": "Absolute",
            "pledge_base_year": "2005",
            "pledge_target_year": "2030",
        },
        "CHN": {
            "iso_code": "CHN",
            "ghg_target": 65.0,
            "pledge_base_year": "2005",
            "pledge_target_year": "2030",
        },
    }


class TestFullPipeline:
    """OWID → Scoring → Gap → Classification"""

    def test_end_to_end_flow(self, energy_df, ndc_data):
        scored = compute_green_score(energy_df, dict(DEFAULT_WEIGHTS))
        assert "green_score" in scored.columns

        year_2021 = scored[scored["year"] == 2021].copy()
        assert len(year_2021) == 3

        gap_df = compute_gap(year_2021, ndc_data, 2021)
        assert "gap" in gap_df.columns
        assert "expected_trajectory" in gap_df.columns

        classified = classify_countries(gap_df)
        assert "classification" in classified.columns
        assert set(classified["classification"]).issubset(
            {"hidden_champion", "on_track", "slightly_behind", "laggard", "no_data"}
        )

    def test_rankings_partitions_all_countries(self, energy_df, ndc_data):
        scored = compute_green_score(energy_df, dict(DEFAULT_WEIGHTS))
        year_2021 = scored[scored["year"] == 2021].copy()
        gap_df = compute_gap(year_2021, ndc_data, 2021)
        classified = classify_countries(gap_df)

        laggards = get_laggards(classified)
        champions = get_hidden_champions(classified)
        all_rankings = get_rankings(classified)

        total_classified = len(laggards) + len(champions)
        assert total_classified <= len(all_rankings)

    def test_green_score_and_gap_correlate(self, energy_df, ndc_data):
        scored = compute_green_score(energy_df, dict(DEFAULT_WEIGHTS))
        year_2021 = scored[scored["year"] == 2021].copy()
        gap_df = compute_gap(year_2021, ndc_data, 2021)

        for _, row in gap_df.iterrows():
            assert row["gap"] == pytest.approx(
                row["green_score"] - row["expected_trajectory"], abs=0.01
            )


class TestValidationAndMerge:
    """validate_energy_data → merge → validate_ndc_data"""

    def test_merge_preserves_energy_data(self, energy_df, ndc_data):
        merged = merge_energy_and_ndc(energy_df, ndc_data)
        assert len(merged) == len(energy_df)
        assert "ghg_target" in merged.columns

    def test_merge_adds_ndc_fields(self, energy_df, ndc_data):
        merged = merge_energy_and_ndc(energy_df, ndc_data)
        ind_row = merged[merged["iso_code"] == "IND"].iloc[0]
        assert ind_row["ghg_target"] == 47.0
        assert ind_row["pledge_base_year"] == "2005"

    def test_valid_data_passes_validation(self, energy_df):
        errors = validate_energy_data(energy_df)
        assert errors == []


class TestScoringToRanking:
    """Scoring weights → different rankings"""

    def test_different_weights_different_rankings(self, energy_df, ndc_data):
        weights_a = {
            "solar_share_energy": 2.0,
            "wind_share_energy": 1.0,
            "hydro_share_energy": 1.0,
            "nuclear_share_energy": 0.5,
            "gas_share_energy": 0.2,
            "coal_share_energy": 0.0,
        }
        weights_b = {
            "solar_share_energy": 0.0,
            "wind_share_energy": 0.0,
            "hydro_share_energy": 0.0,
            "nuclear_share_energy": 0.0,
            "gas_share_energy": 0.0,
            "coal_share_energy": 1.0,
        }

        scored_a = compute_green_score(energy_df, weights_a)
        scored_b = compute_green_score(energy_df, weights_b)

        year_a = scored_a[scored_a["year"] == 2021].copy()
        year_b = scored_b[scored_b["year"] == 2021].copy()

        gap_a = compute_gap(year_a, ndc_data, 2021)
        gap_b = compute_gap(year_b, ndc_data, 2021)

        rankings_a = get_rankings(classify_countries(gap_a))
        rankings_b = get_rankings(classify_countries(gap_b))

        assert not rankings_a["gap"].equals(rankings_b["gap"])


class TestNoNdcCountries:
    """Countries without NDC data should get gap = green_score"""

    def test_no_ndc_gap_equals_score(self, energy_df):
        scored = compute_green_score(energy_df, dict(DEFAULT_WEIGHTS))
        year_2021 = scored[scored["year"] == 2021].copy()
        gap_df = compute_gap(year_2021, {}, 2021)

        for _, row in gap_df.iterrows():
            assert row["expected_trajectory"] == 0.0
            assert row["gap"] == pytest.approx(row["green_score"], abs=0.01)
