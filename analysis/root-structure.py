#!/usr/bin/env python3
"""Voynich Root Structure Decoder — extracts the deep morphological skeleton from EVA transliteration.

This tool treats the manuscript as an unknown language and reconstructs:
1. Morpheme boundary detection (prefix/root/suffix decomposition)
2. Positional frequency analysis (what characters appear at which word positions)
3. Transition probability matrix between EVA character classes
4. Agglutination index (how morphemes chain together)
5. Word class clustering by co-occurrence patterns
6. Grammatical skeleton (probabilistic grammar reconstruction)
"""

import json
import re
import sys
import os
from collections import Counter, defaultdict
from math import log2

# ============================================================
# STEP 1: Load and clean
# ============================================================

def load_voynich(path=None):
    if path is None:
        path = "../data/voynich/EVA-transliteration.txt"
        import os
        # Resolve relative to this script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "..", "data", "voynich", "EVA-transliteration.txt")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # IVTFF format: text lines look like "<f1r.1,@P0> word1.word2.word3..."
    # Extract everything after the last '>' on each line
    lines = []
    for line in text.split('\n'):
        if '>' in line:
            text_part = line.split('>')[-1].strip()
            if text_part:
                lines.append(text_part)
    return ' '.join(lines)

def extract_words(text):
    """Split EVA text into words. EVA uses dots as word separators."""
    words = re.split(r'[\.\s]+', text.lower())
    return [w for w in words if w and len(w) >= 2]

# ============================================================
# STEP 2: Character Class Mapping
# ============================================================

VOWELS = set('aeiouy')
CONSONANTS = set('bcdfghjklmnpqrstvwxz')
GALLOWS = set('fkpqst')  # Voynich gallows characters

def classify_char(c):
    if c in VOWELS:
        return 'V'
    if c in GALLOWS:
        return 'G'  # gallows modifier
    if c in CONSONANTS:
        return 'C'
    return 'X'  # unknown/metadata

def word_signature(word):
    """Convert word to consonant/vowel signature."""
    return ''.join(classify_char(c) for c in word if c.isalpha())

# ============================================================
# STEP 3: Positional Analysis
# ============================================================

def positional_frequency(words, max_pos=12):
    """Count character frequencies at each word position."""
    freq = defaultdict(Counter)
    for w in words:
        for i, c in enumerate(w):
            if i < max_pos and c.isalpha():
                freq[i][c] += 1
    return freq

def positional_char_class(words, max_pos=12):
    """Count V/C/G class at each word position."""
    freq = defaultdict(Counter)
    for w in words:
        for i, c in enumerate(w):
            if i < max_pos and c.isalpha():
                freq[i][classify_char(c)] += 1
    return freq

# ============================================================
# STEP 4: Morpheme Boundary Detection
# ============================================================

def detect_boundaries(words):
    """Find likely morpheme boundaries using bigram drop-offs."""
    # Build character transition matrix
    transitions = Counter()
    for w in words:
        for i in range(len(w) - 1):
            transitions[w[i], w[i+1]] += 1
    
    # Calculate drop-off scores between each pair
    total = sum(transitions.values())
    boundary_scores = Counter()
    
    for (a, b), count in transitions.items():
        freq_ab = count / total
        freq_a = sum(c for (_, _a), c in transitions.items() if _a == a) / total
        freq_b = sum(c for (_b, _), c in transitions.items() if _b == b) / total
        
        # PMI-inspired boundary score
        if freq_a * freq_b > 0:
            pmi = log2(freq_ab / (freq_a * freq_b))
            boundary_scores[(a, b)] = pmi
    
    return boundary_scores

def segment_word(word, boundary_scores, threshold=-1.5):
    """Segment a word into morphemes based on boundary scores."""
    if len(word) < 3:
        return [word]
    
    segments = []
    current = word[0]
    
    for i in range(len(word) - 1):
        pair = (word[i], word[i+1])
        score = boundary_scores.get(pair, 0)
        
        if score < threshold and len(current) >= 2:
            segments.append(current)
            current = word[i+1]
        else:
            current += word[i+1]
    
    segments.append(current)
    return segments

# ============================================================
# STEP 5: Suffix/Prefix Detection
# ============================================================

def detect_affixes(words, min_count=50):
    """Detect recurring prefixes and suffixes."""
    prefixes = Counter()
    suffixes = Counter()
    
    for w in words:
        for length in [2, 3]:
            if len(w) >= length + 2:
                prefixes[w[:length]] += 1
                suffixes[w[-length:]] += 1
    
    # Filter by minimum frequency
    prefixes = {k: v for k, v in prefixes.items() if v >= min_count}
    suffixes = {k: v for k, v in suffixes.items() if v >= min_count}
    
    return prefixes, suffixes

def extract_roots(words, prefixes, suffixes):
    """Strip known affixes to find root morphemes."""
    roots = Counter()
    
    for w in words:
        stripped = w
        
        # Strip prefix
        for p in sorted(prefixes, key=len, reverse=True):
            if stripped.startswith(p) and len(stripped) - len(p) >= 2:
                stripped = stripped[len(p):]
                break
        
        # Strip suffix
        for s in sorted(suffixes, key=len, reverse=True):
            if stripped.endswith(s) and len(stripped) - len(s) >= 2:
                stripped = stripped[:-len(s)]
                break
        
        if len(stripped) >= 2:
            roots[stripped] += 1
    
    return roots

# ============================================================
# STEP 6: Transition Matrix (Bigram/Trigram)
# ============================================================

def build_transition_matrix(words):
    """Build character-level transition matrix."""
    bigrams = Counter()
    trigrams = Counter()
    
    for w in words:
        padded = '^' + w + '$'
        for i in range(len(padded) - 1):
            bigrams[padded[i], padded[i+1]] += 1
        for i in range(len(padded) - 2):
            trigrams[padded[i], padded[i+1], padded[i+2]] += 1
    
    return bigrams, trigrams

def compute_entropy_rate(words):
    """Compute the entropy rate per character (bits/char)."""
    char_freq = Counter()
    for w in words:
        for c in w:
            if c.isalpha():
                char_freq[c] += 1
    
    total = sum(char_freq.values())
    probs = [c/total for c in char_freq.values()]
    
    # Shannon entropy
    entropy = -sum(p * log2(p) for p in probs)
    
    # Bigram entropy
    bigrams, _ = build_transition_matrix(words)
    total_bg = sum(bigrams.values())
    bg_probs = [c/total_bg for c in bigrams.values()]
    bigram_entropy = -sum(p * log2(p) for p in bg_probs)
    
    return entropy, bigram_entropy

# ============================================================
# STEP 7: Agglutination Index
# ============================================================

def agglutination_index(words, prefixes, suffixes, roots):
    """Measure how agglutinative the language is.
    
    High index = many morphemes per word (like Turkish/Finnish)
    Low index = few morphemes per word (like Chinese/English)
    """
    morpheme_count = 0
    word_count = 0
    
    for w in words:
        word_count += 1
        morphemes = 1
        
        # Count prefix
        for p in prefixes:
            if w.startswith(p):
                morphemes += 1
                break
        
        # Count suffix
        for s in suffixes:
            if w.endswith(s):
                morphemes += 1
                break
        
        # Check if in root lexicon
        for r in roots.most_common(500):
            if r[0] in w:
                morphemes += 1
                break
        
        morpheme_count += morphemes
    
    return morpheme_count / word_count if word_count > 0 else 0

# ============================================================
# STEP 8: Word Class Detection (Co-occurrence Clustering)
# ============================================================

def word_class_detection(words, top_n=500):
    """Group words by co-occurrence patterns (distributional semantics)."""
    # Get top N words
    word_freq = Counter(words)
    top_words = set(w for w, _ in word_freq.most_common(top_n))
    
    # Build co-occurrence matrix (words that appear near each other)
    cooccurrence = defaultdict(Counter)
    
    # Use sliding window of 5 words
    for i in range(len(words) - 5):
        window = words[i:i+5]
        for w in window:
            if w in top_words:
                for other in window:
                    if other != w and other in top_words:
                        cooccurrence[w][other] += 1
    
    # Simple clustering: group words by similar co-occurrence signatures
    clusters = defaultdict(list)
    
    for w in top_words:
        if w in cooccurrence:
            # Use top 3 co-occurring words as signature
            sig = tuple(sorted(cooccurrence[w].most_common(3), key=lambda x: -x[1]))
            clusters[sig].append(w)
    
    return clusters, cooccurrence

# ============================================================
# STEP 9: Root Language Structure Output
# ============================================================

def build_structure():
    """Main analysis pipeline."""
    
    print("=" * 70)
    print("VOYNICH ROOT STRUCTURE DECODER")
    print("=" * 70)
    
    # Load
    print("\n[1] Loading Voynich text...")
    text = load_voynich()
    words = extract_words(text)
    print(f"    {len(words)} words extracted")
    
    # Positional analysis
    print("\n[2] Positional character frequency (top 5 positions)...")
    pos_freq = positional_frequency(words)
    for pos in range(5):
        top = pos_freq[pos].most_common(5)
        print(f"    pos {pos}: {dict(top)}")
    
    # Character class by position
    print("\n[3] Character class by word position...")
    pos_class = positional_char_class(words)
    for pos in range(8):
        total = sum(pos_class[pos].values())
        if total > 0:
            dist = {k: round(v/total, 3) for k, v in pos_class[pos].most_common()}
            print(f"    pos {pos}: {dist}")
    
    # Boundary detection
    print("\n[4] Detecting morpheme boundaries...")
    boundary_scores = detect_boundaries(words)
    low_pmi = sorted(boundary_scores.items(), key=lambda x: x[1])[:10]
    print("    Strongest boundaries (lowest PMI):")
    for (a, b), score in low_pmi:
        print(f"      '{a}'→'{b}': {score:.4f}")
    
    # Affix detection
    print("\n[5] Detecting affixes...")
    prefixes, suffixes = detect_affixes(words)
    print(f"    Top prefixes: {dict(Counter(prefixes).most_common(10))}")
    print(f"    Top suffixes: {dict(Counter(suffixes).most_common(10))}")
    
    # Root extraction
    print("\n[6] Extracting roots...")
    roots = extract_roots(words, prefixes, suffixes)
    print(f"    Top roots: {dict(roots.most_common(15))}")
    
    # Entropy
    print("\n[7] Computing entropy...")
    entropy, bigram_entropy = compute_entropy_rate(words)
    print(f"    Character entropy: {entropy:.4f} bits")
    print(f"    Bigram entropy: {bigram_entropy:.4f} bits")
    print(f"    Entropy rate estimate: {bigram_entropy - entropy:.4f} bits/char")
    
    # Agglutination index
    print("\n[8] Computing agglutination index...")
    ai = agglutination_index(words, prefixes, suffixes, roots)
    print(f"    Agglutination index: {ai:.4f}")
    if ai > 1.5:
        print("    → Language is highly agglutinative (like Turkish/Finnish)")
    elif ai > 1.2:
        print("    → Language is moderately agglutinative (like Bantu)")
    else:
        print("    → Language is isolating/fusional (like Chinese/English)")
    
    # Transition matrix summary
    print("\n[9] Transition matrix summary...")
    bigrams, trigrams = build_transition_matrix(words)
    
    # Word-initial characters
    initial = Counter()
    for (a, b), c in bigrams.items():
        if a == '^':
            initial[b] += c
    print(f"    Word-initial chars: {dict(initial.most_common(10))}")
    
    # Word-final characters
    final = Counter()
    for (a, b), c in bigrams.items():
        if b == '$':
            final[a] += c
    print(f"    Word-final chars: {dict(final.most_common(10))}")
    
    # Most common transitions
    common_trans = bigrams.most_common(15)
    print(f"    Top transitions: {[(a+'→'+b, c) for (a,b), c in common_trans]}")
    
    # Word signatures
    print("\n[10] Word structure signatures...")
    sig_freq = Counter()
    for w in words:
        sig_freq[word_signature(w)] += 1
    print(f"    Top 15 word signatures (C=consonant, V=vowel, G=gallows):")
    for sig, count in sig_freq.most_common(15):
        print(f"      {sig:12} {count:6}")
    
    # Build output structure
    output = {
        "metadata": {
            "total_words": len(words),
            "unique_words": len(set(words)),
            "decoder": "Voynich Root Structure Decoder v1.0",
        },
        "phonology": {
            "character_entropy_bits": round(entropy, 4),
            "bigram_entropy_bits": round(bigram_entropy, 4),
            "entropy_rate_bits": round(bigram_entropy - entropy, 4),
        },
        "morphology": {
            "agglutination_index": round(ai, 4),
            "top_prefixes": dict(Counter(prefixes).most_common(15)),
            "top_suffixes": dict(Counter(suffixes).most_common(15)),
            "top_roots": dict(roots.most_common(25)),
        },
        "structure": {
            "word_signatures": {sig: count for sig, count in sig_freq.most_common(25)},
            "word_initial": dict(initial.most_common(15)),
            "word_final": dict(final.most_common(15)),
            "top_transitions": [{"from": a, "to": b, "count": c} for (a, b), c in common_trans[:15]],
        },
        "boundaries": {
            "strongest_morpheme_boundaries": [
                {"from": a, "to": b, "pmi": round(score, 4)}
                for (a, b), score in low_pmi
            ]
        }
    }
    
    # Save
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "..", "data", "analysis", "root-structure.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[✓] Output saved to: {output_path}")
    print("=" * 70)
    
    return output

if __name__ == "__main__":
    build_structure()
