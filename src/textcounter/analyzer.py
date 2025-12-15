"""
Data analysis tools for text analysis.

This module provides the TextAnalyzer class for advanced text analytics
including frequency analysis, readability metrics, and statistical insights.
"""

from __future__ import annotations

import math
import string
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from textcounter.counter import TextCounter


@dataclass
class FrequencyResult:
    """Container for frequency analysis results.
    
    Attributes:
        frequencies: Dictionary mapping items to their counts.
        total_items: Total number of items analyzed.
        unique_items: Number of unique items.
        most_common: List of (item, count) tuples for most common items.
        percentages: Dictionary mapping items to their percentage of total.
    """
    
    frequencies: dict[str, int]
    total_items: int
    unique_items: int
    most_common: list[tuple[str, int]]
    percentages: dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Calculate percentages after initialization."""
        if self.total_items > 0:
            self.percentages = {
                k: (v / self.total_items) * 100
                for k, v in self.frequencies.items()
            }


@dataclass
class ReadabilityResult:
    """Container for readability analysis results.
    
    Attributes:
        flesch_reading_ease: Flesch Reading Ease score (0-100+).
        flesch_kincaid_grade: Flesch-Kincaid Grade Level.
        avg_sentence_length: Average number of words per sentence.
        avg_word_length: Average number of characters per word.
        complexity_rating: Human-readable complexity rating.
    """
    
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    avg_sentence_length: float
    avg_word_length: float
    complexity_rating: str
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ReadabilityResult(flesch_ease={self.flesch_reading_ease:.1f}, "
            f"grade_level={self.flesch_kincaid_grade:.1f}, "
            f"rating='{self.complexity_rating}')"
        )


@dataclass
class TextStatistics:
    """Container for comprehensive text statistics.
    
    Attributes:
        char_count: Total character count.
        word_count: Total word count.
        sentence_count: Total sentence count.
        paragraph_count: Total paragraph count.
        avg_word_length: Average word length in characters.
        avg_sentence_length: Average sentence length in words.
        vocabulary_richness: Ratio of unique words to total words.
        char_frequency: Character frequency analysis.
        word_frequency: Word frequency analysis.
    """
    
    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_word_length: float
    avg_sentence_length: float
    vocabulary_richness: float
    char_frequency: FrequencyResult
    word_frequency: FrequencyResult


class TextAnalyzer:
    """Advanced text analysis with statistics and insights.
    
    Provides frequency analysis, readability metrics, pattern detection,
    and comprehensive statistical analysis of text.
    
    Example:
        >>> analyzer = TextAnalyzer("Hello world! Hello everyone.")
        >>> freq = analyzer.word_frequency()
        >>> freq.most_common[0]
        ('hello', 2)
    """
    
    def __init__(self, text: str = "") -> None:
        """Initialize TextAnalyzer with text.
        
        Args:
            text: The text to analyze.
        
        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected string, got {type(text).__name__}")
        self._text = text
        self._counter = TextCounter(text)
    
    @property
    def text(self) -> str:
        """Get the current text."""
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        """Set new text to analyze.
        
        Args:
            value: The new text.
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected string, got {type(value).__name__}")
        self._text = value
        self._counter.text = value
    
    def char_frequency(
        self,
        case_sensitive: bool = False,
        ignore_spaces: bool = True,
        ignore_punctuation: bool = False,
        top_n: Optional[int] = None,
    ) -> FrequencyResult:
        """Analyze character frequency in the text.
        
        Args:
            case_sensitive: If False, treats 'A' and 'a' as the same.
            ignore_spaces: If True, spaces are not included.
            ignore_punctuation: If True, punctuation is not included.
            top_n: If provided, limit most_common to top N items.
        
        Returns:
            FrequencyResult: Character frequency analysis.
        
        Example:
            >>> analyzer = TextAnalyzer("Hello")
            >>> freq = analyzer.char_frequency()
            >>> freq.frequencies['l']
            2
        """
        result = self._counter.char_count(
            ignore_spaces=ignore_spaces,
            ignore_punctuation=ignore_punctuation,
            case_sensitive=case_sensitive,
        )
        
        frequencies = result.breakdown
        counter = Counter(frequencies)
        most_common = counter.most_common(top_n)
        
        return FrequencyResult(
            frequencies=frequencies,
            total_items=result.total,
            unique_items=len(frequencies),
            most_common=most_common,
        )
    
    def word_frequency(
        self,
        case_sensitive: bool = False,
        min_length: int = 1,
        top_n: Optional[int] = None,
        exclude_words: Optional[set[str]] = None,
    ) -> FrequencyResult:
        """Analyze word frequency in the text.
        
        Args:
            case_sensitive: If False, treats 'Word' and 'word' as the same.
            min_length: Minimum word length to include.
            top_n: If provided, limit most_common to top N items.
            exclude_words: Set of words to exclude from analysis.
        
        Returns:
            FrequencyResult: Word frequency analysis.
        
        Example:
            >>> analyzer = TextAnalyzer("hello world hello")
            >>> freq = analyzer.word_frequency()
            >>> freq.most_common[0]
            ('hello', 2)
        """
        result = self._counter.word_count(
            case_sensitive=case_sensitive,
            min_length=min_length,
        )
        
        frequencies = result.breakdown
        
        if exclude_words:
            exclude = {w.lower() if not case_sensitive else w for w in exclude_words}
            frequencies = {
                k: v for k, v in frequencies.items()
                if (k.lower() if not case_sensitive else k) not in exclude
            }
        
        counter = Counter(frequencies)
        most_common = counter.most_common(top_n)
        total = sum(frequencies.values())
        
        return FrequencyResult(
            frequencies=frequencies,
            total_items=total,
            unique_items=len(frequencies),
            most_common=most_common,
        )
    
    def ngrams(
        self,
        n: int = 2,
        case_sensitive: bool = False,
        top_n: Optional[int] = 10,
    ) -> FrequencyResult:
        """Generate and analyze n-grams from the text.
        
        Args:
            n: Size of n-grams (2 for bigrams, 3 for trigrams, etc.).
            case_sensitive: If False, converts to lowercase.
            top_n: Limit most_common to top N items.
        
        Returns:
            FrequencyResult: N-gram frequency analysis.
        
        Example:
            >>> analyzer = TextAnalyzer("the quick brown fox")
            >>> bigrams = analyzer.ngrams(n=2)
            >>> len(bigrams.frequencies) > 0
            True
        """
        text = self._text if case_sensitive else self._text.lower()
        words = [
            w.strip(string.punctuation)
            for w in text.split()
            if w.strip(string.punctuation)
        ]
        
        if len(words) < n:
            return FrequencyResult(
                frequencies={},
                total_items=0,
                unique_items=0,
                most_common=[],
            )
        
        ngram_list = [
            " ".join(words[i:i + n])
            for i in range(len(words) - n + 1)
        ]
        
        frequencies: dict[str, int] = {}
        for ngram in ngram_list:
            frequencies[ngram] = frequencies.get(ngram, 0) + 1
        
        counter = Counter(frequencies)
        most_common = counter.most_common(top_n)
        
        return FrequencyResult(
            frequencies=frequencies,
            total_items=len(ngram_list),
            unique_items=len(frequencies),
            most_common=most_common,
        )
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word.
        
        Uses a simple vowel-counting heuristic.
        
        Args:
            word: The word to count syllables for.
        
        Returns:
            Estimated syllable count (minimum 1).
        """
        word = word.lower().strip()
        if not word:
            return 0
        
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        
        # Handle silent e
        if word.endswith("e") and count > 1:
            count -= 1
        
        # Handle endings
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            count += 1
        
        return max(1, count)
    
    def readability(self) -> ReadabilityResult:
        """Calculate readability metrics for the text.
        
        Computes Flesch Reading Ease and Flesch-Kincaid Grade Level.
        
        Returns:
            ReadabilityResult: Readability metrics and rating.
        
        Example:
            >>> analyzer = TextAnalyzer("The cat sat on the mat.")
            >>> result = analyzer.readability()
            >>> result.complexity_rating in ['Very Easy', 'Easy', 'Fairly Easy', 
            ...     'Standard', 'Fairly Difficult', 'Difficult', 'Very Difficult']
            True
        """
        # Get word and sentence counts
        words_result = self._counter.word_count()
        sentences_result = self._counter.sentence_count()
        
        word_count = words_result.total
        sentence_count = max(1, sentences_result.total)
        
        # Get words for syllable counting
        text = self._text.lower()
        words = [
            w.strip(string.punctuation)
            for w in text.split()
            if w.strip(string.punctuation)
        ]
        
        if not words:
            return ReadabilityResult(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                avg_sentence_length=0.0,
                avg_word_length=0.0,
                complexity_rating="N/A",
            )
        
        # Calculate syllables
        total_syllables = sum(self._count_syllables(w) for w in words)
        
        # Calculate averages
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = total_syllables / max(1, word_count)
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        # Flesch Reading Ease
        # Score = 206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)
        flesch_ease = (
            206.835
            - (1.015 * avg_sentence_length)
            - (84.6 * avg_syllables_per_word)
        )
        
        # Flesch-Kincaid Grade Level
        # Grade = 0.39 × (words/sentences) + 11.8 × (syllables/words) - 15.59
        flesch_kincaid = (
            (0.39 * avg_sentence_length)
            + (11.8 * avg_syllables_per_word)
            - 15.59
        )
        
        # Determine complexity rating
        if flesch_ease >= 90:
            rating = "Very Easy"
        elif flesch_ease >= 80:
            rating = "Easy"
        elif flesch_ease >= 70:
            rating = "Fairly Easy"
        elif flesch_ease >= 60:
            rating = "Standard"
        elif flesch_ease >= 50:
            rating = "Fairly Difficult"
        elif flesch_ease >= 30:
            rating = "Difficult"
        else:
            rating = "Very Difficult"
        
        return ReadabilityResult(
            flesch_reading_ease=round(flesch_ease, 2),
            flesch_kincaid_grade=round(max(0, flesch_kincaid), 2),
            avg_sentence_length=round(avg_sentence_length, 2),
            avg_word_length=round(avg_word_length, 2),
            complexity_rating=rating,
        )
    
    def vocabulary_richness(self) -> dict[str, float]:
        """Calculate vocabulary richness metrics.
        
        Returns:
            dict: Dictionary with various richness metrics.
                - ttr: Type-Token Ratio (unique words / total words)
                - hapax_ratio: Proportion of words appearing only once
                - yules_k: Yule's K measure of vocabulary richness
        
        Example:
            >>> analyzer = TextAnalyzer("the cat and the dog and the bird")
            >>> richness = analyzer.vocabulary_richness()
            >>> 0 <= richness['ttr'] <= 1
            True
        """
        result = self._counter.word_count(case_sensitive=False)
        frequencies = result.breakdown
        total_words = result.total
        unique_words = len(frequencies)
        
        if total_words == 0:
            return {
                "ttr": 0.0,
                "hapax_ratio": 0.0,
                "yules_k": 0.0,
            }
        
        # Type-Token Ratio
        ttr = unique_words / total_words
        
        # Hapax legomena ratio (words appearing only once)
        hapax_count = sum(1 for count in frequencies.values() if count == 1)
        hapax_ratio = hapax_count / total_words
        
        # Yule's K characteristic
        # K = 10^4 * (Σ(freq_i² * i) - N) / N²
        freq_of_freqs: dict[int, int] = {}
        for count in frequencies.values():
            freq_of_freqs[count] = freq_of_freqs.get(count, 0) + 1
        
        sum_term = sum(
            (freq ** 2) * count
            for freq, count in freq_of_freqs.items()
        )
        
        yules_k = 10000 * (sum_term - total_words) / (total_words ** 2) if total_words > 1 else 0
        
        return {
            "ttr": round(ttr, 4),
            "hapax_ratio": round(hapax_ratio, 4),
            "yules_k": round(yules_k, 4),
        }
    
    def word_length_distribution(self) -> dict[int, int]:
        """Get distribution of word lengths.
        
        Returns:
            dict: Mapping of word length to count of words with that length.
        
        Example:
            >>> analyzer = TextAnalyzer("a to the hello")
            >>> dist = analyzer.word_length_distribution()
            >>> dist[1]  # One-letter words
            1
        """
        words = [
            w.strip(string.punctuation)
            for w in self._text.lower().split()
            if w.strip(string.punctuation)
        ]
        
        distribution: dict[int, int] = {}
        for word in words:
            length = len(word)
            distribution[length] = distribution.get(length, 0) + 1
        
        return dict(sorted(distribution.items()))
    
    def sentence_length_distribution(self) -> dict[int, int]:
        """Get distribution of sentence lengths (in words).
        
        Returns:
            dict: Mapping of sentence length to count of sentences with that length.
        
        Example:
            >>> analyzer = TextAnalyzer("Hi. Hello there. How are you doing today?")
            >>> dist = analyzer.sentence_length_distribution()
            >>> 1 in dist or 2 in dist  # Should have short sentences
            True
        """
        import re
        
        sentences = re.split(r'[.!?]+', self._text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        distribution: dict[int, int] = {}
        for sentence in sentences:
            words = [w for w in sentence.split() if w.strip(string.punctuation)]
            length = len(words)
            if length > 0:
                distribution[length] = distribution.get(length, 0) + 1
        
        return dict(sorted(distribution.items()))
    
    def statistics(self) -> TextStatistics:
        """Get comprehensive text statistics.
        
        Returns:
            TextStatistics: Complete statistical analysis of the text.
        
        Example:
            >>> analyzer = TextAnalyzer("Hello world! How are you?")
            >>> stats = analyzer.statistics()
            >>> stats.word_count > 0
            True
        """
        char_result = self._counter.char_count()
        word_result = self._counter.word_count()
        sentence_result = self._counter.sentence_count()
        paragraph_result = self._counter.paragraph_count()
        
        # Calculate averages
        words = [
            w.strip(string.punctuation)
            for w in self._text.lower().split()
            if w.strip(string.punctuation)
        ]
        
        avg_word_length = (
            sum(len(w) for w in words) / len(words)
            if words else 0.0
        )
        
        avg_sentence_length = (
            word_result.total / sentence_result.total
            if sentence_result.total > 0 else 0.0
        )
        
        # Vocabulary richness
        unique_words = len(word_result.breakdown)
        vocab_richness = (
            unique_words / word_result.total
            if word_result.total > 0 else 0.0
        )
        
        return TextStatistics(
            char_count=char_result.total,
            word_count=word_result.total,
            sentence_count=sentence_result.total,
            paragraph_count=paragraph_result.total,
            avg_word_length=round(avg_word_length, 2),
            avg_sentence_length=round(avg_sentence_length, 2),
            vocabulary_richness=round(vocab_richness, 4),
            char_frequency=self.char_frequency(),
            word_frequency=self.word_frequency(),
        )
    
    def find_patterns(
        self,
        pattern: str,
        case_sensitive: bool = False,
    ) -> list[tuple[int, int, str]]:
        """Find all occurrences of a regex pattern in the text.
        
        Args:
            pattern: Regular expression pattern to search for.
            case_sensitive: If False, search is case-insensitive.
        
        Returns:
            List of tuples (start_pos, end_pos, matched_text).
        
        Example:
            >>> analyzer = TextAnalyzer("Contact: test@email.com or info@site.org")
            >>> emails = analyzer.find_patterns(r'\\w+@\\w+\\.\\w+')
            >>> len(emails)
            2
        """
        import re
        
        flags = 0 if case_sensitive else re.IGNORECASE
        matches = []
        
        for match in re.finditer(pattern, self._text, flags):
            matches.append((match.start(), match.end(), match.group()))
        
        return matches
    
    def extract_emails(self) -> list[str]:
        """Extract email addresses from the text.
        
        Returns:
            List of email addresses found.
        
        Example:
            >>> analyzer = TextAnalyzer("Contact me at test@example.com")
            >>> analyzer.extract_emails()
            ['test@example.com']
        """
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return [match[2] for match in self.find_patterns(pattern)]
    
    def extract_urls(self) -> list[str]:
        """Extract URLs from the text.
        
        Returns:
            List of URLs found.
        
        Example:
            >>> analyzer = TextAnalyzer("Visit https://example.com for more")
            >>> analyzer.extract_urls()
            ['https://example.com']
        """
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return [match[2].rstrip('.,;:!?)') for match in self.find_patterns(pattern)]
    
    def extract_numbers(self) -> list[str]:
        """Extract numbers from the text.
        
        Returns:
            List of number strings found (integers and decimals).
        
        Example:
            >>> analyzer = TextAnalyzer("The price is $19.99 for 3 items")
            >>> '19.99' in analyzer.extract_numbers()
            True
        """
        pattern = r'-?\d+\.?\d*'
        return [match[2] for match in self.find_patterns(pattern)]
    
    def compare(self, other: "TextAnalyzer") -> dict[str, dict[str, float]]:
        """Compare this text with another TextAnalyzer.
        
        Args:
            other: Another TextAnalyzer instance to compare with.
        
        Returns:
            Dictionary with comparison metrics.
        
        Example:
            >>> a1 = TextAnalyzer("Hello world")
            >>> a2 = TextAnalyzer("Hello there world")
            >>> comparison = a1.compare(a2)
            >>> 'word_count' in comparison
            True
        """
        stats1 = self.statistics()
        stats2 = other.statistics()
        
        return {
            "word_count": {
                "text1": stats1.word_count,
                "text2": stats2.word_count,
                "difference": stats2.word_count - stats1.word_count,
            },
            "char_count": {
                "text1": stats1.char_count,
                "text2": stats2.char_count,
                "difference": stats2.char_count - stats1.char_count,
            },
            "avg_word_length": {
                "text1": stats1.avg_word_length,
                "text2": stats2.avg_word_length,
                "difference": round(stats2.avg_word_length - stats1.avg_word_length, 2),
            },
            "vocabulary_richness": {
                "text1": stats1.vocabulary_richness,
                "text2": stats2.vocabulary_richness,
                "difference": round(stats2.vocabulary_richness - stats1.vocabulary_richness, 4),
            },
        }
    
    def __repr__(self) -> str:
        """String representation of the TextAnalyzer."""
        preview = self._text[:50] + "..." if len(self._text) > 50 else self._text
        return f"TextAnalyzer(text={preview!r})"
