"""Tests for DNASequence — the canonical domain object."""

import os
import pytest

from bioseq_toolkit import DNASequence, Annotation, Topology
from bioseq_toolkit import InvalidDNASequence, BioSeqToolkitError
from bioseq_toolkit import ParserError


# ---------------------------------------------------------------------------
# from_string
# ---------------------------------------------------------------------------

class TestFromString:

    def test_basic(self):
        seq = DNASequence.from_string("ATGC")
        assert seq.sequence == "ATGC"

    def test_normalises_to_uppercase(self):
        seq = DNASequence.from_string("atgc")
        assert seq.sequence == "ATGC"

    def test_n_is_valid(self):
        seq = DNASequence.from_string("ATGCN")
        assert seq.is_valid()

    def test_name_and_description(self):
        seq = DNASequence.from_string("ATGC", name="test", description="a test seq")
        assert seq.name == "test"
        assert seq.description == "a test seq"

    def test_topology_default_linear(self):
        seq = DNASequence.from_string("ATGC")
        assert seq.topology == Topology.LINEAR

    def test_topology_circular(self):
        seq = DNASequence.from_string("ATGC", topology=Topology.CIRCULAR)
        assert seq.topology == Topology.CIRCULAR

    def test_molecule_type(self):
        seq = DNASequence.from_string("ATGC")
        assert seq.molecule_type == "DNA"

    def test_empty_raises(self):
        with pytest.raises(InvalidDNASequence):
            DNASequence.from_string("")

    def test_invalid_nucleotide_raises(self):
        with pytest.raises(InvalidDNASequence):
            DNASequence.from_string("ATXC")

    def test_invalid_is_bioseq_error(self):
        with pytest.raises(BioSeqToolkitError):
            DNASequence.from_string("ZZZZZ")


# ---------------------------------------------------------------------------
# validate / is_valid
# ---------------------------------------------------------------------------

class TestValidation:

    def test_is_valid_true(self):
        assert DNASequence.from_string("ATGC").is_valid()

    def test_is_valid_false_after_mutation(self):
        seq = DNASequence.from_string("ATGC")
        # Bypass from_string to inject bad data directly
        seq.sequence = "ATXC"
        assert not seq.is_valid()

    def test_validate_raises_on_bad_char(self):
        seq = DNASequence("ATXC")   # raw construction skips validate
        with pytest.raises(InvalidDNASequence):
            seq.validate()

    def test_validate_raises_on_empty(self):
        seq = DNASequence("")
        with pytest.raises(InvalidDNASequence):
            seq.validate()


# ---------------------------------------------------------------------------
# length
# ---------------------------------------------------------------------------

class TestLength:

    def test_length_property(self):
        seq = DNASequence.from_string("ATGC")
        assert seq.length == 4

    def test_len_builtin(self):
        seq = DNASequence.from_string("ATGCATGC")
        assert len(seq) == 8


# ---------------------------------------------------------------------------
# gc_content
# ---------------------------------------------------------------------------

class TestGCContent:

    def test_half_gc(self):
        seq = DNASequence.from_string("ATGC")
        assert seq.gc_content() == 0.5

    def test_all_gc(self):
        seq = DNASequence.from_string("GCGC")
        assert seq.gc_content() == 1.0

    def test_no_gc(self):
        seq = DNASequence.from_string("ATAT")
        assert seq.gc_content() == 0.0

    def test_longer_sequence(self):
        seq = DNASequence.from_string("ATGCATGC")
        assert seq.gc_content() == 0.5


# ---------------------------------------------------------------------------
# reverse_complement
# ---------------------------------------------------------------------------

class TestReverseComplement:

    def test_basic(self):
        seq = DNASequence.from_string("ATGC")
        rc = seq.reverse_complement()
        assert rc.sequence == "GCAT"

    def test_returns_new_object(self):
        seq = DNASequence.from_string("ATGC")
        rc = seq.reverse_complement()
        assert rc is not seq

    def test_topology_preserved(self):
        seq = DNASequence.from_string("ATGC", topology=Topology.CIRCULAR)
        rc = seq.reverse_complement()
        assert rc.topology == Topology.CIRCULAR

    def test_name_preserved(self):
        seq = DNASequence.from_string("ATGC", name="mygene")
        rc = seq.reverse_complement()
        assert rc.name == "mygene"

    def test_double_rc_is_original(self):
        seq = DNASequence.from_string("ATGCATGC")
        assert seq.reverse_complement().reverse_complement().sequence == seq.sequence


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

class TestSummary:

    def test_keys_present(self):
        seq = DNASequence.from_string("ATGC", name="test", description="desc")
        s = seq.summary()
        assert set(s.keys()) == {
            "name", "description", "length", "gc_content",
            "topology", "annotation_count", "molecule_type",
        }

    def test_values(self):
        seq = DNASequence.from_string("ATGC", name="t", description="d")
        s = seq.summary()
        assert s["name"] == "t"
        assert s["description"] == "d"
        assert s["length"] == 4
        assert s["gc_content"] == 0.5
        assert s["topology"] == "linear"
        assert s["annotation_count"] == 0
        assert s["molecule_type"] == "DNA"

    def test_annotation_count(self):
        ann = Annotation(feature_type="gene", start=0, end=4, strand=1)
        seq = DNASequence.from_string("ATGC", annotations=[ann])
        assert seq.summary()["annotation_count"] == 1


# ---------------------------------------------------------------------------
# to_fasta
# ---------------------------------------------------------------------------

class TestToFasta:

    def test_basic_format(self):
        seq = DNASequence.from_string("ATGC", name="test")
        fasta = seq.to_fasta()
        assert fasta.startswith(">test\n")
        assert "ATGC" in fasta

    def test_header_includes_description(self):
        seq = DNASequence.from_string("ATGC", name="id", description="my seq")
        fasta = seq.to_fasta()
        assert fasta.startswith(">id my seq\n")

    def test_write_to_file(self, tmp_path):
        seq = DNASequence.from_string("ATGC", name="test")
        out = tmp_path / "out.fasta"
        result = seq.to_fasta(path=str(out))
        assert out.exists()
        assert out.read_text() == result


# ---------------------------------------------------------------------------
# to_genbank
# ---------------------------------------------------------------------------

class TestToGenBank:

    def test_contains_locus(self):
        seq = DNASequence.from_string("ATGC", name="myseq")
        gb = seq.to_genbank()
        assert "LOCUS" in gb

    def test_contains_origin(self):
        seq = DNASequence.from_string("ATGC")
        gb = seq.to_genbank()
        assert "ORIGIN" in gb

    def test_ends_with_terminator(self):
        seq = DNASequence.from_string("ATGC")
        gb = seq.to_genbank()
        assert gb.strip().endswith("//")

    def test_write_to_file(self, tmp_path):
        seq = DNASequence.from_string("ATGC", name="test")
        out = tmp_path / "out.gb"
        result = seq.to_genbank(path=str(out))
        assert out.exists()
        assert out.read_text() == result


# ---------------------------------------------------------------------------
# from_file (FASTA)
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestFromFileFasta:

    def test_reads_linear_fasta(self):
        path = os.path.join(DATA_DIR, "linear.fa")
        seq = DNASequence.from_file(path)
        assert seq.name == "SEQ001"
        assert seq.sequence == "ATGCATGCATGCATGCATGC"

    def test_reads_example_fasta(self):
        path = os.path.join(DATA_DIR, "example.fasta")
        seq = DNASequence.from_file(path)
        assert seq.name.startswith("NM_")
        assert len(seq.sequence) > 0

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            DNASequence.from_file("does_not_exist.fasta")


# ---------------------------------------------------------------------------
# repr
# ---------------------------------------------------------------------------

class TestRepr:

    def test_repr_contains_class_name(self):
        seq = DNASequence.from_string("ATGC", name="x")
        assert "DNASequence" in repr(seq)

    def test_repr_truncates_long_sequence(self):
        seq = DNASequence.from_string("A" * 100, name="long")
        assert "..." in repr(seq)
