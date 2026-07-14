"""GenBank flat-file parser."""

from __future__ import annotations

import re
from bioseq_toolkit.parsers.parser import SequenceParser, SourceType, _open_source
from bioseq_toolkit.core.exceptions import ParserError, InvalidDNASequence
from bioseq_toolkit.core.enums import Topology


class GenBankParser(SequenceParser):
    """
    Parse sequences and annotations from a GenBank flat-file.

    Supports the standard GenBank format as produced by NCBI, including
    LOCUS, DEFINITION, ACCESSION, VERSION, SOURCE, FEATURES, and ORIGIN
    sections.

    Both :meth:`parse` and (inherited) :meth:`parse_many` accept either a
    filesystem path (``str`` or ``os.PathLike``) or a file-like text stream
    (``io.StringIO``, ``io.TextIOBase``, ``typing.TextIO``).
    """

    def parse(self, path: SourceType) -> "DNASequence":
        """
        Parse a single-record GenBank source.

        Parameters
        ----------
        path : str, os.PathLike, or TextIO
            Path to a ``.gb`` / ``.gbk`` file, **or** an open text stream
            (e.g. ``io.StringIO``) containing GenBank-formatted data.

        Returns
        -------
        DNASequence
            Includes annotations and metadata parsed from the FEATURES
            and LOCUS/DEFINITION blocks.

        Raises
        ------
        ParserError
            If the source is malformed or contains no sequence data.
        """
        # Lazy import avoids circular dependency at module load time.
        from bioseq_toolkit.models.sequence import DNASequence
        from bioseq_toolkit.core.annotation import Annotation

        src_label = "<stream>" if hasattr(path, "read") else str(path)

        fh, should_close = _open_source(path)
        try:
            content = fh.read()
        except OSError as exc:
            raise ParserError(str(exc), path=src_label) from exc
        finally:
            if should_close:
                fh.close()

        # ----------------------------------------------------------------
        # Split into sections at keyword boundaries (columns 0-11)
        # ----------------------------------------------------------------
        name = ""
        description = ""
        topology = Topology.LINEAR
        metadata: dict[str, str] = {}
        annotations: list = []
        sequence = ""

        lines = content.splitlines()
        i = 0
        in_features = False
        in_origin = False
        current_feature_type = ""
        current_feature_loc = ""
        current_qualifiers: dict[str, str] = {}

        def flush_feature():
            nonlocal current_feature_type, current_feature_loc, current_qualifiers
            if not current_feature_type:
                return
            start, end, strand = _parse_location(current_feature_loc)
            annotations.append(
                Annotation(
                    feature_type=current_feature_type,
                    start=start,
                    end=end,
                    strand=strand,
                    qualifiers=dict(current_qualifiers),
                    label=_resolve_label(current_qualifiers),
                )
            )
            current_feature_type = ""
            current_feature_loc = ""
            current_qualifiers = {}

        while i < len(lines):
            line = lines[i]

            # ---- LOCUS -----------------------------------------------
            if line.startswith("LOCUS"):
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[1]
                topology_str = "linear"
                if "circular" in line.lower():
                    topology_str = "circular"
                topology = (
                    Topology.CIRCULAR
                    if topology_str == "circular"
                    else Topology.LINEAR
                )

            # ---- DEFINITION ------------------------------------------
            elif line.startswith("DEFINITION"):
                desc_parts = [line[12:].strip()]
                i += 1
                while i < len(lines) and lines[i].startswith(" "):
                    desc_parts.append(lines[i].strip())
                    i += 1
                description = " ".join(desc_parts).rstrip(".")
                continue

            # ---- ACCESSION -------------------------------------------
            elif line.startswith("ACCESSION"):
                metadata["accession"] = line[12:].strip().split()[0]

            # ---- VERSION ---------------------------------------------
            elif line.startswith("VERSION"):
                metadata["version"] = line[12:].strip().split()[0]

            # ---- SOURCE ----------------------------------------------
            elif line.startswith("SOURCE"):
                metadata["organism"] = line[12:].strip()

            # ---- FEATURES --------------------------------------------
            elif line.startswith("FEATURES"):
                in_features = True
                in_origin = False

            # ---- ORIGIN ----------------------------------------------
            elif line.startswith("ORIGIN"):
                flush_feature()
                in_features = False
                in_origin = True

            # ---- Record terminator -----------------------------------
            elif line.startswith("//"):
                flush_feature()
                break

            # ---- FEATURES body ---------------------------------------
            elif in_features:
                # Feature header: 5 spaces + feature_type + location
                if len(line) > 5 and line[0] == " " and line[5] != " ":
                    flush_feature()
                    # Format: "     feature_type      location"
                    stripped = line.strip()
                    feature_parts = stripped.split()
                    if feature_parts:
                        current_feature_type = feature_parts[0]
                        current_feature_loc = feature_parts[1] if len(feature_parts) > 1 else ""
                # Qualifier: 21 spaces + /key="value"
                elif line.startswith(" " * 21) and line.strip().startswith("/"):
                    qual = line.strip()[1:]  # strip leading /
                    if "=" in qual:
                        key, _, val = qual.partition("=")
                        current_qualifiers[key] = val.strip('"')
                    else:
                        current_qualifiers[qual] = ""

            # ---- ORIGIN body -----------------------------------------
            elif in_origin:
                # Lines look like: "        1 atgcat gcatgc ..."
                # Strip the position number and whitespace to get bases
                raw = line.strip()
                if raw and raw[0].isdigit():
                    bases = "".join(raw.split()[1:])
                    sequence += bases

            i += 1

        if not sequence:
            raise ParserError(
                f"No sequence (ORIGIN section) found in '{src_label}'.",
                path=src_label,
            )

        try:
            from bioseq_toolkit.models.sequence import DNASequence
            return DNASequence.from_string(
                sequence.upper(),
                name=name,
                description=description,
                topology=topology,
                annotations=annotations,
                metadata=metadata,
            )
        except InvalidDNASequence as exc:
            raise ParserError(str(exc), path=src_label) from exc


def _resolve_label(qualifiers: dict[str, str]) -> str:
    """
    Resolve the preferred human-readable label for a GenBank feature.

    Checks keys in the following priority order:
    1. "gene"
    2. "label"
    3. "product"
    4. "note"
    """
    for key in ("gene", "label", "product", "note"):
        if key in qualifiers:
            return qualifiers[key]
    return ""


# ---------------------------------------------------------------------------
# Location string helpers
# ---------------------------------------------------------------------------

def _parse_location(loc: str) -> tuple[int, int, int]:
    """
    Parse a GenBank location string into (start, end, strand).

    Handles simple ranges (``100..200``) and complement
    (``complement(100..200)``). Returns zero-based half-open [start, end).

    Returns ``(0, 0, 1)`` for unrecognised formats.
    """
    strand = 1
    if loc.startswith("complement("):
        strand = -1
        loc = loc[len("complement("):].rstrip(")")

    m = re.match(r"[<>]?(\d+)\.\.[<>]?(\d+)", loc)
    if m:
        start = int(m.group(1)) - 1   # convert to 0-based
        end = int(m.group(2))         # already exclusive
        return start, end, strand

    # Single-base position (e.g. "42")
    m2 = re.match(r"(\d+)$", loc)
    if m2:
        pos = int(m2.group(1)) - 1
        return pos, pos + 1, strand

    return 0, 0, strand
