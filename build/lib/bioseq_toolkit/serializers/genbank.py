"""GenBank flat-file serializer."""

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bioseq_toolkit.models.sequence import DNASequence


def to_genbank(record: "DNASequence") -> str:
    """
    Serialize a ``DNASequence`` to GenBank flat-file format.

    Produces a minimal but valid GenBank record. Fields that are not
    available on the record are substituted with sensible defaults.

    Parameters
    ----------
    record : DNASequence
        The sequence record to serialize.

    Returns
    -------
    str
        GenBank-formatted string ending with ``//\\n``.
    """
    today = datetime.date.today().strftime("%d-%b-%Y").upper()

    name = (record.name or record.metadata.get("accession", "UNKNOWN"))[:16]
    accession = record.metadata.get("accession", "UNKNOWN")
    version = record.metadata.get("version", accession)
    date_str = record.metadata.get("date", today)
    topology_str = record.topology.value.upper()[:8]

    bp = len(record.sequence)

    lines: list[str] = []

    # LOCUS line — fixed-width format
    locus_name = name.ljust(16)
    lines.append(
        f"LOCUS       {locus_name}{bp:>10} bp    DNA     "
        f"{topology_str:<8} SYN {date_str}"
    )

    definition = record.description or "No definition."
    lines.append(f"DEFINITION  {definition}")
    lines.append(f"ACCESSION   {accession}")
    lines.append(f"VERSION     {version}")

    organism = record.metadata.get("organism", "")
    if organism:
        lines.append(f"SOURCE      {organism}")

    # FEATURES block
    if record.annotations:
        lines.append("FEATURES             Location/Qualifiers")
        for ann in record.annotations:
            loc = f"{ann.start + 1}..{ann.end}"
            if ann.strand == -1:
                loc = f"complement({loc})"
            feature_label = ann.feature_type.ljust(16)
            lines.append(f"     {feature_label}{loc}")
            for key, val in ann.qualifiers.items():
                lines.append(f"                     /{key}=\"{val}\"")

    # ORIGIN block — 60 bases per line, grouped in 10s
    lines.append("ORIGIN")
    seq = record.sequence.lower()
    for i in range(0, len(seq), 60):
        chunk = seq[i : i + 60]
        pos = str(i + 1).rjust(9)
        groups = " ".join(chunk[j : j + 10] for j in range(0, len(chunk), 10))
        lines.append(f"{pos} {groups}")

    lines.append("//")
    return "\n".join(lines) + "\n"
