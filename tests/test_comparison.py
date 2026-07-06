from bioseq_toolkit import hamming_distance
from bioseq_toolkit import motif_search

import pytest


def test_hamming_distance():
    assert hamming_distance("ATGC", "ATGT") == 1


def test_hamming_distance_identical():
    assert hamming_distance("ATGC", "ATGC") == 0


def test_hamming_distance_invalid_length():
    with pytest.raises(ValueError):
        hamming_distance("ATGC", "ATG")


def test_motif_search():
    assert motif_search("ATGCATGC", "AT") == [0, 4]


def test_motif_not_found():
    assert motif_search("ATGC", "GG") == []


def test_motif_entire_sequence():
    assert motif_search("ATGC", "ATGC") == [0]