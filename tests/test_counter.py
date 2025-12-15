"""
Comprehensive test suite for TextCounter module.

Tests cover all functionality including edge cases, performance characteristics,
and Pythonic interface behaviors (iterator protocol, context management, etc.).
"""

import pytest
from textcounter import TextCounter
from textcounter.counter import CountResult


class TestCountResultDataclass:
    """Tests for the CountResult container class."""

    def test_as_integer(self):
        """CountResult can be used as an integer."""
        result = CountResult(total=42, breakdown={"a": 42})
        assert int(result) == 42

    def test_addition_with_int(self):
        """CountResult supports addition with integers."""
        result = CountResult(total=10)
        assert result + 5 == 15
        assert 5 + result == 15

    def test_addition_with_count_result(self):
        """CountResult supports addition with other CountResults."""
        r1 = CountResult(total=10)
        r2 = CountResult(total=20)
        assert r1 + r2 == 30

    def test_equality_with_int(self):
        """CountResult can be compared to integers."""
        result = CountResult(total=10)
        assert result == 10
        assert not (result == 11)

    def test_comparison_operators(self):
        """CountResult supports comparison operators."""
        r1 = CountResult(total=10)
        r2 = CountResult(total=20)
        assert r1 < r2
        assert r1 < 15
        assert not (r1 < 5)

    def test_to_dict(self):
        """CountResult can be serialized to dictionary."""
        result = CountResult(total=5, breakdown={"a": 3, "b": 2})
        d = result.to_dict()
        assert d["total"] == 5
        assert d["breakdown"] == {"a": 3, "b": 2}


class TestTextCounterInit:
    """Tests for TextCounter initialization and properties."""

    def test_init_with_string(self):
        """Initialize with valid string."""
        tc = TextCounter("Hello World")
        assert tc.text == "Hello World"

    def test_init_with_empty_string(self):
        """Initialize with empty string."""
        tc = TextCounter("")
        assert tc.text == ""
        assert len(tc) == 0

    def test_init_default(self):
        """Default initialization creates empty counter."""
        tc = TextCounter()
        assert tc.text == ""

    def test_init_invalid_type_raises(self):
        """Non-string input raises TypeError."""
        with pytest.raises(TypeError, match="Expected str"):
            TextCounter(123)
        with pytest.raises(TypeError):
            TextCounter(["list"])

    def test_text_setter(self):
        """Text property can be updated."""
        tc = TextCounter("Initial")
        tc.text = "Changed"
        assert tc.text == "Changed"

    def test_text_setter_invalid_type(self):
        """Setting non-string text raises TypeError."""
        tc = TextCounter("Initial")
        with pytest.raises(TypeError):
            tc.text = 123


class TestTextCounterProtocols:
    """Tests for Python protocol implementations."""

    def test_len_protocol(self):
        """__len__ returns text length."""
        tc = TextCounter("Hello")
        assert len(tc) == 5

    def test_bool_protocol(self):
        """__bool__ returns True for non-empty text."""
        assert bool(TextCounter("Hello"))
        assert not bool(TextCounter(""))

    def test_iter_protocol(self):
        """__iter__ yields characters."""
        tc = TextCounter("ABC")
        assert list(tc) == ["A", "B", "C"]

    def test_repr(self):
        """__repr__ shows preview and length."""
        tc = TextCounter("Hello")
        assert "Hello" in repr(tc)
        assert "len=5" in repr(tc)

    def test_repr_truncates_long_text(self):
        """Long text is truncated in repr."""
        tc = TextCounter("a" * 100)
        assert "..." in repr(tc)

    def test_str(self):
        """__str__ provides human-readable summary."""
        tc = TextCounter("Hello World")
        s = str(tc)
        assert "11 chars" in s
        assert "2 words" in s

    def test_context_manager(self):
        """Context manager protocol works."""
        with TextCounter("Test") as tc:
            assert tc.char_count().total == 4


class TestCharacterCounting:
    """Tests for char_count method."""

    def test_basic_count(self):
        """Basic character count."""
        tc = TextCounter("Hello")
        assert tc.char_count().total == 5

    def test_with_spaces(self):
        """Count includes spaces by default."""
        tc = TextCounter("Hello World")
        assert tc.char_count().total == 11

    def test_ignore_spaces(self):
        """ignore_spaces excludes space characters."""
        tc = TextCounter("Hello World")
        result = tc.char_count(ignore_spaces=True)
        assert result.total == 10
        assert "ignore_spaces" in result.options_applied

    def test_ignore_punctuation(self):
        """ignore_punctuation excludes punctuation marks."""
        tc = TextCounter("Hello, World!")
        result = tc.char_count(ignore_punctuation=True)
        assert result.total == 11

    def test_ignore_digits(self):
        """ignore_digits excludes numeric characters."""
        tc = TextCounter("Hello123")
        result = tc.char_count(ignore_digits=True)
        assert result.total == 5

    def test_ignore_newlines(self):
        """ignore_newlines excludes newline characters."""
        tc = TextCounter("Hello\nWorld")
        result = tc.char_count(ignore_newlines=True)
        assert result.total == 10

    def test_case_insensitive(self):
        """case_sensitive=False normalizes to lowercase."""
        tc = TextCounter("Hello")
        result = tc.char_count(case_sensitive=False)
        assert "h" in result.breakdown
        assert "H" not in result.breakdown

    def test_custom_ignore(self):
        """custom_ignore excludes specified characters."""
        tc = TextCounter("Hello World")
        result = tc.char_count(custom_ignore="lo")
        # "Hello World" without 'l' and 'o' = "He Wrd" = 6 characters
        assert result.total == 6

    def test_count_only(self):
        """count_only restricts to specific characters."""
        tc = TextCounter("Hello World")
        result = tc.char_count(count_only="aeiou")
        assert result.total == 3  # e, o, o

    def test_multiple_options(self):
        """Multiple filtering options work together."""
        tc = TextCounter("Hello, World! 123")
        result = tc.char_count(
            ignore_spaces=True,
            ignore_punctuation=True,
            ignore_digits=True
        )
        assert result.total == 10

    def test_empty_string(self):
        """Empty string returns zero count."""
        tc = TextCounter("")
        assert tc.char_count().total == 0

    def test_breakdown_frequencies(self):
        """Breakdown contains correct frequencies."""
        tc = TextCounter("aab")
        result = tc.char_count()
        assert result.breakdown == {"a": 2, "b": 1}


class TestWordCounting:
    """Tests for word_count method."""

    def test_basic_count(self):
        """Basic word count."""
        tc = TextCounter("Hello World")
        assert tc.word_count().total == 2

    def test_strips_punctuation_by_default(self):
        """Punctuation stripped by default."""
        tc = TextCounter("Hello, World!")
        assert tc.word_count().total == 2

    def test_ignore_numbers(self):
        """ignore_numbers excludes numeric-only tokens."""
        tc = TextCounter("Hello 123 World")
        result = tc.word_count(ignore_numbers=True)
        assert result.total == 2

    def test_min_length_filter(self):
        """min_length filters short words."""
        tc = TextCounter("I am a developer")
        result = tc.word_count(min_length=2)
        assert result.total == 2  # "am" and "developer"

    def test_max_length_filter(self):
        """max_length filters long words."""
        tc = TextCounter("I am a developer")
        result = tc.word_count(max_length=3)
        assert result.total == 3  # "I", "am", "a"

    def test_unique_only(self):
        """unique_only counts each word once."""
        tc = TextCounter("hello world hello")
        result = tc.word_count(unique_only=True)
        assert result.total == 2

    def test_case_sensitive(self):
        """case_sensitive distinguishes case."""
        tc = TextCounter("Hello hello HELLO")
        result = tc.word_count(case_sensitive=True, unique_only=True)
        assert result.total == 3

    def test_case_insensitive(self):
        """case_sensitive=False normalizes words."""
        tc = TextCounter("Hello hello HELLO")
        result = tc.word_count(case_sensitive=False, unique_only=True)
        assert result.total == 1

    def test_empty_string(self):
        """Empty string returns zero count."""
        tc = TextCounter("")
        assert tc.word_count().total == 0

    def test_breakdown_frequencies(self):
        """Breakdown contains word frequencies."""
        tc = TextCounter("hello world hello")
        result = tc.word_count()
        assert result.breakdown["hello"] == 2
        assert result.breakdown["world"] == 1


class TestLineCounting:
    """Tests for line_count method."""

    def test_single_line(self):
        """Single line text."""
        tc = TextCounter("Hello World")
        assert tc.line_count().total == 1

    def test_multiple_lines(self):
        """Multi-line text."""
        tc = TextCounter("Hello\nWorld\nTest")
        assert tc.line_count().total == 3

    def test_ignore_empty_lines(self):
        """ignore_empty excludes empty lines."""
        tc = TextCounter("Hello\n\nWorld")
        result = tc.line_count(ignore_empty=True)
        assert result.total == 2

    def test_ignore_whitespace_only(self):
        """ignore_whitespace_only excludes whitespace-only lines."""
        tc = TextCounter("Hello\n   \nWorld")
        result = tc.line_count(ignore_whitespace_only=True)
        assert result.total == 2


class TestSentenceCounting:
    """Tests for sentence_count method."""

    def test_single_sentence(self):
        """Single sentence."""
        tc = TextCounter("Hello World.")
        assert tc.sentence_count().total == 1

    def test_multiple_sentences(self):
        """Multiple sentences with varied punctuation."""
        tc = TextCounter("Hello! How are you? I'm fine.")
        assert tc.sentence_count().total == 3

    def test_no_punctuation(self):
        """Text without ending punctuation."""
        tc = TextCounter("Hello World")
        assert tc.sentence_count().total == 1


class TestParagraphCounting:
    """Tests for paragraph_count method."""

    def test_single_paragraph(self):
        """Single paragraph."""
        tc = TextCounter("Hello World")
        assert tc.paragraph_count().total == 1

    def test_multiple_paragraphs(self):
        """Multiple paragraphs separated by blank lines."""
        tc = TextCounter("Para 1\n\nPara 2\n\nPara 3")
        assert tc.paragraph_count().total == 3


class TestSummary:
    """Tests for summary functionality."""

    def test_summary_keys(self):
        """Summary contains expected keys."""
        tc = TextCounter("Hello World!")
        summary = tc.get_summary()
        expected = ["characters", "characters_no_spaces", "words", "lines", "sentences", "paragraphs"]
        for key in expected:
            assert key in summary

    def test_cached_summary(self):
        """Cached summary property works."""
        tc = TextCounter("Hello World!")
        summary = tc.summary
        assert "unique_words" in summary
