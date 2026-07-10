# ADR 0001 — Domain Model First

**Status:** Accepted  
**Date:** 2026-07-10

---

## Context

The initial implementation of bioseq-toolkit exposed only utility functions
(`reverse`, `complement`, `hamming_distance`, etc.). While these are easy to
test and implement, they do not reflect how consumers actually think about
biological sequences.

A consumer of a bioinformatics library thinks in terms of:

- "I have a DNA sequence"
- "I want to know its GC content"
- "I want to parse a FASTA file and get back a sequence object"

Not:

- "I want to call `complement(sequence)` and pass a raw string"

Additionally, the project's primary consumer (CloneLab) depends on
`DNASequence`, `Annotation`, `Topology`, and `SequenceParser` as typed
objects — not free functions.

---

## Decision

Adopt a **domain model first** architecture. The primary public surface of
`bioseq-toolkit` is:

- `DNASequence`
- `RNASequence`
- `Annotation`
- `Primer`
- `RestrictionSite`
- `SequenceParser`

Utility functions (`reverse`, `complement`, etc.) still exist and are still
importable from `bioseq_toolkit.core.sequence`, but they are **not** the
primary public API. They are the implementation backbone that domain model
methods delegate to.

---

## Consequences

**Positive**
- The API reads like biology, not like string manipulation.
- Typed objects enable IDE autocomplete and static analysis.
- CloneLab integration becomes straightforward.
- Adding metadata (topology, annotations) to a sequence is natural.

**Negative**
- Phase 2 (implementation) is now more work — classes must be implemented,
  not just functions.
- Tests must be updated to use the class API once Phase 2 is complete.
  The current tests still exercise utility functions directly.

---

## Alternatives Considered

**Keep utility functions as primary API**  
Simpler to implement. Rejected because it doesn't match the consumer's
mental model and makes CloneLab integration awkward.

**Use dataclasses only (no methods)**  
Would separate data from behaviour completely. Rejected because methods like
`gc_content()` and `reverse_complement()` are natural on the sequence object
itself.
