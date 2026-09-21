#!/usr/bin/env python3
"""Fetch public-domain corpus texts from sacred-texts.org and archive.org."""

import os
import urllib.request
import json
import time

CORPUS_DIR = "data/corpus"

SOURCES = {
    "grimoires": {
        "key-of-solomon": "https://sacred-texts.com/grim/kos/kos00.htm",
        "lesser-key-of-solomon": "https://sacred-texts.com/grim/lks/lks00.htm",
        "picatrix": "https://sacred-texts.com/alc/picatrix.htm",
        "abramelin": "https://sacred-texts.com/grim/abramelin.htm",
    },
    "religious": {
        "bible-kjv": "https://gutenberg.org/cache/epub/10/pg10.txt",
        "quran-yusuf-ali": "https://gutenberg.org/cache/epub/16937/pg16937.txt",
        "book-of-the-dead": "https://sacred-texts.com/egy/ebod/ebod00.htm",
    },
    "esoteric": {
        "liber-777": "https://sacred-texts.com/oto/777/777.htm",
        "kybalion": "https://gutenberg.org/cache/epub/4/pg4.txt",
    }
}

def fetch(url, dest):
    """Fetch URL to dest file."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(dest, "wb") as f:
                f.write(response.read())
        print(f"  ✓ {dest}")
        return True
    except Exception as e:
        print(f"  ✗ {url}: {e}")
        return False

def main():
    for category, sources in SOURCES.items():
        for name, url in sources.items():
            dest = os.path.join(CORPUS_DIR, category, f"{name}.txt")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            fetch(url, dest)
            time.sleep(1)  # be polite

if __name__ == "__main__":
    main()
