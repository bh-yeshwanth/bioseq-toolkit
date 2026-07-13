"""GC-content utility."""

# Valid IUPAC DNA nucleotides accepted by validate() — N is allowed
_VALID_DNA: frozenset[str] = frozenset("ATGCN")


def gc_content(sequence: str) -> float:
    """
    Calculate the GC content of a nucleotide sequence.

    Parameters
    ----------
    sequence : str
        Input DNA sequence (uppercase or lowercase; N allowed).

    Returns
    -------
    float
        Fraction of bases that are G or C (0.0 – 1.0).
        Returns ``0.0`` for an empty sequence.

    Raises
    ------
    ValueError
        If the sequence contains an invalid nucleotide.
    """
    if not sequence:
        return 0.0
    seq = sequence.upper()
    invalid = set(seq) - _VALID_DNA
    if invalid:
        raise ValueError(
            f"Invalid nucleotide(s) in sequence: {', '.join(sorted(invalid))}"
        )
    return sum(1 for base in seq if base in "GC") / len(seq)
