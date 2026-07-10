class InvalidNucleotideError(ValueError):
    """Raised when a sequence contains an unrecognised nucleotide character."""

    def __init__(self, nucleotide: str) -> None:
        super().__init__(f"Invalid nucleotide '{nucleotide}' found.")
        self.nucleotide = nucleotide


class AmbiguousSequenceError(ValueError):
    """Raised when a sequence contains both T and U, making the type ambiguous."""

    def __init__(self) -> None:
        super().__init__(
            "Sequence contains both T and U. "
            "A sequence cannot simultaneously represent DNA and RNA."
        )


class SequenceLengthMismatchError(ValueError):
    """Raised when two sequences are required to be the same length but are not."""

    def __init__(self, len1: int, len2: int) -> None:
        super().__init__(
            f"Sequences must be of equal length, got {len1} and {len2}."
        )
        self.len1 = len1
        self.len2 = len2
