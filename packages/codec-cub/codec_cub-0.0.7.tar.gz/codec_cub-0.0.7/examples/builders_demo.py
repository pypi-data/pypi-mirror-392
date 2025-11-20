"""Demo of general-purpose Python builders (ready for funcy-bear extraction).

This demonstrates the enhanced builders that are now fully decoupled from PyDB
and can generate any Python code: dataclasses, Pydantic models, enums, etc.
"""  # noqa: INP001

from __future__ import annotations

from codec_cub.pythons import (
    Attribute,
    ClassBuilder,
    Decorator,
    EnumBuilder,
    FileBuilder,
    FunctionBuilder,
    ImportManager,
)
from codec_cub.pythons.function_builder import generate_main_block
from codec_cub.pythons.helpers import generate_all_export


def demo_dataclass() -> None:
    """Demonstrate building a dataclass with the ClassBuilder."""
    print("=" * 60)
    print("DATACLASS BUILDER DEMO")
    print("=" * 60)

    user_class = ClassBuilder(
        name="User",
        decorators=[Decorator("dataclass")],
        docstring="Represents a user in the system.",
        attributes=[
            Attribute("id", int),
            Attribute("username", str),
            Attribute("email", "str | None", default="None"),
            Attribute("is_active", bool, default="True"),
            Attribute("created_at", "datetime", default="field(default_factory=datetime.now)"),
        ],
        methods=[
            FunctionBuilder(
                name="to_dict",
                args="self",
                returns="dict[str, Any]",
                docstring="Convert user to dictionary.",
                body="return asdict(self)",
            )
        ],
    )

    print(user_class.render())
    print()


def demo_pydantic() -> None:
    """Demonstrate building a Pydantic model."""
    print("=" * 60)
    print("PYDANTIC MODEL BUILDER DEMO")
    print("=" * 60)

    config_model = ClassBuilder(
        name="ServerConfig",
        bases=["BaseModel"],
        docstring="Server configuration settings.",
        attributes=[
            Attribute("host", str, default='"localhost"'),
            Attribute("port", int, default="8000"),
            Attribute("debug", bool, default="False"),
            Attribute("workers", "int | None", default="None"),
        ],
    )

    print(config_model.render())
    print()


def demo_enum() -> None:
    """Demonstrate building enums."""
    print("=" * 60)
    print("ENUM BUILDER DEMO")
    print("=" * 60)

    # Simple Enum with auto() values
    status_enum = EnumBuilder(
        name="Status",
        members=["PENDING", "APPROVED", "REJECTED"],
        base_class="Enum",
        docstring="Request status values.",
    )

    print(status_enum.render())
    print()

    # IntEnum with explicit values
    priority_enum = EnumBuilder(
        name="Priority",
        members={"LOW": 1, "MEDIUM": 5, "HIGH": 10, "CRITICAL": 99},
        base_class="IntEnum",
        docstring="Task priority levels.",
    )

    print(priority_enum.render())
    print()

    # StrEnum
    env_enum = EnumBuilder(
        name="Environment",
        members={"DEVELOPMENT": "dev", "STAGING": "staging", "PRODUCTION": "prod"},
        base_class="StrEnum",
        docstring="Deployment environments.",
    )

    print(env_enum.render())
    print()


def demo_import_manager() -> None:
    """Demonstrate the ImportManager."""
    print("=" * 60)
    print("IMPORT MANAGER DEMO")
    print("=" * 60)

    imports = ImportManager()

    # Add future imports
    imports.add_import("__future__")

    # Add standard library imports
    imports.add_from_import("typing", ["Any", "Optional", "Dict"])
    imports.add_from_import("dataclasses", "dataclass")
    imports.add_from_import("datetime", "datetime")
    imports.add_import("json")

    # Add third-party imports
    imports.add_from_import("pydantic", ["BaseModel", "Field"], is_third_party=True)
    imports.add_import("pandas", is_third_party=True)

    # Add local imports
    imports.add_from_import(".models", ["User", "Post"], is_local=True)
    imports.add_from_import("..utils", "logger", is_local=True)

    print(imports.render())
    print()


def demo_full_file() -> None:
    """Demonstrate building a complete Python file."""
    print("=" * 60)
    print("COMPLETE FILE BUILDER DEMO")
    print("=" * 60)

    builder = FileBuilder()

    # Header
    builder.add("header", '"""User management module."""')

    # Imports (could use ImportManager here!)
    builder.add("imports", "from __future__ import annotations")
    builder.get_section("imports").newline()
    builder.add("imports", "from dataclasses import dataclass")
    builder.add("imports", "from datetime import datetime")
    builder.add("imports", "from typing import Any")
    builder.get_section("imports").newline()

    # Body - add an enum
    status_enum = EnumBuilder(
        name="UserStatus",
        members=["ACTIVE", "INACTIVE", "BANNED"],
        base_class="Enum",
    )
    builder.add("body", status_enum.render())
    builder.get_section("body").newline()
    builder.get_section("body").newline()

    # Body - add a dataclass
    user_class = ClassBuilder(
        name="User",
        decorators=[Decorator("dataclass")],
        attributes=[
            Attribute("id", int),
            Attribute("name", str),
            Attribute("status", "UserStatus", default="UserStatus.ACTIVE"),
        ],
    )
    builder.add("body", user_class.render())

    print(builder.render(add_section_separators=True))
    print()


def demo_footer_helpers() -> None:
    """Demonstrate footer generation helpers."""
    print("=" * 60)
    print("FOOTER HELPERS DEMO")
    print("=" * 60)

    # Demo 1: __all__ export generation
    print("# Example 1: Simple __all__ export")
    exports = generate_all_export(["User", "Post", "Comment"])
    print(exports)
    print()

    # Demo 2: if __name__ == "__main__": with strings
    print("# Example 2: Main block with simple strings")
    main_block = generate_main_block(
        ["config = load_config()", "app = create_app(config)", "app.run()"],
        include_docstring=True,
    )
    print(main_block)
    print()

    # Demo 3: if __name__ == "__main__": with CodeBuilder objects
    print("# Example 3: Main block with CodeBuilder objects")
    setup_func = FunctionBuilder(
        name="setup",
        args="",
        returns="None",
        body='print("Setting up...")',
    )

    main_block_with_builders = generate_main_block(
        [
            setup_func,  # CodeBuilder object!
            "",
            "setup()",
            'print("Running main logic...")',
        ],
        include_docstring=True,
    )
    print(main_block_with_builders)
    print()


def main() -> None:
    """Run all demos."""
    demo_dataclass()
    demo_pydantic()
    demo_enum()
    demo_import_manager()
    demo_full_file()
    demo_footer_helpers()

    print("=" * 60)
    print("✨ These builders are ready to move to funcy-bear!")
    print("   They're completely decoupled from PyDB.")
    print("=" * 60)


if __name__ == "__main__":
    main()
