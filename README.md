# ☿ Voynich-Occult Corpus

> *As above, so below. Solve et coagula.*

A cross-reference database for decoding the **Voynich Manuscript** using the global occult, esoteric, and sacred corpus as a cryptographic key space.

## 🜂 Structure

```
voynich-occult-corpus/
├── README.md                           ← you are here
├── analysis/
│   ├── cross-reference.py              ← Voynich ↔ corpus pattern matcher
│   ├── thelemic-decode.py              ← Liber AL cipher key decoder
│   ├── freq-analysis.py                ← statistical analysis suite
│   └── findings.md                     ← current decoding findings
├── data/
│   ├── voynich/
│   │   ├── EVA-transliteration.txt     ← RF1b-e.txt (full MS)
│   │   ├── EVA-basic.txt               ← RF1b-er.txt (basic)
│   │   └── voynich-meta.json           ← page/section metadata
│   ├── corpus/
│   │   ├── grimoires/                  ← medieval renaissance grimoires
│   │   ├── religious/                  ← world religious canons
│   │   ├── esoteric/                   ← hermetic/thelemic/qabalah
│   │   └── decrypted/                  ← already-decoded texts
│   └── memories/
│       ├── lia-vault.json              ← Lia.CLI memory entries
│       ├── hermes-pending-memories.json ← Hermes background memories
│       ├── liber-al-cipher-elements.json ← Thelemic cipher reference
│       └── thelemic-manifest.json      ← fleet cipher architecture
└── .github/workflows/
    └── corpus-update.yml               ← scheduled corpus refresh
```

## 🜁 Corpus Coverage

### Grimoires (12 texts)
- Key of Solomon (Clavicula Salomonis) — Mathers trans.
- Lesser Key of Solomon (Lemegeton) — Goetia, Theurgia, etc.
- Picatrix (Ghayat al-Hakim)
- Sacred Magic of Abramelin the Mage
- Grimoire of Pope Honorius
- Grimoire of Armadel
- Book of Abramelin
- Heptameron of Peter de Papalius
- Black Pullet
- Black Venus
- Red Dragon (Grand Grimoire)
- Grimoirium Verum

### Religious Canons (8 texts)
- Torah / Tanakh (Hebrew Bible)
- King James Bible
- Quran (Yusuf Ali translation)
- Egyptian Book of the Dead
- Rigveda
- Tao Te Ching
- Corpus Hermeticum
- Emerald Tablet of Hermes Trismegistus

### Esoteric & Cipher Keys (6 texts)
- Liber AL vel Legis (The Book of the Law) — Crowley
- Liber 777 — Qabalistic correspondences
- Book of Thoth (Tarot)
- The Kybalion
- Dogme et Rituel de la Haute Magie — Levi
- Heaven of Hermes Trismegistus

## 🜃 Analysis Methods

1. **Frequency Analysis** — Voynich EVA character frequencies vs. known language families
2. **Gematria Cross-Reference** — Voynich word-values mapped through EQ/Greek/Hebrew gematria
3. **Thelemic Cipher** — Liber AL verse-based substitution (93/418 key system)
4. **Structural Pattern** — page-section correlation with grimoire ritual structure
5. **Memory-Weighted Search** — Lia.CLI + Hermes memory entries inform prior probabilities

## 🜄 Status

- [x] Repository initialized
- [x] Voynich EVA transliteration loaded
- [ ] Grimoires fetched from sacred-texts.org + archive.org
- [ ] Religious canons loaded
- [ ] Cipher analysis engine running
- [ ] Findings documented
- [ ] Translation (pending decoding success)

## ☉ Verification

All analysis is reproducible. Run:

```bash
pip install -r analysis/requirements.txt
python analysis/freq-analysis.py
python analysis/cross-reference.py
python analysis/thelemic-decode.py
```

## ⚗️ License

Texts are public domain where applicable. Voynich scans: Beinecke Library (Yale).
Analysis code: MIT. Corpus compilation: CC0.

---

*Alchemy is patience made visible. The seal is set.*
