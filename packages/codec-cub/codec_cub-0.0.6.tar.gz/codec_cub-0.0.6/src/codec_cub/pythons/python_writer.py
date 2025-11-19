"""A proof of concept Python file handler for reading/writing Python database modules."""

from __future__ import annotations

from importlib.machinery import ModuleSpec, SourceFileLoader
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Protocol, TypedDict

from codec_cub.general.base_file_handler import BaseFileHandler
from codec_cub.text.bytes_handler import BytesFileHandler

if TYPE_CHECKING:
    from types import ModuleType

    from _typeshed import StrPath


class ColumnType(TypedDict):
    """Row type for 'settings' table."""

    name: str
    type: str
    default: Any
    nullable: bool
    primary_key: bool
    autoincrement: bool


class RowProtocol(Protocol):
    """Protocol for a database row."""


class PyDBProtocol(Protocol):
    """Protocol for Python database modules."""

    VERSION: Final[tuple[int, ...]]
    TABLES: Final[tuple]
    TABLE_COUNT: int

    SCHEMAS: dict[str, list[ColumnType]]
    ROW_COUNT: int
    ROWS: list[RowProtocol]


class PythonWriter(BaseFileHandler):
    """A file handler for writing and reading from Python files."""

    def __init__(self, file: StrPath, touch: bool = False) -> None:
        """Initialize the Python file handler.

        Args:
            file: Path to the Python file
            touch: Whether to create the file if it doesn't exist
        """
        file = Path(file)
        super().__init__(file=file)
        self._bytes = BytesFileHandler(file=file, touch=touch)

    def read(self, **kwargs) -> PyDBProtocol:  # noqa: ARG002
        """Read and return the Python database module."""
        return self._load_module(self.file)  # type: ignore[return-value]

    def append(self, data: Any, **kwargs) -> None:
        """Append data to the Python file."""
        raise NotImplementedError

    def write(self, data: Any, **kwargs) -> None:
        """Write data to the Python file."""
        raise NotImplementedError

    @staticmethod
    def _load_module(path: StrPath) -> ModuleType:
        """Load a Python module from the given file path.

        Args:
            path: Path to the Python file

        Returns:
            The loaded Python module
        """
        pydb = Path(path)
        name: str = pydb.stem
        spec: ModuleSpec | None = spec_from_file_location(
            name,
            pydb,
            loader=SourceFileLoader(name, str(pydb)),
        )
        if spec is None:
            raise ImportError(f"Could not load module spec from path: {path}")
        if spec.loader is None:
            raise ImportError(f"No loader found for module spec from path: {path}")
        module: ModuleType = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
