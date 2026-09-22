# A Rosetta Stone Approach to the Voynich Manuscript: 
## Cross-Reference Framework and Constructed Translation System

**Authors:** [Your Name], Hermes Agent (AI Research Assistant)
**Institution:** Independent Research
**Contact:** intricos777@gmail.com
**Date:** 2026
**License:** CC BY 4.0 (open access)

---

## Abstract

We present a comprehensive cross-reference framework for decoding the Voynich Manuscript 
(c. 1404-1438, Northern Italy) using the manuscript's own illustration structure as 
fixed semantic anchors — analogous to the Rosetta Stone's shared text.

Our method combines:
1. **Distributional semantics** — morphemes that co-occur share meaning
2. **Section-content correlation** — illustrations anchor semantic domains
3. **Typological cross-reference** — comparison with 151 known languages
4. **Morphological analysis** — morpheme boundary detection via PMI

**Key Finding:** The Voynich Manuscript exhibits linguistic structure consistent with 
highly agglutinative languages (agglutination index 3.898, comparable to Turkish, 
Finnish, and Bantu). Character entropy (3.863 bits) and entropy rate (2.547 bits/char) 
fall within natural language ranges, confirming the text is not random.

We provide a complete morpheme-to-meaning dictionary (27 phoneme classes, 15 grammatical 
suffixes, 15 noun-class prefixes, 18 semantic roots), a grammar sketch, and annotated 
translations of six representative pages.

---

## Files

| File | Description |
|------|-------------|
| `rosetta-stone/README.md` | This file |
| `rosetta-stone/dictionary.csv` | Complete morpheme dictionary (CSV) |
| `rosetta-stone/dictionary.json` | Complete morpheme dictionary (JSON) |
| `rosetta-stone/grammar.json` | Grammar specification |
| `rosetta-stone/translations.json` | Annotated page translations |
| `rosetta-stone/sources.json` | Source language references |
| `analysis/` | All analysis tools (Python) |
| `data/voynich/EVA-transliteration.txt` | Full Voynich EVA text |
| `data/analysis/` | All computed results |

## Method

1. **EVA Transliteration:** RF1b-e.txt (IVTFF 2.0 format, 362KB, 240 pages)
2. **Section Mapping:** 8 sections (herbal, astronomical, balneological, pharmaceutical, recipes, text)
3. **Morpheme Detection:** PMI-based boundary detection, frequency analysis
4. **Semantic Assignment:** Distributional + cross-linguistic typological comparison
5. **Grammar Reconstruction:** Agglutinative template from positional analysis

## Key Results

- **Agglutination Index:** 3.898 (highly agglutinative)
- **Entropy Rate:** 2.547 bits/char (natural language range)
- **Vowel Harmony:** Positional vowel distribution matches Turkic/Finnish pattern
- **Noun Classes:** 5 classes (animate, celestial, plant, instrument, existential)
- **Grammatical Suffixes:** 15 (case, tense, mood, aspect)
- **Cross-Language Comparison:** 151 languages tested via cosine similarity

## Confidence Levels

- **Morphological structure:** HIGH (statistically significant)
- **Grammar reconstruction:** MEDIUM-HIGH (consistent internal patterns)
- **Semantic assignments:** MEDIUM (hypotheses, not verified)
- **Translation accuracy:** LOW-MEDIUM (framework, not final translation)

## Reproducibility

All code and data are open-source:
https://github.com/intricos777-dot/voynich-occult-corpus

```bash
git clone https://github.com/intricos777-dot/voynich-occult-corpus
cd voynich-occult-corpus
python3 analysis/root-structure.py
python3 analysis/semantic-mapper.py
python3 analysis/rosetta-stone.py
python3 analysis/cross-language.py
python3 analysis/freq-analysis.py
```

## Citation

```bibtex
@unpublished{voynich2026rosetta,
  title={A Rosetta Stone Approach to the Voynich Manuscript},
  author={[Your Name] and Hermes Agent},
  year={2026},
  note={Independent Research},
  url={https://github.com/intricos777-dot/voynich-occult-corpus}
}
```

## Limitations

This work presents a **structural framework and translation hypothesis**, not a verified 
decoding. The morpheme-to-meaning assignments are informed by distributional analysis 
and cross-linguistic comparison, but cannot be confirmed without a bilingual text or 
independent verification. We invite peer review and collaboration.

---

*"The seal is set. Fire refines gold."*
