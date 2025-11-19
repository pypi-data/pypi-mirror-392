# TOON Codec: Complete Implementation & Refactoring

## Summary

Implements a full-featured TOON (Text Object Notation) codec with comprehensive encoder/decoder, achieving 100% specification compliance. This PR includes extensive refactoring work to establish clean, declarative patterns throughout the codebase.

**Stats**: +3,026 lines across 19 files | 103 passing tests (58 TOON-specific)

## What is TOON?

TOON is a human-readable data serialization format that combines:
- JSON's simplicity for primitives and objects
- Indentation-based structure (like YAML)
- Tabular array support for compact data representation
- Multiple delimiter options (comma, tab, pipe)

## Key Features

### ✅ 100% Spec Compliance
- **Primitives**: null, bool, numbers, strings (quoted/unquoted)
- **Objects**: Nested objects with indentation-based structure
- **Arrays**: Inline primitives, list items, and tabular format
- **Edge Cases**: Leading zeros, special floats (NaN/Inf → null), escaped strings
- **Delimiters**: Comma (default), tab (`\t`), pipe (`|`)

### 🏗️ Architecture Highlights

**Declarative Parsing with pyparsing**
- `PrimitiveParser`: Grammar-based primitive value parsing with strict left-to-right priority
- `ArrayHeaderParser`: Declarative grammar for `[N<delim?>]{fields}:` pattern
- Eliminates fragile string slicing and manual parsing

**State Machine Decoder**
- `IndentationTracker`: Manages line position, depth tracking, and lookahead
- `QuoteAwareScanner`: Consolidated quote-tracking logic using `StringCursor`
- Formal state machine replaces ad-hoc parsing logic

**Builder Pattern Encoder**
- `EncoderBuffer`: Line accumulation with automatic indentation management
- `join(*segments, depth=0, sep="")`: Declarative string construction
- Zero manual f-strings for structure building

**Separation of Concerns**
- `codec.py`: High-level encode/decode API
- `decoder.py`: State machine-based decoder (386 lines)
- `encoder.py`: Builder pattern encoder (336 lines)
- `utils.py`: Shared utilities (quoting, escaping, tabular detection)
- `constants.py`: Centralized string constants

## Refactoring Journey

This PR evolved through multiple refactoring iterations:

### Phase 1: Initial Implementation
- ✅ Basic encoder/decoder with manual string manipulation
- ✅ Nested array support (100% spec complete)
- ✅ Comprehensive test suite

### Phase 2: Formalize Parsing
- 🔧 Replace string slicing with pyparsing grammars
- 🔧 Extract `PrimitiveParser` and `ArrayHeaderParser`
- 🔧 Add `QuoteAwareScanner` for delimiter handling

### Phase 3: State Machine Decoder
- 🔧 Introduce `IndentationTracker` with `LineInfo` NamedTuple
- 🔧 Eliminate index juggling and fragile lookahead logic
- 🔧 Centralize line consumption and depth checking

### Phase 4: Declarative Encoder
- 🔧 Extract `EncoderBuffer` for line accumulation
- 🔧 Add `_at_depth()` helper to eliminate manual indentation
- 🔧 Create `join()` method with variadic signatures
- 🔧 Remove all manual f-strings for structure building
- 🔧 Standardize: `join()` for building, `str.join()` for pre-formatted lines

## Code Quality

### Before Refactoring
```python
# Manual string construction with f-strings
indent = self._indent(depth)
header = f"[{length}{delim_char}]"
if field_names:
    encoded_fields = self._cfg.delimiter.join(encode_key(f) for f in field_names)
    header += f"{{{encoded_fields}}}"
return f"{indent}{marker}{header}{SPACE}{values}"
```

### After Refactoring
```python
# Declarative construction with join()
if field_names:
    encoded_fields = self.join(*(encode_key(f) for f in field_names), sep=self._cfg.delimiter)
    return self.join("[", str(length), delim_char, "]{", encoded_fields, "}:")
return self.join("[", str(length), delim_char, "]:")
```

## Testing

**103 total tests passing** across Python 3.12, 3.13, and 3.14:
- 58 TOON codec tests (primitives, objects, arrays, edge cases, roundtrips)
- 19 MsgPack handler tests
- 26 message pack/unpack tests

**Test Coverage**:
- ✅ Primitive encoding/decoding (all types)
- ✅ Nested objects (multiple levels)
- ✅ Array formats (inline, list items, tabular)
- ✅ Deeply nested arrays and mixed content
- ✅ Delimiter variations (comma, tab, pipe)
- ✅ Edge cases (special floats, escaped strings, empty containers)
- ✅ Round-trip correctness
- ✅ Spec examples validation

## Files Changed

### Core Implementation
- `src/codec_cub/toon/codec.py` - High-level API (190 lines)
- `src/codec_cub/toon/decoder.py` - State machine decoder (386 lines)
- `src/codec_cub/toon/encoder.py` - Builder pattern encoder (336 lines)

### Parsing Infrastructure
- `src/codec_cub/toon/primitive_parser.py` - pyparsing primitives (89 lines)
- `src/codec_cub/toon/header_parser.py` - pyparsing array headers (126 lines)
- `src/codec_cub/toon/quote_scanner.py` - Quote-aware scanning (80 lines)
- `src/codec_cub/toon/indentation_tracker.py` - State machine (127 lines)

### Utilities & Config
- `src/codec_cub/toon/utils.py` - Shared utilities (234 lines)
- `src/codec_cub/toon/constants.py` - String constants
- `src/codec_cub/config.py` - ToonCodecConfig dataclass

### Tests & Examples
- `tests/test_toon_codec.py` - Comprehensive test suite (382 lines)
- `examples/toon_demo.py` - Usage examples (152 lines)

### Documentation
- `src/codec_cub/toon/README.md` - Implementation guide (292 lines)

## Breaking Changes

None - this is a new feature addition.

## Migration Guide

N/A - new implementation.

## Usage Example

```python
from codec_cub.toon import ToonCodec

codec = ToonCodec()

# Simple encoding
data = {
    "name": "Alice",
    "age": 30,
    "tags": ["python", "rust"]
}

toon_str = codec.encode(data)
# Output:
# name: Alice
# age: 30
# tags[2]: python, rust

# Decoding
decoded = codec.decode(toon_str)
assert decoded == data

# Tabular arrays
users = [
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False}
]

toon_str = codec.encode(users)
# Output:
# [2]{id,name,active}:
#   1, Alice, true
#   2, Bob, false
```

## Commit History

19 commits total, organized by phase:

**Initial Implementation**
- Add TOON PoC implementation summary documentation
- Clean up obvious comments in TOON codec
- Implement full nested array support (100% spec complete!)

**Type Safety & Code Quality**
- Enhance TOON codec: improve type annotations and add escape/unescape utility functions
- Refactor TOON codec implementation: streamline code, enhance readability
- Clean up ruff linting issues

**Parser Refactoring**
- Refactor TOON decoder: formalize state machine and eliminate fragile string slicing
- Add pyparsing-based primitive value parser
- Enhance TOON codec implementation: add buffer class and LineInfo

**Encoder Refactoring**
- Refactor _encode_list_item: extract methods for clarity
- Refactor encoder: eliminate manual indent juggling with _at_depth helper
- Refactor EncoderBuffer: enhance segment handling and indentation logic
- Refactor encoder: fully declarative string construction

## Performance Considerations

- **Parsing**: pyparsing grammars are compiled once at initialization
- **Memory**: EncoderBuffer accumulates lines but clears after build
- **Indentation**: Pre-computed per line in decoder, on-demand in encoder

## Future Work

Potential improvements (out of scope for this PR):
- Streaming decoder for large files
- Schema validation
- Performance benchmarks vs JSON/YAML
- CLI tool for format conversion

## Acknowledgements

This implementation went through extensive pair-programming iterations to refine patterns and establish clean abstractions. Special thanks to Bear for the excellent refactoring ideas on the encoder! 🎉
