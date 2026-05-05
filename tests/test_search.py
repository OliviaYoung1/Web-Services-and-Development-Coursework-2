"""
test_search.py - Unit tests for search.py

Run from the repo root with:  python -m pytest tests/ -v
"""

import unittest
import io
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from indexer import build_index
from search import find_pages, print_postings


SAMPLE_PAGES = {
    "http://example.com/page1": "The world created process thinking deeply.",
    "http://example.com/page2": "choices show abilities truly remarkable.",
    "http://example.com/page3": "ways live life nothing miracle wonderful.",
}


class TestFindPages(unittest.TestCase):

    def setUp(self):
        self.doc_index, self.inverted_index = build_index(SAMPLE_PAGES)

    def test_single_word_found(self):
        results = find_pages(self.doc_index, self.inverted_index, "miracle")
        urls = [url for url, _ in results]
        self.assertIn("http://example.com/page3", urls)

    def test_single_word_not_found(self):
        results = find_pages(self.doc_index, self.inverted_index, "zzznonsenseword")
        self.assertEqual(results, [])

    def test_multi_word_intersection(self):
        # "choices" only in page2, "abilities" only in page2
        results = find_pages(self.doc_index, self.inverted_index, "choices abilities")
        urls = [url for url, _ in results]
        self.assertIn("http://example.com/page2", urls)
        self.assertNotIn("http://example.com/page1", urls)

    def test_multi_word_no_match(self):
        results = find_pages(self.doc_index, self.inverted_index, "miracle choices")
        self.assertEqual(results, [])

    def test_three_word_query(self):
        results = find_pages(self.doc_index, self.inverted_index, "choices show abilities")
        urls = [url for url, _ in results]
        self.assertEqual(len(urls), 1)
        self.assertIn("http://example.com/page2", urls)

    def test_case_insensitive_query_upper(self):
        r1 = find_pages(self.doc_index, self.inverted_index, "miracle")
        r2 = find_pages(self.doc_index, self.inverted_index, "MIRACLE")
        self.assertEqual(r1, r2)

    def test_case_insensitive_query_mixed(self):
        r1 = find_pages(self.doc_index, self.inverted_index, "choices")
        r2 = find_pages(self.doc_index, self.inverted_index, "ChOiCeS")
        self.assertEqual(r1, r2)

    def test_results_sorted_descending(self):
        results = find_pages(self.doc_index, self.inverted_index, "world")
        scores = [score for _, score in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_scores_are_positive(self):
        results = find_pages(self.doc_index, self.inverted_index, "miracle")
        for _, score in results:
            self.assertGreater(score, 0)

    def test_empty_query_returns_empty(self):
        results = find_pages(self.doc_index, self.inverted_index, "")
        self.assertEqual(results, [])

    def test_stopword_only_query_returns_empty(self):
        # "the" and "is" are stopwords; they won't be in the index
        results = find_pages(self.doc_index, self.inverted_index, "the is")
        self.assertEqual(results, [])

    def test_returns_list_of_tuples(self):
        results = find_pages(self.doc_index, self.inverted_index, "miracle")
        for item in results:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)

    def test_result_urls_are_strings(self):
        results = find_pages(self.doc_index, self.inverted_index, "miracle")
        for url, _ in results:
            self.assertIsInstance(url, str)
            self.assertTrue(url.startswith("http"))


class TestPrintPostings(unittest.TestCase):

    def setUp(self):
        self.doc_index, self.inverted_index = build_index(SAMPLE_PAGES)

    def _capture(self, word: str) -> str:
        buf = io.StringIO()
        sys.stdout = buf
        print_postings(self.doc_index, self.inverted_index, word)
        sys.stdout = sys.__stdout__
        return buf.getvalue()

    def test_existing_word_shows_url(self):
        output = self._capture("miracle")
        self.assertIn("http://example.com/", output)

    def test_existing_word_shows_doc_id(self):
        output = self._capture("miracle")
        self.assertIn("Doc ID", output)

    def test_existing_word_shows_frequency(self):
        output = self._capture("miracle")
        self.assertIn("Frequency", output)

    def test_existing_word_shows_positions(self):
        output = self._capture("miracle")
        self.assertIn("Positions", output)

    def test_missing_word_shows_not_found(self):
        output = self._capture("zzznonsenseword")
        self.assertIn("not found", output)

    def test_uppercase_input_normalised(self):
        output = self._capture("MIRACLE")
        self.assertIn("http://example.com/", output)

    def test_word_name_appears_in_output(self):
        output = self._capture("miracle")
        self.assertIn("miracle", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)