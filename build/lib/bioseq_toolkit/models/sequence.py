"""
Domain model for biological sequences.

``DNASequence`` is the canonical object in bioseq-toolkit.
Nothing else stores DNA.

Note
----
``RNASequence`` is planned for v0.3. It is intentionally omitted here to
keep the initial API surface small and focused on CloneLab's requirements.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TextIO

from bioseq_toolkit.core.enums import Topology
from bioseq_toolkit.core.annotation import Annotation
from bioseq_toolkit.core.exceptions import InvalidDNASequence, SerializationError


# Valid IUPAC nucleotides accepted by validate().
# N (unknown base) is permitted for real-world sequences from databases.
_VALID_DNA_CHARS: frozenset[str] = frozenset("ATGCN")


@dataclass
class DNASequence:
    """
    Canonical representation of a DNA sequence record.

    ``DNASequence`` is the central domain object in bioseq-toolkit.
    All sequence operations are available as methods. File I/O is
    delegated to the parser and serializer layers, invoked via
    :meth:`from_file`, :meth:`to_fasta`, and :meth:`to_genbank`.

    Parameters
    ----------
    sequence : str
        Raw nucleotide string (A, T, G, C, N). Stored uppercase.
    name : str
        Short human-readable identifier (e.g. ``"ACTB"``).
    description : str
        Longer free-text description (e.g. ``"Homo sapiens actin beta"``).
    topology : Topology
        ``Topology.LINEAR`` (default) or ``Topology.CIRCULAR``.
    molecule_type : str
        Always ``"DNA"`` for this class.
    annotations : list[Annotation]
        Ordered biological feature annotations. Defaults to ``[]``.
    metadata : dict[str, str]
        Additional record-level metadata. Expected keys:
        ``accession``, ``version``, ``organism``, ``date``, ``keywords``.

    Examples
    --------
    >>> seq = DNASequence.from_string("ATGCATGC", name="test")
    >>> seq.gc_content()
    0.5
    >>> seq.reverse_complement().sequence
    'GCATGCAT'
    >>> seq.is_valid()
    True
    >>> seq.summary()["molecule_type"]
    'DNA'
    """

    sequence: str
    name: str = ""
    description: str = ""
    topology: Topology = Topology.LINEAR
    molecule_type: str = "DNA"
    annotations: list[Annotation] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Post-init normalisation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        # Normalise sequence to uppercase on construction.
        self.sequence = self.sequence.upper()

    # ------------------------------------------------------------------
    # Alternative constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_string(cls, sequence: str, **kwargs) -> "DNASequence":
        """
        Construct a validated ``DNASequence`` from a raw nucleotide string.

        Parameters
        ----------
        sequence : str
            Nucleotide string (A, T, G, C, N). Case-insensitive.
        **kwargs
            Optional keyword arguments forwarded to the constructor:
            ``name``, ``description``, ``topology``, ``annotations``,
            ``metadata``, ``molecule_type``.

        Returns
        -------
        DNASequence

        Raises
        ------
        InvalidDNASequence
            If the sequence is empty or contains invalid characters.
        """
        obj = cls(sequence=sequence, **kwargs)
        obj.validate()
        return obj

    @classmethod
    def from_file(
        cls,
        path: "Union[str, os.PathLike[str], TextIO]",
    ) -> "DNASequence":
        """
        Construct a ``DNASequence`` by parsing a sequence file or stream.

        The file format is auto-detected from the extension (for paths) or
        the first non-empty line (for streams). Supported formats: FASTA
        (``.fasta``, ``.fa``) and GenBank (``.gb``, ``.gbk``).

        Parameters
        ----------
        path : str, os.PathLike, or TextIO
            Path to the sequence file **or** an open text stream
            (e.g. ``io.StringIO``, an ``open()`` file handle). When a
            stream is supplied no temporary file is created on disk.

        Returns
        -------
        DNASequence

        Raises
        ------
        FileNotFoundError
            If *path* is a filesystem path that does not exist.
        UnsupportedSequenceFormat
            If the file format cannot be determined.
        ParserError
            If the source is malformed.

        Examples
        --------
        From a filesystem path (existing behaviour, unchanged)::

            seq = DNASequence.from_file("example.fasta")

        From an in-memory stream (new in v0.2.1)::

            from io import StringIO
            fasta = ">MySeq\\nATGCGCGATATAT\\n"
            seq = DNASequence.from_file(StringIO(fasta))
        """
        # Lazy imports to avoid circular dependencies at module load time.
        from bioseq_toolkit.io.detect import detect_format
        from bioseq_toolkit.parsers.fasta import FastaParser
        from bioseq_toolkit.parsers.genbank import GenBankParser

        is_stream = hasattr(path, "read")

        if not is_stream:
            # Path branch: guard against missing files as before.
            str_path = str(path)
            if not os.path.exists(str_path):
                raise FileNotFoundError(f"No such file: '{str_path}'")

        fmt = detect_format(path)  # type: ignore[arg-type]

        parser_map = {
            "fasta": FastaParser,
            "genbank": GenBankParser,
        }
        parser = parser_map[fmt]()
        return parser.parse(path)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate the sequence and raise on the first problem found.

        Checks
        ------
        1. Sequence is not empty.
        2. All characters are valid IUPAC DNA nucleotides (A, T, G, C, N).

        Raises
        ------
        InvalidDNASequence
        """
        if not self.sequence:
            raise InvalidDNASequence(
                "Sequence cannot be empty.",
                sequence=self.sequence,
            )
        invalid = set(self.sequence) - _VALID_DNA_CHARS
        if invalid:
            raise InvalidDNASequence(
                f"Invalid nucleotide(s) found: {', '.join(sorted(invalid))}",
                sequence=self.sequence,
            )

    def is_valid(self) -> bool:
        """
        Return ``True`` if the sequence passes all validation checks.

        Does not raise — catches :exc:`InvalidDNASequence` internally.

        Returns
        -------
        bool
        """
        try:
            self.validate()
            return True
        except InvalidDNASequence:
            return False

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    @property
    def length(self) -> int:
        """Number of bases in the sequence."""
        return len(self.sequence)

    def gc_content(self) -> float:
        """
        Calculate GC content.

        Returns
        -------
        float
            Fraction of bases that are G or C (0.0 – 1.0).
            Returns ``0.0`` for an empty sequence.
        """
        from bioseq_toolkit.utils.gc import gc_content
        return gc_content(self.sequence)

    def reverse_complement(self) -> "DNASequence":
        """
        Return the reverse complement as a new ``DNASequence``.

        Topology, name, and metadata are preserved.
        Annotations are *not* strand-mirrored (Phase 4 feature).

        Returns
        -------
        DNASequence
        """
        from bioseq_toolkit.core.sequence import reverse_complement as _rc

        return DNASequence(
            sequence=_rc(self.sequence),
            name=self.name,
            description=f"reverse complement of {self.name}" if self.name else "",
            topology=self.topology,
            molecule_type=self.molecule_type,
            annotations=[],  # strand-aware mirroring deferred to Phase 4
            metadata=dict(self.metadata),
        )

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
        return {
            "name": self.name,
            "description": self.description,
            "length": self.length,
            "gc_content": self.gc_content(),
            "topology": self.topology.value,
            "annotation_count": len(self.annotations),
            "molecule_type": self.molecule_type,
        }

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
        from bioseq_toolkit.serializers.fasta import to_fasta as _to_fasta

        try:
            header = self.name or "sequence"
            if self.description:
                header = f"{header} {self.description}"
            result = _to_fasta(header, self.sequence)
        except Exception as exc:
            raise SerializationError(f"FASTA serialization failed: {exc}") from exc

        if path is not None:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(result)
            except OSError as exc:
                raise SerializationError(f"Could not write FASTA file: {exc}") from exc

        return result

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
        from bioseq_toolkit.serializers.genbank import to_genbank as _to_genbank

        try:
            result = _to_genbank(self)
        except Exception as exc:
            raise SerializationError(f"GenBank serialization failed: {exc}") from exc

        if path is not None:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(result)
            except OSError as exc:
                raise SerializationError(f"Could not write GenBank file: {exc}") from exc

        return result

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.sequence)

    def __repr__(self) -> str:
        trunc = self.sequence[:20]
        suffix = "..." if len(self.sequence) > 20 else ""
        return (
            f"DNASequence(name={self.name!r}, length={self.length}, "
            f"topology={self.topology.value!r}, sequence={trunc!r}{suffix})"
        )
