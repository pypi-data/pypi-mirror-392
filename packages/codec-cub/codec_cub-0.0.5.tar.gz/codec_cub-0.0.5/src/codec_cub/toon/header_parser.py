"""pyparsing-based parser for TOON array headers."""

from __future__ import annotations

from typing import Any

from pyparsing import (
    Literal,
    Optional,
    ParserElement,
    Suppress,
    Word,
    alphanums,
    delimitedList,
    nums,
    quotedString,
    removeQuotes,
)
from pyparsing.results import ParseResults  # noqa: TC002

from codec_cub.toon.constants import COMMA, PIPE, TAB


class ArrayHeader:
    """Parsed representation of a TOON array header."""

    def __init__(
        self,
        length: int,
        delimiter: str,
        field_names: list[str],
    ) -> None:
        """Initialize parsed header.

        Args:
            length: Declared array length
            delimiter: Delimiter character (comma, tab, or pipe)
            field_names: Field names for tabular format (empty if not tabular)
        """
        self.length: int = length
        self.delimiter: str = delimiter
        self.field_names: list[str] = field_names

    def __repr__(self) -> str:
        """Return string representation."""
        return f"ArrayHeader(length={self.length}, delimiter={self.delimiter!r}, fields={self.field_names})"


class ArrayHeaderParser:
    r"""Parse TOON array headers using pyparsing.

    Replaces manual string slicing with a declarative grammar for:
        [N<delim?>]{field1,field2,...}:

    Where:
        - N is the array length (integer)
        - Optional delimiter marker (\t or |) after length
        - Optional {field_names} for tabular format
        - Followed by colon
    """

    def __init__(self) -> None:
        """Initialize parser with pyparsing grammar."""

        def to_int(tokens: Any) -> int:
            """Convert parsed token to int."""
            return int(str(tokens[0]))

        integer: ParserElement = Word(nums).setParseAction(to_int)

        delimiter_marker: ParserElement = Literal(TAB) | Literal(PIPE)

        field_name: ParserElement = quotedString.setParseAction(removeQuotes) | Word(alphanums + "_")
        field_list: ParserElement = Suppress("{") + delimitedList(field_name) + Suppress("}")

        self._grammar: ParserElement = (
            Suppress("[")
            + integer("length")
            + Optional(delimiter_marker)("delim")
            + Suppress("]")
            + Optional(field_list)("fields")
            + Suppress(":")
        )

    def parse(self, header_line: str) -> ArrayHeader:
        """Parse array header line.

        Args:
            header_line: Line containing array header (e.g., "tags[3]: ..." or "users[2]{id,name}:")

        Returns:
            ArrayHeader with length, delimiter, and field names

        Raises:
            ValueError: If header is malformed
        """
        try:
            result: ParseResults = self._grammar.parseString(header_line)
            length: Any = result["length"]
            delimiter: Any = COMMA  # default
            if "delim" in result:
                delimiter = result["delim"]
            res: Any = result.get("fields", [])
            field_names: list[Any] = list(res) if res else []
            return ArrayHeader(length, delimiter, field_names)

        except Exception as e:
            raise ValueError(f"Malformed array header: {header_line}") from e


_header_parser = ArrayHeaderParser()


def parse_array_header(header_line: str) -> tuple[int, str, list[str]]:
    """Parse array header using pyparsing.

    This replaces the manual string slicing in ToonDecoder._parse_array_header.

    Args:
        header_line: Header line like "[3]:", "[2]{id,name}:", "items[3|]:"

    Returns:
        (length, delimiter, field_names)
    """
    header: ArrayHeader = _header_parser.parse(header_line)
    return (header.length, header.delimiter, header.field_names)
