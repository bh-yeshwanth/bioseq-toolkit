"""FASTA format parser."""

from __future__ import annotations

from bioseq_toolkit.parsers.parser import SequenceParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bioseq_toolkit.models.sequence import DNASequence


class FastaParser(SequenceParser):
    """Parse sequences from a FASTA file."""

    def parse(self, path: str) -> "DNASequence":
        """
        Parse a single-record FASTA file.

        Parameters
        ----------
        path : str
            Path to the ``.fasta`` / ``.fa`` file.

        Returns
        -------
        DNASequence

        Raises
        ------
        ParserError
            If the file is malformed.
        """
        ...

    def parse_many(self, path: str) -> list["DNASequence"]:
        """
        Parse a multi-record FASTA file.

        Parameters
        ----------
        path : str
            Path to the ``.fasta`` / ``.fa`` file.

        Returns
        -------
        list[DNASequence]
        """
        ...
