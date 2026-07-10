# Architecture

> Describes the structural design of `bioseq-toolkit` and the reasoning behind it.

---

## Layered Architecture

```
┌────────────────────────────────────────┐
│           Domain Model                 │
│   DNASequence  RNASequence             │
│   Annotation   Primer  RestrictionSite │
└──────────────┬─────────────────────────┘
               │ uses
┌──────────────▼─────────────────────────┐
│           Parser Layer                 │
│   SequenceParser  FastaParser          │
│   GenBankParser                        │
└──────────────┬─────────────────────────┘
               │ produces
┌──────────────▼─────────────────────────┐
│         Serializer Layer               │
│   to_fasta()   to_genbank()            │
└──────────────┬─────────────────────────┘
               │ delegates to
┌──────────────▼─────────────────────────┐
│            Utilities                   │
│   gc.py  reverse_complement.py         │
│   core/sequence.py                     │
└────────────────────────────────────────┘
```

---

## Layer Descriptions

### Domain Model (`models/`, `core/annotation.py`)

The domain model is the primary public surface of the library. It defines
the biological entities that consumers work with.

| Class             | Location                        | Description                            |
|-------------------|---------------------------------|----------------------------------------|
| `DNASequence`     | `models/sequence.py`            | DNA sequence with topology + metadata. |
| `RNASequence`     | `models/sequence.py`            | RNA sequence with metadata.            |
| `Annotation`      | `core/annotation.py`            | A single feature on a sequence.        |
| `Primer`          | `models/primer.py`              | PCR primer with Tm and GC methods.     |
| `RestrictionSite` | `models/restriction_site.py`    | Restriction enzyme recognition site.   |

Domain objects delegate their I/O to the parser and serializer layers. They
do not implement file parsing themselves.

---

### Parser Layer (`parsers/`)

Parsers are responsible for reading a file from disk and producing domain
model objects. All parsers inherit from `SequenceParser`.

```
parsers/
├── parser.py       ← SequenceParser ABC
├── fasta.py        ← FastaParser
└── genbank.py      ← GenBankParser
```

Format auto-detection (choosing the right parser at runtime) is handled by
`io/detect.py`.

---

### Serializer Layer (`serializers/`)

Serializers convert domain objects into file format strings. They are
invoked by `DNASequence.to_fasta()` and `DNASequence.to_genbank()`.

```
serializers/
├── fasta.py        ← to_fasta(header, sequence) -> str
└── genbank.py      ← to_genbank(record) -> str
```

---

### Utilities (`utils/`, `core/sequence.py`)

Low-level string operations that the domain model methods delegate to. These
are not the primary public API — consumers should prefer the methods on
`DNASequence` and `RNASequence`.

```
utils/
├── gc.py                   ← gc_content()
└── reverse_complement.py   ← re-exports from core.sequence

core/
├── sequence.py             ← reverse, complement, nucleotide_count,
│                             palindromic, dna_to_rna, rna_to_dna,
│                             hamming_distance, motif_search
├── enums.py                ← SequenceType, Topology
├── exceptions.py           ← InvalidNucleotideError, AmbiguousSequenceError,
│                             SequenceLengthMismatchError
└── annotation.py           ← Annotation dataclass
```

---

## Public API Surface

```python
# What consumers import
from bioseq_toolkit import (
    DNASequence,
    RNASequence,
    Annotation,
    Topology,
    SequenceType,
    Primer,
    RestrictionSite,
    SequenceParser,
    FastaParser,
    GenBankParser,
    InvalidNucleotideError,
    AmbiguousSequenceError,
    SequenceLengthMismatchError,
)
```

---

## Error Handling

Custom exception classes live in `core/exceptions.py` and all inherit from
`ValueError` for backwards compatibility. This allows callers to catch either
the specific subclass or the generic `ValueError`.

| Exception                     | Raised when                              |
|-------------------------------|------------------------------------------|
| `InvalidNucleotideError`      | Invalid character in a sequence string.  |
| `AmbiguousSequenceError`      | Sequence contains both T and U.          |
| `SequenceLengthMismatchError` | Hamming distance on unequal lengths.     |

---

## Directory Layout

```
src/bioseq_toolkit/
├── __init__.py              ← Public API (domain model + parsers + exceptions)
├── models/
│   ├── sequence.py          ← DNASequence, RNASequence
│   ├── primer.py            ← Primer
│   └── restriction_site.py  ← RestrictionSite
├── core/
│   ├── sequence.py          ← Utility functions
│   ├── annotation.py        ← Annotation
│   ├── enums.py             ← SequenceType, Topology
│   └── exceptions.py        ← Custom exceptions
├── parsers/
│   ├── parser.py            ← SequenceParser ABC
│   ├── fasta.py             ← FastaParser
│   └── genbank.py           ← GenBankParser
├── serializers/
│   ├── fasta.py             ← to_fasta()
│   └── genbank.py           ← to_genbank()
├── utils/
│   ├── gc.py                ← gc_content()
│   └── reverse_complement.py
└── io/
    └── detect.py            ← Format auto-detection
```
