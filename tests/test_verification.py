"""
v0.2 Verification tests.

Covers the specific checks requested before calling v0.2 complete:

1.  Parser round-trips  (FASTA and GenBank)
2.  Empty sequence contract
3.  Invalid nucleotides
4.  Circular topology through parse → serialize → parse
5.  Annotation ordering contract
6.  Large sequence parsing performance
"""

import os
import time
import random
import tempfile

import pytest

from bioseq_toolkit import (
    DNASequence,
    Annotation,
    Topology,
    InvalidDNASequence,
)


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


# ===========================================================================
# 1. Parser round-trips
# ===========================================================================

class TestFastaRoundTrip:
    """FASTA  →  DNASequence  →  FASTA  →  DNASequence — field equality."""

    def test_sequence_survives_round_trip(self):
        original = DNASequence.from_file(os.path.join(DATA_DIR, "linear.fa"))
        fasta_str = original.to_fasta()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as tmp:
            tmp.write(fasta_str)
            tmp_path = tmp.name

        try:
            restored = DNASequence.from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        assert restored.sequence == original.sequence

    def test_name_survives_round_trip(self):
        original = DNASequence.from_file(os.path.join(DATA_DIR, "linear.fa"))
        fasta_str = original.to_fasta()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as tmp:
            tmp.write(fasta_str)
            tmp_path = tmp.name

        try:
            restored = DNASequence.from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        assert restored.name == original.name

    def test_description_survives_round_trip(self):
        original = DNASequence.from_string(
            "ATGCATGC",
            name="myseq",
            description="a test sequence",
        )
        fasta_str = original.to_fasta()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as tmp:
            tmp.write(fasta_str)
            tmp_path = tmp.name

        try:
            restored = DNASequence.from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        assert restored.description == original.description

    def test_multi_record_parse_many(self):
        """parse_many returns the same records as two individual parses."""
        from bioseq_toolkit.parsers.fasta import FastaParser

        multi_fasta = ">seq1\nATGC\n>seq2\nGCTA\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as tmp:
            tmp.write(multi_fasta)
            tmp_path = tmp.name

        try:
            records = FastaParser().parse_many(tmp_path)
        finally:
            os.unlink(tmp_path)

        assert len(records) == 2
        assert records[0].sequence == "ATGC"
        assert records[1].sequence == "GCTA"
        assert records[0].name == "seq1"
        assert records[1].name == "seq2"


class TestGenBankRoundTrip:
    """GenBank  →  DNASequence  →  GenBank  →  DNASequence — field equality."""

    def _round_trip(self, source_path: str) -> tuple[DNASequence, DNASequence]:
        original = DNASequence.from_file(source_path)
        gb_str = original.to_genbank()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gb", delete=False
        ) as tmp:
            tmp.write(gb_str)
            tmp_path = tmp.name

        try:
            restored = DNASequence.from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        return original, restored

    def test_sequence_survives_round_trip(self):
        original, restored = self._round_trip(
            os.path.join(DATA_DIR, "example.gb")
        )
        assert restored.sequence == original.sequence

    def test_name_survives_round_trip(self):
        original, restored = self._round_trip(
            os.path.join(DATA_DIR, "example.gb")
        )
        assert restored.name == original.name

    def test_description_survives_round_trip(self):
        original, restored = self._round_trip(
            os.path.join(DATA_DIR, "example.gb")
        )
        assert restored.description == original.description

    def test_topology_survives_round_trip(self):
        """Circular topology flag must not be lost through serialise → parse."""
        original, restored = self._round_trip(
            os.path.join(DATA_DIR, "plasmid.gb")
        )
        assert restored.topology == original.topology == Topology.CIRCULAR

    def test_annotation_count_survives_round_trip(self):
        original, restored = self._round_trip(
            os.path.join(DATA_DIR, "example.gb")
        )
        assert len(restored.annotations) == len(original.annotations)


# ===========================================================================
# 2. Empty sequence contract
# ===========================================================================

class TestEmptySequenceContract:
    """
    DNASequence.from_string("") MUST raise InvalidDNASequence.
    Raw construction DNASequence("") is allowed but is_valid() == False.
    """

    def test_from_string_empty_raises(self):
        """Empty string passed through from_string raises immediately."""
        with pytest.raises(InvalidDNASequence, match="empty"):
            DNASequence.from_string("")

    def test_raw_construction_empty_is_invalid(self):
        """Direct dataclass construction of empty sequence is invalid."""
        seq = DNASequence(sequence="")
        assert not seq.is_valid()

    def test_raw_construction_empty_validate_raises(self):
        seq = DNASequence(sequence="")
        with pytest.raises(InvalidDNASequence):
            seq.validate()


# ===========================================================================
# 3. Invalid nucleotides
# ===========================================================================

class TestInvalidNucleotides:
    """ATGCX, ATG123, ATG* all raise InvalidDNASequence via from_string."""

    @pytest.mark.parametrize("bad_sequence, label", [
        ("ATGCX",  "letter X"),
        ("ATG123", "digits"),
        ("ATG*",   "asterisk"),
        ("ATG Z",  "space + letter"),
        ("ATGC\t", "tab character"),
    ])
    def test_invalid_raises(self, bad_sequence: str, label: str):
        with pytest.raises(InvalidDNASequence, match="Invalid"):
            DNASequence.from_string(bad_sequence)

    def test_exception_carries_sequence(self):
        with pytest.raises(InvalidDNASequence) as exc_info:
            DNASequence.from_string("ATGCX")
        # The exception must carry the bad sequence for debugging.
        assert exc_info.value.sequence == "ATGCX"

    def test_valid_characters_do_not_raise(self):
        """Sanity check: A, T, G, C, N are all accepted."""
        DNASequence.from_string("ATGCN")


# ===========================================================================
# 4. Circular topology through parse → serialize → parse
# ===========================================================================

class TestCircularTopologyRoundTrip:
    """Topology.CIRCULAR must survive the full parse → serialize → parse cycle."""

    def test_fasta_does_not_encode_topology(self):
        """
        FASTA format has no topology field.
        After a FASTA round-trip the topology defaults to LINEAR.
        This is the documented, expected behaviour.
        """
        original = DNASequence.from_string(
            "ATGCATGC", topology=Topology.CIRCULAR
        )
        fasta = original.to_fasta()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as tmp:
            tmp.write(fasta)
            tmp_path = tmp.name

        try:
            restored = DNASequence.from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        # FASTA cannot encode topology — this is expected and not a bug.
        assert restored.topology == Topology.LINEAR

    def test_genbank_preserves_circular(self):
        """GenBank LOCUS line carries topology — must survive round-trip."""
        original = DNASequence.from_file(
            os.path.join(DATA_DIR, "plasmid.gb")
        )
        assert original.topology == Topology.CIRCULAR

        gb_str = original.to_genbank()
        assert "circular" in gb_str.lower()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gb", delete=False
        ) as tmp:
            tmp.write(gb_str)
            tmp_path = tmp.name

        try:
            restored = DNASequence.from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        assert restored.topology == Topology.CIRCULAR

    def test_genbank_preserves_linear(self):
        original = DNASequence.from_file(
            os.path.join(DATA_DIR, "example.gb")
        )
        assert original.topology == Topology.LINEAR

        gb_str = original.to_genbank()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gb", delete=False
        ) as tmp:
            tmp.write(gb_str)
            tmp_path = tmp.name

        try:
            restored = DNASequence.from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        assert restored.topology == Topology.LINEAR


# ===========================================================================
# 5. Annotation ordering contract
# ===========================================================================

class TestAnnotationOrdering:
    """
    DNASequence preserves annotation insertion order.
    validate() does NOT sort annotations.
    This is the documented contract.
    """

    def test_insertion_order_preserved(self):
        ann1 = Annotation(feature_type="gene", start=100, end=200, strand=1)
        ann2 = Annotation(feature_type="CDS",  start=10,  end=90,  strand=1)
        ann3 = Annotation(feature_type="exon", start=300, end=400, strand=-1)

        seq = DNASequence.from_string(
            "A" * 500,
            annotations=[ann1, ann2, ann3],
        )

        assert seq.annotations[0].feature_type == "gene"
        assert seq.annotations[1].feature_type == "CDS"
        assert seq.annotations[2].feature_type == "exon"

    def test_validate_does_not_sort(self):
        """validate() must not reorder annotations as a side effect."""
        ann_late  = Annotation(feature_type="CDS",  start=200, end=400, strand=1)
        ann_early = Annotation(feature_type="gene", start=0,   end=100, strand=1)

        seq = DNASequence.from_string(
            "A" * 500,
            annotations=[ann_late, ann_early],
        )
        seq.validate()  # must not raise and must not sort

        assert seq.annotations[0].start == 200   # still first
        assert seq.annotations[1].start == 0     # still second

    def test_empty_annotations_is_valid(self):
        seq = DNASequence.from_string("ATGC")
        seq.validate()
        assert seq.annotations == []


# ===========================================================================
# 6. Large sequence parsing performance
# ===========================================================================

class TestLargeSequenceParsing:
    """
    5 MB FASTA must parse in under 2 seconds.
    Catches O(n²) string concatenation regressions.
    """

    @pytest.fixture
    def large_fasta_file(self, tmp_path):
        """Generate a ~5 MB FASTA file with a single record."""
        random.seed(42)
        bases = "ATGC"
        # 5 000 000 bases ≈ 5 MB of sequence data
        sequence = "".join(random.choices(bases, k=5_000_000))

        fasta_path = tmp_path / "large.fasta"
        with open(fasta_path, "w") as fh:
            fh.write(">large_sequence synthetic 5MB benchmark\n")
            # Write in 70-char lines (standard FASTA)
            for i in range(0, len(sequence), 70):
                fh.write(sequence[i : i + 70] + "\n")

        return fasta_path, sequence

    def test_parse_5mb_fasta_completes(self, large_fasta_file):
        fasta_path, expected_sequence = large_fasta_file
        seq = DNASequence.from_file(str(fasta_path))
        assert seq.sequence == expected_sequence

    def test_parse_5mb_fasta_is_fast(self, large_fasta_file):
        """Parsing 5 MB must complete in under 2 seconds."""
        fasta_path, _ = large_fasta_file

        start = time.perf_counter()
        DNASequence.from_file(str(fasta_path))
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, (
            f"Parsing 5 MB FASTA took {elapsed:.2f}s — possible O(n²) regression"
        )

    def test_gc_content_on_large_sequence(self, large_fasta_file):
        """GC content on a large sequence must be within 1% of 0.5."""
        fasta_path, _ = large_fasta_file
        seq = DNASequence.from_file(str(fasta_path))
        gc = seq.gc_content()
        assert abs(gc - 0.5) < 0.01, f"GC content {gc:.4f} is unexpectedly far from 0.5"


# ===========================================================================
# 7. GenBank Annotation Label Resolution
# ===========================================================================

class TestGenBankLabelResolution:
    """Verify that the GenBank parser correctly resolves annotation labels in priority order."""

    def test_resolve_gene(self):
        from io import StringIO
        gb_content = """LOCUS       test         8 bp    DNA     linear   SYN 13-JUL-2026
FEATURES             Location/Qualifiers
     gene            1..8
                     /gene="lacZ"
                     /label="lacZ-label"
                     /product="beta-galactosidase"
                     /note="a note"
ORIGIN
        1 atgcatgc
//
"""
        seq = DNASequence.from_file(StringIO(gb_content))
        assert len(seq.annotations) == 1
        assert seq.annotations[0].label == "lacZ"

    def test_resolve_label(self):
        from io import StringIO
        gb_content = """LOCUS       test         8 bp    DNA     linear   SYN 13-JUL-2026
FEATURES             Location/Qualifiers
     gene            1..8
                     /label="lacZ-label"
                     /product="beta-galactosidase"
                     /note="a note"
ORIGIN
        1 atgcatgc
//
"""
        seq = DNASequence.from_file(StringIO(gb_content))
        assert len(seq.annotations) == 1
        assert seq.annotations[0].label == "lacZ-label"

    def test_resolve_product(self):
        from io import StringIO
        gb_content = """LOCUS       test         8 bp    DNA     linear   SYN 13-JUL-2026
FEATURES             Location/Qualifiers
     gene            1..8
                     /product="beta-galactosidase"
                     /note="a note"
ORIGIN
        1 atgcatgc
//
"""
        seq = DNASequence.from_file(StringIO(gb_content))
        assert len(seq.annotations) == 1
        assert seq.annotations[0].label == "beta-galactosidase"

    def test_resolve_note(self):
        from io import StringIO
        gb_content = """LOCUS       test         8 bp    DNA     linear   SYN 13-JUL-2026
FEATURES             Location/Qualifiers
     gene            1..8
                     /note="a note"
ORIGIN
        1 atgcatgc
//
"""
        seq = DNASequence.from_file(StringIO(gb_content))
        assert len(seq.annotations) == 1
        assert seq.annotations[0].label == "a note"

    def test_resolve_no_match(self):
        from io import StringIO
        gb_content = """LOCUS       test         8 bp    DNA     linear   SYN 13-JUL-2026
FEATURES             Location/Qualifiers
     gene            1..8
                     /db_xref="GI:12345"
ORIGIN
        1 atgcatgc
//
"""
        seq = DNASequence.from_file(StringIO(gb_content))
        assert len(seq.annotations) == 1
        assert seq.annotations[0].label == ""
