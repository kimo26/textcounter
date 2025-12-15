"""Tests for the TextCounter class."""

import pytest
from textcounter import TextCounter
from textcounter.counter import CountResult


class TestTextCounterInit:
    """Tests for TextCounter initialization."""

    def test_init_with_string(self):
        """Test initialization with a valid string."""
        tc = TextCounter("Hello World")
        assert tc.text == "Hello World"

    def test_init_with_empty_string(self):
        """Test initialization with empty string."""
        tc = TextCounter("")
        assert tc.text == ""

    def test_init_default(self):
        """Test default initialization."""
        tc = TextCounter()
        assert tc.text == ""

    def test_init_with_invalid_type(self):
        """Test initialization with invalid type raises TypeError."""
        with pytest.raises(TypeError):
            TextCounter(123)

    def test_text_setter(self):
        """Test setting text property."""
        tc = TextCounter("Initial")
        tc.text = "Changed"
        assert tc.text == "Changed"

    def test_text_setter_invalid_type(self):
        """Test setting text with invalid type raises TypeError."""
        tc = TextCounter("Initial")
        with pytest.raises(TypeError):
            tc.text = 123


class TestCharCount:
    """Tests for character counting functionality."""

    def test_basic_char_count(self):
        """Test basic character counting."""
        tc = TextCounter("Hello")
        result = tc.char_count()
        assert result.total == 5

    def test_char_count_with_spaces(self):
        """Test character count including spaces."""
        tc = TextCounter("Hello World")
        result = tc.char_count()
        assert result.total == 11

    def test_char_count_ignore_spaces(self):
        """Test character count ignoring spaces."""
        tc = TextCounter("Hello World")
        result = tc.char_count(ignore_spaces=True)
        assert result.total == 10
        assert "ignore_spaces" in result.options_applied

    def test_char_count_ignore_punctuation(self):
        """Test character count ignoring punctuation."""
        tc = TextCounter("Hello, World!")
        result = tc.char_count(ignore_punctuation=True)
        assert result.total == 11  # Without comma and exclamation mark

    def test_char_count_ignore_digits(self):
        """Test character count ignoring digits."""
        tc = TextCounter("Hello123")
        result = tc.char_count(ignore_digits=True)
        assert result.total == 5

    def test_char_count_ignore_newlines(self):
        """Test character count ignoring newlines."""
        tc = TextCounter("Hello\nWorld")
        result = tc.char_count(ignore_newlines=True)
        assert result.total == 10

    def test_char_count_case_insensitive(self):
        """Test case-insensitive character count."""
        tc = TextCounter("Hello")
        result = tc.char_count(case_sensitive=False)
        assert result.breakdown.get("h", 0) == 1
        assert result.breakdown.get("H", 0) == 0

    def test_char_count_custom_ignore(self):
        """Test character count with custom ignore characters."""
        tc = TextCounter("Hello World")
        result = tc.char_count(custom_ignore="lo")
        # "Hello World" without 'l' and 'o' = "He Wrd" = 6 characters
        assert result.total == 6

    def test_char_count_count_only(self):
        """Test counting only specific characters."""
        tc = TextCounter("Hello World")
        result = tc.char_count(count_only="aeiou")
        assert result.total == 3  # e, o, o

    def test_char_count_multiple_options(self):
        """Test character count with multiple options."""
        tc = TextCounter("Hello, World! 123")
        result = tc.char_count(
            ignore_spaces=True,
            ignore_punctuation=True,
            ignore_digits=True
        )
        assert result.total == 10

    def test_char_count_empty_string(self):
        """Test character count on empty string."""
        tc = TextCounter("")
        result = tc.char_count()
        assert result.total == 0

    def test_char_count_breakdown(self):
        """Test that breakdown contains correct frequencies."""
        tc = TextCounter("aab")
        result = tc.char_count()
        assert result.breakdown == {"a": 2, "b": 1}


class TestWordCount:
    """Tests for word counting functionality."""

    def test_basic_word_count(self):
        """Test basic word counting."""
        tc = TextCounter("Hello World")
        result = tc.word_count()
        assert result.total == 2

    def test_word_count_with_punctuation(self):
        """Test word count strips punctuation by default."""
        tc = TextCounter("Hello, World!")
        result = tc.word_count()
        assert result.total == 2

    def test_word_count_ignore_numbers(self):
        """Test word count ignoring pure numbers."""
        tc = TextCounter("Hello 123 World")
        result = tc.word_count(ignore_numbers=True)
        assert result.total == 2

    def test_word_count_min_length(self):
        """Test word count with minimum length filter."""
        tc = TextCounter("I am a developer")
        result = tc.word_count(min_length=2)
        assert result.total == 2  # "am" and "developer"

    def test_word_count_max_length(self):
        """Test word count with maximum length filter."""
        tc = TextCounter("I am a developer")
        result = tc.word_count(max_length=3)
        assert result.total == 3  # "I", "am", "a"

    def test_word_count_unique_only(self):
        """Test counting unique words only."""
        tc = TextCounter("hello world hello")
        result = tc.word_count(unique_only=True)
        assert result.total == 2

    def test_word_count_case_sensitive(self):
        """Test case-sensitive word count."""
        tc = TextCounter("Hello hello HELLO")
        result = tc.word_count(case_sensitive=True, unique_only=True)
        assert result.total == 3

    def test_word_count_case_insensitive(self):
        """Test case-insensitive word count."""
        tc = TextCounter("Hello hello HELLO")
        result = tc.word_count(case_sensitive=False, unique_only=True)
        assert result.total == 1

    def test_word_count_empty_string(self):
        """Test word count on empty string."""
        tc = TextCounter("")
        result = tc.word_count()
        assert result.total == 0

    def test_word_count_breakdown(self):
        """Test that breakdown contains word frequencies."""
        tc = TextCounter("hello world hello")
        result = tc.word_count()
        assert result.breakdown["hello"] == 2
        assert result.breakdown["world"] == 1


class TestLineCount:
    """Tests for line counting functionality."""

    def test_single_line(self):
        """Test counting single line."""
        tc = TextCounter("Hello World")
        result = tc.line_count()
        assert result.total == 1

    def test_multiple_lines(self):
        """Test counting multiple lines."""
        tc = TextCounter("Hello\nWorld\nTest")
        result = tc.line_count()
        assert result.total == 3

    def test_ignore_empty_lines(self):
        """Test ignoring empty lines."""
        tc = TextCounter("Hello\n\nWorld")
        result = tc.line_count(ignore_empty=True)
        assert result.total == 2

    def test_ignore_whitespace_only_lines(self):
        """Test ignoring whitespace-only lines."""
        tc = TextCounter("Hello\n   \nWorld")
        result = tc.line_count(ignore_whitespace_only=True)
        assert result.total == 2


class TestSentenceCount:
    """Tests for sentence counting functionality."""

    def test_single_sentence(self):
        """Test counting single sentence."""
        tc = TextCounter("Hello World.")
        result = tc.sentence_count()
        assert result.total == 1

    def test_multiple_sentences(self):
        """Test counting multiple sentences."""
        tc = TextCounter("Hello! How are you? I'm fine.")
        result = tc.sentence_count()
        assert result.total == 3

    def test_sentence_with_no_punctuation(self):
        """Test sentence without ending punctuation."""
        tc = TextCounter("Hello World")
        result = tc.sentence_count()
        assert result.total == 1


class TestParagraphCount:
    """Tests for paragraph counting functionality."""

    def test_single_paragraph(self):
        """Test counting single paragraph."""
        tc = TextCounter("Hello World")
        result = tc.paragraph_count()
        assert result.total == 1

    def test_multiple_paragraphs(self):
        """Test counting multiple paragraphs."""
        tc = TextCounter("Para 1\n\nPara 2\n\nPara 3")
        result = tc.paragraph_count()
        assert result.total == 3


class TestSummary:
    """Tests for summary functionality."""

    def test_summary_keys(self):
        """Test that summary contains all expected keys."""
        tc = TextCounter("Hello World!")
        summary = tc.summary()
        expected_keys = [
            "characters",
            "characters_no_spaces",
            "words",
            "lines",
            "sentences",
            "paragraphs"
        ]
        for key in expected_keys:
            assert key in summary


class TestCountResult:
    """Tests for CountResult dataclass."""

    def test_count_result_as_int(self):
        """Test using CountResult as integer."""
        result = CountResult(total=10)
        assert int(result) == 10

    def test_count_result_repr(self):
        """Test CountResult string representation."""
        result = CountResult(total=10, options_applied=["test"])
        assert "10" in repr(result)


class TestDunderMethods:
    """Tests for dunder methods."""

    def test_len(self):
        """Test __len__ returns text length."""
        tc = TextCounter("Hello")
        assert len(tc) == 5

    def test_repr(self):
        """Test __repr__ returns valid representation."""
        tc = TextCounter("Hello")
        assert "TextCounter" in repr(tc)
        assert "Hello" in repr(tc)

    def test_repr_long_text(self):
        """Test __repr__ truncates long text."""
        long_text = "a" * 100
        tc = TextCounter(long_text)
        assert "..." in repr(tc)
