"""
test_crawler.py - Unit tests for single page fetching (crawler.py).

Tests cover:
  - extract_links(): internal link extraction and filtering
  - extract_text_content(): visible text extraction
  - get_page(): mocked HTTP request handling

No BFS crawl tests are included yet - those come in the next commit.

Run from the repo root with:  python -m pytest tests/ -v
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from crawler import extract_links, extract_text_content, BASE_URL
from bs4 import BeautifulSoup


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class TestExtractLinks(unittest.TestCase):
    """Tests for the extract_links() function."""

    def test_extracts_internal_link(self):
        soup = make_soup('<a href="/page/2/">Next</a>')
        links = extract_links(soup, BASE_URL)
        self.assertTrue(any("/page/2/" in l for l in links))

    def test_ignores_external_link(self):
        soup = make_soup('<a href="https://google.com">Google</a>')
        links = extract_links(soup, BASE_URL)
        self.assertEqual(links, [])

    def test_resolves_relative_url(self):
        soup = make_soup('<a href="/author/Einstein/">Einstein</a>')
        links = extract_links(soup, BASE_URL)
        expected = BASE_URL + "/author/Einstein/"
        self.assertIn(expected, links)

    def test_no_links_returns_empty(self):
        soup = make_soup("<p>No links here.</p>")
        links = extract_links(soup, BASE_URL)
        self.assertEqual(links, [])

    def test_strips_fragment(self):
        soup = make_soup('<a href="/page/#section">Link</a>')
        links = extract_links(soup, BASE_URL)
        for link in links:
            self.assertNotIn("#", link)

    def test_multiple_links(self):
        html = '<a href="/a/">A</a><a href="/b/">B</a><a href="/c/">C</a>'
        soup = make_soup(html)
        links = extract_links(soup, BASE_URL)
        self.assertEqual(len(links), 3)

    def test_duplicate_links_included(self):
        # extract_links returns all occurrences; deduplication is the crawler's job
        html = '<a href="/page/">A</a><a href="/page/">B</a>'
        soup = make_soup(html)
        links = extract_links(soup, BASE_URL)
        self.assertEqual(len(links), 2)


class TestExtractTextContent(unittest.TestCase):
    """Tests for the extract_text_content() function."""

    def test_returns_visible_text(self):
        soup = make_soup("<p>Hello world</p>")
        text = extract_text_content(soup)
        self.assertIn("Hello world", text)

    def test_strips_script_tags(self):
        soup = make_soup("<p>Hello</p><script>alert('hi')</script>")
        text = extract_text_content(soup)
        self.assertNotIn("alert", text)

    def test_strips_style_tags(self):
        soup = make_soup("<p>Hello</p><style>body { color: red; }</style>")
        text = extract_text_content(soup)
        self.assertNotIn("color", text)

    def test_empty_page(self):
        soup = make_soup("")
        text = extract_text_content(soup)
        self.assertEqual(text.strip(), "")

    def test_nested_tags_flattened(self):
        soup = make_soup("<div><p><strong>Deep</strong> text</p></div>")
        text = extract_text_content(soup)
        self.assertIn("Deep", text)
        self.assertIn("text", text)


class TestGetPage(unittest.TestCase):
    """Tests for the get_page() function using mocked HTTP requests."""

    @patch("crawler.requests.Session.get")
    def test_returns_soup_on_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Hello</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        import requests
        from crawler import get_page
        session = requests.Session()
        result = get_page(BASE_URL, session)
        self.assertIsNotNone(result)

    @patch("crawler.requests.Session.get")
    def test_returns_none_on_http_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("Connection error")

        from crawler import get_page
        session = requests.Session()
        result = get_page(BASE_URL, session)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)