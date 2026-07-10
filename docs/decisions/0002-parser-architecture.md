# ADR 0002 — Parser/Serializer Separation

**Status:** Accepted  
**Date:** 2026-07-10

---

## Context

Reading a sequence from a file and writing a sequence to a file are distinct
concerns. Many libraries conflate them into a single "I/O" module, which
creates tight coupling and makes it hard to add new formats.

---

## Decision

Separate **parsing** (file → domain object) from **serializing** (domain
object → file) into two distinct layers.

```
parsers/        ← read files, produce DNASequence/RNASequence
serializers/    ← accept domain objects, produce formatted strings/files
```

Both layers use an abstract base class (`SequenceParser`) to define a
consistent interface. Adding a new format (e.g. EMBL) requires only:

1. A new `parsers/embl.py` implementing `SequenceParser.parse()`
2. A new `serializers/embl.py` implementing a `to_embl()` function

Format auto-detection at runtime is handled by `io/detect.py`, which is
called by `DNASequence.from_file()` to choose the right parser.

---

## Consequences

**Positive**
- Clean separation of concerns.
- Each format is isolated in its own file — easy to test independently.
- `io/detect.py` is the single place responsible for format sniffing.
- Consumers can inject a specific parser directly if they want to bypass
  auto-detection.

**Negative**
- More files than a monolithic I/O module.
- `DNASequence.from_file()` must coordinate with `io/detect.py` and the
  relevant parser — a small amount of coupling between layers.

---

## Alternatives Considered

**Single `io.py` module with `read()` and `write()` functions**  
Simpler layout. Rejected because it would grow into an unmaintainable
format-dispatch god function.

**Let `DNASequence` own its own parsing**  
Would embed file format knowledge inside the domain model. Rejected because
it violates single responsibility and would make testing harder.
