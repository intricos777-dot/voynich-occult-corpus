#!/usr/bin/env python3
"""Cross-reference Voynich manuscript with occult corpus."""

import json
import re
import os
import sys
from collections import Counter

CORPUS_DIR = "../data/corpus"

def load_corpus():
    """Load all corpus texts."""
    corpus = {}
    for root, dirs, files in os.walk(CORPUS_DIR):
        for f in files:
            if f.endswith(".txt"):
                path = os.path.join(root, f)
                relpath = os.path.relpath(path, CORPUS_DIR)
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    corpus[relpath] = fh.read()
    return corpus

def load_voynich(path="../data/voynich/EVA-transliteration.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_voynich_words(text):
    """Extract Voynich words from EVA transliteration."""
    words = re.split(r'[.\s]+', text)
    return [w.lower() for w in words if w and len(w) > 1]

def find_pattern_matches(voynich_words, corpus_text, min_length=3):
    """Find shared patterns between Voynich and corpus."""
    corpus_lower = corpus_text.lower()
    corpus_words = set(re.findall(r'[a-z]+', corpus_lower))
    
    matches = []
    for word in set(voynich_words):
        if len(word) >= min_length and word in corpus_words:
            matches.append(word)
    return matches

def structural_correlation(voynich_text, corpus_text):
    """Compare sentence/paragraph structures."""
    # Voynich uses dots as word separators
    voynich_lines = [l.strip() for l in voynich_text.split('\n') if l.strip() and not l.strip().startswith('<')]
    
    # Count line lengths
    voynich_lengths = [len(l.split('.')) for l in voynich_lines[:100]]
    
    return {
        "voynich_sample_lines": len(voynich_lengths),
        "avg_line_length": round(sum(voynich_lengths)/len(voynich_lengths), 2) if voynich_lengths else 0,
        "line_length_range": [min(voynich_lengths), max(voynich_lengths)] if voynich_lengths else [0,0]
    }

def main():
    print("Loading corpus...")
    corpus = load_corpus()
    print(f"  Loaded {len(corpus)} texts")
    
    print("Loading Voynich...")
    voynich = load_voynich()
    voynich_words = extract_voynich_words(voynich)
    print(f"  {len(voynich_words)} words extracted")
    
    results = {
        "corpus_size": len(corpus),
        "voynich_words": len(voynich_words),
        "unique_voynich_words": len(set(voynich_words)),
        "matches_by_corpus": {}
    }
    
    for path, text in corpus.items():
        matches = find_pattern_matches(voynich_words, text)
        if matches:
            results["matches_by_corpus"][path] = {
                "match_count": len(matches),
                "matches": matches[:50]  # limit output
            }
    
    # Structural analysis
    results["structural"] = structural_correlation(voynich, corpus.get("esoteric/liber-al-vel-legis.txt", ""))
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
