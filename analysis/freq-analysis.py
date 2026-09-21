#!/usr/bin/env python3
"""Frequency analysis of Voynich EVA text vs. natural languages."""

import json
import re
from collections import Counter
import sys

def analyze_frequencies(text):
    """Character and bigram frequency analysis."""
    # Character frequencies
    chars = Counter(c for c in text if not c.isspace() and c.isalpha())
    total = sum(chars.values())
    char_freq = {k: round(v/total, 6) for k, v in chars.most_common(30)}
    
    # Bigrams
    bigrams = Counter()
    for i in range(len(text)-1):
        if text[i].isalpha() and text[i+1].isalpha():
            bigrams[text[i:i+2]] += 1
    total_bg = sum(bigrams.values())
    bigram_freq = {k: round(v/total_bg, 6) for k, v in bigrams.most_common(30)}
    
    # Words (split by dots and spaces)
    words = re.split(r'[.\s]+', text.lower())
    words = [w for w in words if w]
    word_freq = Counter(words)
    
    return {
        "total_characters": total,
        "total_words": len(words),
        "unique_words": len(word_freq),
        "char_frequencies": char_freq,
        "bigram_frequencies": bigram_freq,
        "most_common_words": word_freq.most_common(25),
        "avg_word_length": round(sum(len(w) for w in words)/len(words), 2)
    }

def entropy(text):
    """Shannon entropy of text."""
    from math import log2
    chars = Counter(text)
    total = sum(chars.values())
    return -sum((count/total) * log2(count/total) for count in chars.values())

if __name__ == "__main__":
    with open(sys.argv[1] if len(sys.argv) > 1 else "../data/voynich/EVA-transliteration.txt") as f:
        text = f.read()
    
    result = analyze_frequencies(text)
    result["entropy_bits"] = round(entropy(text), 4)
    print(json.dumps(result, indent=2))
