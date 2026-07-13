"""FASTA format parser."""

from __future__ import annotations

from bioseq_toolkit.parsers.parser import SequenceParser
from bioseq_toolkit.core.exceptions import ParserError, InvalidDNASequence


class FastaParser(SequenceParser):
    """Parse sequences from a FASTA file."""

    def parse(self, path: str) -> "DNASequence":
        """
        Parse the first record from a FASTA file.

        Parameters
        ----------
        path : str
            Path to the ``.fasta`` / ``.fa`` file.

        Returns
        -------
        DNASequence

        Raises
        ------
        ParserError
            If the file contains no records or is malformed.
        """
        records = self.parse_many(path)
        if not records:
            raise ParserError(f"No sequence records found in '{path}'.", path=path)
        return records[0]

    def parse_many(self, path: str) -> list["DNASequence"]:
        """
        Parse all records from a (multi-)FASTA file.

        Parameters
        ----------
        path : str
            Path to the ``.fasta`` / ``.fa`` file.

        Returns
        -------
        list[DNASequence]

        Raises
        ------
        ParserError
            If the file is malformed or a sequence is invalid.
        """
        # Lazy import avoids circular dependency at module load time.
        from bioseq_toolkit.models.sequence import DNASequence

        records: list[DNASequence] = []
        current_header: str | None = None
        current_seq_parts: list[str] = []

        try:
            with open(path, "r", encoding="utf-8") as fh:
                for lineno, raw_line in enumerate(fh, start=1):
                    line = raw_line.rstrip("\n")

                    if line.startswith(">"):
                        if current_header is not None:
                            records.append(
                                self._build(
                                    current_header,
                                    "".join(current_seq_parts),
                                    path,
                                )
                            )
                        current_header = line[1:].strip()
                        current_seq_parts = []

                    elif line.strip():
                        if current_header is None:
                            raise ParserError(
                                f"Sequence data before header at line {lineno}.",
                                path=path,
                            )
                        current_seq_parts.append(line.strip())

            # Flush last record
            if current_header is not None:
                records.append(
                    self._build(
                        current_header,
                        "".join(current_seq_parts),
                        path,
                    )
                )

        except OSError as exc:
            raise ParserError(str(exc), path=path) from exc

        return records

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build(header: str, sequence: str, path: str) -> "DNASequence":
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
                path=path,
            ) from exc
