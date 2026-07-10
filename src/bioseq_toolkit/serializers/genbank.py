"""GenBank format serializer."""


def to_genbank(record: object) -> str:
    """
    Serialize a sequence record to GenBank flat-file format.

    Parameters
    ----------
    record : object
        A sequence record object containing sequence, annotations,
        and metadata.

    Returns
    -------
    str
        GenBank-formatted string.
    """
    ...
