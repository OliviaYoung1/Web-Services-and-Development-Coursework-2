"""
search.py - Query processing and ranked retrieval.

Implements conjunctive (AND) processing as described in Lecture 13 Slide 10:
"every document returned to the user needs to contain all of the query terms."

Ranking uses document-at-a-time scoring (L13, Slides 4-6): for each candidate
document, the sum of per-term frequencies is computed as the relevance score.
Higher frequency = more relevant (L12, Slide 13-14).

The doc_index (doc_id -> URL) is used to resolve postings back to URLs
for display, keeping the inverted index itself clean of raw URLs (L12, Slide 9).
"""

import math
from indexer import tokenise


def _score(inverted_index: dict, words: list, doc_id: str) -> float:
    """
    Compute a TF * log(df+1) score for a document given a list of query words.
    Returns -1.0 if the document is missing any query term (conjunctive exclusion).
    """
    total = 0.0
    # Rough approximation of total document count from index size
    num_docs = len(set(
        did for postings in inverted_index.values() for did in postings
    )) or 1

    for word in words:
        postings = inverted_index.get(word, {})
        if doc_id not in postings:
            return -1.0  # AND semantics: missing any term = excluded
        tf = postings[doc_id]["freq"]
        df = len(postings)
        idf = math.log((num_docs + 1) / (df + 1)) + 1  # smoothed IDF
        total += tf * idf
    return total


def find_pages(doc_index: dict, inverted_index: dict, query: str) -> list:
    """
    Conjunctive search: returns pages containing ALL query words.
    Implements document-at-a-time evaluation (L13, Slides 4-6).

    Returns a list of (url, score) tuples sorted by descending score.
    """
    words = tokenise(query)
    if not words:
        return []

    # Intersection of posting lists across all query terms (conjunctive, L13 Slide 10)
    candidate_sets = [set(inverted_index.get(w, {}).keys()) for w in words]
    if not all(candidate_sets):
        return []

    candidates = candidate_sets[0].intersection(*candidate_sets[1:])

    scored = []
    for doc_id in candidates:
        score = _score(inverted_index, words, doc_id)
        if score >= 0:
            url = doc_index.get(doc_id, doc_id)  # resolve doc_id -> URL
            scored.append((url, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def print_postings(doc_index: dict, inverted_index: dict, word: str) -> None:
    """
    Print the inverted index entry for a single word.
    Resolves document IDs back to URLs using doc_index (L12, Slide 9).
    """
    word = word.lower().strip()
    postings = inverted_index.get(word)
    if postings is None:
        print(f"  '{word}' not found in the index.")
        return

    print(f"\n  Inverted index for '{word}' ({len(postings)} page(s)):\n")
    for doc_id, stats in sorted(postings.items(), key=lambda x: -x[1]["freq"]):
        url = doc_index.get(doc_id, f"doc:{doc_id}")
        freq = stats["freq"]
        positions = stats["positions"]
        preview = positions[:5]
        more = f" ... (+{len(positions)-5} more)" if len(positions) > 5 else ""
        print(f"    Doc ID   : {doc_id}")
        print(f"    URL      : {url}")
        print(f"    Frequency: {freq}")
        print(f"    Positions: {preview}{more}\n")