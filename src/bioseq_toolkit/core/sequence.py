"""
Core nucleotide sequence operations.

All functions work on plain ``str`` inputs. They validate input and raise
descriptive errors rather than silently producing wrong results.
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DNA_COMPLEMENT: dict[str, str] = {
    'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C',
    'a': 't', 't': 'a', 'c': 'g', 'g': 'c',
}

_RNA_COMPLEMENT: dict[str, str] = {
    'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C',
    'a': 'u', 'u': 'a', 'c': 'g', 'g': 'c',
}


# ---------------------------------------------------------------------------
# sequence.py
# ---------------------------------------------------------------------------

def reverse(sequence: str) -> str:
    """
    Return the reverse of a sequence.

    Parameters
    ----------
    sequence : str
        Input sequence.

    Returns
    -------
    str
        Reversed sequence.
    """
    return sequence[::-1]


def complement(sequence: str) -> str:
    """
    Return the complement of a DNA or RNA sequence.

    Auto-detects molecule type by the presence of ``T`` (DNA) or ``U`` (RNA).
    Defaults to DNA complement rules when neither is present.

    Parameters
    ----------
    sequence : str
        Input DNA or RNA sequence.

    Returns
    -------
    str
        Complement sequence.

    Raises
    ------
    ValueError
        If the sequence contains both T and U, or an invalid nucleotide.
    """
    seq_lower = sequence.lower()
    has_t = 't' in seq_lower
    has_u = 'u' in seq_lower

    if has_t and has_u:
        raise ValueError(
            "Sequence contains both T and U. "
            "A sequence cannot simultaneously represent DNA and RNA."
        )

    complement_map = _RNA_COMPLEMENT if has_u else _DNA_COMPLEMENT

    complement_seq = ""
    for base in sequence:
        if base not in complement_map:
            raise ValueError(f"Invalid nucleotide '{base}' found.")
        complement_seq += complement_map[base]

    return complement_seq


def reverse_complement(sequence: str) -> str:
    """
    Return the reverse complement of a DNA or RNA sequence.

    Parameters
    ----------
    sequence : str
        Input DNA or RNA sequence.

    Returns
    -------
    str
        Reverse complement sequence.

    Raises
    ------
    ValueError
        Propagated from :func:`complement`.
    """
    return complement(reverse(sequence))


def nucleotide_count(sequence: str) -> dict[str, int]:
    """
    Count occurrences of each nucleotide in a sequence.

    Parameters
    ----------
    sequence : str
        Input DNA sequence.

    Returns
    -------
    dict[str, int]
        Counts keyed by nucleotide (``A``, ``T``, ``G``, ``C``).

    Raises
    ------
    ValueError
        If the sequence contains an invalid nucleotide.
    """
    counts: dict[str, int] = {'A': 0, 'T': 0, 'G': 0, 'C': 0}
    for base in sequence.upper():
        if base in counts:
            counts[base] += 1
        else:
            raise ValueError(f"Invalid nucleotide '{base}' found.")
    return counts


def palindromic(sequence: str) -> bool:
    """
    Return ``True`` if *sequence* is a reverse-complement palindrome.

    This is the biological definition: the sequence reads the same on both
    strands in the 5'→3' direction.

    Parameters
    ----------
    sequence : str
        Input DNA sequence.

    Returns
    -------
    bool
        ``True`` if the sequence equals its own reverse complement.
    """
    return sequence == reverse_complement(sequence)


# ---------------------------------------------------------------------------
# transcription.py (moved here)
# ---------------------------------------------------------------------------

def dna_to_rna(sequence: str) -> str:
    """
    Convert a DNA sequence to its RNA transcript (``T`` → ``U``).

    Parameters
    ----------
    sequence : str
        Input DNA sequence.

    Returns
    -------
    str
        RNA sequence (uppercase).

    Raises
    ------
    ValueError
        If the sequence contains ``U``.
    """
    if 'U' in sequence.upper():
        raise ValueError("Sequence contains U, cannot be converted to RNA.")
    return sequence.upper().replace('T', 'U')


def rna_to_dna(sequence: str) -> str:
    """
    Convert an RNA sequence to DNA (``U`` → ``T``).

    Parameters
    ----------
    sequence : str
        Input RNA sequence.

    Returns
    -------
    str
        DNA sequence (uppercase).

    Raises
    ------
    ValueError
        If the sequence contains ``T``.
    """
    if 'T' in sequence.upper():
        raise ValueError("Sequence contains T, cannot be converted to DNA.")
    return sequence.upper().replace('U', 'T')


# ---------------------------------------------------------------------------
# comparison.py (moved here)
# ---------------------------------------------------------------------------

def hamming_distance(sequence1: str, sequence2: str) -> int:
    """
    Calculate the Hamming distance between two equal-length sequences.

    Parameters
    ----------
    sequence1 : str
        First sequence.
    sequence2 : str
        Second sequence.

    Returns
    -------
    int
        Number of positions at which the sequences differ.

    Raises
    ------
    ValueError
        If the sequences are not the same length.
    """
    if len(sequence1) != len(sequence2):
        raise ValueError("Sequences must be of equal length.")
    return sum(a != b for a, b in zip(sequence1, sequence2))


def motif_search(sequence: str, motif: str) -> list[int]:
    """
    Find all (overlapping) occurrences of *motif* within *sequence*.

    Parameters
    ----------
    sequence : str
        The sequence to search.
    motif : str
        The motif to find.

    Returns
    -------
    list[int]
        Zero-based starting indices of every match.
    """
    positions: list[int] = []
    motif_len = len(motif)
    for i in range(len(sequence) - motif_len + 1):
        if sequence[i:i + motif_len] == motif:
            positions.append(i)
    return positions
