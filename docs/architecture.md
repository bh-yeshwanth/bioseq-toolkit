# Architecture

> **Phase 1 Design Document** — describes the structural decisions behind `bioseq-toolkit`.

---

## Overview

`bioseq-toolkit` is a lightweight Python library for DNA and RNA sequence analysis. It is designed to be simple, readable, and easy to extend — not a replacement for mature libraries like Biopython, but a focused toolkit that prioritises clarity.

```
bioseq-toolkit/
├── src/
│   └── bioseq_toolkit/
│       ├── __init__.py        # Public re-exports
│       ├── sequence.py        # Core sequence operations
│       ├── transcription.py   # DNA ↔ RNA conversion
│       └── comparison.py      # Sequence comparison utilities
├── tests/
│   ├── test_sequence.py
│   ├── test_transcription.py
│   └── test_comparison.py
├── docs/
│   ├── api.md                 # Public API signatures (this phase)
│   ├── architecture.md        # This file
│   └── roadmap.md             # Planned work
└── pyproject.toml
```

---

## Design Principles

### 1. Functions first, classes later
The current implementation is entirely function-based. Functions are easier to test in isolation, easier to understand for beginners, and easier to compose. Classes (`DNASequence`, `RNASequence`) are planned for a later phase once the functional core is stable.

### 2. Explicit over implicit
Every function validates its input and raises a descriptive `ValueError` rather than silently producing wrong results. DNA/RNA auto-detection is performed per-function based on the presence of `T` or `U`.

### 3. Standard library only
No third-party runtime dependencies. The package depends only on Python ≥ 3.10 built-ins. This keeps installation trivial and removes version-conflict risk.

### 4. `src/` layout
The package lives under `src/bioseq_toolkit/` (not directly at the project root). This is the modern standard layout recommended by PyPA. It prevents accidental import of the source tree instead of the installed package during testing.

### 5. Single public surface via `__init__.py`
All public functions are re-exported from `bioseq_toolkit/__init__.py`. Consumers import from `bioseq_toolkit` directly; internal module names (`sequence`, `transcription`, `comparison`) are considered implementation detail.

---

## Module Responsibilities

| Module           | Responsibility                                           |
|------------------|----------------------------------------------------------|
| `sequence.py`    | Low-level string operations on nucleotide sequences      |
| `transcription.py` | Conversion between DNA and RNA representations         |
| `comparison.py`  | Pairwise sequence comparison and motif finding           |

---

## Error Handling Strategy

All validation is done at the boundary of each function:

- Invalid nucleotide characters → `ValueError`
- Ambiguous sequence type (both `T` and `U`) → `ValueError`
- Mismatched sequence lengths (Hamming) → `ValueError`

No custom exception classes are defined in Phase 1. This will be revisited in Phase 2 if finer-grained error handling is needed.

---

## Testing Strategy

Tests live in `tests/` and are run with `pytest`. Each module has a corresponding test file. Tests cover:

- Happy path (valid inputs)
- Edge cases (empty strings, single characters)
- Error cases (invalid input, mixed T/U)

---

## Future: Class-Based API

Phase 2 will introduce `DNASequence` and `RNASequence` classes. These will wrap the functional core and add:

- File I/O (`from_file`, `to_fasta`, `to_genbank`)
- Rich metadata (`annotations`, `topology`)
- Chainable operations

The functional API will remain available and will be the implementation backbone for the class methods.
