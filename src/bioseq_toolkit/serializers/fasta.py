"""FASTA format serializer."""

_LINE_LENGTH = 70


def to_fasta(header: str, sequence: str, line_length: int = _LINE_LENGTH) -> str:
    """
    Serialize a sequence to FASTA format.

    Parameters
    ----------
    header : str
        Sequence identifier line (without the leading ``>``).
    sequence : str
        Nucleotide sequence string.
    line_length : int
        Characters per sequence line. Default 70.

    Returns
    -------
    str
        FASTA-formatted string ending with a newline.
    """
    wrapped = "\n".join(
        sequence[i : i + line_length] for i in range(0, len(sequence), line_length)
    )
    return f">{header}\n{wrapped}\n"
