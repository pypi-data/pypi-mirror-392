"""Configuration management for Codec Cub."""

from dataclasses import dataclass, field

from codec_cub._internal._info import _ProjectMetadata
from codec_cub._internal.debug import METADATA


@dataclass(slots=True)
class Metadata:
    """Metadata about the application."""

    info_: _ProjectMetadata = field(default_factory=lambda: METADATA)

    def __getattr__(self, name: str) -> str:
        """Delegate attribute access to the internal _ProjectMetadata instance."""
        return getattr(self.info_, name)


@dataclass(slots=True)
class NixCodecConfig:
    """Configuration options for NixCodec."""

    indent_spaces: int = 2
    newline: str = "\n"
    sort_keys: bool = True
    trailing_semicolon: bool = True
    max_inline_list: int = 6
    str_quote: str = '"'  # reserved, single quote not used in Nix strings
    float_scale: int = 12  # max fractional digits when emitting floats (no exponent)


@dataclass(slots=True)
class ToonCodecConfig:
    """Configuration options for ToonCodec."""

    indent_spaces: int = 2
    newline: str = "\n"
    delimiter: str = ","  # comma (default), tab ("\t"), or pipe ("|")
    strict: bool = True  # strict mode for decoding
    key_folding: str = "off"  # "off" or "safe"
    flatten_depth: int | float = float("inf")  # max depth for key folding
    expand_paths: str = "off"  # "off" or "safe"


@dataclass(slots=True)
class CodecsConfig:
    """Main configuration for Codec Cub."""

    env: str = "prod"
    debug: bool = False
    nix_codec: NixCodecConfig = field(default_factory=NixCodecConfig)
    toon_codec: ToonCodecConfig = field(default_factory=ToonCodecConfig)
    metadata: Metadata = field(default_factory=Metadata)


__all__ = ["CodecsConfig"]
