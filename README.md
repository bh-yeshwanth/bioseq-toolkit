# BioSeq Toolkit

A lightweight Python package for basic DNA/RNA sequence analysis.

> This project was built as part of my journey to learn Python software engineering for computational biology. It is intended as a learning project rather than a replacement for mature libraries such as Biopython.

---

## Features

- Reverse sequence
- Complement & reverse complement
- Nucleotide counting
- Palindrome detection
- DNA ↔ RNA transcription
- Hamming distance
- Motif search

---

## Project Structure

```
bioseq-toolkit/
├── src/
│   └── bioseq_toolkit/
│       ├── __init__.py          # Public API re-exports
│       ├── core/
│       │   ├── sequence.py      # All core sequence operations
│       │   ├── annotation.py    # Annotation dataclass
│       │   ├── enums.py         # SequenceType, Topology enums
│       │   └── exceptions.py    # Custom exception classes
│       ├── parsers/
│       │   ├── parser.py        # BaseParser ABC
│       │   ├── fasta.py         # FASTA parser (stub)
│       │   └── genbank.py       # GenBank parser (stub)
│       ├── serializers/
│       │   ├── fasta.py         # FASTA serializer (stub)
│       │   └── genbank.py       # GenBank serializer (stub)
│       ├── utils/
│       │   ├── gc.py            # GC content utility (stub)
│       │   └── reverse_complement.py
│       ├── models/
│       │   ├── primer.py        # Primer dataclass (stub)
│       │   └── restriction_site.py
│       └── io/
│           └── detect.py        # File-format auto-detection (stub)
├── tests/
│   ├── test_sequence.py
│   ├── test_transcription.py
│   └── test_comparison.py
├── docs/
│   ├── api.md                   # Public API signatures (Phase 1 design)
│   ├── architecture.md          # Structural decisions and principles
│   └── roadmap.md               # Phased development plan
└── pyproject.toml
```

---

## Installation

```bash
git clone https://github.com/bh-yeshwanth/bioseq-toolkit.git

cd bioseq-toolkit

python3 -m venv .venv

source .venv/bin/activate

pip install -e .

