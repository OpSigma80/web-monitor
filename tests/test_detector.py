"""Tests for app.services.detector — change detection and summaries.

Pure logic: no database, no network, no Telegram.
"""

from app.services.detector import (
    build_summary,
    extract_number,
    has_significant_change,
    normalize_text,
)


class TestNormalizeText:
    def test_strips_and_collapses_whitespace(self):
        assert normalize_text("  hello \n\t world  ") == "hello world"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_already_clean(self):
        assert normalize_text("Bitcoin price") == "Bitcoin price"


class TestExtractNumber:
    def test_plain_integer(self):
        assert extract_number("100") == 100.0

    def test_currency_with_thousands_and_decimals(self):
        assert extract_number("$1,234.56") == 1234.56

    def test_european_format(self):
        assert extract_number("1.234,56 €") == 1234.56

    def test_decimal_comma_only(self):
        assert extract_number("12,5") == 12.5

    def test_negative(self):
        assert extract_number("-42.5") == -42.5

    def test_no_number_returns_none(self):
        assert extract_number("no value yet") is None

    def test_empty_returns_none(self):
        assert extract_number("") is None
        assert extract_number(None) is None


class TestHasSignificantChange:
    def test_same_value_is_not_a_change(self):
        assert has_significant_change("100", "100") is False

    def test_whitespace_only_difference_is_not_a_change(self):
        assert has_significant_change("  hello   world ", "hello world") is False

    def test_different_text_is_a_change(self):
        assert has_significant_change("In stock", "Out of stock") is True

    def test_first_value_counts_as_change(self):
        assert has_significant_change(None, "100") is True

    def test_below_threshold_is_not_significant(self):
        # 100 -> 105 is +5%, threshold is 10%
        assert has_significant_change("100", "105", threshold_percent=10) is False

    def test_at_threshold_is_significant(self):
        # 100 -> 110 is exactly +10%
        assert has_significant_change("100", "110", threshold_percent=10) is True

    def test_above_threshold_is_significant(self):
        assert has_significant_change("100", "150", threshold_percent=10) is True

    def test_threshold_with_non_numeric_falls_back_to_text_change(self):
        assert has_significant_change("open", "closed", threshold_percent=10) is True

    def test_threshold_ignored_when_old_is_zero(self):
        assert has_significant_change("0", "5", threshold_percent=50) is True


class TestBuildSummary:
    def test_numeric_rise(self):
        assert build_summary("BTC", "100", "110") == (
            "[BTC] The value rose from 100 to 110 (+10.00 / +10.0%)"
        )

    def test_numeric_fall(self):
        assert build_summary("BTC", "100", "90") == (
            "[BTC] The value fell from 100 to 90 (-10.00 / -10.0%)"
        )

    def test_text_change(self):
        assert build_summary("Shop", "In stock", "Out of stock") == (
            '[Shop] Changed from "In stock" to "Out of stock"'
        )

    def test_no_previous_value(self):
        assert build_summary("BTC", None, "100") == (
            '[BTC] Changed from "(no previous value)" to "100"'
        )
