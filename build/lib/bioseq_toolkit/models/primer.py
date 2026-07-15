"""Primer model."""

from dataclasses import dataclass


@dataclass
class Primer:
    """
    Represents a PCR primer.

    Attributes
    ----------
    name : str
        Human-readable identifier for the primer.
    sequence : str
        Nucleotide sequence of the primer (5'→3').
    """

    name: str
    sequence: str

    @property
    def length(self) -> int:
        """Length of the primer sequence."""
        return len(self.sequence)

    def gc_content(self) -> float:
        """
        Calculate the GC content of the primer.

        Returns
        -------
        float
            Fraction of bases that are G or C (0.0 – 1.0).
        """
        ...

    def melting_temperature(self) -> float:
        """
        Estimate the melting temperature (Tm) of the primer.

        Returns
        -------
        float
            Estimated Tm in degrees Celsius.
        """
        ...
