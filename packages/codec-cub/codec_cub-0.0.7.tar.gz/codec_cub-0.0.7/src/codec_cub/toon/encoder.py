"""TOON encoder implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import TYPE_CHECKING, Any

from codec_cub.config import ToonCodecConfig
from codec_cub.toon.constants import COLON, LIST_ITEM_PREFIX, SPACE
from codec_cub.toon.utils import (
    TabularArray,
    detect_tabular_array,
    encode_key,
    get_delimiter_char,
    normalize_number,
    quote_string,
)
from funcy_bear.api import any_of
from funcy_bear.constants.characters import FALSE_LITERAL, NULL_LITERAL, TRUE_LITERAL
from funcy_bear.tools import Dispatcher
from funcy_bear.typing_stuffs import is_bool, is_dict, is_float, is_int, is_list, is_none, is_str

if TYPE_CHECKING:
    from codec_cub.config import ToonCodecConfig


@dataclass(slots=True)
class EncoderBuffer:
    """Buffer that manages both line accumulation and indentation state."""

    indent_size: int
    _root: list[str] = field(default_factory=list)

    def add_at(self, *segments: str, depth: int) -> None:
        """Add content with automatic indentation at specified depth."""
        indent: str = SPACE * (depth * self.indent_size)
        self._root.append(f"{indent}{''.join(segments)}")

    def add_raw(self, line: str) -> None:
        """Add pre-formatted line without indentation."""
        self._root.append(line)

    def copy(self, clear: bool = False) -> list[str]:
        """Get copy of accumulated lines, optionally clearing buffer."""
        cpy: list[str] = self._root.copy()
        if clear:
            self.clear()
        return cpy

    def build(self, sep: str, clear: bool = False) -> str:
        """Build final TOON string from buffer."""
        out: str = sep.join(self._root)
        if clear:
            self.clear()
        return out

    def clear(self) -> None:
        """Clear the buffer."""
        self._root.clear()

    def is_empty(self) -> bool:
        """Check if the buffer is empty."""
        return len(self._root) == 0


class ToonEncoder:
    """Encode Python objects to TOON format per specification v2.0."""

    def __init__(self, config: ToonCodecConfig) -> None:
        """Initialize encoder with configuration."""
        self._cfg: ToonCodecConfig = config
        self._buffer: EncoderBuffer = EncoderBuffer(indent_size=config.indent_spaces)

    def encode(self, obj: Any) -> str:
        """Encode a Python object to TOON string.

        Args:
            obj: Python object to encode (dict, list, or primitive)

        Returns:
            TOON formatted string
        """
        normalized: Any = normalize_value(obj)
        if isinstance(normalized, dict):
            return self._encode_object(normalized, depth=0) if normalized else ""
        if isinstance(normalized, list):
            return self._encode_root_array(normalized)
        return self._encode_primitive(normalized, self._cfg.delimiter)

    def join(self, *segments: str, depth: int = 0, sep: str = "") -> str:
        """Concatenate segments with indentation at specified depth."""
        indent: str = SPACE * (depth * self._cfg.indent_spaces)
        return f"{indent}{sep.join(segments)}"

    def _encode_primitive(self, value: Any, delimiter: str) -> str:
        """Encode a primitive value (string, number, boolean, null)."""
        if value is None:
            return NULL_LITERAL
        if isinstance(value, bool):
            return TRUE_LITERAL if value else FALSE_LITERAL
        if isinstance(value, (int, float)):
            normalized: str | None = normalize_number(value)
            return normalized if normalized is not None else "null"
        if isinstance(value, str):
            return quote_string(value, delimiter)
        return "null"

    def _encode_object(self, obj: dict[str, Any], depth: int) -> str:
        """Encode an object (dict) per §8."""
        for key, value in obj.items():
            encoded_key: str = encode_key(key)
            if not isinstance(value, (dict, list)):
                primitive_str: str = self._encode_primitive(value, self._cfg.delimiter)
                self._buffer.add_at(encoded_key, COLON, SPACE, primitive_str, depth=depth)
            elif isinstance(value, dict):
                self._buffer.add_at(encoded_key, COLON, depth=depth)
                if value:
                    nested_lines: str = self._encode_object(value, depth + 1)
                    self._buffer.add_raw(nested_lines)
            elif isinstance(value, list):
                array_lines: str = self._encode_keyed_array(encoded_key, value, depth)
                self._buffer.add_raw(array_lines)
        return self._buffer.build(sep=self._cfg.newline, clear=True)

    def _encode_root_array(self, items: list[Any]) -> str:
        """Encode a root array per §5."""
        length: int = len(items)
        delim_char: str = get_delimiter_char(self._cfg.delimiter)
        array: TabularArray = detect_tabular_array(items)
        if array.is_tabular:
            header: str = self._build_array_header(length, array.field_names, delim_char)
            lines: list[str] = [header]
            for item in items:
                row: str = self._encode_tabular_row(item, array.field_names, depth=1)
                lines.append(row)
            return self._cfg.newline.join(lines)
        if self._is_inline_primitive_array(items):
            header = self._build_array_header(length, [], delim_char)
            values: str = self._cfg.delimiter.join(self._encode_primitive(item, self._cfg.delimiter) for item in items)
            return self.join(header, SPACE, values)
        header = self._build_array_header(length, [], delim_char)
        lines = [header]
        for item in items:
            item_line: str = self._encode_list_item(item, depth=1)
            lines.append(item_line)
        return self._cfg.newline.join(lines)

    def _encode_keyed_array(self, key: str, items: list[Any], depth: int) -> str:
        """Encode an array with a key."""
        length: int = len(items)
        delim_char: str = get_delimiter_char(self._cfg.delimiter)
        array: TabularArray = detect_tabular_array(items)

        if array.is_tabular:
            header = self.join(key, self._build_array_header(length, array.field_names, delim_char), depth=depth)
            lines = [header]
            for item in items:
                row: str = self._encode_tabular_row(item, array.field_names, depth + 1)
                lines.append(row)
            return self._cfg.newline.join(lines)

        if self._is_inline_primitive_array(items):
            header: str = self.join(key, self._build_array_header(length, [], delim_char), depth=depth)
            if not items:
                return header
            values: str = self.join(
                *(self._encode_primitive(item, self._cfg.delimiter) for item in items), sep=self._cfg.delimiter
            )
            return self.join(header, SPACE, values)

        lines: list[str] = [self.join(key, self._build_array_header(length, [], delim_char), depth=depth)]
        for item in items:
            item_line: str = self._encode_list_item(item, depth + 1)
            lines.append(item_line)
        return self._cfg.newline.join(lines)

    def _build_array_header(self, length: int, field_names: list[str], delim_char: str) -> str:
        """Build array header: [N<delim>]{fields}:"""
        if field_names:
            encoded_fields: str = self.join(*(encode_key(f) for f in field_names), sep=self._cfg.delimiter)
            return self.join("[", str(length), delim_char, "]{", encoded_fields, "}:")
        return self.join("[", str(length), delim_char, "]:")

    def _is_inline_primitive_array(self, items: list[Any]) -> bool:
        """Check if array can be encoded as inline primitives."""
        return all(not isinstance(item, (dict, list)) for item in items)

    def _encode_tabular_row(self, obj: dict[str, Any], field_names: list[str], depth: int) -> str:
        """Encode a single tabular row."""
        return self.join(
            *(self._encode_primitive(obj[field], self._cfg.delimiter) for field in field_names),
            sep=self._cfg.delimiter,
            depth=depth,
        )

    def _encode_list_item(self, item: Any, depth: int) -> str:
        """Encode a list item per §9.4 and §10."""
        marker: str = LIST_ITEM_PREFIX

        if not isinstance(item, (dict, list)):
            return self.join(marker, self._encode_primitive(item, self._cfg.delimiter), depth=depth)

        if isinstance(item, list):
            return self._encode_list_item_array(item, depth, marker)

        if isinstance(item, dict):
            return self._encode_list_item_dict(item, depth, marker)

        return self.join(marker, "null", depth=depth)  # Handle unexpected types as null

    def _encode_list_item_array(self, item: list[Any], depth: int, marker: str) -> str:
        """Encode array as list item."""
        delim_char: str = get_delimiter_char(self._cfg.delimiter)
        header: str = self._build_array_header(len(item), [], delim_char)
        if self._is_inline_primitive_array(item):
            if not item:
                return self.join(marker, header, depth=depth)
            values: str = self._cfg.delimiter.join(self._encode_primitive(v, self._cfg.delimiter) for v in item)
            return self.join(marker, header, SPACE, values, depth=depth)
        first_line: str = self.join(marker, header, depth=depth)
        nested_items: list[str] = [self._encode_list_item(nested, depth + 1) for nested in item]
        return self._cfg.newline.join([first_line, *nested_items])

    def _encode_list_item_dict(self, item: dict[str, Any], depth: int, marker: str) -> str:
        """Encode dict as list item per §10."""
        if not item:
            return self.join(marker.rstrip(), depth=depth)

        keys: list[str] = list(item.keys())
        first_key: str = keys[0]
        first_value: Any = item[first_key]

        lines: list[str] = [self._encode_dict_first_field(first_key, first_value, depth, marker)]

        for key in keys[1:]:
            lines.append(self._encode_dict_field(key, item[key], depth + 1))

        return self._cfg.newline.join(lines)

    def _encode_dict_first_field(self, key: str, value: Any, depth: int, marker: str) -> str:
        """Encode first field of dict in list item."""
        encoded_key: str = encode_key(key)

        if not isinstance(value, (dict, list)):
            primitive_str: str = self._encode_primitive(value, self._cfg.delimiter)
            return self.join(marker, encoded_key, COLON, SPACE, primitive_str, depth=depth)

        if isinstance(value, list):
            return self._encode_first_field_array(encoded_key, value, depth, marker)

        if not value:
            return self.join(marker, encoded_key, COLON, depth=depth)
        nested: str = self._encode_object(value, depth + 2)
        first_line: str = self.join(marker, encoded_key, COLON, depth=depth)
        return self._cfg.newline.join([first_line, nested])

    def _encode_first_field_array(self, encoded_key: str, value: list[Any], depth: int, marker: str) -> str:
        """Encode array in first field of dict list item."""
        delim_char: str = get_delimiter_char(self._cfg.delimiter)
        header: str = self._build_array_header(len(value), [], delim_char)

        if self._is_inline_primitive_array(value):
            if not value:
                return self.join(marker, encoded_key, header, depth=depth)
            values: str = self._cfg.delimiter.join(self._encode_primitive(v, self._cfg.delimiter) for v in value)
            return self.join(marker, encoded_key, header, SPACE, values, depth=depth)
        return self.join(marker, encoded_key, header, depth=depth)

    def _encode_dict_field(self, key: str, value: Any, depth: int) -> str:
        """Encode subsequent field in dict list item."""
        encoded_key: str = encode_key(key)

        if not isinstance(value, (dict, list)):
            primitive_str: str = self._encode_primitive(value, self._cfg.delimiter)
            return self.join(encoded_key, COLON, SPACE, primitive_str, depth=depth)

        if isinstance(value, dict):
            if not value:
                return self.join(encoded_key, COLON, depth=depth)
            nested: str = self._encode_object(value, depth + 1)
            first_line: str = self.join(encoded_key, COLON, depth=depth)
            return self._cfg.newline.join([first_line, nested])

        return self._encode_keyed_array(encoded_key, value, depth)


norm = Dispatcher("obj")


@norm.dispatcher()
def normalize_value(obj: Any) -> Any:
    """Normalize non-JSON values to JSON data model per §3."""
    raise ValueError(f"Unsupported type for TOON encoding: {type(obj)}")


@norm.register(is_dict)
def _normalize_dict(obj: dict[str, Any]) -> dict[str, Any]:
    """Normalize dictionary values per §3."""
    return {key: normalize_value(value) for key, value in obj.items()}


@norm.register(is_none)
def _normalize_none(obj: None) -> None:  # noqa: ARG001
    """Normalize None per §3."""
    return None  # noqa: RET501


@norm.register(any_of(is_float, is_int))
def _normalize_number(obj: float) -> float | int | None:
    """Normalize numbers per §3."""
    if is_float(obj):
        if math.isnan(obj) or math.isinf(obj):
            return None
        if obj == 0.0:
            return 0
    return obj


@norm.register(is_list)
def _normalize_list(obj: list[Any]) -> list[Any]:
    """Normalize list items per §3."""
    return [normalize_value(item) for item in obj]


@norm.register(any_of(is_str, is_bool))
def _normalize_primitive(obj: str | bool) -> str | bool:
    """Normalize string and boolean per §3."""
    return obj
