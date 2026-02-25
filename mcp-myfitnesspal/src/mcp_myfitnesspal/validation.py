from __future__ import annotations

import re
from datetime import date as _date

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date(value: str, param_name: str = "date") -> None:
    """Raise ValueError if value is not a valid YYYY-MM-DD calendar date."""
    if not _DATE_RE.match(value):
        raise ValueError(f"Invalid {param_name}: {value!r}. Expected YYYY-MM-DD.")
    try:
        _date.fromisoformat(value)
    except ValueError as err:
        raise ValueError(
            f"Invalid {param_name}: {value!r}. Expected a real calendar date."
        ) from err


def validate_date_range(start: str, end: str) -> None:
    """Raise ValueError if start/end are not valid YYYY-MM-DD dates or range is invalid."""
    validate_date(start, param_name="start_date")
    validate_date(end, param_name="end_date")
    start_dt = _date.fromisoformat(start)
    end_dt = _date.fromisoformat(end)
    if start_dt > end_dt:
        raise ValueError(f"start_date {start!r} must be on or before end_date {end!r}.")
    if (end_dt - start_dt).days > 365:
        raise ValueError(f"Date range exceeds 365 days ({start} to {end}).")
