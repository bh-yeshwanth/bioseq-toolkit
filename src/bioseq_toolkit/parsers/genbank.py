"""GenBank format parser."""

from bioseq_toolkit.parsers.parser import BaseParser


class GenBankParser(BaseParser):
    """Parse sequences and annotations from a GenBank file."""

    def parse(self, path: str) -> list:
        """
        Parse a GenBank file.

        Parameters
        ----------
        path : str
            Path to the ``.gb`` / ``.gbk`` file.

        Returns
        -------
        list
            List of parsed GenBank records.
        """
        ...
