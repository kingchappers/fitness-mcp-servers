# tests/unit/test_validation.py
import pytest
from mcp_myfitnesspal.validation import validate_date, validate_date_range


def test_validate_date_accepts_valid() -> None:
    validate_date("2026-02-25")  # should not raise


def test_validate_date_rejects_wrong_format() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("25-02-2026")


def test_validate_date_rejects_invalid_calendar_date() -> None:
    with pytest.raises(ValueError):
        validate_date("2026-02-30")


def test_validate_date_range_accepts_valid() -> None:
    validate_date_range("2026-02-01", "2026-02-25")  # should not raise


def test_validate_date_range_rejects_reversed_range() -> None:
    with pytest.raises(ValueError, match="start_date"):
        validate_date_range("2026-02-25", "2026-02-01")


def test_validate_date_range_rejects_range_over_365_days() -> None:
    with pytest.raises(ValueError, match="365"):
        validate_date_range("2024-01-01", "2026-01-02")


def test_validate_date_range_rejects_exactly_365_day_difference() -> None:
    # 2025-01-01 to 2026-01-01 is exactly 365 day difference (366 inclusive days) — must be rejected
    # 2025 is not a leap year so this is unambiguously 365 days
    with pytest.raises(ValueError, match="365"):
        validate_date_range("2025-01-01", "2026-01-01")


def test_validate_date_range_accepts_364_day_difference() -> None:
    # 2025-01-01 to 2025-12-31 is 364 day difference (365 inclusive days) — should be accepted
    validate_date_range("2025-01-01", "2025-12-31")  # should not raise


def test_validate_date_range_rejects_bad_start_date() -> None:
    with pytest.raises(ValueError, match="start_date"):
        validate_date_range("bad", "2026-02-25")


def test_validate_date_range_rejects_bad_end_date() -> None:
    with pytest.raises(ValueError, match="end_date"):
        validate_date_range("2026-02-01", "bad")
