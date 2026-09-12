import pytest

from mcp_hevy.validation import validate_non_empty_str, validate_positive_int


def test_validate_positive_int_returns_parsed_value() -> None:
    assert validate_positive_int(3, "page", default=1) == 3


def test_validate_positive_int_returns_default_when_none() -> None:
    assert validate_positive_int(None, "page", default=1) == 1


def test_validate_positive_int_accepts_numeric_string() -> None:
    assert validate_positive_int("7", "page", default=1) == 7


def test_validate_positive_int_rejects_zero() -> None:
    with pytest.raises(ValueError, match="page"):
        validate_positive_int(0, "page", default=1)


def test_validate_positive_int_rejects_negative() -> None:
    with pytest.raises(ValueError, match="page"):
        validate_positive_int(-1, "page", default=1)


def test_validate_positive_int_rejects_non_numeric() -> None:
    with pytest.raises(ValueError, match="page"):
        validate_positive_int("abc", "page", default=1)


def test_validate_non_empty_str_accepts_non_empty() -> None:
    validate_non_empty_str("abc123", "workout_id")  # does not raise


def test_validate_non_empty_str_rejects_empty() -> None:
    with pytest.raises(ValueError, match="workout_id"):
        validate_non_empty_str("", "workout_id")
