"""
test_main.py - Unit tests for the CLI shell (main.py).

Tests cover command parsing and shell behaviour only.
No crawler, indexer, or search functionality is tested here.

Run from the repo root with:  python -m pytest tests/ -v
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import parse_command


class TestParseCommand(unittest.TestCase):
    """Tests for the parse_command() function."""

    def test_empty_string_returns_empty(self):
        command, args = parse_command("")
        self.assertEqual(command, "")
        self.assertEqual(args, [])

    def test_whitespace_only_returns_empty(self):
        command, args = parse_command("   ")
        self.assertEqual(command, "")
        self.assertEqual(args, [])

    def test_single_command_no_args(self):
        command, args = parse_command("build")
        self.assertEqual(command, "build")
        self.assertEqual(args, [])

    def test_command_with_single_arg(self):
        command, args = parse_command("print nonsense")
        self.assertEqual(command, "print")
        self.assertEqual(args, ["nonsense"])

    def test_command_with_multiple_args(self):
        command, args = parse_command("find good friends")
        self.assertEqual(command, "find")
        self.assertEqual(args, ["good", "friends"])

    def test_command_lowercased(self):
        command, args = parse_command("BUILD")
        self.assertEqual(command, "build")

    def test_mixed_case_command_lowercased(self):
        command, args = parse_command("Load")
        self.assertEqual(command, "load")

    def test_extra_whitespace_handled(self):
        command, args = parse_command("  find   good   friends  ")
        self.assertEqual(command, "find")
        self.assertEqual(args, ["good", "friends"])

    def test_load_command_no_args(self):
        command, args = parse_command("load")
        self.assertEqual(command, "load")
        self.assertEqual(args, [])

    def test_exit_command(self):
        command, args = parse_command("exit")
        self.assertEqual(command, "exit")
        self.assertEqual(args, [])

    def test_quit_command(self):
        command, args = parse_command("quit")
        self.assertEqual(command, "quit")
        self.assertEqual(args, [])

    def test_help_command(self):
        command, args = parse_command("help")
        self.assertEqual(command, "help")
        self.assertEqual(args, [])

    def test_unknown_command(self):
        command, args = parse_command("foobar")
        self.assertEqual(command, "foobar")
        self.assertEqual(args, [])

    def test_print_with_no_args(self):
        command, args = parse_command("print")
        self.assertEqual(command, "print")
        self.assertEqual(args, [])

    def test_find_with_no_args(self):
        command, args = parse_command("find")
        self.assertEqual(command, "find")
        self.assertEqual(args, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)