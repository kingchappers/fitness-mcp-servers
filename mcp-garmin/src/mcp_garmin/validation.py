import re

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date(date: str, param_name: str = "date") -> None:
    """Raise ValueError if date is not in YYYY-MM-DD format."""
    if not _DATE_RE.match(date):
        raise ValueError(f"Invalid {param_name}: {date!r}. Expected YYYY-MM-DD.")
