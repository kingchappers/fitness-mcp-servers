from __future__ import annotations

from typing import cast


def validate_positive_int(value: object, param_name: str, default: int) -> int:
    """Return `default` if value is None, else parse and validate it as a positive int."""
    if value is None:
        return default
    try:
        result = cast(int, int(value))  # type: ignore[call-overload]
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid {param_name}: {value!r}. Expected an integer.") from err
    if result < 1:
        raise ValueError(f"Invalid {param_name}: {value!r}. Must be 1 or greater.")
    return result


def validate_non_empty_str(value: str, param_name: str) -> None:
    """Raise ValueError if value is empty."""
    if not value:
        raise ValueError(f"{param_name} is required and must not be empty.")
