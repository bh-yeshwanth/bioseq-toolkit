"""File-format auto-detection."""

from bioseq_toolkit.core.enums import SequenceType


def detect_format(path: str) -> str:
    """
    Infer the file format of a sequence file from its path and content.

    Checks the file extension first, then falls back to inspecting the first
    few bytes of the file.

    Parameters
    ----------
    path : str
        Path to the sequence file.

    Returns
    -------
    str
        One of ``"fasta"``, ``"genbank"``, or ``"unknown"``.
    """
    ...


def detect_sequence_type(sequence: str) -> SequenceType:
    """
    Infer whether a sequence string represents DNA, RNA, or is ambiguous.

    Parameters
    ----------
    sequence : str
        Nucleotide sequence string.

    Returns
    -------
    SequenceType
        ``SequenceType.DNA``, ``SequenceType.RNA``, or ``SequenceType.UNKNOWN``.
    """
    ...
