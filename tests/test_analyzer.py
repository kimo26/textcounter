"""
Comprehensive test suite for TextAnalyzer module.

Tests cover frequency analysis, readability metrics, vocabulary richness,
pattern extraction, and advanced NLP-lite features.
"""

import pytest
from textcounter import TextAnalyzer
from textcounter.analyzer import FrequencyResult, ReadabilityResult, TextStatistics


class TestTextAnalyzerInit:
    """Tests for TextAnalyzer initialization."""

    def test_init_with_string(self):
        """Initialize with valid string."""
        analyzer = TextAnalyzer("Hello World")
        assert analyzer.text == "Hello World"

    def test_init_with_empty_string(self):
        """Initialize with empty string."""
        analyzer = TextAnalyzer("")
        assert analyzer.text == ""

    def test_init_default(self):
        """Default initialization."""
        analyzer = TextAnalyzer()
        assert analyzer.text == ""

    def test_init_invalid_type_raises(self):
        """Non-string input raises TypeError."""
        with pytest.raises(TypeError, match="Expected str"):
            TextAnalyzer(123)

    def test_text_setter(self):
        """Text property can be updated."""
        analyzer = TextAnalyzer("Initial")
        analyzer.text = "Changed"
        assert analyzer.text == "Changed"


class TestFrequencyResultDataclass:
    """Tests for FrequencyResult container."""

    def test_getitem(self):
        """Dict-like access works."""
        result = FrequencyResult(
            frequencies={"a": 5, "b": 3},
            total_items=8,
            unique_items=2,
            most_common=[("a", 5), ("b", 3)],
        )
        assert result["a"] == 5
        assert result["z"] == 0  # Missing key returns 0

    def test_contains(self):
        """'in' operator works."""
        result = FrequencyResult(
            frequencies={"a": 5},
            total_items=5,
            unique_items=1,
            most_common=[("a", 5)],
        )
        assert "a" in result
        assert "b" not in result

    def test_iteration(self):
        """Iteration yields most common items."""
        result = FrequencyResult(
            frequencies={"a": 5, "b": 3},
            total_items=8,
            unique_items=2,
            most_common=[("a", 5), ("b", 3)],
        )
        items = list(result)
        assert items == [("a", 5), ("b", 3)]

    def test_top_method(self):
        """top(n) returns top N items."""
        result = FrequencyResult(
            frequencies={"a": 5, "b": 3, "c": 2},
            total_items=10,
            unique_items=3,
            most_common=[("a", 5), ("b", 3), ("c", 2)],
        )
        assert result.top(2) == [("a", 5), ("b", 3)]

    def test_percentages_calculated(self):
        """Percentages are calculated on init."""
        result = FrequencyResult(
            frequencies={"a": 2, "b": 2},
            total_items=4,
            unique_items=2,
            most_common=[("a", 2), ("b", 2)],
        )
        assert result.percentages["a"] == 50.0


class TestCharacterFrequency:
    """Tests for character frequency analysis."""

    def test_basic_frequency(self):
        """Basic character frequency."""
        analyzer = TextAnalyzer("hello")
        result = analyzer.char_frequency()
        assert result["l"] == 2
        assert result["h"] == 1

    def test_case_insensitive(self):
        """Case-insensitive by default."""
        analyzer = TextAnalyzer("Hello")
        result = analyzer.char_frequency(case_sensitive=False)
        assert result["h"] == 1
        assert "H" not in result.frequencies

    def test_ignore_spaces(self):
        """Ignores spaces by default."""
        analyzer = TextAnalyzer("a b c")
        result = analyzer.char_frequency(ignore_spaces=True)
        assert " " not in result.frequencies

    def test_top_n(self):
        """top_n limits results."""
        analyzer = TextAnalyzer("aaabbc")
        result = analyzer.char_frequency(top_n=2)
        assert len(result.most_common) == 2
        assert result.most_common[0] == ("a", 3)


class TestWordFrequency:
    """Tests for word frequency analysis."""

    def test_basic_frequency(self):
        """Basic word frequency."""
        analyzer = TextAnalyzer("hello world hello")
        result = analyzer.word_frequency()
        assert result["hello"] == 2
        assert result["world"] == 1

    def test_case_insensitive(self):
        """Case-insensitive by default."""
        analyzer = TextAnalyzer("Hello HELLO hello")
        result = analyzer.word_frequency(case_sensitive=False)
        assert result["hello"] == 3

    def test_min_length(self):
        """min_length filters short words."""
        analyzer = TextAnalyzer("I am a developer")
        result = analyzer.word_frequency(min_length=3)
        assert "i" not in result.frequencies
        assert "am" not in result.frequencies

    def test_exclude_words(self):
        """exclude_words filters specified words."""
        analyzer = TextAnalyzer("the cat and the dog")
        result = analyzer.word_frequency(exclude_words={"the", "and"})
        assert "the" not in result.frequencies
        assert "and" not in result.frequencies
        assert "cat" in result.frequencies


class TestNgramAnalysis:
    """Tests for n-gram analysis."""

    def test_bigrams(self):
        """Bigram generation."""
        analyzer = TextAnalyzer("the quick brown fox")
        result = analyzer.ngrams(n=2)
        assert "the quick" in result.frequencies

    def test_trigrams(self):
        """Trigram generation."""
        analyzer = TextAnalyzer("the quick brown fox")
        result = analyzer.ngrams(n=3)
        assert "the quick brown" in result.frequencies

    def test_case_insensitive(self):
        """Case-insensitive n-grams."""
        analyzer = TextAnalyzer("The Quick BROWN fox")
        result = analyzer.ngrams(n=2, case_sensitive=False)
        assert "the quick" in result.frequencies

    def test_short_text(self):
        """Text shorter than n returns empty result."""
        analyzer = TextAnalyzer("hello")
        result = analyzer.ngrams(n=2)
        assert result.total_items == 0


class TestReadability:
    """Tests for readability analysis."""

    def test_simple_text(self):
        """Readability on simple text."""
        analyzer = TextAnalyzer("The cat sat on the mat. The dog ran fast.")
        result = analyzer.readability()
        assert isinstance(result.flesch_reading_ease, (int, float))
        assert isinstance(result.flesch_kincaid_grade, (int, float))
        assert result.complexity_rating in [
            "Very Easy", "Easy", "Fairly Easy", "Standard",
            "Fairly Difficult", "Difficult", "Very Difficult"
        ]

    def test_empty_text(self):
        """Readability on empty text."""
        analyzer = TextAnalyzer("")
        result = analyzer.readability()
        assert result.flesch_reading_ease == 0.0
        assert result.complexity_rating == "N/A"

    def test_complex_text(self):
        """Complex text has lower ease score."""
        complex_text = (
            "The implementation of sophisticated algorithms requires "
            "comprehensive understanding of computational complexity theory."
        )
        analyzer = TextAnalyzer(complex_text)
        result = analyzer.readability()
        assert result.flesch_reading_ease < 70

    def test_is_easy_property(self):
        """is_easy property works."""
        analyzer = TextAnalyzer("The cat sat.")
        result = analyzer.readability()
        assert isinstance(result.is_easy, bool)

    def test_target_audience(self):
        """target_audience property works."""
        analyzer = TextAnalyzer("The cat sat.")
        result = analyzer.readability()
        assert result.target_audience in [
            "Elementary school", "Middle school", "High school",
            "College", "Graduate/Professional"
        ]


class TestVocabularyRichness:
    """Tests for vocabulary richness metrics."""

    def test_ttr(self):
        """Type-Token Ratio is calculated."""
        analyzer = TextAnalyzer("the cat and the dog")
        richness = analyzer.vocabulary_richness()
        assert 0 <= richness["ttr"] <= 1

    def test_hapax_ratio(self):
        """Hapax ratio is calculated."""
        analyzer = TextAnalyzer("the cat and the dog")
        richness = analyzer.vocabulary_richness()
        assert 0 <= richness["hapax_ratio"] <= 1

    def test_yules_k(self):
        """Yule's K is calculated."""
        analyzer = TextAnalyzer("the cat and the dog")
        richness = analyzer.vocabulary_richness()
        assert "yules_k" in richness

    def test_empty_text(self):
        """Empty text returns zeros."""
        analyzer = TextAnalyzer("")
        richness = analyzer.vocabulary_richness()
        assert richness["ttr"] == 0.0


class TestDistributions:
    """Tests for distribution analysis."""

    def test_word_length_distribution(self):
        """Word length distribution."""
        analyzer = TextAnalyzer("a to the hello")
        dist = analyzer.word_length_distribution()
        assert dist[1] == 1  # "a"
        assert dist[2] == 1  # "to"
        assert dist[3] == 1  # "the"
        assert dist[5] == 1  # "hello"

    def test_sentence_length_distribution(self):
        """Sentence length distribution."""
        analyzer = TextAnalyzer("Hi. Hello there. How are you today?")
        dist = analyzer.sentence_length_distribution()
        assert 1 in dist or 2 in dist


class TestStatistics:
    """Tests for comprehensive statistics."""

    def test_statistics_structure(self):
        """Statistics returns correct structure."""
        analyzer = TextAnalyzer("Hello world! How are you?")
        stats = analyzer.get_statistics()
        assert isinstance(stats, TextStatistics)
        assert stats.word_count > 0
        assert stats.char_count > 0

    def test_cached_statistics(self):
        """Cached statistics property works."""
        analyzer = TextAnalyzer("Hello world!")
        stats = analyzer.statistics
        assert isinstance(stats, TextStatistics)

    def test_statistics_to_dict(self):
        """Statistics can be serialized."""
        analyzer = TextAnalyzer("Hello world!")
        stats = analyzer.get_statistics()
        d = stats.to_dict()
        assert "words" in d


class TestPatternExtraction:
    """Tests for pattern finding and extraction."""

    def test_find_patterns(self):
        """Basic pattern finding."""
        analyzer = TextAnalyzer("cat and cat")
        matches = analyzer.find_patterns(r"cat")
        assert len(matches) == 2

    def test_find_patterns_case_insensitive(self):
        """Case-insensitive pattern finding."""
        analyzer = TextAnalyzer("Cat and CAT")
        matches = analyzer.find_patterns(r"cat", case_sensitive=False)
        assert len(matches) == 2

    def test_extract_emails(self):
        """Email extraction."""
        analyzer = TextAnalyzer("Contact test@example.com or info@site.org")
        emails = analyzer.extract_emails()
        assert len(emails) == 2
        assert "test@example.com" in emails

    def test_extract_urls(self):
        """URL extraction."""
        analyzer = TextAnalyzer("Visit https://example.com for more")
        urls = analyzer.extract_urls()
        assert len(urls) == 1
        assert "https://example.com" in urls[0]

    def test_extract_numbers(self):
        """Number extraction."""
        analyzer = TextAnalyzer("Price: $19.99 for 3 items")
        numbers = analyzer.extract_numbers()
        assert "19.99" in numbers
        assert "3" in numbers


class TestComparison:
    """Tests for text comparison."""

    def test_compare(self):
        """Basic comparison."""
        a1 = TextAnalyzer("Hello world")
        a2 = TextAnalyzer("Hello there world")
        comparison = a1.compare(a2)
        assert "word_count" in comparison
        assert comparison["word_count"]["text1"] == 2
        assert comparison["word_count"]["text2"] == 3


class TestDunderMethods:
    """Tests for dunder methods."""

    def test_repr(self):
        """__repr__ works."""
        analyzer = TextAnalyzer("Hello")
        assert "TextAnalyzer" in repr(analyzer)

    def test_str(self):
        """__str__ provides summary."""
        analyzer = TextAnalyzer("Hello world. Test.")
        s = str(analyzer)
        assert "words" in s
        assert "sentences" in s
