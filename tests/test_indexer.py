"""
test_indexer.py - Unit tests for indexer.py.

Tests cover:
  - tokenise(): lowercasing, punctuation stripping, stopword removal,
                minimum token length
  - build_index(): doc ID assignment, inverted index structure,
                   frequency and position recording

load_index() is not tested here - that comes in the next commit.

Run from the repo root with:  python -m pytest tests/ -v
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from indexer import tokenise, build_index, STOPWORDS


SAMPLE_PAGES = {
    "http://example.com/page1": "The world created process thinking deeply.",
    "http://example.com/page2": "choices show abilities truly remarkable.",
    "http://example.com/page3": "ways live life nothing miracle wonderful.",
}


class TestTokenise(unittest.TestCase):
    """Tests for the tokenise() function."""

    def test_lowercase(self):
        tokens = tokenise("Hello World")
        self.assertIn("hello", tokens)
        self.assertIn("world", tokens)
        self.assertNotIn("Hello", tokens)

    def test_strips_punctuation(self):
        tokens = tokenise("well, fine!")
        self.assertIn("well", tokens)
        self.assertIn("fine", tokens)

    def test_empty_string(self):
        self.assertEqual(tokenise(""), [])

    def test_numbers_stripped(self):
        tokens = tokenise("page 42 results")
        self.assertIn("page", tokens)
        self.assertIn("results", tokens)
        self.assertNotIn("42", tokens)

    def test_stopwords_removed(self):
        tokens = tokenise("the cat is a mammal")
        self.assertNotIn("the", tokens)
        self.assertNotIn("is", tokens)
        self.assertNotIn("a", tokens)
        self.assertIn("cat", tokens)
        self.assertIn("mammal", tokens)

    def test_min_token_length(self):
        tokens = tokenise("x y hello")
        self.assertNotIn("x", tokens)
        self.assertNotIn("y", tokens)
        self.assertIn("hello", tokens)

    def test_whitespace_only(self):
        self.assertEqual(tokenise("   "), [])

    def test_mixed_case_normalised(self):
        tokens = tokenise("Python PYTHON python")
        self.assertEqual(tokens, ["python", "python", "python"])

    def test_hyphenated_word(self):
        tokens = tokenise("well-known")
        self.assertIn("well", tokens)
        self.assertIn("known", tokens)


class TestBuildIndex(unittest.TestCase):
    """Tests for the build_index() function."""

    def setUp(self):
        self.doc_index, self.inverted_index = build_index(SAMPLE_PAGES)

    def test_doc_index_has_all_urls(self):
        urls = set(self.doc_index.values())
        self.assertIn("http://example.com/page1", urls)
        self.assertIn("http://example.com/page2", urls)
        self.assertIn("http://example.com/page3", urls)

    def test_doc_index_keys_are_numeric_strings(self):
        for key in self.doc_index:
            self.assertTrue(key.isdigit(), f"Expected numeric string, got: {key}")

    def test_inverted_index_uses_doc_ids_not_urls(self):
        # Postings must contain doc IDs (numeric strings), not raw URLs
        for word, postings in self.inverted_index.items():
            for key in postings:
                self.assertTrue(
                    key.isdigit(),
                    f"Posting key '{key}' for word '{word}' is not a doc ID"
                )

    def test_word_present(self):
        self.assertIn("choices", self.inverted_index)

    def test_stopwords_not_indexed(self):
        for sw in STOPWORDS:
            self.assertNotIn(sw, self.inverted_index,
                             f"Stopword '{sw}' should not be in index")

    def test_frequency_correct(self):
        page2_id = next(k for k, v in self.doc_index.items()
                        if v == "http://example.com/page2")
        freq = self.inverted_index["abilities"][page2_id]["freq"]
        self.assertEqual(freq, 1)

    def test_positions_recorded(self):
        page1_id = next(k for k, v in self.doc_index.items()
                        if v == "http://example.com/page1")
        positions = self.inverted_index["thinking"][page1_id]["positions"]
        self.assertIsInstance(positions, list)
        self.assertGreater(len(positions), 0)

    def test_positions_are_integers(self):
        page2_id = next(k for k, v in self.doc_index.items()
                        if v == "http://example.com/page2")
        positions = self.inverted_index["abilities"][page2_id]["positions"]
        for p in positions:
            self.assertIsInstance(p, int)

    def test_case_insensitive_storage(self):
        self.assertNotIn("The", self.inverted_index)

    def test_word_only_in_correct_page(self):
        page3_id = next(k for k, v in self.doc_index.items()
                        if v == "http://example.com/page3")
        page1_id = next(k for k, v in self.doc_index.items()
                        if v == "http://example.com/page1")
        postings = self.inverted_index.get("miracle", {})
        self.assertIn(page3_id, postings)
        self.assertNotIn(page1_id, postings)

    def test_empty_pages_produces_empty_index(self):
        doc_index, inv = build_index({})
        self.assertEqual(doc_index, {})
        self.assertEqual(inv, {})

    def test_index_structure(self):
        for word, postings in self.inverted_index.items():
            for doc_id, stats in postings.items():
                self.assertIn("freq", stats)
                self.assertIn("positions", stats)

    def test_position_count_matches_frequency(self):
        for word, postings in self.inverted_index.items():
            for doc_id, stats in postings.items():
                self.assertEqual(stats["freq"], len(stats["positions"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)