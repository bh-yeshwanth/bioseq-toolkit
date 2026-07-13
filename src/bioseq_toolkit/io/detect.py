"""File-format and sequence-type auto-detection."""

from bioseq_toolkit.core.enums import SequenceType
from bioseq_toolkit.core.exceptions import UnsupportedSequenceFormat


def detect_format(path: str) -> str:
    """
    Infer the file format of a sequence file.

    Checks the file extension first; falls back to inspecting the first
    non-whitespace character of the file.

    Parameters
    ----------
    path : str
        Path to the sequence file.

    Returns
    -------
    str
        One of ``"fasta"`` or ``"genbank"``.

    Raises
    ------
    UnsupportedSequenceFormat
        If the format cannot be determined.
    """
    path_lower = str(path).lower()

    # Extension sniff
    if path_lower.endswith(('.fasta', '.fa', '.fna', '.ffn', '.frn')):
        return "fasta"
    if path_lower.endswith(('.gb', '.gbk', '.genbank')):
        return "genbank"

    # Content sniff — read first non-empty line
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    if line.startswith('>'):
                        return "fasta"
                    if line.startswith('LOCUS'):
                        return "genbank"
                    break
    except OSError:
        raise

    raise UnsupportedSequenceFormat(str(path))


def detect_sequence_type(sequence: str) -> SequenceType:
    """
    Infer whether a nucleotide string represents DNA, RNA, or is ambiguous.

    Parameters
    ----------
    sequence : str
        Nucleotide sequence string.

    Returns
    -------
    SequenceType
        ``DNA``, ``RNA``, or ``UNKNOWN`` if both T and U are present.
    """
    seq = sequence.upper()
    has_t = 'T' in seq
    has_u = 'U' in seq

    if has_t and not has_u:
        return SequenceType.DNA
    if has_u and not has_t:
        return SequenceType.RNA
    return SequenceType.UNKNOWN
