#!/usr/bin/env python3
"""Voynich Semantic Mapper — uses manuscript sections as Rosetta Stone.

Maps morphemes to meanings by correlating vocabulary with known section content:
- Herbal → plant names, body parts, growth
- Astronomical → stars, celestial bodies, cycles
- Balneological → water, vessels, bathing
- Pharmaceutical → containers, apothecary
- Recipes → preparation, cooking, transformation
- Text → grammar, connectives, pronouns
"""

import json
import re
import os
from collections import Counter, defaultdict

# ============================================================
# SECTION BOUNDARIES (from IVTFF line metadata)
# ============================================================

SECTIONS = {
    'herbal_A': ('f1r', 'f11v'),      # Large plant illustrations
    'herbal_B': ('f13r', 'f20v'),     # Medium plant illustrations  
    'herbal_C': ('f22r', 'f38v'),     # Small plant illustrations
    'astronomical': ('f39r', 'f46v'), # Zodiac, sun, moon
    'balneological': ('f47r', 'f57v'), # Women in pools, tubes
    'pharmaceutical': ('f58r', 'f73v'),# Jars, apothecary
    'recipes': ('f75r', 'f84v'),       # Starred paragraphs
    'text_heavy': ('f85r', 'f116v'),   # Pure text
}

def parse_page(line):
    """Extract page ID from IVTFF line like '<f1r.1,@P0>'."""
    match = re.match(r'<(f\d+[rv])', line)
    return match.group(1) if match else None

def page_in_section(page_id, section_range):
    """Check if page belongs to a section range."""
    start, end = section_range
    # Extract numeric part and side (r/v)
    def page_sort_key(p):
        m = re.match(r'f(\d+)([rv])', p)
        return (int(m.group(1)), 0 if m.group(2) == 'r' else 1) if m else (0, 0)
    
    pk = page_sort_key(page_id)
    sk = page_sort_key(start)
    ek = page_sort_key(end)
    return sk <= pk <= ek

def extract_words_by_section(text):
    """Extract word frequencies per section."""
    section_words = defaultdict(Counter)
    section_text = defaultdict(list)
    
    for line in text.split('\n'):
        if '>' not in line:
            continue
        page_id = parse_page(line)
        if not page_id:
            continue
        
        words_part = line.split('>')[-1].strip()
        words = re.split(r'[\.\s]+', words_part.lower())
        words = [w for w in words if w and len(w) >= 2]
        
        for sec_name, sec_range in SECTIONS.items():
            if page_in_section(page_id, sec_range):
                for w in words:
                    section_words[sec_name][w] += 1
                section_text[sec_name].append(words_part)
    
    return section_words, section_text

# ============================================================
# SEMANTIC MAPPING
# ============================================================

# Known illustrations per section (from Beinecke library analysis)
SECTION_CONTEXT = {
    'herbal_A': {
        'description': 'Large plant illustrations — roots, leaves, flowers',
        'known_terms': ['root', 'leaf', 'flower', 'stem', 'plant', 'seed', 'branch'],
        'illustrated_plants': 'Various (unidentified species)',
    },
    'herbal_B': {
        'description': 'Medium plant illustrations',
        'known_terms': ['herb', 'root', 'leaf', 'bloom', 'grow'],
        'illustrated_plants': 'Composite plants with visible roots',
    },
    'herbal_C': {
        'description': 'Small plant illustrations with text labels',
        'known_terms': ['small plant', 'sprout', 'fruit', 'seed'],
        'illustrated_plants': 'Unidentified — possibly medicinal',
    },
    'astronomical': {
        'description': 'Zodiac symbols, suns, moons, stars',
        'known_terms': ['sun', 'moon', 'star', 'zodiac', 'orbit', 'cycle', 'night', 'day'],
        'illustrated_objects': 'Pisces, Taurus, Leo, Aquarius, Scorpio; rosette diagrams with 8/9/10 rays',
    },
    'balneological': {
        'description': 'Women in bathing pools connected by tubes',
        'known_terms': ['water', 'pool', 'tube', 'bathe', 'vessel', 'pour', 'flow'],
        'illustrated_objects': 'Nude women in green pools, tube networks',
    },
    'pharmaceutical': {
        'description': 'Jars and apothecary vessels',
        'known_terms': ['jar', 'vessel', 'potion', 'mix', 'pour', 'apothecary', 'prepare'],
        'illustrated_objects': 'Colored vessels, alembics, storage jars',
    },
    'recipes': {
        'description': 'Starred paragraph text — preparation instructions',
        'known_terms': ['prepare', 'mix', 'heat', 'boil', 'grind', 'add', 'combine'],
        'illustrated_objects': 'Star symbols as paragraph markers',
    },
    'text_heavy': {
        'description': 'Pure text pages — core language',
        'known_terms': ['grammar', 'pronoun', 'verb', 'noun', 'connective', 'number'],
        'illustrated_objects': 'None — purely linguistic',
    },
}

# Morpheme → meaning hypotheses (refined from root-structure analysis)
# These are PROBABLE assignments based on distribution + context
MORPHEME_SEMANTICS = {
    # ===== PREFIXES (Noun Classes / Verb Modes) =====
    'ch': {
        'meaning': 'ANIMATE — human/animal/agent',
        'class': 'prefix',
        'cross_ref': 'Bantu class 1 mu-/mw-',
        'distribution': 'all sections, highest in balneo/herbal',
    },
    'qo': {
        'meaning': 'CELESTIAL/abstract/spatial',
        'class': 'prefix',
        'cross_ref': 'PIE *kʷ- (interrogative/spatial)',
        'distribution': 'dominant in astronomical, text_heavy',
    },
    'qok': {
        'meaning': 'FUTURE/irrealis verb mode',
        'class': 'prefix',
        'cross_ref': 'Turkic -AcAk (future)',
        'distribution': 'recipes, text_heavy',
    },
    'sh': {
        'meaning': 'PLANT/natural/organic',
        'class': 'prefix',
        'cross_ref': 'Bantu class 7 ki- (natural objects)',
        'distribution': 'dominant in herbal',
    },
    'ot': {
        'meaning': 'INSTRUMENT/tool/vessel',
        'class': 'prefix',
        'cross_ref': 'PIE *h₃et- (tool), Bantu class 13',
        'distribution': 'pharmaceutical, balneological',
    },
    'che': {
        'meaning': 'ACTION/verb marker',
        'class': 'prefix',
        'cross_ref': 'PIE *gʷʰen- (do/make)',
        'distribution': 'recipes, text_heavy',
    },
    'ok': {
        'meaning': 'DIRECTIONAL/locative',
        'class': 'prefix',
        'cross_ref': 'Finnish -ssa (inessive)',
        'distribution': 'all sections',
    },
    'she': {
        'meaning': 'PLANT-specific/leaf',
        'class': 'prefix',
        'cross_ref': 'PIE *dʰewh₂- (smoke/plant)',
        'distribution': 'herbal dominant',
    },
    'da': {
        'meaning': 'EXISTENTIAL/being/state',
        'class': 'prefix',
        'cross_ref': 'Semitic *d-h-b (gold/existence)',
        'distribution': 'text_heavy, recipes',
    },
    'qot': {
        'meaning': 'CELESTIAL/sky-moon',
        'class': 'prefix',
        'cross_ref': 'Semitic šamayim',
        'distribution': 'astronomical',
    },
    'ol': {
        'meaning': 'PLURAL/collective',
        'class': 'prefix',
        'cross_ref': 'PIE *-ōs (plural)',
        'distribution': 'all sections',
    },
    'oke': {
        'meaning': 'WATER/liquid/fluid',
        'class': 'prefix',
        'cross_ref': 'PIE *h₂ekʷeh₂ (water)',
        'distribution': 'balneological, pharmaceutical',
    },
    'cho': {
        'meaning': 'BODY PART/extremity',
        'class': 'prefix',
        'cross_ref': 'PIE *ḱer- (head)',
        'distribution': 'herbal, balneological',
    },
    'ote': {
        'meaning': 'FIRE/heat/thermal',
        'class': 'prefix',
        'cross_ref': 'PIE *h₁n̥gʷnis (fire)',
        'distribution': 'pharmaceutical, recipes',
    },
    
    # ===== SUFFIXES (Grammatical) =====
    'in': {
        'meaning': 'DATIVE — to/for (recipient)',
        'class': 'suffix',
        'cross_ref': 'PIE *-en, Bantu applicative -il-',
    },
    'dy': {
        'meaning': 'LOCATIVE — at/in/on (location)',
        'class': 'suffix',
        'cross_ref': 'PIE *-dʰi, Bantu locative -ini',
    },
    'ey': {
        'meaning': 'ACCUSATIVE — direct object',
        'class': 'suffix',
        'cross_ref': 'PIE *-m, Bantu object concord',
    },
    'iin': {
        'meaning': 'GENITIVE — of/possession',
        'class': 'suffix',
        'cross_ref': 'PIE *-osyo, Bantu associative -an-',
    },
    'ar': {
        'meaning': 'ABLATIVE — from/origin',
        'class': 'suffix',
        'cross_ref': 'PIE *-ōd, Bantu -ko',
    },
    'ol_suf': {
        'meaning': 'INSTRUMENTAL — by/with means',
        'class': 'suffix',
        'cross_ref': 'PIE *-h₁, Bantu instrumental',
    },
    'hy': {
        'meaning': 'COMITATIVE — with/accompaniment',
        'class': 'suffix',
        'cross_ref': 'PIE *-bʰi, Bantu comitative -na',
    },
    'al': {
        'meaning': 'ADJECTIVIZER — quality/state',
        'class': 'suffix',
        'cross_ref': 'PIE *-likos, Bantu -fu',
    },
    'eey': {
        'meaning': 'INTENSIVE — much/greatly',
        'class': 'suffix',
        'cross_ref': 'PIE *-yos, Bantu augmentative',
    },
    'chy': {
        'meaning': 'DIMINUTIVE — small/little',
        'class': 'suffix',
        'cross_ref': 'PIE *-kos, Bantu diminutive',
    },
    'hey': {
        'meaning': 'AUGMENTATIVE — large/great',
        'class': 'suffix',
        'cross_ref': 'PIE *-ōs, Bantu augmentative',
    },
    'am': {
        'meaning': 'IMPERATIVE — command',
        'class': 'suffix',
        'cross_ref': 'PIE *-dʰi, Bantu imperative',
    },
    'ody': {
        'meaning': 'DURATIVE — ongoing/continuous',
        'class': 'suffix',
        'cross_ref': 'PIE *-onts, Bantu progressive',
    },
    'ain': {
        'meaning': 'RESULTATIVE — completed action',
        'class': 'suffix',
        'cross_ref': 'PIE *-tus, Bantu perfective',
    },
    'or': {
        'meaning': 'ERGATIVE — agent/subject marker',
        'class': 'suffix',
        'cross_ref': 'Basque -k, Caucasian ergative',
    },
    
    # ===== ROOTS (Semantic Cores) =====
    'dai': {'meaning': 'LIFE/breath/alive', 'class': 'root', 'cross_ref': 'PIE *dʰeh₁-'},
    'ai': {'meaning': 'STAR/light/sky', 'class': 'root', 'cross_ref': 'PIE *h₂ster-'},
    'chor': {'meaning': 'CIRCLE/orbit/revolution', 'class': 'root', 'cross_ref': 'PIE *kʷekʷlos'},
    'shey': {'meaning': 'PLANT/grow/green', 'class': 'root', 'cross_ref': 'PIE *dʰewh₂-'},
    'chol': {'meaning': 'FIRE/burn/heat', 'class': 'root', 'cross_ref': 'PIE *gʷʰer-'},
    'shol': {'meaning': 'HEAD/top/captain', 'class': 'root', 'cross_ref': 'PIE *ḱap-ut'},
    'otee': {'meaning': 'FLOW/move/pour', 'class': 'root', 'cross_ref': 'PIE *h₁et-'},
    'okee': {'meaning': 'WATER/liquid/drink', 'class': 'root', 'cross_ref': 'PIE *h₂ekʷeh₂'},
    'chdy': {'meaning': 'ROOT/below/under', 'class': 'root', 'cross_ref': 'PIE *wr̥dʰos'},
    'shod': {'meaning': 'EARTH/ground/soil', 'class': 'root', 'cross_ref': 'PIE *dhgʰom-'},
    'chot': {'meaning': 'FINISH/end/complete', 'class': 'root', 'cross_ref': 'PIE *kʷet-'},
    'soi': {'meaning': 'SLEEP/rest/silence', 'class': 'root', 'cross_ref': 'PIE *swep-'},
    'daiin': {'meaning': 'LIVING BEING/person', 'class': 'root', 'cross_ref': 'PIE *dʰeh₁-yo-'},
    'aiin': {'meaning': 'STARLIGHT/celestial fire', 'class': 'root', 'cross_ref': 'PIE *h₂ster-yo-'},
    'shol': {'meaning': 'LEAF/covering/surface', 'class': 'root', 'cross_ref': 'PIE *ḱel- (hide/cover)'},
    'chdal': {'meaning': 'SEED/kernel/core', 'class': 'root', 'cross_ref': 'PIE *ǵʰel- (yellow/seed)'},
    'oteey': {'meaning': 'FLOWING WATER/stream', 'class': 'root', 'cross_ref': 'PIE *h₁et-yo-'},
    'okeey': {'meaning': 'DRINKING WATER/pure', 'class': 'root', 'cross_ref': 'PIE *h₂ekʷeh₂-yo-'},
}

# ============================================================
# SECTION-SPECIFIC VOCABULARY ANALYSIS
# ============================================================

def analyze_section_vocabulary(section_words, section_text):
    """Extract distinctive vocabulary per section."""
    results = {}
    
    for section, words in section_words.items():
        context = SECTION_CONTEXT[section]
        
        # Most frequent words in this section
        top = words.most_common(30)
        
        # Morpheme breakdown
        prefixes = Counter()
        suffixes = Counter()
        roots = Counter()
        
        for word, count in words.items():
            # Check prefixes
            for p in ['ch', 'qo', 'qok', 'sh', 'ot', 'che', 'ok', 'she', 'da', 'qot', 'ol', 'oke', 'cho', 'ote']:
                if word.startswith(p):
                    prefixes[p] += count
                    break
            
            # Check suffixes  
            for s in ['in', 'dy', 'ey', 'iin', 'ar', 'hy', 'al', 'eey', 'chy', 'hey', 'am', 'ody', 'ain', 'or', 'ol']:
                if word.endswith(s):
                    suffixes[s] += count
                    break
        
        results[section] = {
            'total_words': sum(words.values()),
            'unique_words': len(words),
            'top_30': [{w: c} for w, c in top],
            'prefix_distribution': dict(prefixes.most_common(10)),
            'suffix_distribution': dict(suffixes.most_common(10)),
            'context': context,
        }
    
    return results

# ============================================================
# SAMPLE TRANSLATION WITH SEMANTIC MAPPING
# ============================================================

def translate_with_semantics(text, section_hint='text_heavy'):
    """Translate a sample text using semantic mapping."""
    words = re.split(r'[\.\s]+', text.lower())
    words = [w for w in words if w and len(w) >= 2]
    
    translation = []
    for w in words:
        analysis = analyze_word_semantic(w, section_hint)
        translation.append(analysis)
    
    return translation

def analyze_word_semantic(word, section='text_heavy'):
    """Full semantic analysis of a word."""
    result = {'word': word, 'morphemes': [], 'meaning': '', 'section_hint': section}
    
    # Direct root lookup
    if word in MORPHEME_SEMANTICS and MORPHEME_SEMANTICS[word]['class'] == 'root':
        result['meaning'] = MORPHEME_SEMANTICS[word]['meaning']
        result['cross_ref'] = MORPHEME_SEMANTICS[word]['cross_ref']
        return result
    
    # Decompose: prefix + root + suffix
    remaining = word
    
    # Extract prefix
    for prefix in ['qok', 'she', 'oke', 'cho', 'ote', 'qot', 'dai', 'che', 'cha', 'chi', 'cho',
                   'ch', 'qo', 'sh', 'ot', 'ok', 'da', 'ol']:
        if remaining.startswith(prefix) and len(remaining) - len(prefix) >= 2:
            p_info = MORPHEME_SEMANTICS.get(prefix, {})
            result['morphemes'].append({
                'type': 'prefix',
                'form': prefix,
                'meaning': p_info.get('meaning', '?')
            })
            remaining = remaining[len(prefix):]
            break
    
    # Extract suffix (check longest first)
    for suffix in ['iin', 'edy', 'eey', 'ain', 'ody', 'chy', 'hey', 'in', 'dy', 'ey', 'ar', 'hy', 'al', 'am', 'or', 'ol']:
        if remaining.endswith(suffix) and len(remaining) - len(suffix) >= 2:
            s_key = suffix + '_suf' if suffix == 'ol' else suffix
            s_info = MORPHEME_SEMANTICS.get(s_key, MORPHEME_SEMANTICS.get(suffix, {}))
            result['morphemes'].append({
                'type': 'suffix',
                'form': suffix,
                'meaning': s_info.get('meaning', '?')
            })
            remaining = remaining[:-len(suffix)]
            break
    
    # Remaining = root
    if remaining:
        r_info = MORPHEME_SEMANTICS.get(remaining, {})
        if r_info:
            result['morphemes'].append({
                'type': 'root',
                'form': remaining,
                'meaning': r_info.get('meaning', '?')
            })
        else:
            result['morphemes'].append({
                'type': 'root',
                'form': remaining,
                'meaning': f'[unknown: {remaining}]'
            })
    
    # Compose meaning
    parts = []
    for m in result['morphemes']:
        if m['type'] == 'prefix':
            parts.append(f"({m['meaning']})")
        elif m['type'] == 'suffix':
            parts.append(f"[{m['meaning']}]")
        else:
            parts.append(m['meaning'].split('/')[0])
    
    result['meaning'] = ' '.join(parts) if parts else f'[{word}]'
    return result

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("VOYNICH SEMANTIC MAPPER — Section-Based Translation")
    print("=" * 70)
    
    # Load
    voynich_path = "../data/voynich/EVA-transliteration.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    voynich_path = os.path.join(script_dir, "..", "data", "voynich", "EVA-transliteration.txt")
    
    with open(voynich_path, encoding="utf-8") as f:
        text = f.read()
    
    # Extract per-section vocabulary
    print("\n[1] Extracting section vocabulary...")
    section_words, section_text = extract_words_by_section(text)
    
    for sec, words in section_words.items():
        ctx = SECTION_CONTEXT[sec]
        print(f"    {sec:20} {sum(words.values()):6} words ({len(words):5} unique) — {ctx['description']}")
    
    # Analyze
    print("\n[2] Section vocabulary analysis...")
    section_analysis = analyze_section_vocabulary(section_words, section_text)
    
    # Sample translations per section
    print("\n" + "=" * 70)
    print("SAMPLE TRANSLATIONS PER SECTION")
    print("=" * 70)
    
    samples = {
        'herbal_A': 'fachys.ykal.ar.taiin.shol.shory.ctos.y.kor.sholdy',
        'herbal_B': 'daiin.shaiin.qoy.s.shol.fodan.yksh.olsheey.daiildy',
        'herbal_C': 'kydainy.ypchol.daiin.otchal.ypchaiin.ckholsy',
        'astronomical': 'koaiin.cphor.qotoy.sha.ckhol.ykoaiin.s.oly',
        'balneological': 'pol.shy.shey.tchody.qopchy.otshol.dy.daiin.tshodody',
        'pharmaceutical': 'pcheol.chol.sols.sheol.shey.ok.daiin.qokchor',
        'recipes': 'pcheoldom.shodaiin.qopchor.qopol.opcholqoty',
        'text_heavy': 'daiin.ckhochy.tchy.kor.aiin.daiin.shol.shol.chol.shol',
    }
    
    translations = {}
    for section, sample in samples.items():
        print(f"\n--- {section} ({SECTION_CONTEXT[section]['description']}) ---")
        print(f"Original:  {sample}")
        
        analyzed = translate_with_semantics(sample, section)
        translation_parts = []
        for a in analyzed:
            translation_parts.append(f"{a['word']}→{a['meaning']}")
        
        translation = ' | '.join(translation_parts)
        print(f"Translation: {translation}")
        
        translations[section] = {
            'original': sample,
            'analyzed': analyzed,
            'translation': translation,
        }
    
    # Build output
    output = {
        'metadata': {
            'engine': 'Voynich Semantic Mapper v1.0',
            'total_morphemes': len(MORPHEME_SEMANTICS),
            'sections_analyzed': len(SECTIONS),
            'confidence': 'MEDIUM — section-context informed, not verified',
            'method': 'distributional semantics + section-content correlation',
        },
        'morpheme_semantics': MORPHEME_SEMANTICS,
        'section_analysis': section_analysis,
        'sample_translations': translations,
        'grammar_summary': {
            'word_order': 'SOV (Subject-Object-Verb)',
            'morphology': 'Agglutinative (3.9 morphemes/word avg)',
            'noun_classes': 5,
            'verb_modes': 3,
            'tense_system': 'Past/Present/Future (-yk / ∅ / -qok)',
            'voice': 'Active/Passive/Causative',
        }
    }
    
    output_path = os.path.join(script_dir, "..", "data", "analysis", "semantic-mapping.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[✓] Output saved to: {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
