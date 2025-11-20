"""Demo: Dynamic Plugin Registry Generator using codec-cub pythons utilities.

This example shows how to generate a dynamic Python file that discovers and registers
plugin backends (like storage backends, parsers, serializers, etc.) with full type safety.

It demonstrates:
- FileBuilder for organizing code into sections
- ImportManager for automatic import deduplication
- Type alias generation (PEP 613 syntax)
- Literal type generation
- Function overloads for type-safe plugin factory
- Dict literal generation with proper formatting

This refactored approach is cleaner than manual string concatenation:
- Automatic indentation management
- Section-based organization (header, imports, type_checking, body, footer)
- Type-safe building blocks
- Easier to maintain and extend
"""  # noqa: INP001

from __future__ import annotations

from pathlib import Path
from typing import Final

from codec_cub.pythons import (
    Decorator,
    DocstringBuilder,
    FileBuilder,
    FunctionBuilder,
    ImportManager,
    TypeAnnotation,
    generate_all_export,
    generate_dict_literal,
)

DEFAULT_BACKEND: Final[str] = "jsonl"
TYPE_CHECKING_STR: Final = "TYPE_CHECKING"


def discover_storage_backends() -> dict[str, tuple[str, str]]:
    """Scan storage directory for Storage subclasses.

    Args:
        package_name: The package to scan for backends.

    Returns:
        Dict mapping storage key to (class_name, module_name) tuple.
    """
    return {
        "jsonl": ("JSONLStorage", "jsonl"),
        "json": ("JsonStorage", "json"),
        "msgpack": ("MsgPackStorage", "msgpack"),
        "toml": ("TomlStorage", "toml"),
        "yaml": ("YamlStorage", "yaml"),
        "xml": ("XmlStorage", "xml"),
    }


def generate_storage_file(output_path: Path | None = None) -> str:
    """Generate _dynamic_storage.py with auto-discovered storage backends.

    This refactored version uses codec-cub's pythons utilities for cleaner code generation.

    Args:
        output_path: Optional path to write the file. If None, returns the content.

    Returns:
        The generated Python file content.
    """
    backends: dict[str, tuple[str, str]] = discover_storage_backends()
    sorted_backends: dict[str, tuple[str, str]] = dict(sorted(backends.items()))
    file = FileBuilder()
    imports = ImportManager()

    # ============================================================================
    # 1. HEADER SECTION - Module docstring with warning
    # ============================================================================
    file.header.docstring(
        "Dynamic storage backend registry.",
        "",
        "THIS FILE IS AUTO-GENERATED - DO NOT EDIT MANUALLY",
        "Run the generator script to regenerate.",
    )

    # ============================================================================
    # 2. IMPORTS SECTION
    # ============================================================================
    imports.add_from_import("__future__", "annotations").add_from_import(
        "typing", ["Literal", "overload", TYPE_CHECKING_STR]
    )

    for class_name, module_name in sorted_backends.values():
        imports.add_from_import(f".{module_name}", class_name, is_local=True)

    file.add("imports", imports.render())

    # ============================================================================
    # 3. TYPE_CHECKING SECTION
    # ============================================================================
    with file.type_checking.if_block():
        file.type_checking.add("from ._base_storage import Storage")

    # ============================================================================
    # 4. BODY SECTION
    # ============================================================================
    file.body.type_alias("StorageChoices").literal(*list(sorted_backends.keys()), "default")

    storage_dict_items: dict[str, str] = {key: class_name for key, (class_name, _) in sorted_backends.items()}
    default_backend: str = sorted_backends.get(DEFAULT_BACKEND, next(iter(sorted_backends.values())))[0]
    storage_dict_items["default"] = default_backend

    storage_map_value: str = generate_dict_literal(storage_dict_items, multiline=True, indent=0)
    type_hint = TypeAnnotation.dict_of("str", TypeAnnotation.type_of("Storage"))
    file.body.variable("storage_map").type_hint(type_hint).value(storage_map_value)
    file.body.newline()

    for key, (class_name, _) in sorted_backends.items():
        overload_func = FunctionBuilder(
            name="get_storage",
            args=f"storage: {TypeAnnotation.literal(key).render()}",
            returns=TypeAnnotation.type_of(class_name),
            decorators=[Decorator("overload")],
        )
        file.body.add(overload_func)

    default_overload = FunctionBuilder(
        name="get_storage",
        args=f"storage: {TypeAnnotation.literal('default').render()}",
        returns=TypeAnnotation.type_of(default_backend),
        decorators=[Decorator("overload")],
    )
    file.body.add(default_overload)

    main_docstring = (
        DocstringBuilder()
        .summary("Factory function to get a storage backend by name.")
        .arg("storage", "Storage backend name")
        .returns("Storage backend class")
    )

    main_func = FunctionBuilder(
        name="get_storage",
        args='storage: StorageChoices = "default"',
        returns=TypeAnnotation.type_of("Storage"),
        docstring=main_docstring,
        body='storage_type: type[Storage] = storage_map.get(storage, storage_map["default"])\n    return storage_type',
    )
    file.body.add(main_func)

    # ============================================================================
    # 5. FOOTER SECTION - __all__ export
    # ============================================================================
    file.footer.newline()
    file.footer.add(generate_all_export(["StorageChoices", "get_storage", "storage_map"]))

    output: str = file.render(add_section_separators=True)

    if output_path:
        output_path.write_text(output)

    return output


def main() -> None:
    """Run the demo to show the generated output."""
    print("=== Dynamic Plugin Registry Generator Demo ===\n")
    print("Generated Python file:\n")
    print("-" * 80)

    generated_code: str = generate_storage_file()
    Path("test.py").write_text(generated_code)
    print(generated_code)

    print("-" * 80)
    print("\n✨ This demonstrates how codec-cub's pythons utilities make")
    print("   dynamic code generation clean, maintainable, and type-safe!")


if __name__ == "__main__":
    main()
