#!/usr/bin/env python3
"""Thelemic Cipher Engine — decode Voynich via Liber AL cipher system."""

import json
import re
from collections import Counter

# English Qaballa mapping (order & value)
EQ_MAP = {
    "A": 1, "L": 2, "W": 3, "H": 4, "S": 5, "D": 6, "O": 7, "Z": 8,
    "K": 9, "V": 10, "G": 11, "R": 12, "C": 13, "N": 14, "Y": 15,
    "J": 16, "U": 17, "F": 18, "Q": 19, "B": 20, "M": 21, "X": 22,
    "I": 23, "T": 24, "E": 25, "P": 26
}

# EVA alphabet to Latin mapping (approximate)
EVA_TO_LATIN = {
    "a": "a", "b": "b", "c": "c", "d": "d", "e": "e", "f": "f",
    "g": "g", "h": "h", "i": "i", "k": "k", "l": "l", "m": "m",
    "n": "n", "o": "o", "p": "p", "q": "q", "r": "r", "s": "s",
    "t": "t", "y": "y", "ch": "c", "sh": "s", "ct": "t", "ck": "k",
    "ee": "e", "ei": "e", "ii": "i", "oo": "o", "ou": "u",
    "al": "l", "ol": "l", "am": "m", "om": "m", "an": "n", "on": "n",
    "ar": "r", "or": "r", "ai": "i", "oi": "i", "ei": "i"
}

def eq_sum(word):
    """Calculate English Qaballa value of a word."""
    return sum(EQ_MAP.get(c, 0) for c in word.upper())

def gematria_match(number, corpus_terms):
    """Find words in corpus that match a gematria value."""
    matches = []
    for term, value in corpus_terms.items():
        if value == number:
            matches.append(term)
    return matches

def thelemic_key(verse_ref):
    """Derive cipher key from Liber AL verse reference (e.g., '1:46')."""
    chapter, verse = map(int, verse_ref.split(":"))
    return (chapter * 100) + verse  # e.g., 1:46 -> 146

def decode_with_key(ciphertext, key):
    """Simple rotation cipher with Thelemic key."""
    result = []
    for char in ciphertext:
        if char.isalpha():
            shifted = ord(char) + (key % 26)
            if char.isupper():
                if shifted > ord('Z'): shifted -= 26
                result.append(chr(shifted))
            else:
                if shifted > ord('z'): shifted -= 26
                result.append(chr(shifted))
        else:
            result.append(char)
    return "".join(result)

def voynich_word_analysis(text):
    """Analyze Voynich word frequency and structure."""
    words = text.split()
    word_counts = Counter(words)
    lengths = Counter(len(w) for w in words)
    return {
        "total_words": len(words),
        "unique_words": len(word_counts),
        "most_common": word_counts.most_common(20),
        "length_distribution": dict(sorted(lengths.items()))
    }

def find_voynich_correlations(voynich_words, corpus_words):
    """Find structural correlations between Voynich and corpus texts."""
    correlations = []
    # Look for similar word-length patterns
    voynich_lengths = Counter(len(w) for w in voynich_words)
    corpus_lengths = Counter(len(w) for w in corpus_words)
    
    for length in voynich_lengths:
        if length in corpus_lengths:
            voynich_pct = voynich_lengths[length] / len(voynich_words)
            corpus_pct = corpus_lengths[length] / len(corpus_words)
            diff = abs(voynich_pct - corpus_pct)
            correlations.append({
                "length": length,
                "voynich_pct": round(voynich_pct, 4),
                "corpus_pct": round(corpus_pct, 4),
                "diff": round(diff, 4)
            })
    
    return sorted(correlations, key=lambda x: x["diff"])

if __name__ == "__main__":
    import sys
    with open(sys.argv[1] if len(sys.argv) > 1 else "../data/voynich/EVA-transliteration.txt") as f:
        voynich = f.read()
    
    words = voynich.split()
    analysis = voynich_word_analysis(words)
    print(json.dumps(analysis, indent=2))
