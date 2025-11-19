"""A set of utility functions for CodecCub."""

from funcy_bear.constants.characters import DASH, UNDERSCORE
from funcy_bear.ops.strings.manipulation import first_item


def is_bare_identifier(s: str) -> bool:
    """Return True if s is a valid bare identifier in Nix.

    Args:
        s: The string to check.

    Returns:
        True if s is a valid bare identifier, False otherwise.
    """
    if not s:
        return False
    first: str = first_item(s)
    if not (first.isalpha() or first == UNDERSCORE):
        return False
    return all(ch.isalnum() or ch in {UNDERSCORE, DASH} for ch in s[1:])
