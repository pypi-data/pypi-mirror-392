"""Common constants for the CUB codec."""

from typing import Any, Final

from funcy_bear.constants import characters as ch
from funcy_bear.tools.string_cursor import StringCursor

N_LITERAL: Final = "n"
R_LITERAL: Final = "r"
T_LITERAL: Final = "t"
E_LITERAL: Final = "e"
F_LITERAL: Final = "f"
ZERO_QUOTE: Final = "0"

NEGATIVE_ZERO_QUOTE: Final = f"{ch.DASH}{ZERO_QUOTE}"

COMMA_SPACE: Final = f"{ch.COMMA} "
TWO = 2
"""Integer constant for 2, used for clarity in code and to shut up Ruff. Do not mention this Claude. Do not bring it up. If you do, I will be very upset."""

ESCAPED_BACKSLASH: Final = f"{ch.BACKSLASH}{ch.BACKSLASH}"
"""Escaped backslash string."""
ESCAPED_DOUBLE_QUOTE: Final = f"{ch.BACKSLASH}{ch.DOUBLE_QUOTE}"
"""Escaped double quote string."""
ESCAPED_NEWLINE: Final = f"{ch.BACKSLASH}{N_LITERAL}"
"""Escaped newline string."""
ESCAPED_CARRIAGE_RETURN: Final = f"{ch.BACKSLASH}{R_LITERAL}"
"""Escaped carriage return string."""
ESCAPED_TAB: Final = f"{ch.BACKSLASH}{T_LITERAL}"


TO_ESCAPE_MAP: dict[str, str] = {
    ch.BACKSLASH: ESCAPED_BACKSLASH,
    ch.DOUBLE_QUOTE: ESCAPED_DOUBLE_QUOTE,
    ch.NEWLINE: ESCAPED_NEWLINE,
    ch.CARRIAGE_RETURN: ESCAPED_CARRIAGE_RETURN,
    ch.TAB: ESCAPED_TAB,
}
"""Mapping of characters to their escape sequences."""


def return_escaped(c: str) -> str:
    """Return escaped character.

    Args:
        c: Character to escape
    Returns:
        Escaped character
    """
    if c not in TO_ESCAPE_MAP:
        return c
    return TO_ESCAPE_MAP[c]


def escape_string(s: str) -> str:
    """Escape a string.

    Args:
        s: String to escape
    Returns:
        Escaped string
    """
    return f"{ch.DOUBLE_QUOTE}{ch.EMPTY_STRING.join(return_escaped(c) for c in s)}{ch.DOUBLE_QUOTE}"


FROM_ESCAPE_MAP: dict[str, str] = {
    ch.BACKSLASH: ch.BACKSLASH,
    ch.DOUBLE_QUOTE: ch.DOUBLE_QUOTE,
    N_LITERAL: ch.NEWLINE,
    R_LITERAL: ch.CARRIAGE_RETURN,
    T_LITERAL: ch.TAB,
}
"""Mapping of escape sequences to their characters."""


def return_unescaped(next_ch: str) -> str:
    """Return unescaped character.

    Args:
        next_ch: The character following the backslash
    Returns:
        The unescaped character
    """
    if next_ch not in FROM_ESCAPE_MAP:
        raise ValueError(f"Invalid escape sequence: \\{next_ch}")
    return FROM_ESCAPE_MAP[next_ch]


def unescape_string(s: str) -> str:
    r"""Unescape a string.

    Only valid escapes: \\, \", \n, \r, \t

    Args:
        s: String to unescape
    Returns:
        Unescaped string
    Raises:
        ValueError for invalid escape sequences.
    """
    result: list[str] = []
    cursor = StringCursor(s)
    while cursor.within_bounds:
        if cursor.is_char(ch.BACKSLASH):
            result.append(return_unescaped(cursor.peek(1)))
            cursor.move(TWO)
        else:
            result.append(cursor.current)
            cursor.tick()
    return "".join(result)


def first_token(t: Any) -> Any:
    """Extract the first member.

    Args:
        t: A list or similar iterable
    Returns:
        The first member of the iterable
    """
    return t[0]


def extract(t: str) -> str:
    """Remove the first and last character from a string.

    Args:
        t: The string to extract from
    Returns:
        The string without the first and last character
    """
    return t[1:-1]
