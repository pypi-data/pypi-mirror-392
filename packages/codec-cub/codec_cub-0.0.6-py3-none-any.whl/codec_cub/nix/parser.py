"""Nix encoder/decoder for a pragmatic subset of Nix syntax."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import math
from typing import TYPE_CHECKING, Any

import pyparsing as pp

from funcy_bear.constants import characters as ch
from funcy_bear.ops.math.infinity import is_infinite
from funcy_bear.ops.strings.escaping import unescape_string as unescaped_str
from funcy_bear.ops.strings.manipulation import extract, first_item
from funcy_bear.type_stuffs.conversions import parse_bool

if TYPE_CHECKING:
    from codec_cub.config import NixCodecConfig

TWO = 2
comment = pp.Regex(r"#[^\n]*")


class _NixParser:
    def __init__(self, cfg: NixCodecConfig) -> None:
        self._cfg: NixCodecConfig = cfg
        self.grammar: pp.ParserElement = self._build()

    def _build(self) -> pp.ParserElement:
        """Build the Nix grammar using pyparsing combinators."""
        pp.ParserElement.set_default_whitespace_chars(f" {ch.TAB}{ch.CARRIAGE}{ch.NEWLINE}")

        # Structural symbols (Suppress means they're parsed but not in results)
        LBRACE = pp.Suppress(ch.LEFT_BRACE)
        RBRACE = pp.Suppress(ch.RIGHT_BRACE)
        LBRACK = pp.Suppress(ch.LEFT_BRACKET)
        RBRACK = pp.Suppress(ch.RIGHT_BRACKET)
        EQUAL = pp.Suppress(ch.EQUALS)
        SEMI = pp.Suppress(ch.SEMICOLON)

        # Keyword literals
        true_kw = pp.Keyword(ch.TRUE_LITERAL)
        false_kw = pp.Keyword(ch.FALSE_LITERAL)
        null_kw = pp.Keyword(ch.NULL_LITERAL)

        # Identifier pattern: starts with letter/underscore, continues with alphanums/underscore/dash
        ident_start: str = pp.alphas + ch.UNDERSCORE
        ident_body: str = pp.alphanums + f"{ch.UNDERSCORE}{ch.DASH}"
        identifier = pp.Word(ident_start, ident_body)

        def unescape_string(tokens: list[str]) -> list[Any]:
            """Unescape a Nix string literal."""
            text: str = extract(first_item(tokens))
            return [unescaped_str(text)]

        str_literal: pp.ParserElement = pp.Regex(r'"(?:[^"\\]|\\.)*"').set_parse_action(unescape_string)  # pyright: ignore[reportArgumentType]
        str_key: pp.ParserElement = pp.Regex(r'"(?:[^"\\]|\\.)*"').set_parse_action(unescape_string)  # pyright: ignore[reportArgumentType]

        # Number patterns: unsigned int/float, then optional sign
        unsigned_int = pp.Word(pp.nums)
        unsigned_float = pp.Combine(unsigned_int + ch.DOT + unsigned_int)
        signed: pp.ParserElement = pp.oneOf(f"{ch.PLUS} {ch.DASH}")
        number = pp.Combine(pp.Optional(signed) + (unsigned_float | unsigned_int))

        # Forward reference for recursive grammar (expr can contain expr)
        expr: pp.Forward = pp.Forward()

        def to_bool(tokens: list) -> bool:
            """Convert parsed boolean keyword to Python bool."""
            return parse_bool(first_item(tokens))

        def to_null(_: Any) -> list[None]:
            """Convert parsed null keyword to Python None."""
            return [None]

        def to_int_or_float(tokens: list[Any]) -> float | int | None:
            """Convert parsed number string to Python int or float."""
            text: Any = first_item(tokens)
            if ch.DOT in text:
                try:
                    dec = Decimal(text)
                except InvalidOperation:
                    return 0
                as_float = float(dec)
                if is_infinite(as_float) or math.isnan(as_float):
                    return None
                return as_float
            try:
                return int(text)
            except ValueError:
                return 0

        def to_list(tokens: list[Any]) -> list[Any]:
            """Convert grouped parse results to a Python list."""
            result = []
            for item in tokens:
                if isinstance(item, pp.ParseResults):
                    result.append(item.as_list())
                else:
                    result.append(item)
            return result

        def _is_nested(tokens: list[Any]) -> bool:
            """Check if pyparsing wrapped results in extra nesting."""
            return bool(tokens and isinstance(tokens[0], (list, pp.ParseResults)))

        def to_attrset(tokens: list[Any]) -> dict[str, Any]:
            """Convert grouped attribute pairs to a Python dict."""
            result: dict[str, Any] = {}
            actual_pairs: list[Any] | pp.ParseResults = first_item(tokens) if _is_nested(tokens) else tokens  # type: ignore[assignment]
            for pair in actual_pairs:
                if len(pair) == TWO:
                    result[pair[0]] = pair[1]
            return result

        # Value parsers with their conversion actions
        bool_val: pp.ParserElement = (true_kw | false_kw).set_parse_action(to_bool)  # pyright: ignore[reportArgumentType]
        null_val: pp.ParserElement = null_kw.set_parse_action(to_null)
        num_val: pp.ParserElement = number.set_parse_action(to_int_or_float)  # pyright: ignore[reportArgumentType]
        str_val: pp.ParserElement = str_literal  # Already has unescape_string parse action

        # Keys can be bare identifiers or quoted strings
        key_atom: pp.ParserElement = str_key | identifier

        # List: [ expr expr ... ]
        list_items = pp.ZeroOrMore(expr)
        list_val: pp.ParserElement = pp.Group(LBRACK + list_items + RBRACK).set_parse_action(to_list)  # pyright: ignore[reportArgumentType]

        # Attrset: { key = expr; key = expr; ... }
        attr_pair = pp.Group(key_atom + EQUAL + expr + pp.Optional(SEMI))
        attr_list = pp.ZeroOrMore(attr_pair)
        attrset_val: pp.ParserElement = pp.Group(LBRACE + attr_list + RBRACE).set_parse_action(to_attrset)  # pyright: ignore[reportArgumentType]

        # Complete value is any of these types (order matters for | operator)
        value: pp.ParserElement = null_val | bool_val | num_val | str_val | list_val | attrset_val

        # Wire up the forward reference for recursion
        expr <<= value

        return expr + pp.StringEnd()


# ruff: noqa: N806
