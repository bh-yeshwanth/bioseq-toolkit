"""GC-content utility."""


def gc_content(sequence: str) -> float:
    """
    Calculate the GC content of a nucleotide sequence.

    Parameters
    ----------
    sequence : str
        Input DNA or RNA sequence.

    Returns
    -------
    float
        Fraction of bases that are G or C (0.0 – 1.0).
        Returns 0.0 for an empty sequence.

    Raises
    ------
    ValueError
        If the sequence contains an invalid nucleotide.
    """
    ...
