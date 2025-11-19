"""A set of common utilities for CodecCub."""

from typing import Any

from funcy_bear.constants.characters import SPACE
from funcy_bear.constants.escaping import COMMA_SPACE


def first(obj: Any) -> Any:
    """Return the first item of a sequence or the object itself if not a sequence.

    Args:
        obj: The object to get the first item from.

    Returns:
        The first item of the sequence or the object itself.
    """
    try:
        return obj[0]
    except (TypeError, IndexError):
        return obj


def spaced(s: str) -> str:
    """Return the string with a leading and trailing space.

    Args:
        s: The string to space.

    Returns:
        The spaced string.
    """
    return f"{SPACE}{s}{SPACE}"


def comma_sep(items: list[str]) -> str:
    """Return a comma-separated string from a list of strings.

    Args:
        items: The list of strings.

    Returns:
        The comma-separated string.
    """
    return COMMA_SPACE.join(items)


def piped(*segs: object) -> str:
    """Join segments with pipe character.

    Args:
        *segs: The segments to join.

    Returns:
        The joined string.
    """
    return " | ".join(str(seg) for seg in segs)


TWO = 2


__all__ = ["COMMA_SPACE", "TWO", "comma_sep", "first", "piped", "spaced"]
