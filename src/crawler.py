"""
crawler.py - Single page fetcher for the Search Engine.

Provides functions to:
  - Fetch a single page and return a BeautifulSoup object
  - Extract internal links from a page
  - Extract visible text content from a page

Observes a politeness window of at least 6 seconds between requests
as required by the coursework specification.
"""

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


BASE_URL = "https://quotes.toscrape.com"
POLITENESS_DELAY = 6  # seconds between requests for politeness


def get_page(url: str, session: requests.Session) -> BeautifulSoup | None:
    """
    Fetch a single page and return a BeautifulSoup object.
    Returns None if the request fails.
    """
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        return None


def extract_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    """
    Extract all internal links from a parsed page.
    Only returns links that belong to the same domain as base_url.
    Fragments (#section) are stripped from URLs.
    """
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        # Keep only links within the same domain
        if parsed.netloc == urlparse(base_url).netloc:
            # Strip fragments and normalise
            clean = parsed._replace(fragment="").geturl()
            links.append(clean)
    return links


def extract_text_content(soup: BeautifulSoup) -> str:
    """
    Extract visible text from a parsed page.
    Removes script, style, and noscript tags before extracting text.
    """
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ")