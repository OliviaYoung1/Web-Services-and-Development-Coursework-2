"""
indexer.py - Builds and stores an inverted index.

Design follows Lecture 12 (COMP3011):
  - Postings store document numbers (not raw URLs), with a separate
    doc_index lookup table mapping doc_id -> URL  (L12, Slide 9).
  - Each posting records word count (frequency) and word positions
    (L12, Slides 13 & 15).
  - Stopwords are removed before indexing (L11, Slides 15-17).
  - Tokens must be at least 2 characters long (L11, Slide 7).

Saved JSON structure:
{
  "doc_index": {"0": "https://...", "1": "https://...", ...},
  "inverted_index": {
    "word": {
      "0": {"freq": int, "positions": [int, ...]},
      ...
    },
    ...
  }
}
"""

import re
import json
from pathlib import Path

INDEX_FILE = "../data/index.json"

# Common English stopwords (L11, Slides 15-16).
# These words have little meaning in isolation and are excluded from the index.
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "not",
    "no", "nor", "so", "yet", "both", "either", "whether", "that", "this",
    "these", "those", "it", "its", "as", "up", "out", "about", "into",
    "than", "then", "when", "where", "who", "which", "what", "how", "all",
    "each", "every", "few", "more", "most", "other", "some", "such",
    "own", "same", "too", "very", "just", "also", "any", "there",
    "their", "they", "them", "we", "our", "you", "your", "he", "she", "his",
    "her", "him", "my", "me", "us", "i", "am", "s", "t"
}

MIN_TOKEN_LENGTH = 2  # Lecture 11, Slide 7: discard very short tokens


def tokenise(text: str) -> list[str]:
    """
    Lowercase the text, split on any non-alphabetic character, then filter:
      - tokens shorter than MIN_TOKEN_LENGTH are discarded (L11, Slide 7)
      - stopwords are removed (L11, Slides 15-17)
    Returns a flat list of meaningful tokens.
    """
    text = text.lower()
    raw_tokens = re.split(r"[^a-z]+", text)
    return [
        t for t in raw_tokens
        if len(t) >= MIN_TOKEN_LENGTH and t not in STOPWORDS
    ]


def build_index(pages: dict) -> tuple:
    """
    Given a mapping of URL -> raw text, build and return:
      - doc_index: {str(doc_id) -> url}
      - inverted_index: {word -> {str(doc_id) -> {"freq": int, "positions": [int]}}}

    Using numeric document IDs in postings rather than raw URLs follows
    Lecture 12 Slide 9: each page is given a unique number to make it
    more efficient for storing document pointers. A separate doc_index
    links document numbers with their URLs.
    """
    doc_index = {}        # str(doc_id) -> url
    inverted_index = {}   # word -> {doc_id -> stats}

    for doc_id, (url, text) in enumerate(pages.items()):
        str_id = str(doc_id)
        doc_index[str_id] = url

        tokens = tokenise(text)
        for position, word in enumerate(tokens):
            if word not in inverted_index:
                inverted_index[word] = {}
            if str_id not in inverted_index[word]:
                inverted_index[word][str_id] = {"freq": 0, "positions": []}
            inverted_index[word][str_id]["freq"] += 1
            inverted_index[word][str_id]["positions"].append(position)

    return doc_index, inverted_index


def save_index(doc_index: dict, inverted_index: dict, filepath: str = INDEX_FILE) -> None:
    """Serialise both the doc_index and inverted_index to a single JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"doc_index": doc_index, "inverted_index": inverted_index}
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"  Index saved to '{filepath}' ({path.stat().st_size // 1024} KB).")