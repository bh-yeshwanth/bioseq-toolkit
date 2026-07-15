from dataclasses import dataclass, field


@dataclass
class Annotation:
    """
    A single feature annotation on a biological sequence.

    Attributes
    ----------
    feature_type : str
        The type of biological feature (e.g. "gene", "CDS", "exon").
    start : int
        Zero-based start position (inclusive).
    end : int
        Zero-based end position (exclusive).
    strand : int
        ``+1`` for forward strand, ``-1`` for reverse strand.
    qualifiers : dict[str, str]
        Arbitrary key-value metadata (e.g. ``{"gene": "BRCA1"}``).
    label : str
        A human-readable label for the annotation. Defaults to ``""``.
    """

    feature_type: str
    start: int
    end: int
    strand: int = 1
    qualifiers: dict[str, str] = field(default_factory=dict)
    label: str = ""

    def __len__(self) -> int:
        return self.end - self.start

