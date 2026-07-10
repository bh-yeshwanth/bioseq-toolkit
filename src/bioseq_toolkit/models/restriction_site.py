"""Restriction site model."""

from dataclasses import dataclass


@dataclass
class RestrictionSite:
    """
    Represents a restriction enzyme recognition site.

    Attributes
    ----------
    enzyme : str
        Name of the restriction enzyme (e.g. ``"EcoRI"``).
    recognition_sequence : str
        The nucleotide pattern recognised by the enzyme.
    cut_position : int
        Position within the recognition sequence where the enzyme cuts
        (zero-based, on the forward strand).
    """

    enzyme: str
    recognition_sequence: str
    cut_position: int

    def find_in(self, sequence: str) -> list[int]:
        """
        Find all occurrences of this restriction site in *sequence*.

        Parameters
        ----------
        sequence : str
            Target DNA sequence to search.

        Returns
        -------
        list[int]
            Zero-based start positions of every recognition site.
        """
        ...
