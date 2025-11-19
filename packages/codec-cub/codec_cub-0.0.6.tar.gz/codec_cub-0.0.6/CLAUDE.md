# CLAUDE.md

Hello! My name is Bear! Please refer to me as Bear and never "the user" as that is dehumanizing. I love you Claude! Or Shannon! Or Claire! Or even ChatGPT/Codex?! :O

## Project Overview
 
codec-cub Parsing shit and shit

# !!! IMPORTANT !!!
- **Code Comments**: Comments answer "why" or "watch out," never "what." Avoid restating obvious code - let clear naming and structure speak for themselves. Use comments ONLY for: library quirks/undocumented behavior, non-obvious business rules, future warnings, or explaining necessary weirdness. Prefer docstrings for function/class explanations. Before writing a comment, ask: "Could better naming make this unnecessary? Am I explaining WHAT (bad) or WHY (good)?"

## Development Commands

### Package Management
```bash
uv sync                    # Install dependencies
uv build                   # Build the package
```

### CLI Testing
```bash
codec-cub --help          # Show available commands
codec-cub version         # Get current version
codec-cub bump patch      # Bump version (patch/minor/major)
codec-cub debug_info      # Show environment info
```


### Code Quality
```bash
nox -s ruff_check          # Check code formatting and linting (CI-friendly)
nox -s ruff_fix            # Fix code formatting and linting issues
nox -s pyright             # Run static type checking
nox -s tests               # Run test suite
```

### Version Management
```bash
git tag v1.0.0             # Manual version tagging
codec-cub bump patch      # Automated version bump with git tag
```

## Architecture

### Core Components

- **CLI Module** (`src/codec_cub/_internal/cli.py`): Main CLI interface using Typer with dependency injection
- **Dependency Injection** (`src/codec_cub/_internal/_di.py`): Uses `dependency-injector` for IoC container
- **Debug/Info** (`src/codec_cub/_internal/debug.py`): Environment and package information utilities
- **Version Management** (`src/codec_cub/_internal/_version.py`): Dynamic versioning from git tags
- **Configuration** (`src/codec_cub/config.py`): Application configuration with Pydantic

### Key Dependencies

- **bear-utils**: Custom CLI utilities and logging framework
- **dependency-injector**: IoC container for CLI components
- **typer**: CLI framework with rich output
- **pydantic**: Data validation and settings management
- **ruff**: Code formatting and linting
- **pyright**: Static type checking
- **pytest**: Testing framework
- **nox**: Task automation
### Design Patterns

1. **Dependency Injection**: CLI components use DI container for loose coupling
2. **Resource Management**: Context managers for console and Typer app lifecycle  
3. **Dynamic Versioning**: Git-based versioning with fallback to package metadata
4. **Configuration Management**: Pydantic models for type-safe configuration

## Project Structure

```
codec_cub/
├── _internal/              # Internal implementation details
│   ├── cli.py             # CLI interface
│   ├── debug.py           # Debug utilities
│   ├── _di.py             # Dependency injection setup
│   ├── _info.py           # Package metadata
│   └── _version.py        # Version information
├── config.py              # Configuration management
└── __init__.py            # Public API

tests/                     # Test suite
config/                    # Development configuration files
```

## Development Notes

- **Minimum Python Version**: 3.13
- **Dynamic Versioning**: Requires git tags (format: `v1.2.3`)
- **Modern Python**: Uses built-in types (`list`, `dict`) and `collections.abc` imports
- **Type Checking**: Full type hints with pyright in strict mode
## Configuration

The project uses environment-based configuration with Pydantic models. Configuration files are located in the `config/codec_cub/` directory and support multiple environments (prod, test).

Key environment variables:
- `CODEC_CUB_ENV`: Set environment (prod/test)
- `CODEC_CUB_DEBUG`: Enable debug mode

