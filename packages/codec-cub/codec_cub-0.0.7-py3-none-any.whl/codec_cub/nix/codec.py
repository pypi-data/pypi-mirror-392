"""Nix codec implementation."""

from __future__ import annotations

import re
from typing import Any

from pyparsing import ParseException, ParserElement, ParseResults

from codec_cub.config import NixCodecConfig
from funcy_bear.constants.characters import EMPTY_STRING
from funcy_bear.ops.strings.manipulation import first_item


class NixCodec:
    """Encode/decode a pragmatic Nix subset:

    Python → Nix
      None → null
      bool → true/false
      int  → decimal
      float (finite) → decimal/no-exponent; -0.0 => 0; non-finite => null
      str  → "..."
      list/tuple → [ v1 v2 ... ]
      dict[str, Any] → { key = value; ... } with keys as identifiers or strings

    Decoding recognizes the same subset. This does NOT evaluate Nix expressions.
    """

    def __init__(self, config: NixCodecConfig | None = None) -> None:
        """Initialize NixCodec with optional configuration."""
        from codec_cub.nix.parser import _NixParser  # noqa: PLC0415

        self._cfg: NixCodecConfig = config if config is not None else NixCodecConfig()
        self._parser: ParserElement = _NixParser(self._cfg).grammar

    def encode(self, obj: Any) -> str:
        """Encode a Python object to Nix syntax string."""
        from codec_cub.nix.encoder import _NixEncoder  # noqa: PLC0415

        encoder = _NixEncoder(cfg=self._cfg)
        return encoder.encode(obj)

    def decode(self, text: str) -> Any:
        """Decode a Nix syntax string to a Python object."""
        try:
            filtered: str = re.sub(r"#.*", EMPTY_STRING, text)
            parsed: ParseResults = self._parser.parse_string(filtered, parse_all=True)
        except ParseException as exc:
            msg: str = f"Nix parse error at line {exc.lineno}, col {exc.col}: {exc.msg}"
            raise ValueError(msg) from exc
        if len(parsed) == 0:
            return None
        result: str = first_item(parsed)
        if isinstance(result, ParseResults):
            return result.as_list()
        return result
