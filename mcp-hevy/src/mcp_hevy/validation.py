from __future__ import annotations


def validate_positive_int(
    value: object, param_name: str, default: int, maximum: int | None = None
) -> int:
    """Return `default` if value is None, else parse and validate it as a positive int.

    If `maximum` is given, raises ValueError when the parsed value exceeds it.
    """
    if value is None:
        return default
    if not isinstance(value, (int, str, float)) or isinstance(value, bool):
        raise ValueError(f"Invalid {param_name}: {value!r}. Expected an integer.")
    try:
        result = int(value)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid {param_name}: {value!r}. Expected an integer.") from err
    if result < 1:
        raise ValueError(f"Invalid {param_name}: {value!r}. Must be 1 or greater.")
    if maximum is not None and result > maximum:
        raise ValueError(f"Invalid {param_name}: {value!r}. Must be {maximum} or less.")
    return result


def validate_non_empty_str(value: object, param_name: str) -> str:
    """Raise ValueError if value is empty or not a string; otherwise return it."""
    if not value or not isinstance(value, str):
        raise ValueError(f"{param_name} is required and must not be empty.")
    return value
