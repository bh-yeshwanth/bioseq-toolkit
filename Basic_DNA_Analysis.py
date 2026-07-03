def dna_Counter(DNA):
    counts = {'A':0,'T':0,'G':0,'C':0}
    for base in DNA:
        counts[base] += 1
    return(counts)

DNA_1 = 'ATGCGCGCTA'
print(dna_Counter(DNA_1))


def reverse(DNA):
    DNA_Rev = DNA[ : :-1]
    return(DNA_Rev)

def complement(DNA):
    complement = {
    'A': 'T',
    'T': 'A',
    'C': 'G',
    'G': 'C'}
    complement_seq = ''
    for base in DNA:
       complement_seq = complement_seq + complement[base]
    return(complement_seq)

def reverse_complement(DNA):
    R_C = complement(reverse(DNA))
    return R_C


print(reverse(DNA_1))
print(complement(DNA_1))
print(reverse_complement(DNA_1))


# TO find the longest DNA sequence
sequences = [
    "ATG",
    "ATGCGC",
    "ATTTAACCGGATCG",
    "ATGCGCGCTA"
    ]
i = 0
a = ""
for DNA in sequences:
    while i < len(sequences):
        if len(sequences[i]) >= len(a):
            a = sequences[i]
        i += 1

print(a)


# Count Codons
DNA_1 = 'ATGCGCGCTA'

def No_of_codons(DNA):
    return((len(DNA)/3))

print(No_of_codons(DNA_1))


# palindromic sequence analysis
dna = "ATCGCTAT"

def palindromic(DNA):
    if DNA == DNA[ : :-1]:
        print("given sequence is palindromic")
    else:
        print("Given sequence is not palindromic")


# Hamming Distance
s1 = "GGGCCGTTGGT"
s2 = "GGACCGTTGAC"
a = 0
i = 0
while i < len(s1):
    if s1[i] != s2[i]:
        a += 1
    i += 1

print(a)


# motif search
sequence = "GATATATGCATATACTT"
motif = "ATAT"
a = 0
i = 0
while i < len(sequence):
    if motif[0:] == sequence[i:]:
        print(sequence[i:])
        print(motif[0:])
        a += 1
    i += 1

print(a)


# RNA_to_DNA
def RNA_to_DNA(RNA):
    i = 0
    dna = ''
    while i < len(RNA):
        if RNA[i] == 'U':
            dna = dna + 'T'
        else:
            dna = dna + RNA[i]
        i += 1
    return dna

print(RNA_to_DNA('AUGUAGCUAACUCAGGUUACAUGGGGAUGACCCCGCGACUUGGAUUAGAGUCUCUUUUGGAAUAAGCCUGAAUGAUCCGAGUAGCAUCUCAGAUGGGGAUGACCCCGCGACUUGGAUUAGAGUCUCUUUUGGAAUAAGCCUGAAUGAUCCGAGUAGCAUCUCAGAUGACCCCGCGACUUGGAUUAGAGUCUCUUUUGGAAUAAGCCUGAAUGAUCCGAGUAGCAUCUCAG'))