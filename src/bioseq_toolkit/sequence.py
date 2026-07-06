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
    Return the complement of a sequence 
    Parameters
    ----------
    sequence : str
        Input sequence.

    Returns
    -------
    str
        Complement sequence.
    """
    # 1. Standardisation of checks using lowercase
    has_t = 't' in sequence.lower()
    has_u = 'u' in sequence.lower()
    
    # 2. Validation first
    if has_t and has_u:
        raise ValueError("Sequence contains both T and U. A sequence cannot simultaneously represent DNA and RNA")
        
    # 3. Determination of DNA or RNA (defaulting to DNA if neither is present)
    if has_u:
        complement_map = {
            'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C',
            'a': 'u', 'u': 'a', 'c': 'g', 'g': 'c'
        }
    else:
        complement_map = {
            'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C',
            'a': 't', 't': 'a', 'c': 'g', 'g': 'c'
        }
        
    # 4. Building of the complement sequence (returning after the loop completes)
        complement_seq = ""

    for base in sequence:
        if base not in complement_map:
            raise ValueError(f"Invalid nucleotide '{base}' found.")

        complement_seq += complement_map[base]

    return complement_seq

def reverse_complement(sequence: str) -> str:
    """
    Return the reverse complement of a sequence.

    Parameters
    ----------
    sequence : str
        Input sequence.

    Returns
    -------
    str
        Reverse complement sequence.
    """
    return complement(reverse(sequence))

def nucleotide_count(sequence: str) -> dict:
    """
    Count the occurrences of each nucleotide in a biological sequence.
        Parameters
    ----------
    sequence : str
        Input sequence.

    Returns
    -------
    dict
        Nucleotide counts.
    """
    counts = {'A':0,'T':0,'G':0,'C':0}
    for base in sequence.upper():
        if base in counts:
            counts[base] += 1
        else:
            raise ValueError(f"Invalid nucleotide '{base}' found.")
    return counts

def palindromic(sequence: str) -> bool:
    """
    Check if a sequence is palindromic.(This checks for a reverse-complement palindrome)
    
    Parameters
    ----------
    sequence : str
        Input sequence.
    
    Returns
    -------
    bool
        True if the sequence is palindromic, False otherwise.
    """
    return sequence == reverse_complement(sequence)
