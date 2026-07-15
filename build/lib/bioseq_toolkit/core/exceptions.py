# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

class BioSeqToolkitError(Exception):
    """
    Base class for all bioseq-toolkit errors.

    Downstream applications (e.g. CloneLab) can catch this single class to
    handle any error raised by the library.
    """


# ---------------------------------------------------------------------------
# Sequence errors
# ---------------------------------------------------------------------------

class InvalidDNASequence(BioSeqToolkitError):
    """
    Raised when a nucleotide sequence string is invalid.

    Covers both unrecognised characters and ambiguous molecule types
    (i.e. a string containing both T and U).
    """

    def __init__(self, message: str, sequence: str = "") -> None:
        super().__init__(message)
        self.sequence = sequence


# ---------------------------------------------------------------------------
# Parser errors
# ---------------------------------------------------------------------------

class ParserError(BioSeqToolkitError):
    """
    Raised when a sequence file cannot be parsed.

    Subclass this for format-specific parse failures.
    """

    def __init__(self, message: str, path: str = "") -> None:
        super().__init__(message)
        self.path = path


class UnsupportedSequenceFormat(ParserError):
    """
    Raised when the file format is not recognised or not supported.

    Returned by ``io.detect`` when format auto-detection fails.
    """

    def __init__(self, path: str) -> None:
        super().__init__(
            f"Cannot determine sequence format for file: '{path}'",
            path=path,
        )


# ---------------------------------------------------------------------------
# Serializer errors
# ---------------------------------------------------------------------------

class SerializationError(BioSeqToolkitError):
    """Raised when a domain object cannot be serialized to a file format."""


# ---------------------------------------------------------------------------
# Restriction errors
# ---------------------------------------------------------------------------

class RestrictionError(BioSeqToolkitError):
    """Raised during restriction site search or cut operations."""

