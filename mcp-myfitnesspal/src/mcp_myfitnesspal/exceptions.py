from __future__ import annotations


class MFPShapeError(Exception):
    """Raised when a MyFitnessPal response is missing expected fields.

    This typically means MyFitnessPal changed their HTML structure.
    The fix is to update the python-myfitnesspal library.
    """


_DAY_ATTRS = ("meals", "totals", "goals")


def validate_day_shape(day: object, date: str) -> None:
    """Raise MFPShapeError if the Day object is missing expected attributes."""
    missing = [attr for attr in _DAY_ATTRS if not hasattr(day, attr)]
    if missing:
        raise MFPShapeError(
            f"MFP response for {date} is missing fields: {missing}. "
            "MyFitnessPal may have changed their format — "
            "check for python-myfitnesspal updates."
        )
