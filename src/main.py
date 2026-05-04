#!/usr/bin/env python3
"""
main.py - Command-line shell for the COMP3011 Search Engine Tool.

Commands:
  build          Crawl the website, build and save the index.
  load           Load a previously saved index from disk.
  print <word>   Print the inverted index entry for <word>.
  find <query>   Find pages containing all words in <query>.
  help           Show this help message.
  exit / quit    Exit the shell.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from crawler import crawl, BASE_URL
from indexer import build_index, save_index, INDEX_FILE

BANNER = r"""
  Search Engine  |  quotes.toscrape.com
  Type 'help' for a list of commands.
"""


def show_help() -> None:
    print("""
  Commands:
    build              Crawl the site, build and save the index.
    load               Load an existing index from disk.
    print <word>       Show the inverted index entry for <word>.
    find <query>       Find pages containing all words in <query>.
    help               Show this message.
    exit / quit        Exit the shell.
""")


def parse_command(raw: str) -> tuple:
    """
    Parse a raw input string into a (command, args) tuple.
    Returns ('', []) for empty input.
    """
    parts = raw.strip().split()
    if not parts:
        return ('', [])
    return (parts[0].lower(), parts[1:])


def cmd_build() -> tuple:
    """Crawl the website, build the index and save it to disk."""
    print(f"\n  Starting crawl of {BASE_URL} ...")
    print(f"  (Politeness window: 6 s between requests)\n")
    pages = crawl(BASE_URL, verbose=True)
    print(f"\n  Crawled {len(pages)} page(s). Building index ...")
    doc_index, inverted_index = build_index(pages)
    print(f"  Index built: {len(doc_index)} pages, {len(inverted_index)} unique terms.")
    save_index(doc_index, inverted_index, INDEX_FILE)
    return doc_index, inverted_index


def main() -> None:
    print(BANNER)

    doc_index: dict = {}
    inverted_index: dict = {}

    while True:
        try:
            raw = input("  > ")
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            sys.exit(0)

        command, args = parse_command(raw)

        if not command:
            continue

        if command == "build":
            doc_index, inverted_index = cmd_build()
        elif command == "load":
            print("  [load] Not yet implemented.")
        elif command == "print":
            if not args:
                print("  Usage: print <word>")
            else:
                print("  [print] Not yet implemented.")
        elif command == "find":
            if not args:
                print("  Usage: find <word> [word2] ...")
            else:
                print("  [find] Not yet implemented.")
        elif command in ("help", "?"):
            show_help()
        elif command in ("exit", "quit", "q"):
            print("  Goodbye!")
            sys.exit(0)
        else:
            print(f"  Unknown command: '{command}'. Type 'help' for a list.")


if __name__ == "__main__":
    main()