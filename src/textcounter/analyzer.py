"""
Advanced text analysis and NLP-lite tools.

This module provides the TextAnalyzer class for comprehensive text analytics.
All algorithms are implemented from scratch without relying on external
libraries or heavy standard library abstractions like dataclasses.

Demonstrates: algorithm design, caching strategies, computational linguistics.
"""

from __future__ import annotations

import re
import string
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, TypeVar

from textcounter.counter import CountResult, TextCounter

# Type variable for generic operations
T = TypeVar("T")


def memoize(func: Callable[..., T]) -> Callable[..., T]:
    """Custom memoization decorator.

    Hand-implemented caching decorator demonstrating decorator patterns
    and closure-based state management. Uses weak references for methods.

    This is a simplified version that caches based on instance + method name.
    """
    cache: Dict[int, T] = {}

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> T:
        # Create cache key from instance id and arguments
        key = hash((id(self), args, tuple(sorted(kwargs.items()))))

        if key not in cache:
            cache[key] = func(self, *args, **kwargs)

        return cache[key]

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper._cache = cache  # type: ignore

    return wrapper


class FrequencyResult:
    """Container for frequency analysis results.

    Hand-implemented class with full Python protocol support.
    Provides dict-like access, iteration, and statistical methods.
    """

    __slots__ = ("_frequencies", "_total", "_unique", "_most_common", "_percentages")

    def __init__(
        self,
        frequencies: Dict[str, int],
        total_items: int,
        unique_items: int,
        most_common: List[Tuple[str, int]],
    ) -> None:
        """Initialize with pre-computed values."""
        self._frequencies = frequencies
        self._total = total_items
        self._unique = unique_items
        self._most_common = most_common

        # Compute percentages
        self._percentages: Dict[str, float] = {}
        if total_items > 0:
            for key, count in frequencies.items():
                self._percentages[key] = round((count / total_items) * 100, 2)

    @property
    def frequencies(self) -> Dict[str, int]:
        """Frequency mapping (copy for immutability)."""
        return dict(self._frequencies)

    @property
    def total_items(self) -> int:
        """Total item count."""
        return self._total

    @property
    def unique_items(self) -> int:
        """Unique item count."""
        return self._unique

    @property
    def most_common(self) -> List[Tuple[str, int]]:
        """Most common items (copy)."""
        return list(self._most_common)

    @property
    def percentages(self) -> Dict[str, float]:
        """Percentage distribution."""
        return dict(self._percentages)

    # Dict-like access
    def __getitem__(self, key: str) -> int:
        """Get frequency of item."""
        return self._frequencies.get(key, 0)

    def __contains__(self, key: str) -> bool:
        """Check if item exists."""
        return key in self._frequencies

    def __len__(self) -> int:
        """Number of unique items."""
        return self._unique

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        """Iterate over most common items."""
        return iter(self._most_common)

    def __bool__(self) -> bool:
        """True if any items exist."""
        return self._total > 0

    def __repr__(self) -> str:
        """Debug representation."""
        return f"FrequencyResult(total={self._total}, unique={self._unique})"

    def top(self, n: int = 10) -> List[Tuple[str, int]]:
        """Get top N items."""
        return self._most_common[:n]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "frequencies": self._frequencies,
            "total": self._total,
            "unique": self._unique,
            "top_10": self._most_common[:10],
        }


class ReadabilityResult:
    """Container for readability analysis results.

    Implements Flesch-Kincaid readability formulas.
    Immutable value object pattern.
    """

    __slots__ = (
        "_flesch_ease",
        "_flesch_grade",
        "_avg_sentence_len",
        "_avg_word_len",
        "_avg_syllables",
        "_rating",
    )

    def __init__(
        self,
        flesch_reading_ease: float,
        flesch_kincaid_grade: float,
        avg_sentence_length: float,
        avg_word_length: float,
        avg_syllables_per_word: float,
        complexity_rating: str,
    ) -> None:
        """Initialize with all metrics."""
        self._flesch_ease = flesch_reading_ease
        self._flesch_grade = flesch_kincaid_grade
        self._avg_sentence_len = avg_sentence_length
        self._avg_word_len = avg_word_length
        self._avg_syllables = avg_syllables_per_word
        self._rating = complexity_rating

    @property
    def flesch_reading_ease(self) -> float:
        """Flesch Reading Ease score (0-100+)."""
        return self._flesch_ease

    @property
    def flesch_kincaid_grade(self) -> float:
        """Flesch-Kincaid Grade Level."""
        return self._flesch_grade

    @property
    def avg_sentence_length(self) -> float:
        """Average words per sentence."""
        return self._avg_sentence_len

    @property
    def avg_word_length(self) -> float:
        """Average characters per word."""
        return self._avg_word_len

    @property
    def avg_syllables_per_word(self) -> float:
        """Average syllables per word."""
        return self._avg_syllables

    @property
    def complexity_rating(self) -> str:
        """Human-readable rating."""
        return self._rating

    @property
    def is_easy(self) -> bool:
        """True if text is easy to read (grade 8 or below)."""
        return self._flesch_ease >= 60

    @property
    def target_audience(self) -> str:
        """Suggested target audience."""
        grade = self._flesch_grade
        if grade <= 5:
            return "Elementary school"
        elif grade <= 8:
            return "Middle school"
        elif grade <= 12:
            return "High school"
        elif grade <= 16:
            return "College"
        return "Graduate/Professional"

    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"ReadabilityResult(ease={self._flesch_ease:.1f}, "
            f"grade={self._flesch_grade:.1f}, rating='{self._rating}')"
        )

    def __eq__(self, other: object) -> bool:
        """Compare by all metrics."""
        if not isinstance(other, ReadabilityResult):
            return NotImplemented
        return (
            self._flesch_ease == other._flesch_ease
            and self._flesch_grade == other._flesch_grade
        )

    def __hash__(self) -> int:
        """Hash by metrics."""
        return hash((self._flesch_ease, self._flesch_grade, self._rating))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "flesch_reading_ease": self._flesch_ease,
            "flesch_kincaid_grade": self._flesch_grade,
            "avg_sentence_length": self._avg_sentence_len,
            "avg_word_length": self._avg_word_len,
            "avg_syllables_per_word": self._avg_syllables,
            "complexity_rating": self._rating,
            "is_easy": self.is_easy,
            "target_audience": self.target_audience,
        }


class TextStatistics:
    """Comprehensive text statistics container.

    Aggregates all metrics with lazy computation support.
    """

    __slots__ = (
        "_char_count",
        "_word_count",
        "_unique_word_count",
        "_sentence_count",
        "_paragraph_count",
        "_avg_word_len",
        "_avg_sentence_len",
        "_vocab_richness",
        "_char_freq",
        "_word_freq",
    )

    def __init__(
        self,
        char_count: int,
        word_count: int,
        unique_word_count: int,
        sentence_count: int,
        paragraph_count: int,
        avg_word_length: float,
        avg_sentence_length: float,
        vocabulary_richness: float,
        char_frequency: FrequencyResult,
        word_frequency: FrequencyResult,
    ) -> None:
        """Initialize with all statistics."""
        self._char_count = char_count
        self._word_count = word_count
        self._unique_word_count = unique_word_count
        self._sentence_count = sentence_count
        self._paragraph_count = paragraph_count
        self._avg_word_len = avg_word_length
        self._avg_sentence_len = avg_sentence_length
        self._vocab_richness = vocabulary_richness
        self._char_freq = char_frequency
        self._word_freq = word_frequency

    # Properties for all fields
    @property
    def char_count(self) -> int:
        return self._char_count

    @property
    def word_count(self) -> int:
        return self._word_count

    @property
    def unique_word_count(self) -> int:
        return self._unique_word_count

    @property
    def sentence_count(self) -> int:
        return self._sentence_count

    @property
    def paragraph_count(self) -> int:
        return self._paragraph_count

    @property
    def avg_word_length(self) -> float:
        return self._avg_word_len

    @property
    def avg_sentence_length(self) -> float:
        return self._avg_sentence_len

    @property
    def vocabulary_richness(self) -> float:
        return self._vocab_richness

    @property
    def char_frequency(self) -> FrequencyResult:
        return self._char_freq

    @property
    def word_frequency(self) -> FrequencyResult:
        return self._word_freq

    def __repr__(self) -> str:
        return f"TextStatistics(words={self._word_count}, chars={self._char_count})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "characters": self._char_count,
            "words": self._word_count,
            "unique_words": self._unique_word_count,
            "sentences": self._sentence_count,
            "paragraphs": self._paragraph_count,
            "avg_word_length": self._avg_word_len,
            "avg_sentence_length": self._avg_sentence_len,
            "vocabulary_richness": self._vocab_richness,
        }


class TextAnalyzer:
    """Advanced text analysis engine.

    Provides comprehensive analytics including frequency analysis,
    readability metrics, vocabulary richness, and pattern extraction.

    All algorithms are implemented from scratch to demonstrate
    deep understanding of computational linguistics.
    """

    __slots__ = ("_text", "_counter", "_cache")

    # Pre-compiled patterns for performance
    _EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    _URL_PATTERN = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
    _NUMBER_PATTERN = re.compile(r"-?\d+\.?\d*")

    # Vowels for syllable counting
    VOWELS: frozenset = frozenset("aeiouyAEIOUY")

    def __init__(self, text: str = "") -> None:
        """Initialize analyzer."""
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")
        self._text = text
        self._counter = TextCounter(text)
        self._cache: Dict[str, Any] = {}

    @property
    def text(self) -> str:
        """Get analyzed text."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """Set new text and clear caches."""
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")
        self._text = value
        self._counter.text = value
        self._cache.clear()

    def _get_words(self, case_sensitive: bool = False) -> List[str]:
        """Extract cleaned words from text.

        Custom tokenization without external dependencies.
        """
        text = self._text if case_sensitive else self._text.lower()
        words: List[str] = []
        current: List[str] = []

        for char in text:
            if char.isspace():
                if current:
                    word = "".join(current)
                    # Strip punctuation from boundaries
                    word = self._strip_punctuation(word)
                    if word:
                        words.append(word)
                    current = []
            else:
                current.append(char)

        # Last word
        if current:
            word = "".join(current)
            word = self._strip_punctuation(word)
            if word:
                words.append(word)

        return words

    @staticmethod
    def _strip_punctuation(word: str) -> str:
        """Strip punctuation from word boundaries."""
        punctuation = set(string.punctuation)

        start = 0
        while start < len(word) and word[start] in punctuation:
            start += 1

        end = len(word) - 1
        while end >= start and word[end] in punctuation:
            end -= 1

        return word[start : end + 1]

    def _sort_by_frequency(self, items: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        """Sort items by frequency descending, then alphabetically.

        Uses merge sort for stable O(n log n) performance.
        Hand-implemented to demonstrate algorithm knowledge.
        """
        if len(items) <= 1:
            return items

        mid = len(items) // 2
        left = self._sort_by_frequency(items[:mid])
        right = self._sort_by_frequency(items[mid:])

        return self._merge(left, right)

    def _merge(
        self, left: List[Tuple[str, int]], right: List[Tuple[str, int]]
    ) -> List[Tuple[str, int]]:
        """Merge two sorted lists.

        Comparison: higher frequency first, then alphabetical.
        """
        result: List[Tuple[str, int]] = []
        i = j = 0

        while i < len(left) and j < len(right):
            # Compare by frequency (descending)
            if left[i][1] > right[j][1]:
                result.append(left[i])
                i += 1
            elif left[i][1] < right[j][1]:
                result.append(right[j])
                j += 1
            else:
                # Equal frequency: sort alphabetically
                if left[i][0] <= right[j][0]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def char_frequency(
        self,
        case_sensitive: bool = False,
        ignore_spaces: bool = True,
        ignore_punctuation: bool = False,
        top_n: Optional[int] = None,
    ) -> FrequencyResult:
        """Analyze character frequency.

        Single-pass O(n) algorithm with custom sorting.
        """
        result = self._counter.char_count(
            ignore_spaces=ignore_spaces,
            ignore_punctuation=ignore_punctuation,
            case_sensitive=case_sensitive,
        )

        frequencies = result.breakdown
        items = list(frequencies.items())
        sorted_items = self._sort_by_frequency(items)

        most_common = sorted_items[:top_n] if top_n else sorted_items

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
        exclude_words: Optional[Set[str]] = None,
    ) -> FrequencyResult:
        """Analyze word frequency.

        Supports stopword filtering and minimum length.
        """
        result = self._counter.word_count(
            case_sensitive=case_sensitive,
            min_length=min_length,
        )

        frequencies = dict(result.breakdown)

        # Apply exclusion filter
        if exclude_words:
            exclude_normalized = {
                w.lower() if not case_sensitive else w for w in exclude_words
            }
            frequencies = {
                k: v for k, v in frequencies.items() if k not in exclude_normalized
            }

        # Sort and limit
        items = list(frequencies.items())
        sorted_items = self._sort_by_frequency(items)
        most_common = sorted_items[:top_n] if top_n else sorted_items

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
        """Generate n-gram frequency analysis.

        Custom sliding window implementation.
        """
        words = self._get_words(case_sensitive)

        if len(words) < n:
            return FrequencyResult(
                frequencies={},
                total_items=0,
                unique_items=0,
                most_common=[],
            )

        # Sliding window for n-gram generation
        frequencies: Dict[str, int] = {}
        total = 0

        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i : i + n])
            if ngram in frequencies:
                frequencies[ngram] += 1
            else:
                frequencies[ngram] = 1
            total += 1

        items = list(frequencies.items())
        sorted_items = self._sort_by_frequency(items)
        most_common = sorted_items[:top_n] if top_n else sorted_items

        return FrequencyResult(
            frequencies=frequencies,
            total_items=total,
            unique_items=len(frequencies),
            most_common=most_common,
        )

    def _count_syllables(self, word: str) -> int:
        """Estimate syllables using vowel-counting heuristic.

        Custom implementation of syllable counting algorithm.
        Handles common English patterns including:
        - Silent 'e' at end
        - Consecutive vowels (diphthongs)
        - '-le' endings after consonants

        This is a simplified version; perfect syllable counting
        requires a pronunciation dictionary.
        """
        word = word.lower().strip()
        if not word:
            return 0

        count = 0
        prev_is_vowel = False

        for char in word:
            is_vowel = char in self.VOWELS

            # Count vowel groups (not individual vowels)
            if is_vowel and not prev_is_vowel:
                count += 1

            prev_is_vowel = is_vowel

        # Handle silent 'e' at end (not part of -le)
        if word.endswith("e") and count > 1 and len(word) >= 2 and word[-2] not in "l":
            count -= 1

        # Handle '-le' endings (e.g., "table", "simple")
        if len(word) >= 3 and word.endswith("le") and word[-3] not in self.VOWELS:
            count += 1

        # Handle common patterns that reduce syllables
        # '-ed' is usually silent unless preceded by t or d
        if word.endswith("ed") and len(word) > 2 and word[-3] not in "td":
            count = max(1, count - 1)

        return max(1, count)

    def readability(self) -> ReadabilityResult:
        """Calculate Flesch-Kincaid readability metrics.

        Implements standard formulas used in education:

        Flesch Reading Ease = 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
        Flesch-Kincaid Grade = 0.39(words/sentences) + 11.8(syllables/words) - 15.59

        Score Interpretation:
            90-100: Very Easy (5th grade)
            80-89:  Easy (6th grade)
            70-79:  Fairly Easy (7th grade)
            60-69:  Standard (8th-9th grade)
            50-59:  Fairly Difficult (10th-12th grade)
            30-49:  Difficult (College)
            0-29:   Very Difficult (Graduate)
        """
        words_result = self._counter.word_count()
        sentences_result = self._counter.sentence_count()

        word_count = words_result.total
        sentence_count = max(1, sentences_result.total)

        words = self._get_words()

        if not words:
            return ReadabilityResult(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                avg_sentence_length=0.0,
                avg_word_length=0.0,
                avg_syllables_per_word=0.0,
                complexity_rating="N/A",
            )

        # Calculate syllables
        total_syllables = 0
        total_chars = 0
        for word in words:
            total_syllables += self._count_syllables(word)
            total_chars += len(word)

        # Calculate averages
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = total_syllables / max(1, word_count)
        avg_word_length = total_chars / len(words)

        # Flesch Reading Ease formula
        flesch_ease = (
            206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        )

        # Flesch-Kincaid Grade Level formula
        flesch_kincaid = (
            (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        )

        # Determine complexity rating based on ease score
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
            avg_syllables_per_word=round(avg_syllables_per_word, 2),
            complexity_rating=rating,
        )

    def vocabulary_richness(self) -> Dict[str, float]:
        """Calculate vocabulary richness metrics.

        Implements three standard computational linguistics measures:

        1. TTR (Type-Token Ratio): unique_words / total_words
           Range: 0-1, higher = more diverse vocabulary

        2. Hapax Legomena Ratio: words_appearing_once / total_words
           Range: 0-1, higher = more unique word usage

        3. Yule's K Characteristic:
           K = 10^4 * (Σ(m² * V_m) - N) / N²
           where V_m = words appearing exactly m times
           Lower K = more diverse vocabulary
        """
        result = self._counter.word_count(case_sensitive=False)
        frequencies = result.breakdown
        total_words = result.total
        unique_words = len(frequencies)

        if total_words == 0:
            return {"ttr": 0.0, "hapax_ratio": 0.0, "yules_k": 0.0}

        # Type-Token Ratio
        ttr = unique_words / total_words

        # Hapax legomena (words appearing exactly once)
        hapax_count = 0
        for count in frequencies.values():
            if count == 1:
                hapax_count += 1
        hapax_ratio = hapax_count / total_words

        # Yule's K characteristic
        # First, compute frequency-of-frequencies (spectrum)
        freq_spectrum: Dict[int, int] = {}
        for count in frequencies.values():
            if count in freq_spectrum:
                freq_spectrum[count] += 1
            else:
                freq_spectrum[count] = 1

        # Calculate sum term: Σ(m² * V_m)
        sum_term = 0
        for freq, num_words in freq_spectrum.items():
            sum_term += (freq**2) * num_words

        # Yule's K formula
        if total_words > 1:
            yules_k = 10000 * (sum_term - total_words) / (total_words**2)
        else:
            yules_k = 0.0

        return {
            "ttr": round(ttr, 4),
            "hapax_ratio": round(hapax_ratio, 4),
            "yules_k": round(yules_k, 4),
        }

    def word_length_distribution(self) -> Dict[int, int]:
        """Get distribution of word lengths.

        Returns dict mapping word_length -> count of words.
        """
        words = self._get_words()
        distribution: Dict[int, int] = {}

        for word in words:
            length = len(word)
            if length in distribution:
                distribution[length] += 1
            else:
                distribution[length] = 1

        # Sort by key (word length)
        return dict(sorted(distribution.items()))

    def sentence_length_distribution(self) -> Dict[int, int]:
        """Get distribution of sentence lengths.

        Returns dict mapping sentence_length (in words) -> count.
        """
        sentences = self._split_sentences()
        distribution: Dict[int, int] = {}

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Count words in sentence
            word_count = 0
            in_word = False
            for char in sentence:
                if char.isspace():
                    in_word = False
                elif not in_word:
                    word_count += 1
                    in_word = True

            if word_count > 0:
                if word_count in distribution:
                    distribution[word_count] += 1
                else:
                    distribution[word_count] = 1

        return dict(sorted(distribution.items()))

    def _split_sentences(self) -> List[str]:
        """Split text into sentences.

        Custom sentence boundary detection without regex.
        """
        sentences: List[str] = []
        current: List[str] = []
        terminators = frozenset(".!?")

        i = 0
        while i < len(self._text):
            char = self._text[i]
            current.append(char)

            if char in terminators:
                # Skip consecutive terminators
                while i + 1 < len(self._text) and self._text[i + 1] in terminators:
                    i += 1
                    current.append(self._text[i])

                sentence = "".join(current).strip()
                if sentence:
                    sentences.append(sentence)
                current = []

            i += 1

        # Handle text without ending punctuation
        if current:
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)

        return sentences

    @property
    def statistics(self) -> TextStatistics:
        """Get comprehensive statistics.

        Uses internal caching for performance.
        """
        cache_key = "statistics"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._compute_statistics()
        return self._cache[cache_key]

    def _compute_statistics(self) -> TextStatistics:
        """Compute all statistics."""
        char_result = self._counter.char_count()
        word_result = self._counter.word_count()
        sentence_result = self._counter.sentence_count()
        paragraph_result = self._counter.paragraph_count()

        words = self._get_words()

        # Calculate averages
        if words:
            total_chars = sum(len(w) for w in words)
            avg_word_length = total_chars / len(words)
        else:
            avg_word_length = 0.0

        avg_sentence_length = (
            word_result.total / sentence_result.total
            if sentence_result.total > 0
            else 0.0
        )

        unique_words = len(word_result.breakdown)
        vocab_richness = (
            unique_words / word_result.total if word_result.total > 0 else 0.0
        )

        return TextStatistics(
            char_count=char_result.total,
            word_count=word_result.total,
            unique_word_count=unique_words,
            sentence_count=sentence_result.total,
            paragraph_count=paragraph_result.total,
            avg_word_length=round(avg_word_length, 2),
            avg_sentence_length=round(avg_sentence_length, 2),
            vocabulary_richness=round(vocab_richness, 4),
            char_frequency=self.char_frequency(),
            word_frequency=self.word_frequency(),
        )

    def get_statistics(self) -> TextStatistics:
        """Get statistics (method version)."""
        return self._compute_statistics()

    def find_patterns(
        self,
        pattern: str,
        case_sensitive: bool = False,
    ) -> List[Tuple[int, int, str]]:
        """Find regex pattern matches.

        Returns list of (start, end, matched_text) tuples.
        """
        flags = 0 if case_sensitive else re.IGNORECASE
        matches: List[Tuple[int, int, str]] = []

        for match in re.finditer(pattern, self._text, flags):
            matches.append((match.start(), match.end(), match.group()))

        return matches

    def extract_emails(self) -> List[str]:
        """Extract email addresses."""
        return self._EMAIL_PATTERN.findall(self._text)

    def extract_urls(self) -> List[str]:
        """Extract URLs with trailing punctuation stripped."""
        urls = self._URL_PATTERN.findall(self._text)

        # Strip trailing punctuation manually
        cleaned: List[str] = []
        trailing = set(".,;:!?)")
        for url in urls:
            while url and url[-1] in trailing:
                url = url[:-1]
            if url:
                cleaned.append(url)

        return cleaned

    def extract_numbers(self) -> List[str]:
        """Extract numeric values."""
        return self._NUMBER_PATTERN.findall(self._text)

    def compare(self, other: "TextAnalyzer") -> Dict[str, Dict[str, float]]:
        """Compare with another text.

        Returns comparison metrics with differences.
        """
        stats1 = self._compute_statistics()
        stats2 = other._compute_statistics()

        return {
            "word_count": {
                "text1": float(stats1.word_count),
                "text2": float(stats2.word_count),
                "difference": float(stats2.word_count - stats1.word_count),
            },
            "char_count": {
                "text1": float(stats1.char_count),
                "text2": float(stats2.char_count),
                "difference": float(stats2.char_count - stats1.char_count),
            },
            "avg_word_length": {
                "text1": stats1.avg_word_length,
                "text2": stats2.avg_word_length,
                "difference": round(stats2.avg_word_length - stats1.avg_word_length, 2),
            },
            "vocabulary_richness": {
                "text1": stats1.vocabulary_richness,
                "text2": stats2.vocabulary_richness,
                "difference": round(
                    stats2.vocabulary_richness - stats1.vocabulary_richness, 4
                ),
            },
        }

    def __repr__(self) -> str:
        """Debug representation."""
        preview = self._text[:40] + "..." if len(self._text) > 40 else self._text
        return f"TextAnalyzer({preview!r})"

    def __str__(self) -> str:
        """Human-readable summary."""
        stats = self._compute_statistics()
        return (
            f"TextAnalyzer: {stats.word_count} words, {stats.sentence_count} sentences"
        )


