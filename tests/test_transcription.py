from bioseq_toolkit.core.sequence import dna_to_rna
from bioseq_toolkit.core.sequence import rna_to_dna

import pytest


def test_dna_to_rna():
    assert dna_to_rna("ATGC") == "AUGC"


def test_rna_to_dna():
    assert rna_to_dna("AUGC") == "ATGC"


def test_dna_to_rna_lowercase():
    assert dna_to_rna("atgc") == "AUGC"


def test_rna_to_dna_lowercase():
    assert rna_to_dna("augc") == "ATGC"


def test_invalid_dna_to_rna():
    with pytest.raises(ValueError):
        dna_to_rna("ATUG")


def test_invalid_rna_to_dna():
    with pytest.raises(ValueError):
        rna_to_dna("AUTG")