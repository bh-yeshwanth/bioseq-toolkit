# Roadmap

> High-level plan for `bioseq-toolkit`. Subject to change.

---

## Phase 1 — API Design ✅

**Goal:** Define the public API and architecture before writing implementation.

- [x] Create `docs/` directory
- [x] Write `architecture.md` — layered architecture (domain → parser → serializer → utils)
- [x] Write `api.md` — full API signatures for all public objects
- [x] Define `DNASequence` with `list[Annotation]`, typed metadata, `validate()`, `summary()`
- [x] Define `SequenceParser` ABC with `parse() -> DNASequence` and `parse_many()`
- [x] Define exception hierarchy rooted at `BioSeqToolkitError`
- [x] Create `tests/data/` with FASTA and GenBank fixtures
- [x] Write Architecture Decision Records (`docs/decisions/`)
- [x] Restructure package into `core/`, `models/`, `parsers/`, `serializers/`, `utils/`, `io/`

**Deferred to later phases:**
- `RNASequence` → v0.3 (no current consumer need)

---

## Phase 2 — DNASequence Implementation

**Goal:** Implement `DNASequence` and all its dependencies.

- [ ] Implement `core/sequence.py` utility functions
  - [ ] `reverse`, `complement`, `reverse_complement`
  - [ ] `nucleotide_count`, `palindromic`
  - [ ] `dna_to_rna`, `rna_to_dna`
  - [ ] `hamming_distance`, `motif_search`
- [ ] Implement `utils/gc.py` — `gc_content()`
- [ ] Implement `DNASequence`
  - [ ] `from_string()` with validation
  - [ ] `validate()` and `is_valid()`
  - [ ] `gc_content()`, `reverse_complement()`, `summary()`
- [ ] Full test coverage for all utility functions
- [ ] CI pipeline (GitHub Actions) — run `pytest` on push

---

## Phase 3 — Parsers & Serializers

**Goal:** Implement file I/O. Every parsed object must pass `validate()`.

- [ ] `io/detect.py` — format auto-detection
- [ ] `parsers/fasta.py` — `FastaParser.parse()` and `parse_many()`
- [ ] `parsers/genbank.py` — `GenBankParser.parse()` (FEATURES + metadata)
- [ ] `serializers/fasta.py` — `to_fasta()`
- [ ] `serializers/genbank.py` — `to_genbank()`
- [ ] `DNASequence.from_file()` and `to_fasta()` / `to_genbank()` wired up
- [ ] Parser tests using `tests/data/` fixtures
- [ ] `RNASequence` (v0.3)

---

## Phase 4 — Extended Analysis

**Goal:** Add biologically useful features.

- [ ] ORF (Open Reading Frame) detection
- [ ] Codon → amino acid translation
- [ ] `RestrictionSite.find_in()` implementation
- [ ] `Primer.gc_content()` and `Primer.melting_temperature()`
- [ ] Strand-aware annotation mirroring in `reverse_complement()`

---

## Phase 5 — Polish & Publication

**Goal:** Make the package production-ready.

- [ ] Auto-generated API docs (`pdoc` or `mkdocs`)
- [ ] `CHANGELOG.md`
- [ ] `CONTRIBUTING.md`
- [ ] Semantic versioning (`v1.0.0`)
- [ ] Publish to PyPI
