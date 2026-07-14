# API Reference

> **Phase 1 Design Document** — signatures only. No implementation details.

The primary public surface is the **domain model**. Utility functions that
back the implementation are documented at the end.

---

## `DNASequence`

```python
from bioseq_toolkit import DNASequence
```

The central domain object. Wraps a DNA nucleotide string together with
topology, a list of annotations, and structured metadata.

### Properties

| Name          | Type              | Description                                          |
|---------------|-------------------|------------------------------------------------------|
| `sequence`    | `str`             | Raw nucleotide string (A, T, G, C — uppercase).      |
| `topology`    | `Topology`        | `LINEAR` or `CIRCULAR`.                              |
| `annotations` | `list[Annotation]`| Ordered feature annotations. See `Annotation` below. |
| `metadata`    | `dict[str, str]`  | Record-level metadata. Expected keys below.          |

**Metadata keys**

| Key           | Example                  | Description                       |
|---------------|--------------------------|-----------------------------------|
| `accession`   | `"NM_001101"`            | Primary database accession.       |
| `version`     | `"NM_001101.5"`          | Versioned accession.              |
| `organism`    | `"Homo sapiens"`         | Source organism.                  |
| `date`        | `"12-JAN-2024"`          | Record date.                      |
| `keywords`    | `"actin; cytoskeleton"`  | Semicolon-separated keywords.     |
| `name`        | `"ACTB"`                 | Short human-readable name.        |
| `description` | `"Actin, cytoplasmic 1"` | Longer free-text description.     |

### Class Methods

```python
@classmethod
def from_string(cls, sequence: str, **kwargs) -> DNASequence: ...
#   kwargs: topology, annotations, metadata

@classmethod
def from_file(cls, path: str | os.PathLike) -> DNASequence: ...
#   Format auto-detected via io.detect
```

### Validation

```python
def validate(self) -> None: ...
#   Raises InvalidDNASequence on failure

def is_valid(self) -> bool: ...
#   Returns True / False without raising
```

### Analysis

```python
def gc_content(self) -> float: ...         # 0.0 – 1.0
def reverse_complement(self) -> DNASequence: ...
```

### `summary()`

```python
def summary(self) -> dict: ...
```

Returns:

```python
{
    "name":             str,    # from metadata["name"] or ""
    "description":      str,    # from metadata["description"] or ""
    "length":           int,
    "gc_content":       float,
    "topology":         str,    # "linear" | "circular"
    "annotation_count": int,
    "molecule_type":    str,    # "DNA"
}
```

### Export

```python
def to_fasta(self, path: str | os.PathLike | None = None) -> str: ...
def to_genbank(self, path: str | os.PathLike | None = None) -> str: ...
```

### Raises

| Exception          | When                                         |
|--------------------|----------------------------------------------|
| `InvalidDNASequence` | Invalid character or ambiguous molecule type.|
| `ParserError`      | File is malformed (raised via `from_file`).  |
| `SerializationError` | Cannot serialize to the target format.     |

### Example

```python
from bioseq_toolkit import DNASequence, Topology

seq = DNASequence.from_string(
    "ATGCATGC",
    topology=Topology.LINEAR,
    metadata={"name": "test", "organism": "E. coli"},
)

seq.is_valid()              # True
seq.gc_content()            # 0.5
seq.reverse_complement()    # DNASequence("GCATGCAT")

seq.summary()
# {
#     "name": "test",
#     "description": "",
#     "length": 8,
#     "gc_content": 0.5,
#     "topology": "linear",
#     "annotation_count": 0,
#     "molecule_type": "DNA",
# }

seq.to_fasta()              # ">test\nATGCATGC\n"
seq.to_fasta("out.fasta")   # writes file, returns str
```

---

## `Annotation`

```python
from bioseq_toolkit import Annotation
```

A dataclass representing a single biological feature on a sequence.

### Fields

| Name           | Type             | Description                               |
|----------------|------------------|-------------------------------------------|
| `feature_type` | `str`            | e.g. `"gene"`, `"CDS"`, `"exon"`.        |
| `start`        | `int`            | Zero-based start position (inclusive).    |
| `end`          | `int`            | Zero-based end position (exclusive).      |
| `strand`       | `int`            | `+1` forward, `-1` reverse. Default `+1`.|
| `qualifiers`   | `dict[str, str]` | Arbitrary key-value metadata.             |
| `label`        | `str`            | Preferred human-readable label. Default `""`.|

### Methods

```python
def __len__(self) -> int: ...   # end - start
```

### Example

```python
from bioseq_toolkit import DNASequence, Annotation

gene = Annotation(
    feature_type="gene",
    start=0,
    end=720,
    strand=1,
    qualifiers={"gene": "ACTB"},
    label="ACTB",
)

seq = DNASequence.from_string(
    "ATGC" * 180,
    annotations=[gene],
)
seq.summary()["annotation_count"]  # 1
```

---

## `Topology`

```python
from bioseq_toolkit import Topology
```

```python
class Topology(Enum):
    LINEAR   = "linear"
    CIRCULAR = "circular"
```

---

## `SequenceType`

```python
from bioseq_toolkit import SequenceType
```

```python
class SequenceType(Enum):
    DNA     = "DNA"
    RNA     = "RNA"
    UNKNOWN = "UNKNOWN"
```

---

## `SequenceParser`

```python
from bioseq_toolkit import SequenceParser
```

Abstract base class for all parsers.

```python
class SequenceParser(ABC):

    @abstractmethod
    def parse(self, path: str) -> DNASequence: ...
    #   Single-record parse

    def parse_many(self, path: str) -> list[DNASequence]: ...
    #   Multi-record parse (default wraps parse())
```

### Concrete Parsers

| Class           | Format  | Supports `parse_many` |
|-----------------|---------|-----------------------|
| `FastaParser`   | FASTA   | Yes (multi-FASTA)     |
| `GenBankParser` | GenBank | Planned               |

```python
class FastaParser(SequenceParser):
    def parse(self, path: str) -> DNASequence: ...
    def parse_many(self, path: str) -> list[DNASequence]: ...

class GenBankParser(SequenceParser):
    def parse(self, path: str) -> DNASequence: ...
```

---

## `Primer`

```python
from bioseq_toolkit import Primer
```

```python
@dataclass
class Primer:
    name: str
    sequence: str

    @property
    def length(self) -> int: ...

    def gc_content(self) -> float: ...
    def melting_temperature(self) -> float: ...
```

---

## `RestrictionSite`

```python
from bioseq_toolkit import RestrictionSite
```

```python
@dataclass
class RestrictionSite:
    enzyme: str
    recognition_sequence: str
    cut_position: int

    def find_in(self, sequence: str) -> list[int]: ...
```

---

## Exceptions

```
BioSeqToolkitError          ← catch this to handle any library error
├── InvalidDNASequence      ← invalid nucleotide string
├── ParserError             ← file cannot be parsed
│   └── UnsupportedSequenceFormat  ← format not recognised
├── SerializationError      ← cannot write to target format
└── RestrictionError        ← restriction site operation failed
```

```python
from bioseq_toolkit import (
    BioSeqToolkitError,
    InvalidDNASequence,
    ParserError,
    UnsupportedSequenceFormat,
    SerializationError,
    RestrictionError,
)
```

| Exception                   | `path` attr | `sequence` attr | When raised                         |
|-----------------------------|-------------|-----------------|-------------------------------------|
| `InvalidDNASequence`        | —           | ✓               | Bad nucleotide or ambiguous type.   |
| `ParserError`               | ✓           | —               | Malformed file.                     |
| `UnsupportedSequenceFormat` | ✓           | —               | Format unrecognised by `io.detect`. |
| `SerializationError`        | —           | —               | Cannot write to target format.      |
| `RestrictionError`          | —           | —               | Restriction operation failed.       |

---

## Utility Functions

Low-level string operations used internally. Prefer the methods on
``DNASequence`` in application code.

```python
from bioseq_toolkit.core.sequence import (
    reverse, complement, reverse_complement,
    nucleotide_count, palindromic,
    dna_to_rna, rna_to_dna,
    hamming_distance, motif_search,
)
from bioseq_toolkit.utils.gc import gc_content
```

| Function              | Signature                                     | Returns     |
|-----------------------|-----------------------------------------------|-------------|
| `reverse`             | `(sequence: str) -> str`                      | `str`       |
| `complement`          | `(sequence: str) -> str`                      | `str`       |
| `reverse_complement`  | `(sequence: str) -> str`                      | `str`       |
| `nucleotide_count`    | `(sequence: str) -> dict[str, int]`           | `dict`      |
| `palindromic`         | `(sequence: str) -> bool`                     | `bool`      |
| `dna_to_rna`          | `(sequence: str) -> str`                      | `str`       |
| `rna_to_dna`          | `(sequence: str) -> str`                      | `str`       |
| `hamming_distance`    | `(sequence1: str, sequence2: str) -> int`     | `int`       |
| `motif_search`        | `(sequence: str, motif: str) -> list[int]`    | `list[int]` |
| `gc_content`          | `(sequence: str) -> float`                    | `float`     |

---

## Not Yet Implemented

The following are planned but intentionally omitted from v0.x:

- `RNASequence` — planned for v0.3
- ORF detection
- Codon translation
- Restriction site scanning (beyond the `RestrictionSite` model)
