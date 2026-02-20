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
