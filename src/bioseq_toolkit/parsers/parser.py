"""Base parser interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bioseq_toolkit.models.sequence import DNASequence


class SequenceParser(ABC):
    """
    Abstract base class for all sequence file parsers.

    Subclass this and implement :meth:`parse` to support a new file format.
    For multi-record formats, also implement :meth:`parse_many`.
    """

    @abstractmethod
    def parse(self, path: str) -> "DNASequence":
        """
        Parse a single-record sequence file.

        Parameters
        ----------
        path : str
            Path to the input file.

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

    def parse_many(self, path: str) -> list["DNASequence"]:
        """
        Parse a multi-record sequence file.

        The default implementation calls :meth:`parse` and wraps the result
        in a list. Override for formats that natively support multiple records
        (e.g. multi-FASTA).

        Parameters
        ----------
        path : str
            Path to the input file.

        Returns
        -------
        list[DNASequence]
            All parsed sequence records.
        """
        ...


# Backwards-compatible alias
BaseParser = SequenceParser
