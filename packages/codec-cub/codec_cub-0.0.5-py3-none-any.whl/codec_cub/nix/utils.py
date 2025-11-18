"""A set of utility functions for CodecCub."""

from codec_cub.common import first_token
from funcy_bear.constants.characters import DASH, UNDERSCORE


def is_bare_identifier(s: str) -> bool:
    """Return True if s is a valid bare identifier in Nix.

    Args:
        s: The string to check.

    Returns:
        True if s is a valid bare identifier, False otherwise.
    """
    if not s:
        return False
    first: str = first_token(s)
    if not (first.isalpha() or first == UNDERSCORE):
        return False
    return all(ch.isalnum() or ch in {UNDERSCORE, DASH} for ch in s[1:])
