"""
test_crawler.py - Unit tests for crawler.py.

Tests cover:
  - extract_links(): internal link extraction and filtering
  - extract_text_content(): visible text extraction
  - get_page(): mocked HTTP request handling
  - crawl(): BFS multi-page crawl using mocked pages

All tests use mocks - no real network requests are made.

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


class TestCrawlIntegration(unittest.TestCase):
    """Integration-style tests for crawl() using mocked HTTP responses."""

    @patch("crawler.get_page")
    @patch("crawler.time.sleep")
    def test_crawl_visits_linked_pages(self, mock_sleep, mock_get_page):
        """Crawler should follow links and visit all reachable pages."""
        page1_html = '<html><body><p>Hello</p><a href="/page2/">Next</a></body></html>'
        page2_html = "<html><body><p>World</p></body></html>"

        def side_effect(url, session):
            if url == BASE_URL:
                return make_soup(page1_html)
            elif url == BASE_URL + "/page2/":
                return make_soup(page2_html)
            return None

        mock_get_page.side_effect = side_effect

        from crawler import crawl
        pages = crawl(BASE_URL, verbose=False)

        self.assertIn(BASE_URL, pages)
        self.assertIn(BASE_URL + "/page2/", pages)

    @patch("crawler.get_page", return_value=None)
    @patch("crawler.time.sleep")
    def test_crawl_handles_failed_page(self, mock_sleep, mock_get_page):
        """A page that fails to load should not appear in results."""
        from crawler import crawl
        pages = crawl(BASE_URL, verbose=False)
        self.assertEqual(pages, {})

    @patch("crawler.time.sleep")
    @patch("crawler.get_page")
    def test_crawl_no_duplicate_visits(self, mock_get_page, mock_sleep):
        """Each URL should only be visited once, even if linked multiple times."""
        html = f'<html><body><a href="{BASE_URL}">self</a></body></html>'
        mock_get_page.return_value = make_soup(html)

        from crawler import crawl
        pages = crawl(BASE_URL, verbose=False)
        self.assertEqual(len(pages), 1)

    @patch("crawler.time.sleep")
    @patch("crawler.get_page")
    def test_crawl_returns_text_for_each_page(self, mock_get_page, mock_sleep):
        """Each crawled page should have its text content stored."""
        html = "<html><body><p>Some content here</p></body></html>"
        mock_get_page.return_value = make_soup(html)

        from crawler import crawl
        pages = crawl(BASE_URL, verbose=False)
        for url, text in pages.items():
            self.assertIsInstance(text, str)
            self.assertGreater(len(text.strip()), 0)

    @patch("crawler.time.sleep")
    @patch("crawler.get_page")
    def test_crawl_ignores_external_links(self, mock_get_page, mock_sleep):
        """External links should not be followed."""
        html = '<html><body><a href="https://google.com">Google</a></body></html>'
        mock_get_page.return_value = make_soup(html)

        from crawler import crawl
        pages = crawl(BASE_URL, verbose=False)
        for url in pages:
            self.assertIn("quotes.toscrape.com", url)

    @patch("crawler.time.sleep")
    @patch("crawler.get_page")
    def test_politeness_sleep_called_between_requests(self, mock_get_page, mock_sleep):
        """time.sleep() should be called between page requests."""
        page1_html = f'<html><body><a href="{BASE_URL}/page2/">Next</a></body></html>'
        page2_html = "<html><body><p>Page 2</p></body></html>"

        def side_effect(url, session):
            if url == BASE_URL:
                return make_soup(page1_html)
            return make_soup(page2_html)

        mock_get_page.side_effect = side_effect

        from crawler import crawl
        crawl(BASE_URL, verbose=False)

        # Sleep should have been called at least once for the second request
        mock_sleep.assert_called()

    @patch("crawler.time.sleep")
    @patch("crawler.get_page")
    def test_crawl_three_pages_linked_in_chain(self, mock_get_page, mock_sleep):
        """Crawler should follow a chain of links across multiple pages."""
        pages_html = {
            BASE_URL: f'<html><body><p>Page1</p><a href="{BASE_URL}/p2/">p2</a></body></html>',
            BASE_URL + "/p2/": f'<html><body><p>Page2</p><a href="{BASE_URL}/p3/">p3</a></body></html>',
            BASE_URL + "/p3/": "<html><body><p>Page3</p></body></html>",
        }

        mock_get_page.side_effect = lambda url, session: make_soup(pages_html.get(url, ""))

        from crawler import crawl
        pages = crawl(BASE_URL, verbose=False)

        self.assertEqual(len(pages), 3)
        self.assertIn(BASE_URL, pages)
        self.assertIn(BASE_URL + "/p2/", pages)
        self.assertIn(BASE_URL + "/p3/", pages)


if __name__ == "__main__":
    unittest.main(verbosity=2)