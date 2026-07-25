"""Tests for Climate Watch NDC API client."""

from unittest.mock import MagicMock, patch

from src.data.cache import clear_cache
from src.data.climate_watch import (
    _parse_ghg_percentage,
    _parse_ndc_entry,
    fetch_all_ndcs,
)


class TestParseGhgPercentage:
    def test_range_percent(self):
        assert _parse_ghg_percentage("33 to 35 percent") == 34.0

    def test_range_dash(self):
        assert _parse_ghg_percentage("33-35%") == 34.0

    def test_range_decimals(self):
        assert _parse_ghg_percentage("33.5 to 35.5 percent") == 34.5

    def test_single_percent(self):
        assert _parse_ghg_percentage("45%") == 45.0

    def test_single_word(self):
        assert _parse_ghg_percentage("47 percent") == 47.0

    def test_per_cent(self):
        assert _parse_ghg_percentage("40 per cent") == 40.0

    def test_bare_number_with_keyword(self):
        assert _parse_ghg_percentage("reduce emissions by 30%") == 30.0

    def test_no_numbers(self):
        assert _parse_ghg_percentage("no numbers here") is None

    def test_none_input(self):
        assert _parse_ghg_percentage(None) is None

    def test_empty_string(self):
        assert _parse_ghg_percentage("") is None

    def test_non_string_input(self):
        assert _parse_ghg_percentage(123) is None

    def test_float_number(self):
        assert _parse_ghg_percentage("22.5%") == 22.5

    def test_target_prefix(self):
        assert _parse_ghg_percentage("Target: 45%") == 45.0


class TestParseNdcEntry:
    def test_valid_entry(self):
        entry = {
            "ndc_text": "Test NDC",
            "indicators": [
                {"name": "GHG Target", "value": "45%"},
                {"name": "Target Year", "value": "2030"},
            ],
        }
        result = _parse_ndc_entry(entry, "IND")
        assert result is not None
        assert result["iso_code"] == "IND"
        assert result["ghg_target"] == 45.0
        assert result["pledge_target_year"] == "2030"

    def test_no_indicators(self):
        entry = {"ndc_text": "Test", "indicators": []}
        result = _parse_ndc_entry(entry, "IND")
        assert result is None

    def test_no_matching_indicators(self):
        entry = {
            "ndc_text": "Test",
            "indicators": [
                {"name": "unrelated_field", "value": "something"},
            ],
        }
        result = _parse_ndc_entry(entry, "IND")
        assert result is not None
        assert result["ghg_target"] is None

    def test_numeric_target_value(self):
        entry = {
            "ndc_text": "Test",
            "indicators": [
                {"name": "GHG Target", "value": 45},
            ],
        }
        result = _parse_ndc_entry(entry, "IND")
        assert result is not None
        assert result["ghg_target"] == 45.0


class TestFetchAllNdc:
    def setup_method(self):
        clear_cache()

    @patch("src.data.climate_watch.requests.get")
    def test_successful_bulk_fetch(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": [
                {
                    "iso_code3": "IND",
                    "ndc_text": "India NDC",
                    "indicators": [
                        {"name": "GHG Target", "value": "47%"},
                    ],
                },
                {
                    "iso_code3": "USA",
                    "ndc_text": "US NDC",
                    "indicators": [
                        {"name": "GHG Target", "value": "50%"},
                    ],
                },
            ]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = fetch_all_ndcs()
        assert "IND" in result
        assert "USA" in result
        assert result["IND"]["ghg_target"] == 47.0

    @patch("src.data.climate_watch.requests.get")
    def test_bulk_fetch_network_failure(self, mock_get):
        import requests

        mock_get.side_effect = requests.RequestException("timeout")
        result = fetch_all_ndcs()
        assert result == {}

    @patch("src.data.climate_watch.requests.get")
    def test_bulk_fetch_empty_response(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": []}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        result = fetch_all_ndcs()
        assert result == {}

    @patch("src.data.climate_watch.requests.get")
    def test_bulk_fetch_malformed_json(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.side_effect = ValueError("bad json")
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        result = fetch_all_ndcs()
        assert result == {}

    @patch("src.data.climate_watch.requests.get")
    def test_cached_second_call(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": [
                {
                    "iso_code3": "USA",
                    "ndc_text": "US NDC",
                    "indicators": [
                        {"name": "GHG Target", "value": "50%"},
                    ],
                }
            ]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result1 = fetch_all_ndcs()
        result2 = fetch_all_ndcs()
        assert mock_get.call_count == 1
        assert result1 == result2
