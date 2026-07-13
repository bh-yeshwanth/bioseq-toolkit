"""FASTA format parser."""

from __future__ import annotations

from bioseq_toolkit.parsers.parser import SequenceParser, SourceType, _open_source
from bioseq_toolkit.core.exceptions import ParserError, InvalidDNASequence


class FastaParser(SequenceParser):
    """Parse sequences from a FASTA file or text stream."""

    def parse(self, path: SourceType) -> "DNASequence":
        """
        Parse the first record from a FASTA source.

        Parameters
        ----------
        path : str, os.PathLike, or TextIO
            Path to a ``.fasta`` / ``.fa`` file, **or** an open text stream
            (e.g. ``io.StringIO``) containing FASTA-formatted data.

        Returns
        -------
        DNASequence

        Raises
        ------
        ParserError
            If the source contains no records or is malformed.
        """
        records = self.parse_many(path)
        if not records:
            src_label = "<stream>" if hasattr(path, "read") else str(path)
            raise ParserError(
                f"No sequence records found in '{src_label}'.",
                path=src_label,
            )
        return records[0]

    def parse_many(self, path: SourceType) -> list["DNASequence"]:
        """
        Parse all records from a (multi-)FASTA source.

        Parameters
        ----------
        path : str, os.PathLike, or TextIO
            Path to a ``.fasta`` / ``.fa`` file, **or** an open text stream
            (e.g. ``io.StringIO``) containing FASTA-formatted data.

        Returns
        -------
        list[DNASequence]

        Raises
        ------
        ParserError
            If the source is malformed or a sequence is invalid.
        """
        # Lazy import avoids circular dependency at module load time.
        from bioseq_toolkit.models.sequence import DNASequence

        src_label = "<stream>" if hasattr(path, "read") else str(path)
        records: list[DNASequence] = []
        current_header: str | None = None
        current_seq_parts: list[str] = []

        fh, should_close = _open_source(path)
        try:
            for lineno, raw_line in enumerate(fh, start=1):
                line = raw_line.rstrip("\n")

                if line.startswith(">"):
                    if current_header is not None:
                        records.append(
                            self._build(
                                current_header,
                                "".join(current_seq_parts),
                                src_label,
                            )
                        )
                    current_header = line[1:].strip()
                    current_seq_parts = []

                elif line.strip():
                    if current_header is None:
                        raise ParserError(
                            f"Sequence data before header at line {lineno}.",
                            path=src_label,
                        )
                    current_seq_parts.append(line.strip())

            # Flush last record
            if current_header is not None:
                records.append(
                    self._build(
                        current_header,
                        "".join(current_seq_parts),
                        src_label,
                    )
                )

        except OSError as exc:
            raise ParserError(str(exc), path=src_label) from exc
        finally:
            if should_close:
                fh.close()

        return records

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build(header: str, sequence: str, src_label: str) -> "DNASequence":
        """Build a validated DNASequence from a parsed header + sequence."""
        from bioseq_toolkit.models.sequence import DNASequence

        parts = header.split(None, 1)
        name = parts[0] if parts else ""
        description = parts[1] if len(parts) > 1 else ""

        try:
            return DNASequence.from_string(sequence, name=name, description=description)
        except InvalidDNASequence as exc:
            raise ParserError(
                f"Invalid sequence for record '{name}': {exc}",
                path=src_label,
            ) from exc
