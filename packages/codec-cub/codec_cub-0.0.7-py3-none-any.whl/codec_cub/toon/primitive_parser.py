"""pyparsing-based parser for TOON primitive values."""

from __future__ import annotations

from typing import Any

from pyparsing import Literal, MatchFirst, ParserElement, ParseResults, Regex, pyparsing_common, quotedString

from funcy_bear.constants.characters import FALSE_LITERAL, NULL_LITERAL, TRUE_LITERAL
from funcy_bear.ops.strings.manipulation import extract, first_item


class PrimitiveParser:
    """Parse TOON primitive values using pyparsing."""

    def __init__(self) -> None:
        """Initialize parser with pyparsing grammar for primitives."""

        def unescape_string(s: Any) -> str:
            """Unescape a quoted string."""
            return s.encode("utf-8").decode("unicode_escape")

        quoted: ParserElement = quotedString.copy()
        quoted.setParseAction(lambda t: unescape_string(extract(first_item(t))))
        null = Literal(NULL_LITERAL)
        null.setParseAction(lambda: [None])
        true_lit = Literal(TRUE_LITERAL)
        true_lit.setParseAction(lambda: [True])
        false_lit = Literal(FALSE_LITERAL)
        false_lit.setParseAction(lambda: [False])
        leading_zero_string = Regex(r"0\d+")  # Numbers: handle leading zeros specially
        leading_zero_string.setParseAction(lambda t: first_item(t))
        float_num: ParserElement = pyparsing_common.number.copy()
        integer: ParserElement = pyparsing_common.signed_integer.copy()
        unquoted = Regex(r"[^\s:,\|\t]+")
        unquoted.setParseAction(lambda t: first_item(t))
        self._primitive = MatchFirst(
            [
                quoted,
                null,
                true_lit,
                false_lit,
                leading_zero_string,
                float_num,
                integer,
                unquoted,
            ]
        )

    def parse(self, token: str) -> Any:
        """Parse a primitive token.

        Args:
            token: Token string to parse

        Returns:
            Parsed primitive value (str, int, float, bool, None)
        """
        token = token.strip()
        if not token:
            return ""

        try:
            result: ParseResults = self._primitive.parseString(token, parseAll=True)
            return first_item(result)
        except Exception:
            return token


_primitive_parser = PrimitiveParser()


def parse_primitive(token: str) -> Any:
    """Parse a TOON primitive value.

    Args:
        token: Token string to parse

    Returns:
        Parsed primitive value
    """
    return _primitive_parser.parse(token)
