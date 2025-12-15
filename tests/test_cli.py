"""
Comprehensive test suite for CLI module.

Tests cover argument parsing, all command modes, output formats,
filtering options, and error handling.
"""

import json
import os
import tempfile

import pytest

from textcounter.cli import create_parser, main


class TestArgumentParsing:
    """Tests for CLI argument parser."""

    def test_parser_creation(self):
        """Parser creates successfully."""
        parser = create_parser()
        assert parser is not None

    def test_version_flag(self):
        """--version exits cleanly."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_chars_flag(self):
        """--chars flag is recognized."""
        parser = create_parser()
        args = parser.parse_args(["--chars", "-t", "test"])
        assert args.chars is True

    def test_words_flag(self):
        """--words flag is recognized."""
        parser = create_parser()
        args = parser.parse_args(["--words", "-t", "test"])
        assert args.words is True

    def test_text_input(self):
        """--text / -t accepts input."""
        parser = create_parser()
        args = parser.parse_args(["-t", "Hello World"])
        assert args.text == "Hello World"


class TestBasicCounting:
    """Tests for basic counting commands."""

    def test_character_count(self, capsys):
        """Character counting works."""
        exit_code = main(["-t", "Hello World", "-c"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "11" in captured.out or "characters" in captured.out

    def test_word_count(self, capsys):
        """Word counting works."""
        exit_code = main(["-t", "Hello World", "-w", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["words"] == 2

    def test_line_count(self, capsys):
        """Line counting works."""
        exit_code = main(["-t", "Hello\nWorld", "-l", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["lines"] == 2

    def test_sentence_count(self, capsys):
        """Sentence counting works."""
        exit_code = main(["-t", "Hello! How are you?", "-s", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["sentences"] == 2

    def test_all_counts(self, capsys):
        """--all shows all counts."""
        exit_code = main(["-t", "Hello World!", "-a"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "words" in captured.out.lower() or "2" in captured.out


class TestOutputFormats:
    """Tests for output format options."""

    def test_json_output(self, capsys):
        """--json produces valid JSON."""
        exit_code = main(["-t", "Hello World", "--json", "-c"])
        captured = capsys.readouterr()
        assert exit_code == 0
        data = json.loads(captured.out)
        assert "characters" in data

    def test_quiet_mode(self, capsys):
        """--quiet shows only numbers."""
        exit_code = main(["-t", "Hello World", "-w", "--quiet"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert captured.out.strip() == "2"


class TestFilteringOptions:
    """Tests for filtering options."""

    def test_no_spaces(self, capsys):
        """--no-spaces excludes spaces."""
        exit_code = main(["-t", "Hello World", "-c", "--no-spaces", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["characters"] == 10

    def test_no_punctuation(self, capsys):
        """--no-punctuation excludes punctuation."""
        exit_code = main(["-t", "Hello, World!", "-c", "--no-punctuation", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["characters"] == 11

    def test_no_digits(self, capsys):
        """--no-digits excludes digits."""
        exit_code = main(["-t", "Hello123", "-c", "--no-digits", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["characters"] == 5

    def test_unique_words(self, capsys):
        """--unique counts unique words."""
        exit_code = main(["-t", "hello world hello", "-w", "--unique", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["words"] == 2

    def test_min_length(self, capsys):
        """--min-length filters by word length."""
        exit_code = main(
            ["-t", "I am a developer", "-w", "--min-length", "3", "--json"]
        )
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["words"] == 1  # Only "developer"


class TestAnalysisCommands:
    """Tests for analysis commands."""

    def test_char_frequency(self, capsys):
        """--frequency chars works."""
        exit_code = main(["-t", "hello", "--frequency", "chars", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "frequency" in data

    def test_word_frequency(self, capsys):
        """--frequency words works."""
        exit_code = main(["-t", "hello world hello", "--frequency", "words", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "frequency" in data

    def test_readability(self, capsys):
        """--readability works."""
        exit_code = main(["-t", "The cat sat on the mat.", "--readability", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "readability" in data

    def test_ngrams(self, capsys):
        """--ngrams works."""
        exit_code = main(["-t", "the quick brown fox", "--ngrams", "2", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "ngrams" in data

    def test_statistics(self, capsys):
        """--stats works."""
        exit_code = main(["-t", "Hello World!", "--stats", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "statistics" in data


class TestFileInput:
    """Tests for file input handling."""

    def test_read_from_file(self, capsys):
        """Reading from file works."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Hello World")
            f.flush()
            temp_path = f.name

        try:
            exit_code = main([temp_path, "-c", "--json"])
            captured = capsys.readouterr()
            data = json.loads(captured.out)
            assert exit_code == 0
            assert data["characters"] == 11
        finally:
            os.unlink(temp_path)

    def test_file_not_found(self):
        """Missing file raises error."""
        with pytest.raises(SystemExit):
            main(["nonexistent_file_12345.txt", "-c"])
