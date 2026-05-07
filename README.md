# COMP3011 Coursework 2: Search Engine Tool
 
## Project Overview and Purpose
 
A command-line search engine for [quotes.toscrape.com](https://quotes.toscrape.com), built in Python as part of the COMP3011 Web Services and Web Data module at the University of Leeds.
 
The tool crawls the entire quotes.toscrape.com website, builds an inverted index of all word occurrences across every page, and allows the user to search for pages containing specific terms via an interactive command-line shell.
 
Key features:
- **BFS web crawler** with a 6-second politeness window between requests
- **Inverted index** storing term frequency and word positions per document, following the structure taught in COMP3011 Lecture 12
- **Stopword removal** and minimum token length filtering (Lecture 11)
- **Numeric document IDs** in postings with a separate URL lookup table (Lecture 12, Slide 9)
- **TF-IDF ranked retrieval** with conjunctive (AND) multi-term query support (Lecture 13)
- **Persistent index** saved to and loaded from disk as JSON
---
 
## Installation and Setup
 
### Requirements
 
- Python 3.10 or higher
- pip
### Steps
 
1. Clone the repository:
```bash
git clone https://github.com/OliviaYoung1/Web-Services-and-Development-Coursework-2
cd Web-Services-and-Development-Coursework-2
```
 
2. Install dependencies:
```bash
pip install -r requirements.txt
```
 
3. Run the search engine from the `src/` directory:
```bash
cd src
python main.py
```
 
---
 
## Usage Examples
 
The tool runs as an interactive command-line shell. Once started, you will see a prompt:
 
```
  >
```
 
### `build`
 
Crawls the entire quotes.toscrape.com website, builds the inverted index, and saves it to `data/index.json`. This command takes approximately 20–25 minutes due to the required 6-second politeness delay between requests.
 
```
  > build
 
  Starting crawl of https://quotes.toscrape.com ...
  (Politeness window: 6 s between requests)
 
  Crawling [1]: https://quotes.toscrape.com
  Crawling [2]: https://quotes.toscrape.com/
  ...
  Crawling [215]: https://quotes.toscrape.com/tag/better-life-empathy/page/1/
 
  Crawled 214 page(s). Building index ...
  Index built: 214 pages, 4211 unique terms.
  Index saved to '.../data/index.json' (1730 KB).
```
 
---
 
### `load`
 
Loads a previously built index from `data/index.json` into memory. Use this to avoid re-crawling the site on subsequent sessions. Requires `build` to have been run at least once beforehand.
 
```
  > load
 
  Index loaded from '.../data/index.json' (214 pages, 4211 unique terms).
```
 
If no index file exists yet:
 
```
  > load
 
  [ERROR] Index file '...' not found. Run 'build' first.
```
 
---
 
### `print`
 
Prints the full inverted index entry for a given word, showing every page it appears on along with its document ID, frequency, and the positions in the token stream where it occurs.
 
```
  > print nonsense
 
  Inverted index for 'nonsense' (6 page(s)):
 
    Doc ID   : 12
    URL      : https://quotes.toscrape.com/tag/life/page/1/
    Frequency: 1
    Positions: [251]
 
    Doc ID   : 37
    URL      : https://quotes.toscrape.com/page/2/
    Frequency: 1
    Positions: [203]
 
    ...
```
 
---
 
### `find`
 
Searches the index for pages containing a given word or phrase. For multi-word queries, only pages containing **all** query terms are returned (conjunctive/AND semantics). Results are ranked by TF-IDF score, with the most relevant pages listed first.
 
Single-word search:
 
```
  > find indifference
 
  Results for 'indifference' — 11 page(s) found:
 
     1. [score=23.31]  https://quotes.toscrape.com/tag/indifference/page/1/
     2. [score=19.43]  https://quotes.toscrape.com/tag/hate/page/1/
     3. [score=19.43]  https://quotes.toscrape.com/tag/activism/page/1/
    ...
```
 
Multi-word search:
 
```
  > find good friends
 
  Results for 'good friends' — 35 page(s) found:
 
     1. [score=21.63]  https://quotes.toscrape.com/tag/friends/page/1/
     2. [score=21.63]  https://quotes.toscrape.com/tag/friends/
     3. [score=19.16]  https://quotes.toscrape.com/page/2/
    ...
```
 
---
 
## Testing Instructions
 
All tests are located in the `tests/` directory and use Python's built-in `unittest` framework with `pytest` as the test runner. All tests use mocked data and do not make any real network requests, so they run in a few seconds.
 
### Run the full test suite
 
From the **repository root**:
 
```bash
python -m pytest tests/ -v
```
 
### Run a single test file
 
```bash
python -m pytest tests/test_crawler.py -v
python -m pytest tests/test_indexer.py -v
python -m pytest tests/test_search.py -v
```
 
### Run a single test class or test
 
```bash
python -m pytest tests/test_indexer.py::TestTokenise -v
python -m pytest tests/test_indexer.py::TestTokenise::test_stopwords_removed -v
```
 
### Test files and what they cover
 
| File | Classes | What is tested |
|---|---|---|
| `test_crawler.py` | `TestExtractLinks`, `TestExtractTextContent`, `TestGetPage`, `TestCrawlIntegration` | Link extraction, text extraction, HTTP error handling, BFS crawl logic |
| `test_indexer.py` | `TestTokenise`, `TestBuildIndex`, `TestSaveAndLoadIndex` | Tokenisation, stopword removal, index structure, JSON round-trip |
| `test_search.py` | `TestFindPages`, `TestPrintPostings` | Single and multi-term search, ranking, case insensitivity, edge cases |
 
---
 
## Dependencies
 
| Package | Version | Purpose |
|---|---|---|
| `requests` | >= 2.31.0 | HTTP requests for the web crawler |
| `beautifulsoup4` | >= 4.12.0 | HTML parsing to extract text and links |
| `pytest` | >= 7.0.0 | Test runner (optional, only needed to run tests) |
 
### Install all dependencies
 
```bash
pip install -r requirements.txt
```
 
To also install pytest for running tests:
 
```bash
pip install pytest
```
 
### `requirements.txt`
 
```
requests>=2.31.0
beautifulsoup4>=4.12.0
```
 
---
 
## Repository Structure
 
```
COMP3011--coursework-2/
├── src/
│   ├── main.py        # CLI shell and entry point
│   ├── crawler.py     # BFS web crawler with politeness window
│   ├── indexer.py     # Tokenisation, index building, JSON I/O
│   └── search.py      # Query processing and TF-IDF ranking
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
│   └── index.json     # Generated at runtime by 'build'
├── requirements.txt
└── README.md
```
 
---
 
## Design Decisions
 
### Inverted index structure
Follows the structure taught in Lecture 12: each word maps to a posting list of document IDs (not raw URLs), with a separate `doc_index` lookup table linking IDs to URLs. Each posting stores both term frequency and token positions, enabling both TF-IDF ranking and potential future phrase search.
 
### Tokenisation
Text is lowercased and split on any non-alphabetic character (`[^a-z]+`), removing punctuation and digits in one pass. Common English stopwords are removed (Lecture 11) and tokens shorter than 2 characters are discarded.
 
### Ranking
Multi-term queries rank pages by the sum of TF × smoothed-IDF across all query terms. Pages missing any query term are excluded entirely (AND semantics, Lecture 13 Slide 10).
 
### Politeness
`time.sleep(6)` is called between every consecutive HTTP request, only when there is a next URL to fetch, avoiding an unnecessary delay at the end of the crawl.

---
 
## GenAI Decleration

I acknowledge the use of Claude Sonnet 4.6 (Anthropic, https://claude.ai) to support this coursework, aligning with the information that we were allowed to use any AI tool on the Teams page. I used it to assist with planning the incremental development structure, generating initial versions of the crawler, indexer, search, and test files, debugging issues in the TF-IDF scoring logic and index file path resolution, drafting inline code comments, and generating the README and video demonstration script. I also used it to generate the PowerPoint slides for the GenAI critical evaluation section of the video demonstration.
All AI-generated code and content was reviewed, tested, and adapted by me before implementation. Where AI suggestions did not align with the module's taught material, including the inverted index structure (Lecture 12), stopword removal (Lecture 11), and the development and testing workflow, I identified the discrepancies, pushed back, and corrected them myself.