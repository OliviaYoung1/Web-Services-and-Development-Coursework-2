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


def main() -> None:
    print(BANNER)

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
            print("  [build] Not yet implemented.")
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