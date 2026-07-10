"""GenBank format parser."""

from __future__ import annotations

from bioseq_toolkit.parsers.parser import SequenceParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bioseq_toolkit.models.sequence import DNASequence


class GenBankParser(SequenceParser):
    """Parse sequences and annotations from a GenBank file."""

    def parse(self, path: str) -> "DNASequence":
        """
        Parse a single-record GenBank file.

        Parameters
        ----------
        path : str
            Path to the ``.gb`` / ``.gbk`` file.

        Returns
        -------
        DNASequence
            Includes annotations and metadata parsed from the FEATURES
            and LOCUS/DEFINITION blocks.

        Raises
        ------
        ParserError
            If the file is malformed.
        """
        ...
