"""Base parser interface."""

from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Abstract base class for all sequence file parsers."""

    @abstractmethod
    def parse(self, path: str) -> list:
        """
        Parse a sequence file and return a list of sequence records.

        Parameters
        ----------
        path : str
            Path to the input file.

        Returns
        -------
        list
            Parsed sequence records.
        """
        ...
