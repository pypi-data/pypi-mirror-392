"""Utility functions for TOON codec."""

from __future__ import annotations

from decimal import Decimal
import math
import re
from typing import TYPE_CHECKING, Any, NamedTuple

from codec_cub.common import E_LITERAL, N_LITERAL, R_LITERAL, T_LITERAL, ZERO_QUOTE
from codec_cub.toon.constants import (
    BACKSLASH,
    CARRIAGE_RETURN,
    COLON,
    COMMA,
    DOUBLE_QUOTE,
    FALSE_LITERAL,
    LIST_ITEM_MARKER,
    NEWLINE,
    NULL_LITERAL,
    PIPE,
    TAB,
    TRUE_LITERAL,
)
from funcy_bear.constants.characters import DOT

if TYPE_CHECKING:
    from _collections_abc import dict_keys


def return_escaped(ch: str) -> str:
    """Return escaped version of a character for TOON strings."""
    if ch == BACKSLASH:
        return f"\\{BACKSLASH}"
    if ch == DOUBLE_QUOTE:
        return f"\\{DOUBLE_QUOTE}"
    if ch == NEWLINE:
        return f"\\{N_LITERAL}"
    if ch == CARRIAGE_RETURN:
        return f"\\{R_LITERAL}"
    if ch == TAB:
        return f"\\{T_LITERAL}"
    return ch


def is_identifier_segment(s: str) -> bool:
    """Check if string is a valid identifier segment for safe folding/expansion.

    Must match: ^[A-Za-z_][A-Za-z0-9_]*$ (no dots allowed).
    """
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", s))


def is_valid_unquoted_key(s: str) -> bool:
    """Check if string can be used as an unquoted key.

    Must match: ^[A-Za-z_][A-Za-z0-9_.]*$
    """
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", s))


def is_numeric_like(s: str) -> bool:
    """Check if string looks like a number."""
    if re.match(r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$", s):
        return True
    return bool(re.match(r"^0\d+$", s))


def needs_quoting(value: str, delimiter: str) -> bool:
    """Determine if a string value needs quoting per TOON spec §7.2.

    Args:
        value: The string value to check
        delimiter: The active delimiter (comma, tab, or pipe)

    Returns:
        True if the value must be quoted
    """
    return (
        not value
        or value != value.strip()
        or value in (TRUE_LITERAL, FALSE_LITERAL, NULL_LITERAL)
        or is_numeric_like(value)
        or any(ch in value for ch in "[]{}")
        or any(ch in value for ch in (NEWLINE, CARRIAGE_RETURN, TAB))
        or any(ch in value for ch in (COLON, DOUBLE_QUOTE, BACKSLASH))
        or delimiter in value
        or value.startswith(LIST_ITEM_MARKER)
        or value == LIST_ITEM_MARKER
    )


def escape_string(s: str) -> str:
    r"""Escape a string for TOON format per §7.1.

    Only escapes: \\, ", \n, \r, \t
    """
    result: list[str] = []
    for ch in s:
        result.append(return_escaped(ch))
    return "".join(result)


def quote_string(value: str, delimiter: str) -> str:
    """Quote and escape a string if needed.

    Args:
        value: The string value
        delimiter: The active delimiter

    Returns:
        Quoted and escaped string, or unquoted if safe
    """
    if needs_quoting(value, delimiter):
        return f'"{escape_string(value)}"'
    return value


def encode_key(key: str) -> str:
    """Encode an object key per §7.3.

    Keys must be quoted unless they match: ^[A-Za-z_][A-Za-z0-9_.]*$
    """
    if is_valid_unquoted_key(key):
        return key
    return f'"{escape_string(key)}"'


def normalize_number(value: float) -> str | None:
    """Normalize a number to canonical TOON form per §2.

    Returns:
        Canonical string representation, or None for non-finite values
    """
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        if value == 0.0:
            return ZERO_QUOTE
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if E_LITERAL in text.lower():
        dec = Decimal(text)
        text: str = format(dec, "f")
    if DOT in text:
        text = text.rstrip(ZERO_QUOTE).rstrip(DOT)
    return text or ZERO_QUOTE


def get_delimiter_char(delimiter: str) -> str:
    """Get the delimiter character for array headers.

    Returns empty string for comma (default), TAB for tab, "|" for pipe.
    """
    return "" if delimiter == COMMA else TAB if delimiter == TAB else PIPE if delimiter == PIPE else ""


class TabularArray(NamedTuple):
    """Result of tabular array detection."""

    is_tabular: bool
    field_names: list[str]

    @classmethod
    def create(cls, field_names: list[str]) -> TabularArray:
        """Return success result."""
        return TabularArray(is_tabular=True, field_names=field_names)

    @classmethod
    def nulled(cls) -> TabularArray:
        """Return failure result."""
        return TabularArray(is_tabular=False, field_names=[])


def detect_tabular_array(items: list[Any]) -> TabularArray:
    """Detect if array qualifies for tabular format per §9.3.

    Returns:
        (is_tabular, field_names) - field_names is empty if not tabular
    """
    if not items or not all(isinstance(item, dict) for item in items) or not items[0]:
        return TabularArray.nulled()
    item_dicts: list[dict[str, Any]] = items
    keys: dict_keys[str, Any] = item_dicts[0].keys()
    first_keys: set[str] = set(keys)
    for item in item_dicts[1:]:
        if set(item.keys()) != first_keys:
            return TabularArray.nulled()
    for item in item_dicts:
        for value in item.values():
            if isinstance(value, (dict, list)):
                return TabularArray.nulled()
    return TabularArray.create(list(keys))
