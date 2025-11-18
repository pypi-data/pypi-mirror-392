"""PyDB codec for creating and manipulating Python database files."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lazy_bear import lazy

from codec_cub.common import TWO
from funcy_bear.ops.math import neg

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec, SourceFileLoader
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path
    from types import ModuleType

    from codec_cub.pythons.file_builder import CodeSection
else:
    ModuleSpec, SourceFileLoader = lazy("importlib.machinery").to("ModuleSpec", "SourceFileLoader")
    module_from_spec, spec_from_file_location = lazy("importlib.util").to("module_from_spec", "spec_from_file_location")


class PyDBCodec:
    """Encode and decode Python Database (.py) format.

    PyDB files are executable Python modules that store structured data
    in a human-readable, version-controllable format.

    Features:
        - Create .py database files with schema and initial data
        - Fast append operations using byte counting
        - Load database files as Python modules (no parsing needed!)
        - Type-safe access to data

    Example:
        >>> codec = PyDBCodec()
        >>> codec.create(
        ...     file_path=Path("data.py"),
        ...     version=(1, 0, 0),
        ...     tables={"users": {"columns": [...], "rows": [...]}},
        ... )
        >>> codec.append_row(Path("data.py"), {"id": 1, "name": "Alice"})
        >>> module = codec.load(Path("data.py"))
        >>> print(module.ROWS)
    """

    def __init__(self) -> None:
        """Initialize PyDBCodec."""

    def create(
        self,
        file_path: Path,
        version: tuple[int, ...],
        tables: dict[str, Any],
    ) -> None:
        """Create a new Python database file with schema and optional initial data.

        Args:
            file_path: Path where the database file will be created
            version: Semantic version tuple (e.g., (1, 0, 0))
            tables: Dictionary mapping table names to their schema and rows
                   Format: {
                       "table_name": {
                           "columns": [
                               {"name": str, "type": str, "nullable": bool, "primary_key": bool},
                               ...
                           ],
                           "rows": [dict, ...]  # Optional initial data
                       }
                   }

        Raises:
            ValueError: If schema is invalid
            IOError: If file cannot be written
        """
        from codec_cub.pythons.class_builder import ClassBuilder  # noqa: PLC0415
        from codec_cub.pythons.file_builder import FileBuilder  # noqa: PLC0415
        from codec_cub.pythons.parts import Attribute  # noqa: PLC0415

        builder = FileBuilder()

        builder.add("header", f'"""Python Database file: {file_path.stem}.py"""')
        builder.add("header", "# fmt: off")
        builder.get_section("header").add_blank()

        builder.add("imports", "from __future__ import annotations")
        builder.get_section("imports").add_blank()
        builder.add("imports", "from typing import Any, Final, Literal, TypedDict")
        builder.get_section("imports").add_blank()

        body: CodeSection = builder.get_section("body")

        version_str: str = repr(version)
        body.add(f"VERSION: Final[tuple[int, ...]] = {version_str}")

        table_names: tuple[str, ...] = tuple(tables.keys())
        if table_names:
            tables_type: str = f"Final[tuple[Literal[{', '.join(repr(t) for t in table_names)}]]]"
            body.add(f"TABLES: {tables_type} = {table_names!r}")
        else:
            body.add("TABLES: Final[tuple] = ()")

        body.add(f"COUNT: int = {len(table_names)}")
        body.add_blank()

        column_type_class = ClassBuilder(
            name="ColumnType",
            bases=["TypedDict"],
            docstring="Column definition for database schema.",
            attributes=[
                Attribute("name", str),
                Attribute("type", str),
                Attribute("default", Any),
                Attribute("nullable", bool),
                Attribute("primary_key", bool),
                Attribute("autoincrement", bool),
            ],
        )
        body.add(column_type_class.render())
        body.add_blank()

        if table_names:
            body.add("SCHEMAS: dict[str, list[ColumnType]] = {")
            for table_name, table_data in tables.items():
                columns: Any = table_data.get("columns", [])
                body.add(f'    "{table_name}": [')

                for col in columns:
                    col_dict: dict[str, Any] = {
                        "name": col["name"],
                        "type": col["type"],
                        "default": col.get(
                            "default", None if col.get("nullable") else 0 if col["type"] == "int" else ""
                        ),
                        "nullable": col.get("nullable", False),
                        "primary_key": col.get("primary_key", False),
                        "autoincrement": col.get("autoincrement", False),
                    }
                    col_repr = repr(col_dict)
                    body.add(f"        {col_repr},")

                body.add("    ],")
            body.add("}")
        else:
            body.add("SCHEMAS: dict[str, list[ColumnType]] = {}")
        body.add_blank()
        body.add_blank()

        all_rows = []
        for table_data in tables.values():
            all_rows.extend(table_data.get("rows", []))

        body.add("ROWS: list[dict[str, Any]] = [")
        for row in all_rows:
            row_repr: str = repr(row)
            body.add(f"    {row_repr},")
        body.add("    ")  # Blank line before closing bracket
        body.add("]")

        content: str = builder.render()
        if not content.endswith("\n"):
            content += "\n"
        file_path.write_text(content)

    def load(self, file_path: Path) -> ModuleType:
        """Load a Python database file as a module.

        Args:
            file_path: Path to the database file

        Returns:
            The loaded module with attributes: VERSION, TABLES, COUNT, SCHEMAS, ROWS

        Raises:
            FileNotFoundError: If file doesn't exist
            ImportError: If file is not valid Python
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PyDB file not found: {file_path}")

        name: str = file_path.stem
        spec: ModuleSpec | None = spec_from_file_location(
            name,
            file_path,
            loader=SourceFileLoader(name, str(file_path)),
        )
        if spec is None:
            raise ImportError(f"Could not load module spec from path: {file_path}")
        if spec.loader is None:
            raise ImportError(f"No loader found for module spec from path: {file_path}")

        module: ModuleType = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def append_row(self, file_path: Path, row: dict[str, Any]) -> None:
        """Append a row to the database file using fast byte-counting.

        This method uses byte offset calculation to append data without
        parsing the entire file, making it very fast even for large files.

        Args:
            file_path: Path to the database file
            row: Dictionary containing the row data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If row data is invalid
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PyDB file not found: {file_path}")

        row_repr: str = repr(row)
        new_content: str = f"    {row_repr},\n    \n]\n"
        with open(file_path, "r+b") as f:
            f.seek(neg(TWO), TWO)  # 2 = from end of file
            f.write(new_content.encode("utf-8"))
            f.truncate()

    def _calculate_append_offset(self, _: Path) -> int:
        r"""Calculate the byte offset for appending data.

        The database file format ends with:
            ROWS: list[dict[str, Any]] = [
                ... existing rows ...

            ]

        The closing structure is:
            - 4 spaces (blank line indentation)
            - newline
            - ]
            - newline

        Total: 7 bytes from EOF

        Args:
            file_path: Path to the .pydb file

        Returns:
            Number of bytes from end of file to insert position (always 2 for "]\n")
        """
        # The file always ends with "]\n" (2 bytes)
        # We want to insert before the "]", so offset is 2
        # actually count the bytes to be safe
        return TWO


__all__ = ["PyDBCodec"]
