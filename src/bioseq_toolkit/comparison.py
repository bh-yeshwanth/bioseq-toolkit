def hamming_distance(sequence1: str, sequence2: str) -> int:
    """
    Calculate the Hamming distance between two sequences.

    Parameters
    ----------
    sequence1 : str
        Input sequence.
    sequence2 : str
        Input sequence.

    Returns
    -------
    int
        Hamming distance.
    """
    if len(sequence1) != len(sequence2):
        raise ValueError("Sequences must be of equal length")
    else:
        distance = 0
        for i in range(len(sequence1)):
            if sequence1[i] != sequence2[i]:
                distance += 1
        return distance

def motif_search(sequence: str, motif: str) -> list[int]:
    """
    Find all occurrences of a motif in a sequence.

    Parameters
    ----------
    sequence : str
        Input sequence.
    motif : str
        Input motif.

    Returns
    -------
    list[int]
        List of starting positions of the motif in the sequence.
    """
    positions = []
    for i in range(len(sequence) - len(motif) + 1):
        if sequence[i:i + len(motif)] == motif:
            positions.append(i)
    return positions

