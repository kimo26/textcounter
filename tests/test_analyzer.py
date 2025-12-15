"""Tests for the TextAnalyzer class."""

import pytest
from textcounter import TextAnalyzer
from textcounter.analyzer import FrequencyResult, ReadabilityResult, TextStatistics


class TestTextAnalyzerInit:
    """Tests for TextAnalyzer initialization."""

    def test_init_with_string(self):
        """Test initialization with a valid string."""
        analyzer = TextAnalyzer("Hello World")
        assert analyzer.text == "Hello World"

    def test_init_with_empty_string(self):
        """Test initialization with empty string."""
        analyzer = TextAnalyzer("")
        assert analyzer.text == ""

    def test_init_default(self):
        """Test default initialization."""
        analyzer = TextAnalyzer()
        assert analyzer.text == ""

    def test_init_with_invalid_type(self):
        """Test initialization with invalid type raises TypeError."""
        with pytest.raises(TypeError):
            TextAnalyzer(123)

    def test_text_setter(self):
        """Test setting text property."""
        analyzer = TextAnalyzer("Initial")
        analyzer.text = "Changed"
        assert analyzer.text == "Changed"


class TestCharFrequency:
    """Tests for character frequency analysis."""

    def test_basic_char_frequency(self):
        """Test basic character frequency."""
        analyzer = TextAnalyzer("hello")
        result = analyzer.char_frequency()
        assert result.frequencies["l"] == 2
        assert result.frequencies["h"] == 1

    def test_char_frequency_case_insensitive(self):
        """Test case-insensitive character frequency."""
        analyzer = TextAnalyzer("Hello")
        result = analyzer.char_frequency(case_sensitive=False)
        assert result.frequencies.get("h", 0) == 1
        assert result.frequencies.get("H", 0) == 0

    def test_char_frequency_ignore_spaces(self):
        """Test character frequency ignoring spaces."""
        analyzer = TextAnalyzer("a b c")
        result = analyzer.char_frequency(ignore_spaces=True)
        assert " " not in result.frequencies

    def test_char_frequency_top_n(self):
        """Test limiting most_common to top N."""
        analyzer = TextAnalyzer("aaabbc")
        result = analyzer.char_frequency(top_n=2)
        assert len(result.most_common) == 2
        assert result.most_common[0] == ("a", 3)


class TestWordFrequency:
    """Tests for word frequency analysis."""

    def test_basic_word_frequency(self):
        """Test basic word frequency."""
        analyzer = TextAnalyzer("hello world hello")
        result = analyzer.word_frequency()
        assert result.frequencies["hello"] == 2
        assert result.frequencies["world"] == 1

    def test_word_frequency_case_insensitive(self):
        """Test case-insensitive word frequency."""
        analyzer = TextAnalyzer("Hello HELLO hello")
        result = analyzer.word_frequency(case_sensitive=False)
        assert result.frequencies["hello"] == 3

    def test_word_frequency_min_length(self):
        """Test word frequency with minimum length."""
        analyzer = TextAnalyzer("I am a developer")
        result = analyzer.word_frequency(min_length=3)
        assert "i" not in result.frequencies
        assert "am" not in result.frequencies

    def test_word_frequency_exclude_words(self):
        """Test excluding specific words."""
        analyzer = TextAnalyzer("the cat and the dog")
        result = analyzer.word_frequency(exclude_words={"the", "and"})
        assert "the" not in result.frequencies
        assert "and" not in result.frequencies
        assert "cat" in result.frequencies

    def test_word_frequency_most_common(self):
        """Test most common words."""
        analyzer = TextAnalyzer("hello world hello hello world")
        result = analyzer.word_frequency()
        assert result.most_common[0][0] == "hello"
        assert result.most_common[0][1] == 3


class TestNgrams:
    """Tests for n-gram analysis."""

    def test_bigrams(self):
        """Test bigram generation."""
        analyzer = TextAnalyzer("the quick brown fox")
        result = analyzer.ngrams(n=2)
        assert "the quick" in result.frequencies

    def test_trigrams(self):
        """Test trigram generation."""
        analyzer = TextAnalyzer("the quick brown fox")
        result = analyzer.ngrams(n=3)
        assert "the quick brown" in result.frequencies

    def test_ngrams_case_insensitive(self):
        """Test case-insensitive n-grams."""
        analyzer = TextAnalyzer("The Quick BROWN fox")
        result = analyzer.ngrams(n=2, case_sensitive=False)
        assert "the quick" in result.frequencies

    def test_ngrams_short_text(self):
        """Test n-grams with text shorter than n."""
        analyzer = TextAnalyzer("hello")
        result = analyzer.ngrams(n=2)
        assert result.total_items == 0


class TestReadability:
    """Tests for readability analysis."""

    def test_readability_simple_text(self):
        """Test readability on simple text."""
        analyzer = TextAnalyzer("The cat sat on the mat. The dog ran fast.")
        result = analyzer.readability()
        assert isinstance(result.flesch_reading_ease, (int, float))
        assert isinstance(result.flesch_kincaid_grade, (int, float))
        assert result.complexity_rating in [
            "Very Easy", "Easy", "Fairly Easy", "Standard",
            "Fairly Difficult", "Difficult", "Very Difficult"
        ]

    def test_readability_empty_text(self):
        """Test readability on empty text."""
        analyzer = TextAnalyzer("")
        result = analyzer.readability()
        assert result.flesch_reading_ease == 0.0
        assert result.complexity_rating == "N/A"

    def test_readability_complex_text(self):
        """Test readability on more complex text."""
        complex_text = (
            "The implementation of sophisticated algorithms requires "
            "comprehensive understanding of computational complexity theory."
        )
        analyzer = TextAnalyzer(complex_text)
        result = analyzer.readability()
        # Complex text should have lower ease score
        assert result.flesch_reading_ease < 70


class TestVocabularyRichness:
    """Tests for vocabulary richness metrics."""

    def test_vocabulary_richness_ttr(self):
        """Test Type-Token Ratio calculation."""
        analyzer = TextAnalyzer("the cat and the dog")
        richness = analyzer.vocabulary_richness()
        assert 0 <= richness["ttr"] <= 1

    def test_vocabulary_richness_hapax(self):
        """Test hapax ratio calculation."""
        analyzer = TextAnalyzer("the cat and the dog")
        richness = analyzer.vocabulary_richness()
        assert 0 <= richness["hapax_ratio"] <= 1

    def test_vocabulary_richness_empty(self):
        """Test vocabulary richness on empty text."""
        analyzer = TextAnalyzer("")
        richness = analyzer.vocabulary_richness()
        assert richness["ttr"] == 0.0


class TestDistributions:
    """Tests for distribution analysis."""

    def test_word_length_distribution(self):
        """Test word length distribution."""
        analyzer = TextAnalyzer("a to the hello")
        dist = analyzer.word_length_distribution()
        assert dist[1] == 1  # "a"
        assert dist[2] == 1  # "to"
        assert dist[3] == 1  # "the"
        assert dist[5] == 1  # "hello"

    def test_sentence_length_distribution(self):
        """Test sentence length distribution."""
        analyzer = TextAnalyzer("Hi. Hello there. How are you today?")
        dist = analyzer.sentence_length_distribution()
        assert 1 in dist or 2 in dist


class TestStatistics:
    """Tests for comprehensive statistics."""

    def test_statistics_structure(self):
        """Test statistics returns correct structure."""
        analyzer = TextAnalyzer("Hello world! How are you?")
        stats = analyzer.statistics()
        assert isinstance(stats, TextStatistics)
        assert stats.word_count > 0
        assert stats.char_count > 0

    def test_statistics_values(self):
        """Test statistics values are reasonable."""
        analyzer = TextAnalyzer("Hello world")
        stats = analyzer.statistics()
        assert stats.word_count == 2
        assert stats.sentence_count >= 1


class TestPatternFinding:
    """Tests for pattern finding functionality."""

    def test_find_patterns_basic(self):
        """Test basic pattern finding."""
        analyzer = TextAnalyzer("cat and cat")
        matches = analyzer.find_patterns(r"cat")
        assert len(matches) == 2

    def test_find_patterns_case_insensitive(self):
        """Test case-insensitive pattern finding."""
        analyzer = TextAnalyzer("Cat and CAT")
        matches = analyzer.find_patterns(r"cat", case_sensitive=False)
        assert len(matches) == 2

    def test_extract_emails(self):
        """Test email extraction."""
        analyzer = TextAnalyzer("Contact test@example.com or info@site.org")
        emails = analyzer.extract_emails()
        assert len(emails) == 2
        assert "test@example.com" in emails

    def test_extract_urls(self):
        """Test URL extraction."""
        analyzer = TextAnalyzer("Visit https://example.com for more")
        urls = analyzer.extract_urls()
        assert len(urls) == 1
        assert "https://example.com" in urls[0]

    def test_extract_numbers(self):
        """Test number extraction."""
        analyzer = TextAnalyzer("Price: $19.99 for 3 items")
        numbers = analyzer.extract_numbers()
        assert "19.99" in numbers
        assert "3" in numbers


class TestComparison:
    """Tests for text comparison."""

    def test_compare_basic(self):
        """Test basic text comparison."""
        a1 = TextAnalyzer("Hello world")
        a2 = TextAnalyzer("Hello there world")
        comparison = a1.compare(a2)
        assert "word_count" in comparison
        assert "char_count" in comparison
        assert comparison["word_count"]["text1"] == 2
        assert comparison["word_count"]["text2"] == 3


class TestFrequencyResult:
    """Tests for FrequencyResult dataclass."""

    def test_percentages_calculation(self):
        """Test that percentages are calculated correctly."""
        result = FrequencyResult(
            frequencies={"a": 2, "b": 1},
            total_items=3,
            unique_items=2,
            most_common=[("a", 2), ("b", 1)],
        )
        assert abs(result.percentages["a"] - 66.67) < 1
        assert abs(result.percentages["b"] - 33.33) < 1


class TestReadabilityResult:
    """Tests for ReadabilityResult dataclass."""

    def test_repr(self):
        """Test string representation."""
        result = ReadabilityResult(
            flesch_reading_ease=70.0,
            flesch_kincaid_grade=8.0,
            avg_sentence_length=15.0,
            avg_word_length=4.5,
            complexity_rating="Standard",
        )
        assert "70.0" in repr(result)
        assert "Standard" in repr(result)


class TestDunderMethods:
    """Tests for dunder methods."""

    def test_repr(self):
        """Test __repr__ returns valid representation."""
        analyzer = TextAnalyzer("Hello")
        assert "TextAnalyzer" in repr(analyzer)
        assert "Hello" in repr(analyzer)

    def test_repr_long_text(self):
        """Test __repr__ truncates long text."""
        long_text = "a" * 100
        analyzer = TextAnalyzer(long_text)
        assert "..." in repr(analyzer)
