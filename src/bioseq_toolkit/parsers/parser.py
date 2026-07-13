"""Base parser interface and shared I/O helpers."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TextIO
    from bioseq_toolkit.models.sequence import DNASequence

# Public type alias re-used by every parser.
SourceType = Union[str, "os.PathLike[str]", "TextIO"]


# ---------------------------------------------------------------------------
# Internal helper shared by all concrete parsers
# ---------------------------------------------------------------------------

def _open_source(
    source: SourceType,
) -> tuple["TextIO", bool]:
    """Normalise *source* into an open text stream.

    Parameters
    ----------
    source : str, os.PathLike, or TextIO
        A filesystem path or an already-open text stream.

    Returns
    -------
    tuple[TextIO, bool]
        ``(handle, should_close)``

        * *handle* — a readable text stream.
        * *should_close* — ``True`` when this function opened the file and the
          caller is responsible for closing it; ``False`` when *source* was
          already a stream and must **not** be closed by the caller.

    Raises
    ------
    ParserError
        If *source* is a path that cannot be opened.
    """
    from bioseq_toolkit.core.exceptions import ParserError

    if hasattr(source, "read"):
        # Already a stream — hand it back as-is.
        return source, False  # type: ignore[return-value]

    try:
        fh = open(source, "r", encoding="utf-8")  # type: ignore[arg-type]
        return fh, True
    except OSError as exc:
        raise ParserError(str(exc), path=str(source)) from exc


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class SequenceParser(ABC):
    """
    Abstract base class for all sequence file parsers.

    Subclass this and implement :meth:`parse` to support a new file format.
    For multi-record formats, also implement :meth:`parse_many`.

    Both :meth:`parse` and :meth:`parse_many` accept either a filesystem path
    (``str`` or ``os.PathLike``) or a file-like text stream
    (``io.StringIO``, ``io.TextIOBase``, ``typing.TextIO``).
    """

    @abstractmethod
    def parse(self, path: SourceType) -> "DNASequence":
        """
        Parse a single-record sequence file or stream.

        Parameters
        ----------
        path : str, os.PathLike, or TextIO
            Path to the input file, or an open text stream.

        Returns
        -------
        DNASequence
            The parsed sequence record.

        Raises
        ------
        ParserError
            If the file is malformed or cannot be read.
        UnsupportedSequenceFormat
            If the format is not supported by this parser.
        """
        ...

    def parse_many(self, path: SourceType) -> list["DNASequence"]:
        """
        Parse a multi-record sequence file or stream.

        The default implementation calls :meth:`parse` and wraps the result
        in a list. Override for formats that natively support multiple records
        (e.g. multi-FASTA).

        Parameters
        ----------
        path : str, os.PathLike, or TextIO
            Path to the input file, or an open text stream.

        Returns
        -------
        list[DNASequence]
            All parsed sequence records.
        """
        ...


# Backwards-compatible alias
BaseParser = SequenceParser
