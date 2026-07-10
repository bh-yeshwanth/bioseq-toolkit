"""FASTA format parser."""

from bioseq_toolkit.parsers.parser import BaseParser


class FastaParser(BaseParser):
    """Parse sequences from a FASTA file."""

    def parse(self, path: str) -> list:
        """
        Parse a FASTA file.

        Parameters
        ----------
        path : str
            Path to the ``.fasta`` / ``.fa`` file.

        Returns
        -------
        list
            List of ``(header, sequence)`` tuples.
        """
        ...
