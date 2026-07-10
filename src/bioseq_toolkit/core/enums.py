from enum import Enum


class SequenceType(Enum):
    """The molecular type of a biological sequence."""
    DNA = "DNA"
    RNA = "RNA"
    UNKNOWN = "UNKNOWN"


class Topology(Enum):
    """The topology of a DNA molecule."""
    LINEAR = "linear"
    CIRCULAR = "circular"
