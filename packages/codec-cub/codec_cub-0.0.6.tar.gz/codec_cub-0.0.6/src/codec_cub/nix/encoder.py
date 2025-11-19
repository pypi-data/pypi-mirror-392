"""Nix encoder implementation."""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal, DecimalTuple, InvalidOperation
import math
from typing import TYPE_CHECKING, Any, cast

from codec_cub.nix.utils import is_bare_identifier
from funcy_bear.constants import characters as ch
from funcy_bear.constants.escaping import F_LITERAL, NEGATIVE_ZERO_QUOTE, ZERO_QUOTE
from funcy_bear.ops.func_stuffs import any_of, complement
from funcy_bear.ops.math import neg
from funcy_bear.ops.math.infinity import is_infinite
from funcy_bear.ops.strings.escaping import escape_string
from funcy_bear.tools import Dispatcher
from funcy_bear.type_stuffs.validate import is_bool, is_float, is_int, is_list, is_mapping, is_none, is_str

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import NoneType

    from codec_cub.config import NixCodecConfig


class _NixEncoder:
    def __init__(self, cfg: NixCodecConfig) -> None:
        self._cfg: NixCodecConfig = cfg

    def encode(self, obj: Any) -> str:
        return self._emit_value(obj, 0)

    def _emit_value(self, obj: Any, depth: int) -> str:
        return to_value(obj, encoder=self, depth=depth)

    def _emit_key(self, key: str) -> str:
        if is_bare_identifier(key):
            return key
        return to_string(key, encoder=self)

    def _indent(self, depth: int) -> str:
        return ch.SPACE * (self._cfg.indent_spaces * depth)

    def _is_atomic(self, x: Any) -> bool:
        return x is None or isinstance(x, (bool, int, float, str))

    def _is_inline_list(self, x: Any) -> bool:
        if not isinstance(x, list):
            return False
        return len(x) <= self._cfg.max_inline_list and all(self._is_atomic(item) for item in x)


encode = Dispatcher("obj")


@encode.dispatcher()
def to_value(obj: Any, encoder: _NixEncoder, depth: int) -> str:
    """Encode a Python object to Nix syntax string."""
    raise TypeError(f"Unsupported type for Nix encoding: {type(obj).__name__}")


@encode.register(any_of(is_none, is_infinite))
def to_null(obj: float | NoneType, encoder: _NixEncoder, depth: int) -> str:
    """Encode None as null in Nix."""
    return ch.NULL_LITERAL


@encode.register(is_bool)
def to_bool(obj: bool, encoder: _NixEncoder, depth: int) -> str:
    """Encode bool as true/false in Nix."""
    return ch.TRUE_LITERAL if obj else ch.FALSE_LITERAL


@encode.register(is_int)
def to_int(obj: int, encoder: _NixEncoder, depth: int) -> str:
    """Encode int as decimal in Nix."""
    return str(obj)


def to_decimal_no_exponent(obj: float, encoder: _NixEncoder) -> Decimal:
    """Convert float to Decimal without exponent, respecting max_scale."""
    max_scale: int = encoder._cfg.float_scale
    try:
        dec = Decimal(repr(obj))
    except InvalidOperation:
        return Decimal(0)

    if dec.is_nan():
        return Decimal(0)

    quant: Decimal = Decimal(1).scaleb(neg(max_scale))
    normalized: Decimal = dec.quantize(quant, rounding=ROUND_HALF_EVEN).normalize()
    if normalized == Decimal(NEGATIVE_ZERO_QUOTE):
        return Decimal(0)
    norm_tuple: DecimalTuple = normalized.as_tuple()
    if abs(cast("int", norm_tuple.exponent)) > max_scale:
        return normalized.quantize(quant, rounding=ROUND_HALF_EVEN)
    return normalized


@encode.register(is_float, complement(is_infinite))
def to_float(obj: float, encoder: _NixEncoder, depth: int) -> str:
    """Encode float as decimal/no-exponent in Nix."""
    if math.isnan(obj):
        return ch.NULL_LITERAL
    if obj == 0.0:
        return ZERO_QUOTE
    dec: Decimal = to_decimal_no_exponent(obj, encoder)
    text: str = format(dec, F_LITERAL)
    if ch.DOT in text:
        text: str = text.rstrip(ZERO_QUOTE).rstrip(ch.DOT)
    return text or ZERO_QUOTE


@encode.register(is_str)
def to_string(obj: str, encoder: _NixEncoder, depth: int = 0) -> str:
    """Encode str as "..." in Nix."""
    return escape_string(obj)


@encode.register(is_list)
def to_list(obj: list[Any], encoder: _NixEncoder, depth: int) -> str:
    """Encode list/tuple as [...] in Nix."""
    indent: str = encoder._indent(depth)
    inner_indent: str = encoder._indent(depth + 1)
    open_br: str = ch.LEFT_BRACKET
    close_br: str = ch.RIGHT_BRACKET

    if len(obj) <= encoder._cfg.max_inline_list and all(
        encoder._is_atomic(x) or encoder._is_inline_list(x) for x in obj
    ):
        if not obj:
            return f"{open_br} {close_br}"
        rendered: str = ch.SPACE.join(encoder._emit_value(x, depth + 1) for x in obj)
        return f"{open_br} {rendered} {close_br}"

    lines: list[str] = []
    lines.append(f"{open_br}")
    for x in obj:
        lines.append(f"{inner_indent}{encoder._emit_value(x, depth + 1)}")
    lines.append(f"{indent}{close_br}")
    return encoder._cfg.newline.join(lines)


@encode.register(is_mapping)
def to_attrset(obj: Mapping[str, Any], encoder: _NixEncoder, depth: int) -> str:
    """Encode dict as {...} in Nix."""
    keys: list[str] = list(obj.keys())
    if encoder._cfg.sort_keys:
        keys.sort()

    indent: str = encoder._indent(depth)
    inner_indent: str = encoder._indent(depth + 1)
    open_br: str = ch.LEFT_BRACE
    close_br: str = ch.RIGHT_BRACE
    eq: str = ch.EQUALS
    semi: str = ch.SEMICOLON

    if not keys:
        return f"{open_br} {close_br}"

    lines: list[str] = []
    lines.append(f"{open_br}")
    for k in keys:
        key_text: str = encoder._emit_key(k)
        value_text: str = encoder._emit_value(obj[k], depth + 1)
        end: str = semi if encoder._cfg.trailing_semicolon else ch.EMPTY_STRING
        lines.append(f"{inner_indent}{key_text} {eq} {value_text}{end}")
    lines.append(f"{indent}{close_br}")
    return encoder._cfg.newline.join(lines)


# ruff: noqa: ARG001
