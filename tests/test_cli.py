"""Tests for the CLI module."""

import pytest
from io import StringIO
import sys
import json
import tempfile
import os

from textcounter.cli import main, create_parser, get_text


class TestCLIParser:
    """Tests for CLI argument parsing."""

    def test_parser_creation(self):
        """Test parser is created successfully."""
        parser = create_parser()
        assert parser is not None

    def test_parser_version(self):
        """Test version argument."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_parser_chars_flag(self):
        """Test --chars flag."""
        parser = create_parser()
        args = parser.parse_args(["--chars", "-t", "test"])
        assert args.chars is True

    def test_parser_words_flag(self):
        """Test --words flag."""
        parser = create_parser()
        args = parser.parse_args(["--words", "-t", "test"])
        assert args.words is True

    def test_parser_text_input(self):
        """Test --text input."""
        parser = create_parser()
        args = parser.parse_args(["-t", "Hello World"])
        assert args.text == "Hello World"


class TestCLIMain:
    """Tests for main CLI function."""

    def test_main_with_text(self, capsys):
        """Test main with direct text input."""
        exit_code = main(["-t", "Hello World", "-c"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "11" in captured.out or "characters" in captured.out

    def test_main_all_counts(self, capsys):
        """Test main with all counts."""
        exit_code = main(["-t", "Hello World!", "-a"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "words" in captured.out.lower() or "2" in captured.out

    def test_main_json_output(self, capsys):
        """Test JSON output format."""
        exit_code = main(["-t", "Hello World", "--json", "-c"])
        captured = capsys.readouterr()
        assert exit_code == 0
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "characters" in data

    def test_main_no_spaces(self, capsys):
        """Test --no-spaces option."""
        exit_code = main(["-t", "Hello World", "-c", "--no-spaces", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["characters"] == 10

    def test_main_quiet_mode(self, capsys):
        """Test quiet mode output."""
        exit_code = main(["-t", "Hello World", "-w", "--quiet"])
        captured = capsys.readouterr()
        assert exit_code == 0
        # Should just be the number
        assert captured.out.strip() == "2"

    def test_main_word_count(self, capsys):
        """Test word counting."""
        exit_code = main(["-t", "Hello World", "-w", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["words"] == 2

    def test_main_line_count(self, capsys):
        """Test line counting."""
        exit_code = main(["-t", "Hello\nWorld", "-l", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["lines"] == 2

    def test_main_sentence_count(self, capsys):
        """Test sentence counting."""
        exit_code = main(["-t", "Hello! How are you?", "-s", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["sentences"] == 2

    def test_main_frequency_chars(self, capsys):
        """Test character frequency analysis."""
        exit_code = main(["-t", "hello", "--frequency", "chars", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "frequency" in data

    def test_main_frequency_words(self, capsys):
        """Test word frequency analysis."""
        exit_code = main(["-t", "hello world hello", "--frequency", "words", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "frequency" in data

    def test_main_readability(self, capsys):
        """Test readability analysis."""
        exit_code = main(["-t", "The cat sat on the mat.", "--readability", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "readability" in data

    def test_main_ngrams(self, capsys):
        """Test n-gram analysis."""
        exit_code = main(["-t", "the quick brown fox", "--ngrams", "2", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "ngrams" in data

    def test_main_stats(self, capsys):
        """Test comprehensive statistics."""
        exit_code = main(["-t", "Hello World!", "--stats", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "statistics" in data


class TestCLIFileInput:
    """Tests for file input handling."""

    def test_file_input(self, capsys):
        """Test reading from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
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

    def test_file_not_found(self, capsys):
        """Test error handling for missing file."""
        with pytest.raises(SystemExit):
            main(["nonexistent_file.txt", "-c"])


class TestCLIFilterOptions:
    """Tests for filtering options."""

    def test_no_punctuation(self, capsys):
        """Test --no-punctuation option."""
        exit_code = main(["-t", "Hello, World!", "-c", "--no-punctuation", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["characters"] == 11  # Without comma and exclamation

    def test_no_digits(self, capsys):
        """Test --no-digits option."""
        exit_code = main(["-t", "Hello123", "-c", "--no-digits", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["characters"] == 5

    def test_unique_words(self, capsys):
        """Test --unique option for words."""
        exit_code = main(["-t", "hello world hello", "-w", "--unique", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["words"] == 2

    def test_min_length(self, capsys):
        """Test --min-length option."""
        exit_code = main(["-t", "I am a developer", "-w", "--min-length", "3", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["words"] == 1  # Only "developer"
