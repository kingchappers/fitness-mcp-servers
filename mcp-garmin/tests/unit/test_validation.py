import pytest

from mcp_garmin.validation import validate_date


def test_valid_date_passes() -> None:
    validate_date("2026-02-20")  # should not raise


def test_invalid_format_raises() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("20-02-2026")


def test_non_date_string_raises() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("not-a-date")


def test_empty_string_raises() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("")


def test_custom_param_name_in_error() -> None:
    with pytest.raises(ValueError, match="start_date"):
        validate_date("bad", param_name="start_date")


def test_impossible_month_raises() -> None:
    with pytest.raises(ValueError, match="real calendar date"):
        validate_date("2026-13-01")


def test_impossible_day_raises() -> None:
    with pytest.raises(ValueError, match="real calendar date"):
        validate_date("2026-02-30")
