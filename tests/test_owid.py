"""Tests for OWID energy data ingestion."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from src.config import ISO_COL, OWID_CSV
from src.data.owid import download_owid_csv, get_owid_year_range, load_owid_data


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
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
        }
    )


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
        if not OWID_CSV.exists():
            pytest.skip("OWID CSV not available locally")
        result = load_owid_data()
        assert len(result) > 0
        assert ISO_COL in result.columns
        assert "year" in result.columns

    def test_filters_aggregates(self):
        if not OWID_CSV.exists():
            pytest.skip("OWID CSV not available locally")
        result = load_owid_data()
        assert "World" not in result["country"].values


class TestDownloadOwidCsv:
    def test_returns_existing_without_network(self, tmp_path, monkeypatch):
        target = tmp_path / "owid.csv"
        target.write_bytes(b"cached,data\n")
        monkeypatch.setattr("src.data.owid.OWID_CSV", target)
        with patch("src.data.owid.requests.get") as mock_get:
            result = download_owid_csv()
        assert result == target
        mock_get.assert_not_called()

    @patch("src.data.owid.requests.get")
    def test_downloads_and_writes_bytes(self, mock_get, tmp_path, monkeypatch):
        target = tmp_path / "raw" / "owid.csv"  # parent absent -> exercises mkdir
        monkeypatch.setattr("src.data.owid.OWID_CSV", target)
        mock_resp = MagicMock()
        mock_resp.content = b"iso_code,year\nIND,2020\n"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = download_owid_csv()

        assert result == target
        assert target.read_bytes() == b"iso_code,year\nIND,2020\n"
        mock_get.assert_called_once()

    @patch("src.data.owid.requests.get")
    def test_empty_response_writes_empty_file(self, mock_get, tmp_path, monkeypatch):
        target = tmp_path / "owid.csv"
        monkeypatch.setattr("src.data.owid.OWID_CSV", target)
        mock_resp = MagicMock()
        mock_resp.content = b""
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = download_owid_csv()

        assert result == target
        assert target.exists()
        assert target.read_bytes() == b""

    @patch("src.data.owid.requests.get")
    def test_network_failure_propagates(self, mock_get, tmp_path, monkeypatch):
        target = tmp_path / "owid.csv"
        monkeypatch.setattr("src.data.owid.OWID_CSV", target)
        mock_get.side_effect = requests.ConnectionError("no network")
        with pytest.raises(requests.RequestException):
            download_owid_csv()
        assert not target.exists()

    @patch("src.data.owid.requests.get")
    def test_http_error_propagates(self, mock_get, tmp_path, monkeypatch):
        target = tmp_path / "owid.csv"
        monkeypatch.setattr("src.data.owid.OWID_CSV", target)
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_resp
        with pytest.raises(requests.RequestException):
            download_owid_csv()
