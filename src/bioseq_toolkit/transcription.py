def rna_to_dna(sequence: str) -> str:
    """
    Convert an RNA sequence to a DNA sequence.

    Parameters
    ----------
    sequence : str
        Input RNA sequence.

    Returns
    -------
    str
        DNA sequence.
    """
    if sequence.count("T") > 0:
        raise ValueError("Sequence contains T, cannot be converted to DNA")
    else:
        sequence = sequence.upper()
        return sequence.replace("U", "T")

def dna_to_rna(sequence: str) -> str:
    """
    Convert a DNA sequence to an RNA sequence.

    Parameters
    ----------
    sequence : str
        Input DNA sequence.

    Returns
    -------
    str
        RNA sequence.
    """
    if sequence.count("U") > 0:
        raise ValueError("Sequence contains U, cannot be converted to RNA")
    else:
        sequence = sequence.upper()
        return sequence.replace('T', 'U')
