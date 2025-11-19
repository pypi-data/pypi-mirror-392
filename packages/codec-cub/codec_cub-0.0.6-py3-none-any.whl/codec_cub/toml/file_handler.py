"""TOML file handler for Bear Dereth."""

from __future__ import annotations

import tomllib
from typing import IO, TYPE_CHECKING, Any, Self

import tomlkit

from codec_cub.general.base_file_handler import BaseFileHandler
from codec_cub.general.file_lock import LockExclusive, LockShared

if TYPE_CHECKING:
    from pathlib import Path

TomlData = dict[str, Any]


class TomlFileHandler(BaseFileHandler[TomlData]):
    """TOML file handler with caching and utilities."""

    def __init__(self, file: Path | str, touch: bool = False) -> None:
        """Initialize the handler with a file path.

        Args:
            path: Path to the TOML file
        """
        super().__init__(file, mode="r+", encoding="utf-8", touch=touch)

    def read(self, **kwargs) -> TomlData:
        """Read the entire file (or up to n chars) as text with a shared lock."""
        handle: IO[Any] | None = self.handle()
        if handle is None:
            raise ValueError("File handle is not available.")
        with LockShared(handle):
            handle.seek(0)
            data: str = handle.read(kwargs.pop("n", -1))
            return self.to_dict(data) if data else {}

    def write(self, data: TomlData, **kwargs) -> None:
        """Replace file contents with text using an exclusive lock.

        Args:
            data: Data to write to the TOML file
            **kwargs: Additional keyword arguments like 'sort_keys' (bool)

        Raises:
            ValueError: If file cannot be written
        """
        handle: IO[Any] | None = self.handle()
        if handle is None:
            raise ValueError("File handle is not available.")
        with LockExclusive(handle):
            handle.seek(0)
            handle.truncate(0)
            handle.write(self.to_string(data, sort_keys=kwargs.get("sort_keys", False)))
            handle.flush()

    def to_dict(self, s: str) -> dict[str, Any]:
        """Parse a TOML string into a dictionary.

        Args:
            s: TOML string to parse

        Returns:
            Parsed TOML data as dictionary

        Raises:
            tomllib.TOMLDecodeError: If file contains invalid TOML
            ValueError: If file cannot be read
        """
        try:
            return tomllib.loads(s)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML in {self.file}: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading TOML file {self.file}: {e}") from e

    def to_string(self, data: TomlData, sort_keys: bool = False) -> str:
        """Convert data to TOML string.

        Args:
            data: Data to serialize

        Returns:
            TOML formatted string

        Raises:
            ValueError: If data cannot be serialized
        """
        try:
            return tomlkit.dumps(data, sort_keys=sort_keys)
        except Exception as e:
            raise ValueError(f"Cannot serialize data to TOML: {e}") from e

    def get_section(
        self,
        data: TomlData | None,
        section: str,
        default: TomlData | None = None,
    ) -> dict[str, Any] | None:
        """Get a specific section from TOML data.

        Args:
            data: TOML data to search
            section: Section name (supports dot notation like 'tool.poetry')
            default: Default value if section not found

        Returns:
            Section data or default
        """
        current: TomlData = data or self.read()
        for key in section.split("."):
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current if isinstance(current, dict) else default

    def __enter__(self) -> Self:
        """Enter context manager."""
        self.read()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit context manager."""


__all__ = ["TomlData", "TomlFileHandler"]
