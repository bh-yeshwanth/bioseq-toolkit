"""
Domain model for biological sequences.

``DNASequence`` is the primary public object of bioseq-toolkit.

Note
----
``RNASequence`` is planned for v0.3. It is intentionally omitted here to
keep the initial API surface small and focused on CloneLab's requirements.
"""

from __future__ import annotations

import os
from bioseq_toolkit.core.enums import Topology
from bioseq_toolkit.core.annotation import Annotation


# ---------------------------------------------------------------------------
# DNASequence
# ---------------------------------------------------------------------------

class DNASequence:
    """
    Represents a DNA sequence with topology, annotations, and metadata.

    This is the central domain object in bioseq-toolkit. All sequence
    operations are available as methods. File I/O is delegated to the
    parser and serializer layers, invoked via :meth:`from_file`,
    :meth:`to_fasta`, and :meth:`to_genbank`.

    Parameters
    ----------
    sequence : str
        Raw nucleotide string (A, T, G, C). Case-insensitive; stored uppercase.
    topology : Topology
        ``Topology.LINEAR`` (default) or ``Topology.CIRCULAR``.
    annotations : list[Annotation]
        Ordered list of biological feature annotations. Defaults to ``[]``.
    metadata : dict[str, str]
        Record-level metadata. Expected keys:

        - ``"accession"`` — primary database accession (e.g. ``"NM_001101"``).
        - ``"version"``   — versioned accession (e.g. ``"NM_001101.5"``).
        - ``"organism"``  — source organism (e.g. ``"Homo sapiens"``).
        - ``"date"``      — record date (e.g. ``"12-JAN-2024"``).
        - ``"keywords"``  — semicolon-separated keywords.
        - ``"name"``      — short human-readable name.
        - ``"description"`` — longer free-text description.

        Unknown keys are accepted and preserved.

    Examples
    --------
    >>> seq = DNASequence.from_string("ATGCATGC")
    >>> seq.gc_content()
    0.5
    >>> seq.reverse_complement().sequence
    'GCATGCAT'
    >>> seq.is_valid()
    True
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        sequence: str,
        topology: Topology = Topology.LINEAR,
        annotations: list[Annotation] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        ...

    @classmethod
    def from_string(cls, sequence: str, **kwargs) -> "DNASequence":
        """
        Construct a ``DNASequence`` from a raw nucleotide string.

        Parameters
        ----------
        sequence : str
            Nucleotide string (A, T, G, C). Case-insensitive.
        **kwargs
            Optional: ``topology``, ``annotations``, ``metadata``.

        Returns
        -------
        DNASequence

        Raises
        ------
        InvalidDNASequence
            If the sequence contains an invalid or ambiguous character.
        """
        ...

    @classmethod
    def from_file(cls, path: str | os.PathLike) -> "DNASequence":
        """
        Construct a ``DNASequence`` by parsing a sequence file.

        Format is auto-detected from the file extension and content via
        ``io.detect``. Supports FASTA (``.fasta``, ``.fa``) and GenBank
        (``.gb``, ``.gbk``).

        Parameters
        ----------
        path : str or os.PathLike
            Path to the sequence file.

        Returns
        -------
        DNASequence

        Raises
        ------
        FileNotFoundError
            If *path* does not exist.
        UnsupportedSequenceFormat
            If the file format cannot be determined.
        ParserError
            If the file is malformed.
        """
        ...

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def sequence(self) -> str:
        """The raw nucleotide string (uppercase)."""
        ...

    @property
    def topology(self) -> Topology:
        """Whether the molecule is ``LINEAR`` or ``CIRCULAR``."""
        ...

    @property
    def annotations(self) -> list[Annotation]:
        """
        Ordered list of biological feature annotations.

        Each item is an :class:`~bioseq_toolkit.core.annotation.Annotation`
        with ``feature_type``, ``start``, ``end``, ``strand``, and
        ``qualifiers``.
        """
        ...

    @property
    def metadata(self) -> dict[str, str]:
        """
        Record-level metadata.

        Expected keys: ``accession``, ``version``, ``organism``, ``date``,
        ``keywords``, ``name``, ``description``. Unknown keys are preserved.
        """
        ...

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate the sequence and raise on the first problem found.

        Checks performed:

        1. All characters are valid DNA nucleotides (A, T, G, C).
        2. The sequence is not empty.

        Raises
        ------
        InvalidDNASequence
            If any validation check fails.
        """
        ...

    def is_valid(self) -> bool:
        """
        Return ``True`` if the sequence passes all validation checks.

        Equivalent to calling :meth:`validate` and catching
        :exc:`~bioseq_toolkit.core.exceptions.InvalidDNASequence`.

        Returns
        -------
        bool
        """
        ...

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def gc_content(self) -> float:
        """
        Calculate GC content.

        Returns
        -------
        float
            Fraction of bases that are G or C (0.0 – 1.0).
            Returns ``0.0`` for an empty sequence.
        """
        ...

    def reverse_complement(self) -> "DNASequence":
        """
        Return the reverse complement as a new ``DNASequence``.

        Topology and metadata are preserved. Annotations are not
        transformed (strand-aware annotation mirroring is a Phase 4 feature).

        Returns
        -------
        DNASequence
        """
        ...

    def summary(self) -> dict:
        """
        Return a structured summary of the sequence record.

        Returns
        -------
        dict
            ``{
                "name": str,
                "description": str,
                "length": int,
                "gc_content": float,
                "topology": str,
                "annotation_count": int,
                "molecule_type": str,
            }``
        """
        ...

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def to_fasta(self, path: str | os.PathLike | None = None) -> str:
        """
        Serialize to FASTA format.

        Parameters
        ----------
        path : str or os.PathLike, optional
            If provided, write the output to this file as well as returning it.

        Returns
        -------
        str
            FASTA-formatted string.

        Raises
        ------
        SerializationError
            If the record cannot be serialized.
        """
        ...

    def to_genbank(self, path: str | os.PathLike | None = None) -> str:
        """
        Serialize to GenBank flat-file format.

        Parameters
        ----------
        path : str or os.PathLike, optional
            If provided, write the output to this file as well as returning it.

        Returns
        -------
        str
            GenBank-formatted string.

        Raises
        ------
        SerializationError
            If the record cannot be serialized.
        """
        ...

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the length of the sequence."""
        ...

    def __repr__(self) -> str:
        ...
