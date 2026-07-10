# Roadmap

> High-level plan for `bioseq-toolkit`. Subject to change.

---

## Phase 1 — API Design ✅

**Goal:** Define the public API before writing implementation.

- [x] Create `docs/` directory
- [x] Write `architecture.md`
- [x] Write `api.md` — all public function signatures
- [x] Define planned class signatures (`DNASequence`, `RNASequence`, `SequenceComparison`)

---

## Phase 2 — Functional Core

**Goal:** Implement and test all standalone functions.

- [ ] `sequence.py` — `reverse`, `complement`, `reverse_complement`, `nucleotide_count`, `palindromic`
- [ ] `transcription.py` — `dna_to_rna`, `rna_to_dna`
- [ ] `comparison.py` — `hamming_distance`, `motif_search`
- [ ] Full test coverage for all functions
- [ ] CI pipeline (GitHub Actions) — run `pytest` on push

---

## Phase 3 — Class-Based API

**Goal:** Wrap the functional core in `DNASequence` and `RNASequence` classes.

- [ ] `DNASequence` class
  - [ ] `from_string()` constructor
  - [ ] `from_file()` — FASTA support
  - [ ] `to_fasta()`, `to_genbank()` export
  - [ ] `summary()`, `gc_content()`, `reverse_complement()` methods
  - [ ] `sequence`, `annotations`, `metadata`, `topology` properties
- [ ] `RNASequence` class
  - [ ] Mirror of `DNASequence` (minus GenBank, plus `to_dna()`)
- [ ] `SequenceComparison` class
  - [ ] Wraps `hamming_distance` and `motif_search`
  - [ ] `summary()` method

---

## Phase 4 — Extended Analysis

**Goal:** Add biologically useful analysis features.

- [ ] GC content calculation (`gc_content`)
- [ ] ORF (Open Reading Frame) detection
- [ ] Translation — codon → amino acid
- [ ] Restriction site detection
- [ ] Basic FASTA multi-record file parsing

---

## Phase 5 — Polish & Publication

**Goal:** Make the package usable by others.

- [ ] Full API documentation (auto-generated with `pdoc` or `mkdocs`)
- [ ] Publish to PyPI
- [ ] `CHANGELOG.md`
- [ ] `CONTRIBUTING.md`
- [ ] Semantic versioning (`v1.0.0`)
