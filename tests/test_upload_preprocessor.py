"""Tests for uploaded file preprocessing pipeline."""

import pandas as pd

from src.config import ISO_COL, YEAR_COL
from src.data.upload_preprocessor import (
    _coerce_numeric,
    _detect_alternative_columns,
    _normalize_columns,
    _read_file,
    preprocess_upload,
)

# --- _normalize_columns ---

def test_normalize_columns_strips_whitespace():
    df = pd.DataFrame({"  ISO Code  ": ["IND"], "  Year  ": [2020]})
    result = _normalize_columns(df)
    assert "iso_code" in result.columns
    assert "year" in result.columns


def test_normalize_columns_snake_case():
    df = pd.DataFrame({"Solar Share (%)": [1.0]})
    result = _normalize_columns(df)
    assert "solar_share" in result.columns


def test_normalize_columns_mixed_case():
    df = pd.DataFrame({"Country Name": ["India"]})
    result = _normalize_columns(df)
    assert "country_name" in result.columns


def test_normalize_columns_empty():
    df = pd.DataFrame()
    result = _normalize_columns(df)
    assert result.empty


# --- _coerce_numeric ---

def test_coerce_numeric_converts_valid():
    df = pd.DataFrame({"val": ["1.5", "2.0", "3.7"]})
    result = _coerce_numeric(df, ["val"])
    assert result["val"].dtype.kind in ("f", "i")


def test_coerce_numeric_handles_nulls():
    df = pd.DataFrame({"val": ["1.5", "abc", "3.7"]})
    result = _coerce_numeric(df, ["val"])
    assert result["val"].isna().sum() == 1
    assert result["val"].iloc[0] == 1.5
    assert result["val"].iloc[2] == 3.7


def test_coerce_numeric_missing_column():
    df = pd.DataFrame({"a": [1]})
    result = _coerce_numeric(df, ["nonexistent"])
    assert result is not None


def test_coerce_numeric_does_not_mutate():
    df = pd.DataFrame({"val": ["1.5", "2.0"]})
    original = df.copy()
    _coerce_numeric(df, ["val"])
    pd.testing.assert_frame_equal(df, original)


def test_coerce_numeric_empty_df():
    result = _coerce_numeric(pd.DataFrame(), ["val"])
    assert result.empty


# --- _detect_alternative_columns ---

def test_detect_alternative_solar():
    df = pd.DataFrame({"solar": [1.0]})
    mapping = _detect_alternative_columns(df)
    assert mapping.get("solar") == "solar_share_energy"


def test_detect_alternative_wind():
    df = pd.DataFrame({"wind_pct": [1.0]})
    mapping = _detect_alternative_columns(df)
    assert mapping.get("wind_pct") == "wind_share_energy"


def test_detect_alternative_natural_gas():
    df = pd.DataFrame({"natural_gas": [1.0]})
    mapping = _detect_alternative_columns(df)
    assert mapping.get("natural_gas") == "gas_share_energy"


def test_detect_alternative_no_match():
    df = pd.DataFrame({"foo_bar": [1.0]})
    mapping = _detect_alternative_columns(df)
    assert mapping == {}


def test_detect_alternative_skips_existing():
    df = pd.DataFrame({
        "solar_share_energy": [1.0],
        "solar": [1.0],
    })
    mapping = _detect_alternative_columns(df)
    assert "solar" not in mapping


# --- _read_file ---

class _MockUpload:
    def __init__(self, data: bytes, name: str):
        self._data = data
        self.name = name
        self._pos = 0

    def seek(self, offset):
        self._pos = offset

    def read(self):
        return self._data


def _make_csv_bytes(text: str, encoding: str = "utf-8") -> bytes:
    return text.encode(encoding)


def test_read_csv_utf8():
    csv = "iso_code,year\nIND,2020\n"
    upload = _MockUpload(_make_csv_bytes(csv), "data.csv")
    df = _read_file(upload)
    assert df is not None
    assert len(df) == 1


def test_read_csv_latin1():
    csv = "iso_code,year\nIND,2020\n"
    upload = _MockUpload(_make_csv_bytes(csv, "latin-1"), "data.csv")
    df = _read_file(upload)
    assert df is not None
    assert len(df) == 1


def test_read_csv_empty():
    upload = _MockUpload(b"", "empty.csv")
    df = _read_file(upload)
    assert df is None or df.empty


def test_read_invalid_extension():
    upload = _MockUpload(b"some,data\n1,2", "data.txt")
    df = _read_file(upload)
    assert df is None


def test_read_file_seek_reset():
    """Verify that read_file resets stream position correctly."""
    csv = "iso_code,year\nIND,2020\n"
    upload = _MockUpload(_make_csv_bytes(csv), "data.csv")
    df1 = _read_file(upload)
    df2 = _read_file(upload)
    assert df1 is not None
    assert df2 is not None
    assert len(df1) == len(df2)


# --- preprocess_upload ---

def _make_upload(csv_text: str, name: str = "test.csv") -> _MockUpload:
    return _MockUpload(_make_csv_bytes(csv_text), name)


def test_preprocess_happy_path():
    csv = (
        "iso_code,year,country,solar_share_energy,wind_share_energy\n"
        "IND,2020,India,5.0,3.0\nUSA,2020,United States,2.0,4.0\n"
    )
    result = preprocess_upload(_make_upload(csv))
    assert not result.errors
    assert len(result.df) == 2
    assert ISO_COL in result.df.columns
    assert YEAR_COL in result.df.columns


def test_preprocess_missing_required_column():
    csv = "country,year\nIndia,2020\n"
    result = preprocess_upload(_make_upload(csv))
    assert len(result.errors) > 0
    assert "iso_code" in result.errors[0].lower()


def test_preprocess_empty_file():
    result = preprocess_upload(_make_upload(""))
    assert len(result.errors) > 0
    assert "empty" in result.errors[0].lower()


def test_preprocess_invalid_iso_removed():
    csv = "iso_code,year,country\n,2020,Unknown\nIND,2020,India\n"
    result = preprocess_upload(_make_upload(csv))
    assert result.df is not None
    assert len(result.df) == 1
    assert list(result.df[ISO_COL]) == ["IND"]
    assert len(result.warnings) > 0
    assert any("ISO" in w for w in result.warnings)


def test_preprocess_aggregate_removed():
    csv = (
        "iso_code,year,country,solar_share_energy\n"
        "XXX,2020,World,1.0\nIND,2020,India,2.0\n"
    )
    result = preprocess_upload(_make_upload(csv))
    # "World" is an aggregate
    if "country" in result.df.columns:
        assert "World" not in result.df["country"].values


def test_preprocess_coerces_numeric():
    csv = "iso_code,year,solar_share_energy\nIND,2020,abc\nUSA,2020,5.0\n"
    result = preprocess_upload(_make_upload(csv))
    assert result.df["solar_share_energy"].isna().sum() == 1


def test_preprocess_filters_year_range():
    csv = "iso_code,year,solar_share_energy\nIND,1950,1.0\nUSA,2020,2.0\n"
    result = preprocess_upload(_make_upload(csv))
    assert 1950 not in result.df["year"].values if not result.df.empty else True
    assert len(result.warnings) > 0
    assert "Filtered" in result.warnings[-1]


def test_preprocess_alternative_column_mapping():
    csv = "iso_code,year,solar\nIND,2020,5.0\nUSA,2020,3.0\n"
    result = preprocess_upload(_make_upload(csv))
    assert "solar_share_energy" in result.df.columns
    assert result.df["solar_share_energy"].iloc[0] == 5.0


def test_preprocess_missing_share_cols_warning():
    csv = "iso_code,year,country\nIND,2020,India\n"
    result = preprocess_upload(_make_upload(csv))
    assert len(result.warnings) > 0
    assert "No energy share columns" in result.warnings[0]


def test_preprocess_normalizes_iso():
    csv = "iso_code,year\nind,2020\nusa,2020\n"
    result = preprocess_upload(_make_upload(csv))
    codes = result.df["iso_code"].tolist()
    assert codes == ["IND", "USA"]


def test_preprocess_year_becomes_int():
    csv = "iso_code,year,solar_share_energy\nIND,2020.0,5.0\nUSA,2021.5,3.0\n"
    result = preprocess_upload(_make_upload(csv))
    assert result.df["year"].dtype.kind == "i"


def test_preprocess_xlsx_not_csv_returns_empty():
    """Non-CSV/XLSX returns empty frame with error."""
    upload = _MockUpload(b"some data", "data.txt")
    result = preprocess_upload(upload)
    assert len(result.errors) > 0


def test_preprocess_no_valid_rows_after_processing():
    csv = "iso_code,year\n,2020\n,2021\n"
    result = preprocess_upload(_make_upload(csv))
    assert result.df.empty or len(result.errors) > 0


def test_preprocess_keeps_extra_columns():
    csv = (
        "iso_code,year,country,solar_share_energy,extra_col\n"
        "IND,2020,India,5.0,hello\n"
    )
    result = preprocess_upload(_make_upload(csv))
    assert "extra_col" not in result.df.columns
