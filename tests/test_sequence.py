from bioseq_toolkit import palindromic
from bioseq_toolkit import nucleotide_count
from bioseq_toolkit import reverse_complement
from bioseq_toolkit import reverse
from bioseq_toolkit import complement

import pytest


def test_reverse():
    assert reverse("ATGC") == "CGTA"

def test_complement():
    assert complement("ATGC") == "TACG"

def test_reverse_complement():
    assert reverse_complement("ATGC") == "GCAT"

def test_nucleotide_count():
    assert nucleotide_count("ATGC") == {"A": 1, "T": 1, "G": 1, "C": 1}

def test_palindromic():
    assert palindromic("ATGC") == False

def test_reverse_empty():
    assert reverse("") == ""


def test_reverse_single():
    assert reverse("A") == "A"


def test_invalid_complement():
    with pytest.raises(ValueError):
        complement("ATBX")