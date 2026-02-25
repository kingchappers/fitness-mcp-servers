import pytest
from mcp_myfitnesspal.exceptions import MFPShapeError, validate_day_shape


def test_mfp_shape_error_is_exception() -> None:
    err = MFPShapeError("test")
    assert isinstance(err, Exception)


def test_validate_day_shape_passes_valid_object() -> None:
    class FakeDay:
        meals = []
        totals = {}
        goals = {}

    validate_day_shape(FakeDay(), "2026-02-25")  # should not raise


def test_validate_day_shape_raises_on_missing_attr() -> None:
    class BrokenDay:
        meals = []
        # missing totals and goals

    with pytest.raises(MFPShapeError, match="totals"):
        validate_day_shape(BrokenDay(), "2026-02-25")


def test_validate_day_shape_error_message_mentions_mfp() -> None:
    class BrokenDay:
        pass

    with pytest.raises(MFPShapeError, match="MyFitnessPal"):
        validate_day_shape(BrokenDay(), "2026-02-25")
