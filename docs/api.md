# API Reference

> **Phase 1 Design Document** — signatures only. No implementation details.

This document defines every public function and planned class in `bioseq-toolkit`. It is the authoritative contract for what the library exposes.

---

## Module: `bioseq_toolkit.sequence`

Functions for manipulating nucleotide sequences.

---

### `reverse`

```python
def reverse(sequence: str) -> str:
    ...
```

**Parameters**

| Name       | Type  | Description      |
|------------|-------|------------------|
| `sequence` | `str` | Input sequence.  |

**Returns** `str` — The reversed sequence.

---

### `complement`

```python
def complement(sequence: str) -> str:
    ...
```

Auto-detects DNA (contains `T`) or RNA (contains `U`). Raises `ValueError` if both are present or an invalid nucleotide is found.

**Parameters**

| Name       | Type  | Description                  |
|------------|-------|------------------------------|
| `sequence` | `str` | Input DNA or RNA sequence.   |

**Returns** `str` — The complement sequence.

**Raises** `ValueError`

---

### `reverse_complement`

```python
def reverse_complement(sequence: str) -> str:
    ...
```

**Parameters**

| Name       | Type  | Description             |
|------------|-------|-------------------------|
| `sequence` | `str` | Input DNA/RNA sequence. |

**Returns** `str` — The reverse complement.

**Raises** `ValueError`

---

### `nucleotide_count`

```python
def nucleotide_count(sequence: str) -> dict[str, int]:
    ...
```

**Parameters**

| Name       | Type  | Description      |
|------------|-------|------------------|
| `sequence` | `str` | Input sequence.  |

**Returns** `dict[str, int]` — Counts keyed by nucleotide (`A`, `T`, `G`, `C`).

**Raises** `ValueError` — On invalid nucleotide.

---

### `palindromic`

```python
def palindromic(sequence: str) -> bool:
    ...
```

Checks for a **reverse-complement palindrome** (biological definition, not string reversal).

**Parameters**

| Name       | Type  | Description      |
|------------|-------|------------------|
| `sequence` | `str` | Input sequence.  |

**Returns** `bool` — `True` if the sequence equals its own reverse complement.

---

## Module: `bioseq_toolkit.transcription`

Functions for converting between DNA and RNA.

---

### `dna_to_rna`

```python
def dna_to_rna(sequence: str) -> str:
    ...
```

Converts a DNA sequence to its RNA transcript by replacing `T` → `U`.

**Parameters**

| Name       | Type  | Description         |
|------------|-------|---------------------|
| `sequence` | `str` | Input DNA sequence. |

**Returns** `str` — RNA sequence (uppercase).

**Raises** `ValueError` — If the sequence contains `U`.

---

### `rna_to_dna`

```python
def rna_to_dna(sequence: str) -> str:
    ...
```

Converts an RNA sequence to DNA by replacing `U` → `T`.

**Parameters**

| Name       | Type  | Description         |
|------------|-------|---------------------|
| `sequence` | `str` | Input RNA sequence. |

**Returns** `str` — DNA sequence (uppercase).

**Raises** `ValueError` — If the sequence contains `T`.

---

## Module: `bioseq_toolkit.comparison`

Functions for comparing sequences.

---

### `hamming_distance`

```python
def hamming_distance(sequence1: str, sequence2: str) -> int:
    ...
```

Counts positions where two equal-length sequences differ.

**Parameters**

| Name        | Type  | Description      |
|-------------|-------|------------------|
| `sequence1` | `str` | First sequence.  |
| `sequence2` | `str` | Second sequence. |

**Returns** `int` — Number of differing positions.

**Raises** `ValueError` — If sequences differ in length.

---

### `motif_search`

```python
def motif_search(sequence: str, motif: str) -> list[int]:
    ...
```

Finds all (overlapping) occurrences of `motif` within `sequence`.

**Parameters**

| Name       | Type  | Description              |
|------------|-------|--------------------------|
| `sequence` | `str` | The sequence to search.  |
| `motif`    | `str` | The motif to find.       |

**Returns** `list[int]` — Zero-based starting indices of every match.

---

## Planned Classes (Future Phases)

The following classes are **not yet implemented**. Their signatures are defined here as design targets.

---

### `DNASequence`

```python
class DNASequence:

    # --- Properties ---

    @property
    def sequence(self) -> str: ...

    @property
    def annotations(self) -> dict[str, str]: ...

    @property
    def metadata(self) -> dict[str, str]: ...

    @property
    def topology(self) -> str: ...          # "linear" | "circular"

    # --- Constructors ---

    @classmethod
    def from_string(cls, sequence: str, **kwargs) -> "DNASequence": ...

    @classmethod
    def from_file(cls, path: str) -> "DNASequence": ...

    # --- Export ---

    def to_fasta(self, path: str | None = None) -> str: ...

    def to_genbank(self, path: str | None = None) -> str: ...

    # --- Analysis ---

    def summary(self) -> dict: ...

    def reverse_complement(self) -> "DNASequence": ...

    def gc_content(self) -> float: ...
```

---

### `RNASequence`

```python
class RNASequence:

    # --- Properties ---

    @property
    def sequence(self) -> str: ...

    @property
    def annotations(self) -> dict[str, str]: ...

    @property
    def metadata(self) -> dict[str, str]: ...

    # --- Constructors ---

    @classmethod
    def from_string(cls, sequence: str, **kwargs) -> "RNASequence": ...

    @classmethod
    def from_file(cls, path: str) -> "RNASequence": ...

    # --- Export ---

    def to_fasta(self, path: str | None = None) -> str: ...

    # --- Analysis ---

    def summary(self) -> dict: ...

    def reverse_complement(self) -> "RNASequence": ...

    def gc_content(self) -> float: ...

    # --- Conversion ---

    def to_dna(self) -> "DNASequence": ...
```

---

### `SequenceComparison`

```python
class SequenceComparison:

    # --- Constructor ---

    def __init__(self, seq1: str, seq2: str) -> None: ...

    # --- Methods ---

    def hamming_distance(self) -> int: ...

    def motif_search(self, motif: str) -> list[int]: ...

    def summary(self) -> dict: ...
```
