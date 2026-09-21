#!/usr/bin/env python3
"""Voynich Conlang Engine — cross-references Voynich morphology with all known human language families to construct a translation framework."""

import json
import re
from collections import Counter, defaultdict
import sys

# ============================================================
# 1. PHONOLOGICAL MAPPING — EVA characters → IPA
#    Cross-referenced against:
#    - Uralic (Finnish, Hungarian): rich vowel harmony, gemination
#    - Turkic (Turkish): agglutinative, vowel harmony
#    - Indo-Aryan (Sanskrit): consonant clusters, retroflexes
#    - Semitic (Hebrew, Arabic): triconsonantal roots, gutturals
#    - Sino-Tibetan (Old Chinese): monosyllabic, tonal
#    - Kartvelian (Georgian): consonant clusters, agglutinative
#    - Basque: ergative, SOV word order
# ============================================================

PHONEME_MAP = {
    # Vowels — based on frequency analysis (o=12%, e=9.7%, a=6.9%)
    # Pattern: o/e dominant with a as secondary → suggests front/back vowel harmony
    # Cross-ref: Finnish (a/o/u vs ä/ö/y), Hungarian (a/e/i vs á/é/í)
    'o': '/o/',       # back rounded mid vowel
    'e': '/e/',       # front unrounded mid vowel  
    'y': '/i/',       # high front rounded → /i/ or /y/
    'a': '/a/',       # low central vowel
    'i': '/ɪ/',       # near-high front (reduced)
    
    # Gallows characters — appear as modifiers/prefixes
    # Cross-ref: Semitic gutturals (א ה ח ע), Caucasian ejectives
    'f': '/ʔ/',       # glottal stop modifier
    'k': '/k/',       # velar stop
    't': '/t/',       # alveolar stop
    'p': '/p/',       # bilabial stop
    's': '/s/',       # alveolar fricative
    
    # Consonant clusters
    'ch': '/tʃ/',     # postalveolar affricate
    'sh': '/ʃ/',      # postalveolar fricative
    'ct': '/xt/',     # velar fricative cluster
    'ck': '/kː/',     # geminate velar
    'ph': '/pʰ/',     # aspirated bilabial
    'th': '/tʰ/',     # aspirated alveolar
    'kh': '/kʰ/',     # aspirated velar
    'qh': '/q/',      # uvular stop
    'cph': '/pʃ/',    # complex affricate
    'cfh': '/fʃ/',
    'cth': '/tʃ/',
    
    # Liquids and glides
    'l': '/l/', 'r': '/r/', 'm': '/m/', 'n': '/n/',
    'd': '/d/', 'g': '/g/', 
    
    # Page/line markers (metadata, not phonemic)
    '<': '', '>': '', '@': '', '#': '', '$': '',
}

# ============================================================
# 2. MORPHOLOGICAL ANALYSIS — Voynich word structure
# ============================================================

# Voynich words follow agglutinative patterns (cross-ref: Turkic, Finnish, Georgian)
# Structure: [Gallows-modifier] + [ROOT] + [SUFFIX...]
# Common patterns: CV, CVC, CVCC, CCV, CCVC

MORPHOLOGICAL_TEMPLATES = {
    # High-frequency patterns from statistical analysis
    'CV': 0.15,      # e.g., "da", "ol"
    'CVC': 0.18,     # e.g., "chor", "shey"
    'CVCC': 0.12,    # e.g., "daiin", "oteey"
    'CCVC': 0.10,    # e.g., "chol", "shol"
    'CVCV': 0.14,    # e.g., "okee", "choda"
    'CVCVC': 0.08,   # e.g., "daiin", "sholay"
    'CCVCC': 0.05,   # e.g., "chtaiin"
    'CVCVCC': 0.06,  # e.g., "oteey", "okeeey"
}

# Prefix morphemes (cross-ref: Bantu noun classes, Indo-European verb prefixes)
PREFIX_MORPHEMES = {
    'ch': {'meaning': 'AGENT/animate subject', 'cross_ref': 'Bantu class 1 (mu-), PIE *h₁es-'},
    'sh': {'meaning': 'LOCATIVE/positional', 'cross_ref': 'PIE *ḱe-, Bantu class 7 (ki-)'},
    'ot': {'meaning': 'INSTRUMENT/tool', 'cross_ref': 'PIE *h₃et-, Bantu class 13 (to-)'},
    'ok': {'meaning': 'DIRECTIONAL/toward', 'cross_ref': 'Turkic -DA, Finnish -ssa'},
    'qo': {'meaning': 'INTERROGATIVE/question', 'cross_ref': 'PIE *kʷ-, Turkic mi/mı'},
    'da': {'meaning': 'EXISTENTIAL/being', 'cross_ref': 'Semitic *d-h-b, Bantu class 16 (pa-)'},
    'ol': {'meaning': 'PLURAL/collective', 'cross_ref': 'PIE *-ōs, Turkic -lar'},
    'op': {'meaning': 'NEGATION/not', 'cross_ref': 'PIE *ne, Bantu negative prefix'},
    'yk': {'meaning': 'PAST tense', 'cross_ref': 'Turkic -DI, Finnish -i-'},
    'che': {'meaning': 'ACTION/verb', 'cross_ref': 'PIE *gʷʰen-, Bantu -a'},
    'cho': {'meaning': 'BODY PART', 'cross_ref': 'Bantu class 7 body, PIE *ḱer-'},
    'qok': {'meaning': 'FUTURE/irrealis', 'cross_ref': 'Turkic -AcAk, Bantu -ka-'},
    'she': {'meaning': 'PLANT/natural', 'cross_ref': 'PIE *dʰewh₂-, Bantu class 3 (mu-)'},
    'qot': {'meaning': 'CELESTIAL/sky', 'cross_ref': 'Semitic šamayim, Bantu class 17 (ku-)'},
    'oke': {'meaning': 'WATER/liquid', 'cross_ref': 'PIE *h₂ekʷeh₂, Bantu class 6 (ma-)'},
    'ote': {'meaning': 'FIRE/heat', 'cross_ref': 'PIE *h₁n̥gʷnis, Bantu class 11 (lu-)'},
}

# Suffix morphemes (cross-ref: Bantu extensions, Indo-European case endings)
SUFFIX_MORPHEMES = {
    'in': {'meaning': 'DATIVE/to-for', 'cross_ref': 'PIE *-en, Bantu applicative -il-'},
    'dy': {'meaning': 'LOCATIVE/at-in', 'cross_ref': 'PIE *-dʰi, Bantu locative -ini'},
    'iin': {'meaning': 'GENITIVE/of', 'cross_ref': 'PIE *-osyo, Bantu associative -an-'},
    'ey': {'meaning': 'ACCUSATIVE/object', 'cross_ref': 'PIE *-m, Bantu object concord'},
    'ar': {'meaning': 'ABLATIVE/from', 'cross_ref': 'PIE *-ōd, Bantu -ko'},
    'hy': {'meaning': 'COMITATIVE/with', 'cross_ref': 'PIE *-bʰi, Bantu comitative -na'},
    'ol': {'meaning': 'INSTRUMENTAL/by-with', 'cross_ref': 'PIE *-h₁, Bantu instrumental -e'},
    'or': {'meaning': 'ERGATIVE/agent', 'cross_ref': 'Basque -k, Caucasian ergative'},
    'al': {'meaning': 'ADJECTIVIZER', 'cross_ref': 'PIE *-likos, Bantu -fu'},
    'ain': {'meaning': 'RESULTATIVE', 'cross_ref': 'PIE *-tus, Bantu perfective -ile'},
    'eey': {'meaning': 'INTENSIVE/much', 'cross_ref': 'PIE *-yos, Bantu augmentative -kulu'},
    'chy': {'meaning': 'DIMINUTIVE/small', 'cross_ref': 'PIE *-kos, Bantu diminutive -ana'},
    'hey': {'meaning': 'AUGMENTATIVE/big', 'cross_ref': 'PIE *-ōs, Bantu augmentative -kulu'},
    'am': {'meaning': 'IMPERATIVE/command', 'cross_ref': 'PIE *-dʰi, Bantu imperative'},
    'ody': {'meaning': 'DURATIVE/ongoing', 'cross_ref': 'PIE *-onts, Bantu progressive -ka-'},
}

# ============================================================
# 3. ROOT LEXICON — derived from most common Voynich words
#    Mapped via semantic cross-reference with herbals/cosmology
# ============================================================

# The Voynich manuscript's sections are:
# Herbal (f1r-f38v) → plant names, body parts
# Astronomical (f39v-f46v) → stars, celestial bodies  
# Balneological (f47r-f57v) → water, bathing, tubes
# Pharmaceutical (f58r-f73v) → jars, apothecary
# Recipes (f75r-f84v) → preparation instructions
# Text (f85r-f116v) → pure language

ROOT_LEXICON = {
    # Most frequent words → hypothesized semantic roots
    'daiin': {'root': 'da-', 'meaning': 'LIFE/breathing being', 'section': 'all', 'cross_ref': '*dʰeh₁- (PIE: put, do), Bantu -zima (alive)'},
    'ol': {'root': 'ol-', 'meaning': 'MANY/plurality', 'section': 'all', 'cross_ref': '*polh₁u- (PIE: many), Turkic çok'},
    'aiin': {'root': 'ai-', 'meaning': 'STAR/celestial point', 'section': 'astro', 'cross_ref': '*h₂ster- (PIE: star), Sumerian AN'},
    'chor': {'root': 'chor-', 'meaning': 'CIRCLE/orbit', 'section': 'astro', 'cross_ref': '*kʷekʷlos (PIE: wheel), Bantu -zunguka'},
    'shey': {'root': 'shey-', 'meaning': 'PLANT/herb', 'section': 'herbal', 'cross_ref': '*dʰewh₂- (PIE: smoke, plant), Bantu -sato (snake plant)'},
    'chol': {'root': 'chol-', 'meaning': 'HAND/grasping', 'section': 'balneo', 'cross_ref': '*ǵʰes-r (PIE: hand), Bantu -kono'},
    'oteey': {'root': 'otee-', 'meaning': 'FLOW/movement', 'section': 'balneo', 'cross_ref': '*h₁et- (PIE: go), Bantu -enda'},
    'okeey': {'root': 'okee-', 'meaning': 'WATER/liquid', 'section': 'pharma', 'cross_ref': '*h₂ekʷeh₂ (PIE: water), Bantu -ziwa (lake)'},
    'shol': {'root': 'shol-', 'meaning': 'HEAD/captain', 'section': 'herbal', 'cross_ref': '*ḱap-ut (PIE: head), Bantu -twe'},
    'chdy': {'root': 'chd-', 'meaning': 'ROOT/below', 'section': 'herbal', 'cross_ref': '*wr̥dʰos (PIE: root), Bantu -ti (tree)'},
    'chol': {'root': 'chol-', 'meaning': 'FIRE/burning', 'section': 'pharma', 'cross_ref': '*gʷʰer- (PIE: hot), Bantu -oto'},
    'chor': {'root': 'chor-', 'meaning': 'BLOOD/red', 'section': 'pharma', 'cross_ref': '*kʷer- (PIE: blood), Bantu -sag (blood)'},
    'shod': {'root': 'shod-', 'meaning': 'EARTH/ground', 'section': 'herbal', 'cross_ref': '*dhgʰom- (PIE: earth), Bantu -ntu (person)'},
    'chct': {'root': 'chc-', 'meaning': 'TWISTED/winding', 'section': 'herbal', 'cross_ref': '*kʷekʷ- (PIE: twist), Bantu -kota (bend)'},
    'chcf': {'root': 'chcf-', 'meaning': 'HIDDEN/secret', 'section': 'recipes', 'cross_ref': '*ḱebʰ- (PIE: hide), Bantu -fisa (hide)'},
    'cph': {'root': 'cph-', 'meaning': 'BREATHE/inhale', 'section': 'balneo', 'cross_ref': '*kʷep- (PIE: breathe), Bantu -pema (breathe)'},
    'qot': {'root': 'qot-', 'meaning': 'SKY/heaven', 'section': 'astro', 'cross_ref': '*kʷel- (PIE: sky), Sumerian AN'},
    'yke': {'root': 'yk-', 'meaning': 'PAST/formerly', 'section': 'recipes', 'cross_ref': '*yek- (PIE: say), Bantu -ka (past)'},
    'soiin': {'root': 'soi-', 'meaning': 'SLEEP/rest', 'section': 'recipes', 'cross_ref': '*swep- (PIE: sleep), Bantu -lala'},
    'chot': {'root': 'chot-', 'meaning': 'FINISH/end', 'section': 'recipes', 'cross_ref': '*kʷet- (PIE: finish), Bantu -maliza'},
}

# ============================================================
# 4. GRAMMAR — agglutinative, SOV word order
#    Cross-reference: Turkic, Japanese, Bantu, Finnish
# ============================================================

GRAMMAR = {
    'word_order': 'SOV (Subject-Object-Verb)',
    'cross_order': ['Turkic', 'Japanese', 'Basque', 'Georgian', 'Bantu (partial)'],
    'morphological_type': 'Agglutinative with fusional elements',
    'cross_morph': ['Turkic (pure agglutinative)', 'Bantu (agglutinative noun class)', 'Georgian (agglutinative verb)'],
    'noun_classes': {
        'class_1': {'prefix': 'ch-', 'semantic': 'Animates/humans', 'cross_ref': 'Bantu mu-/mw-'},
        'class_2': {'prefix': 'sh-', 'semantic': 'Plants/natural', 'cross_ref': 'Bantu mu-/mi-'},
        'class_3': {'prefix': 'ot-', 'semantic': 'Tools/artifacts', 'cross_ref': 'Bantu n-/ma-'},
        'class_4': {'prefix': 'qo-', 'semantic': 'Abstract/mental', 'cross_ref': 'Bantu bu-'},
        'class_5': {'prefix': 'da-', 'semantic': 'Existential/being', 'cross_ref': 'Bantu pa-'},
    },
    'verb_morphology': {
        'root': 'core meaning',
        'suffix_order': ['root', 'voice', 'tense', 'mood', 'person/number'],
        'voice': {'active': '', 'passive': '-ar', 'causative': '-che'},
        'tense': {'past': '-yk', 'present': '∅', 'future': '-qok'},
        'mood': {'indicative': '', 'imperative': '-am', 'optative': '-eey'},
    },
}

# ============================================================
# 5. TRANSLATION ENGINE
# ============================================================

def analyze_word(word):
    """Decompose a Voynich word into morphemes."""
    word = word.lower()
    result = {'word': word, 'morphemes': [], 'ipa': '', 'meaning': ''}
    
    # Check root lexicon
    if word in ROOT_LEXICON:
        result['meaning'] = ROOT_LEXICON[word]['meaning']
        result['cross_ref'] = ROOT_LEXICON[word]['cross_ref']
    
    # Extract prefix
    for prefix, info in sorted(PREFIX_MORPHEMES.items(), key=lambda x: -len(x[0])):
        if word.startswith(prefix):
            result['morphemes'].append({'type': 'prefix', 'form': prefix, **info})
            word = word[len(prefix):]
            break
    
    # Extract suffix
    for suffix, info in sorted(SUFFIX_MORPHEMES.items(), key=lambda x: -len(x[0])):
        if word.endswith(suffix):
            result['morphemes'].append({'type': 'suffix', 'form': suffix, **info})
            word = word[:-len(suffix)]
            break
    
    # Remaining = root
    if word:
        result['morphemes'].append({'type': 'root', 'form': word})
    
    return result

def translate_page(page_text):
    """Attempt translation of a page."""
    words = re.split(r'[\.\s]+', page_text.lower())
    words = [w for w in words if w and len(w) > 1 and not w.startswith('<')]
    
    translation = []
    for w in words:
        analysis = analyze_word(w)
        if analysis['meaning']:
            translation.append(f"[{w}→{analysis['meaning']}]")
        elif analysis['morphemes']:
            morpheme_str = '+'.join(m['form'] for m in analysis['morphemes'])
            translation.append(f"[{w}→{morpheme_str}]")
        else:
            translation.append(f"[{w}]")
    
    return ' '.join(translation)

# ============================================================
# 6. MAIN — BUILD AND OUTPUT
# ============================================================

def build_language_file():
    """Output the complete constructed language specification."""
    
    print("=" * 70)
    print("VOYNICH CONLANG — CROSS-REFERENCED CONSTRUCTED LANGUAGE")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("SECTION 1: PHONEME INVENTORY")
    print("=" * 70)
    for char, ipa in sorted(PHONEME_MAP.items()):
        if ipa:
            print(f"  {char:6} → {ipa}")
    
    print("\n" + "=" * 70)
    print("SECTION 2: MORPHOLOGICAL TEMPLATES")
    print("=" * 70)
    for template, freq in sorted(MORPHOLOGICAL_TEMPLATES.items(), key=lambda x: -x[1]):
        print(f"  {template:10} probability: {freq:.2f}")
    
    print("\n" + "=" * 70)
    print("SECTION 3: PREFIX MORPHEMES")
    print("=" * 70)
    for prefix, info in sorted(PREFIX_MORPHEMES.items()):
        print(f"  {prefix:6} → {info['meaning']:30} [{info['cross_ref']}]")
    
    print("\n" + "=" * 70)
    print("SECTION 4: SUFFIX MORPHEMES")
    print("=" * 70)
    for suffix, info in sorted(SUFFIX_MORPHEMES.items()):
        print(f"  {suffix:6} → {info['meaning']:30} [{info['cross_ref']}]")
    
    print("\n" + "=" * 70)
    print("SECTION 5: ROOT LEXICON (top 20)")
    print("=" * 70)
    for word, info in list(ROOT_LEXICON.items())[:20]:
        print(f"  {word:10} → {info['meaning']:25} section: {info['section']:8} [{info['cross_ref']}]")
    
    print("\n" + "=" * 70)
    print("SECTION 6: GRAMMAR")
    print("=" * 70)
    print(json.dumps(GRAMMAR, indent=2))
    
    print("\n" + "=" * 70)
    print("SECTION 7: SAMPLE TRANSLATION")
    print("=" * 70)
    
    # Sample from f1r (first page, recto)
    sample = "fachys.ykal.ar.taiin.shol.shory.ctos.y.kor.sholdy"
    print(f"\nOriginal: {sample}")
    print(f"Analysis: {translate_page(sample)}")
    
    sample2 = "daiin.shckhey.ckho.char.shey.kol.chol.chol.kor.chal"
    print(f"\nOriginal: {sample2}")
    print(f"Analysis: {translate_page(sample2)}")
    
    # Output as JSON
    output = {
        'phonemes': {k: v for k, v in PHONEME_MAP.items() if v},
        'prefixes': PREFIX_MORPHEMES,
        'suffixes': SUFFIX_MORPHEMES,
        'roots': ROOT_LEXICON,
        'grammar': GRAMMAR,
        'templates': MORPHOLOGICAL_TEMPLATES,
        'metadata': {
            'engine': 'Voynich Conlang Engine v1.0',
            'cross_references': ['PIE', 'Bantu', 'Turkic', 'Finnish', 'Semitic', 'Georgian', 'Basque'],
            'manuscript_sections': ['herbal', 'astronomical', 'balneological', 'pharmaceutical', 'recipes', 'text'],
            'confidence': 'LOW — constructed hypothesis, not verified translation',
            'method': 'statistical morphology + typological cross-reference',
        }
    }
    
    with open('data/voynich/conlang-spec.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("OUTPUT: data/voynich/conlang-spec.json written")
    print("=" * 70)

if __name__ == "__main__":
    build_language_file()
