"""File-format and sequence-type auto-detection."""

from __future__ import annotations

import os
from typing import Union, TYPE_CHECKING

from bioseq_toolkit.core.enums import SequenceType
from bioseq_toolkit.core.exceptions import UnsupportedSequenceFormat

if TYPE_CHECKING:
    from typing import TextIO

# Type alias used in signatures throughout this module.
_Source = Union[str, "os.PathLike[str]", "TextIO"]


def _is_stream(source: _Source) -> bool:
    """Return True if *source* is a file-like text stream rather than a path."""
    return hasattr(source, "read")


def detect_format(source: _Source) -> str:
    """
    Infer the file format of a sequence source.

    Accepts either a filesystem path **or** a file-like text stream.

    When given a **path** (``str`` or ``os.PathLike``):

    1. Checks the file extension first.
    2. Falls back to reading the first non-whitespace line of the file.

    When given a **stream** (``io.StringIO``, ``io.TextIOBase``, or any
    ``typing.TextIO``):

    1. Reads the first non-empty line.
    2. Seeks back to the original position (stream state is preserved).

    Parameters
    ----------
    source : str, os.PathLike, or TextIO
        Path to a sequence file, or an open text stream whose current
        position is at (or near) the beginning.

    Returns
    -------
    str
        One of ``"fasta"`` or ``"genbank"``.

    Raises
    ------
    UnsupportedSequenceFormat
        If the format cannot be determined from either the extension or
        the file contents.
    """
    if _is_stream(source):
        return _detect_from_stream(source)  # type: ignore[arg-type]
    return _detect_from_path(source)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _detect_from_path(path: "str | os.PathLike[str]") -> str:
    """Detect format from a filesystem path (extension then content sniff)."""
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


def _detect_from_stream(stream: "TextIO") -> str:
    """Detect format by sniffing the first non-empty line of *stream*.

    The stream position is restored to where it was before this call.
    """
    original_pos: int | None = None
    try:
        original_pos = stream.tell()
    except Exception:
        # Some streams (e.g. sys.stdin) are not seekable; we try our best.
        pass

    try:
        for raw_line in stream:
            line = raw_line.strip()
            if line:
                if line.startswith('>'):
                    return "fasta"
                if line.startswith('LOCUS'):
                    return "genbank"
                # First non-empty line matched neither sentinel.
                break
    finally:
        # Always attempt to restore position.
        if original_pos is not None:
            try:
                stream.seek(original_pos)
            except Exception:
                pass

    raise UnsupportedSequenceFormat("<stream>")


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
