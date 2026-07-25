"""Tests for country code mapping and aggregate detection."""

from src.data.country_codes import AGGREGATE_NAMES, is_aggregate, normalize_iso3


class TestNormalizeIso3:
    def test_normal_uppercase(self):
        assert normalize_iso3("IND") == "IND"

    def test_lowercase_input(self):
        assert normalize_iso3("ind") == "IND"

    def test_leading_trailing_spaces(self):
        assert normalize_iso3("  IND  ") == "IND"

    def test_empty_string(self):
        assert normalize_iso3("") == ""

    def test_none_input(self):
        assert normalize_iso3(None) == ""

    def test_non_string_input(self):
        assert normalize_iso3(123) == ""

    def test_long_name_truncated(self):
        assert normalize_iso3("INDONESIA") == "IND"

    def test_short_code(self):
        assert normalize_iso3("IN") == "IN"

    def test_mixed_case_with_spaces(self):
        assert normalize_iso3("  Usa  ") == "USA"

    def test_unknown_code_passthrough(self):
        # No validation or fallback lookup: unknown codes pass through.
        assert normalize_iso3("xyz") == "XYZ"

    def test_whitespace_only(self):
        assert normalize_iso3("   ") == ""

    def test_non_string_float_nan(self):
        assert normalize_iso3(float("nan")) == ""

    def test_non_string_list(self):
        assert normalize_iso3(["IND"]) == ""


class TestIsAggregate:
    def test_world_is_aggregate(self):
        assert is_aggregate("World") is True

    def test_india_not_aggregate(self):
        assert is_aggregate("India") is False

    def test_russia_not_aggregate(self):
        assert is_aggregate("Russia") is False

    def test_africa_is_aggregate(self):
        assert is_aggregate("Africa") is True

    def test_empty_string(self):
        assert is_aggregate("") is False

    def test_unknown_country(self):
        assert is_aggregate("Narnia") is False

    def test_all_aggregates_are_strings(self):
        for name in AGGREGATE_NAMES:
            assert isinstance(name, str)

    def test_no_leading_spaces_in_aggregates(self):
        for name in AGGREGATE_NAMES:
            assert name == name.strip(), f"Aggregate has whitespace: '{name}'"
