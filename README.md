# BioSeq Toolkit

A Python toolkit for working with DNA sequences — parsing, analysis, annotation, and serialization.

> This project was built as part of my journey to learn Python software engineering for computational biology. It is intended as a learning project rather than a replacement for mature libraries such as Biopython.

---

## Core Abstractions

| Object            | Description                                                      |
|-------------------|------------------------------------------------------------------|
| `DNASequence`     | DNA sequence with topology, annotations list, and metadata.      |
| `Annotation`      | A single biological feature (gene, CDS, exon, etc.).             |
| `Topology`        | `LINEAR` or `CIRCULAR`.                                          |
| `SequenceParser`  | Abstract base for FASTA and GenBank parsers.                     |
| `FastaParser`     | Parses single and multi-record FASTA files.                      |
| `GenBankParser`   | Parses GenBank records including FEATURES and metadata.          |
| `Primer`          | PCR primer with GC content and melting temperature.              |
| `RestrictionSite` | Restriction enzyme recognition site and cut finder.              |

---

## Quick Look

```python
from bioseq_toolkit import DNASequence, Topology, Annotation

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
```

```python
from bioseq_toolkit import DNASequence

seq = DNASequence.from_file("example.fasta")   # format auto-detected
seq.to_genbank("out.gb")
```

```python
# v0.2.1 — parse directly from a pathlib.Path
from pathlib import Path
from bioseq_toolkit import DNASequence

seq = DNASequence.from_file(Path("example.fasta"))
```

---

## Parsing from a Stream (v0.2.1)

`from_file()` now accepts file-like text streams in addition to filesystem paths.
This lets web applications (e.g. FastAPI) parse uploaded files **without writing
them to disk**.

```python
from io import StringIO
from bioseq_toolkit import DNASequence

fasta = """\
>Example
ATGCGCGATATAT
"""

sequence = DNASequence.from_file(StringIO(fasta))
print(sequence.summary())
# {
#     "name": "Example",
#     "description": "",
#     "length": 13,
#     "gc_content": 0.46...,
#     "topology": "linear",
#     "annotation_count": 0,
#     "molecule_type": "DNA",
# }
```

The same works with GenBank streams and any `typing.TextIO`-compatible object
(e.g. an `open()` file handle, `io.StringIO`, `io.TextIOBase`).

```python
# FastAPI upload example (no temp file needed)
from io import StringIO
from fastapi import UploadFile
from bioseq_toolkit import DNASequence

async def parse_upload(file: UploadFile) -> dict:
    text = (await file.read()).decode("utf-8")
    seq = DNASequence.from_file(StringIO(text))
    return seq.summary()
```

---

## Error Handling

All errors share a common base class:

```python
from bioseq_toolkit import BioSeqToolkitError

try:
    seq = DNASequence.from_file("data.fasta")
except BioSeqToolkitError as e:
    print(e)
```

Full hierarchy:

```
BioSeqToolkitError
├── InvalidDNASequence
├── ParserError
│   └── UnsupportedSequenceFormat
├── SerializationError
└── RestrictionError
```

---

## Architecture

```
Domain Model  →  Parser Layer   →  Serializer Layer  →  Utilities
DNASequence      SequenceParser     to_fasta()            gc_content()
Annotation       FastaParser        to_genbank()          reverse_complement()
Primer           GenBankParser
RestrictionSite
```

See [`docs/architecture.md`](docs/architecture.md) and [`docs/decisions/`](docs/decisions/) for design rationale.

---

## Project Structure

```
bioseq-toolkit/
├── src/
│   └── bioseq_toolkit/
│       ├── __init__.py          # Public API
│       ├── models/
│       │   ├── sequence.py      # DNASequence
│       │   ├── primer.py        # Primer
│       │   └── restriction_site.py
│       ├── core/
│       │   ├── sequence.py      # Utility functions
│       │   ├── annotation.py    # Annotation
│       │   ├── enums.py         # SequenceType, Topology
│       │   └── exceptions.py    # BioSeqToolkitError hierarchy
│       ├── parsers/             # SequenceParser, FastaParser, GenBankParser
│       ├── serializers/         # to_fasta(), to_genbank()
│       ├── utils/               # gc_content, reverse_complement
│       └── io/                  # Format auto-detection
├── tests/
│   ├── data/                    # example.fasta, example.gb, plasmid.gb, ...
│   ├── test_sequence.py
│   ├── test_transcription.py
│   └── test_comparison.py
└── docs/
    ├── api.md                   # Full API reference
    ├── architecture.md          # Layered architecture
    ├── roadmap.md               # Phased development plan
    └── decisions/
        ├── 0001-domain-model.md
        └── 0002-parser-architecture.md
```

---

## Installation

```bash
git clone https://github.com/bh-yeshwanth/bioseq-toolkit.git

cd bioseq-toolkit

python3 -m venv .venv

source .venv/bin/activate

pip install -e .
