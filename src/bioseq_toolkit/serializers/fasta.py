"""FASTA format serializer."""


def to_fasta(header: str, sequence: str) -> str:
    """
    Serialize a sequence to FASTA format.

    Parameters
    ----------
    header : str
        Sequence identifier (without the leading ``>``).
    sequence : str
        Nucleotide sequence string.

    Returns
    -------
    str
        FASTA-formatted string.
    """
    ...
