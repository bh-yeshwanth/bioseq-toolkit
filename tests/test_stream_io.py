"""
Tests for stream-based I/O — bioseq-toolkit v0.2.1.

Covers every requirement from the v0.2.1 spec:

✓ pathlib.Path input
✓ string path input
✓ StringIO input (FASTA)
✓ StringIO input (GenBank)
✓ TextIO file handle input
✓ stream position restored after format detection
✓ FASTA via stream — single record
✓ FASTA via stream — multi-record (parse_many)
✓ GenBank via stream — with annotations
✓ invalid stream raises UnsupportedSequenceFormat
✓ existing path behaviour remains unchanged
"""

from __future__ import annotations

import io
import os
import pathlib

import pytest

from bioseq_toolkit import DNASequence, FastaParser, GenBankParser
from bioseq_toolkit import ParserError, UnsupportedSequenceFormat
from bioseq_toolkit.io.detect import detect_format


# ---------------------------------------------------------------------------
# Fixtures / constants
# ---------------------------------------------------------------------------

DATA_DIR = pathlib.Path(__file__).parent / "data"

FASTA_SINGLE = """\
>SEQ001
ATGCATGCATGCATGCATGC
"""

FASTA_MULTI = """\
>SEQ001
ATGCATGCATGCATGCATGC
>SEQ002
GCTAGCTAGCTAGCTAGCTA
"""

GENBANK_MINIMAL = """\
LOCUS       TESTSEQ               20 bp    DNA     linear   SYN 01-JAN-2024
DEFINITION  A minimal synthetic test record.
ACCESSION   TESTSEQ
VERSION     TESTSEQ.1
FEATURES             Location/Qualifiers
     gene            1..20
                     /gene="TEST"
ORIGIN
        1 atgcatgcat gcatgcatgc
//
"""

INVALID_CONTENT = """\
This is not a biological sequence file.
No FASTA or GenBank headers here.
"""


# ---------------------------------------------------------------------------
# 1. detect_format — path variants (existing behaviour unchanged)
# ---------------------------------------------------------------------------

class TestDetectFormatPaths:

    def test_fasta_extension_fa(self):
        path = DATA_DIR / "linear.fa"
        assert detect_format(path) == "fasta"

    def test_fasta_extension_fasta(self):
        path = DATA_DIR / "example.fasta"
        assert detect_format(path) == "fasta"

    def test_genbank_extension_gb(self):
        path = DATA_DIR / "example.gb"
        assert detect_format(path) == "genbank"

    def test_string_path_fasta(self):
        path = str(DATA_DIR / "linear.fa")
        assert detect_format(path) == "fasta"

    def test_pathlib_path_genbank(self):
        path = DATA_DIR / "example.gb"
        assert detect_format(path) == "genbank"


# ---------------------------------------------------------------------------
# 2. detect_format — stream variants
# ---------------------------------------------------------------------------

class TestDetectFormatStreams:

    def test_fasta_stream_detected(self):
        stream = io.StringIO(FASTA_SINGLE)
        assert detect_format(stream) == "fasta"

    def test_genbank_stream_detected(self):
        stream = io.StringIO(GENBANK_MINIMAL)
        assert detect_format(stream) == "genbank"

    def test_stream_position_restored_after_detection(self):
        """detect_format must seek(0) so the caller can still read the stream."""
        stream = io.StringIO(FASTA_SINGLE)
        stream.seek(0)
        detect_format(stream)
        # Position must be back at the start.
        assert stream.tell() == 0

    def test_stream_position_preserved_mid_stream(self):
        """If caller advances the stream, detection restores to that position."""
        content = "   \n" + FASTA_SINGLE   # leading blank line
        stream = io.StringIO(content)
        # Advance 4 bytes (the leading spaces) — a non-zero start position.
        stream.seek(4)
        detect_format(stream)
        assert stream.tell() == 4

    def test_invalid_stream_raises(self):
        stream = io.StringIO(INVALID_CONTENT)
        with pytest.raises(UnsupportedSequenceFormat):
            detect_format(stream)

    def test_empty_stream_raises(self):
        stream = io.StringIO("")
        with pytest.raises(UnsupportedSequenceFormat):
            detect_format(stream)


# ---------------------------------------------------------------------------
# 3. FastaParser — stream variants
# ---------------------------------------------------------------------------

class TestFastaParserStream:

    def test_parse_stringio(self):
        stream = io.StringIO(FASTA_SINGLE)
        parser = FastaParser()
        seq = parser.parse(stream)
        assert seq.name == "SEQ001"
        assert seq.sequence == "ATGCATGCATGCATGCATGC"

    def test_parse_many_stringio(self):
        stream = io.StringIO(FASTA_MULTI)
        parser = FastaParser()
        records = parser.parse_many(stream)
        assert len(records) == 2
        assert records[0].name == "SEQ001"
        assert records[1].name == "SEQ002"
        assert records[0].sequence == "ATGCATGCATGCATGCATGC"
        assert records[1].sequence == "GCTAGCTAGCTAGCTAGCTA"

    def test_parse_textio_file_handle(self):
        """An open() file handle (TextIO) must work exactly like StringIO."""
        path = DATA_DIR / "linear.fa"
        with open(path, "r", encoding="utf-8") as fh:
            seq = FastaParser().parse(fh)
        assert seq.name == "SEQ001"
        assert seq.sequence == "ATGCATGCATGCATGCATGC"

    def test_parse_empty_stream_raises(self):
        stream = io.StringIO("")
        with pytest.raises(ParserError):
            FastaParser().parse(stream)

    def test_parse_stream_with_description(self):
        fasta = ">NM_001101.5 Homo sapiens actin beta\nATGCATGC\n"
        stream = io.StringIO(fasta)
        seq = FastaParser().parse(stream)
        assert seq.name == "NM_001101.5"
        assert "Homo sapiens" in seq.description


# ---------------------------------------------------------------------------
# 4. GenBankParser — stream variants
# ---------------------------------------------------------------------------

class TestGenBankParserStream:

    def test_parse_stringio(self):
        stream = io.StringIO(GENBANK_MINIMAL)
        seq = GenBankParser().parse(stream)
        assert seq.name == "TESTSEQ"
        assert seq.sequence == "ATGCATGCATGCATGCATGC"

    def test_parse_annotations_from_stream(self):
        stream = io.StringIO(GENBANK_MINIMAL)
        seq = GenBankParser().parse(stream)
        assert len(seq.annotations) >= 1
        assert seq.annotations[0].feature_type == "gene"

    def test_parse_textio_file_handle(self):
        path = DATA_DIR / "example.gb"
        with open(path, "r", encoding="utf-8") as fh:
            seq = GenBankParser().parse(fh)
        assert seq.name == "NM_001101"
        assert len(seq.sequence) > 0

    def test_parse_metadata_from_stream(self):
        stream = io.StringIO(GENBANK_MINIMAL)
        seq = GenBankParser().parse(stream)
        assert seq.metadata.get("accession") == "TESTSEQ"


# ---------------------------------------------------------------------------
# 5. DNASequence.from_file — all input types
# ---------------------------------------------------------------------------

class TestFromFileAllInputTypes:

    # --- path inputs (existing behaviour, must remain unchanged) ---

    def test_string_path_fasta(self):
        path = str(DATA_DIR / "linear.fa")
        seq = DNASequence.from_file(path)
        assert seq.name == "SEQ001"
        assert seq.sequence == "ATGCATGCATGCATGCATGC"

    def test_pathlib_path_fasta(self):
        path = DATA_DIR / "linear.fa"
        seq = DNASequence.from_file(path)
        assert seq.name == "SEQ001"
        assert seq.sequence == "ATGCATGCATGCATGCATGC"

    def test_string_path_genbank(self):
        path = str(DATA_DIR / "example.gb")
        seq = DNASequence.from_file(path)
        assert seq.name == "NM_001101"

    def test_pathlib_path_genbank(self):
        path = DATA_DIR / "example.gb"
        seq = DNASequence.from_file(path)
        assert seq.name == "NM_001101"

    def test_missing_path_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            DNASequence.from_file("does_not_exist.fasta")

    # --- stream inputs (new in v0.2.1) ---

    def test_stringio_fasta(self):
        stream = io.StringIO(FASTA_SINGLE)
        seq = DNASequence.from_file(stream)
        assert seq.name == "SEQ001"
        assert seq.sequence == "ATGCATGCATGCATGCATGC"

    def test_stringio_genbank(self):
        stream = io.StringIO(GENBANK_MINIMAL)
        seq = DNASequence.from_file(stream)
        assert seq.name == "TESTSEQ"
        assert seq.sequence == "ATGCATGCATGCATGCATGC"

    def test_textio_fasta_file_handle(self):
        path = DATA_DIR / "linear.fa"
        with open(path, "r", encoding="utf-8") as fh:
            seq = DNASequence.from_file(fh)
        assert seq.name == "SEQ001"

    def test_textio_genbank_file_handle(self):
        path = DATA_DIR / "example.gb"
        with open(path, "r", encoding="utf-8") as fh:
            seq = DNASequence.from_file(fh)
        assert seq.name == "NM_001101"

    def test_definition_of_done_snippet(self):
        """The exact code snippet from the spec must work without disk I/O."""
        fasta = ">Example\nATGCGCGATATAT\n"
        sequence = DNASequence.from_file(io.StringIO(fasta))
        s = sequence.summary()
        assert s["name"] == "Example"
        assert s["length"] == 13
        assert s["molecule_type"] == "DNA"

    def test_invalid_stream_raises(self):
        stream = io.StringIO(INVALID_CONTENT)
        with pytest.raises(UnsupportedSequenceFormat):
            DNASequence.from_file(stream)
