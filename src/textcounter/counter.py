"""
Core counting functionality for TextCounter.

This module provides the TextCounter class for counting characters and words
in text with various filtering options.
"""

from __future__ import annotations

import string
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CountResult:
    """Result container for count operations with detailed breakdown.
    
    Attributes:
        total: Total count value.
        breakdown: Optional dictionary with detailed breakdown.
        text_length: Original text length.
        options_applied: List of options that were applied.
    """
    
    total: int
    breakdown: dict[str, int] = field(default_factory=dict)
    text_length: int = 0
    options_applied: list[str] = field(default_factory=list)
    
    def __int__(self) -> int:
        """Allow using the result as an integer."""
        return self.total
    
    def __repr__(self) -> str:
        """String representation of the count result."""
        return f"CountResult(total={self.total}, options={self.options_applied})"


class TextCounter:
    """A class for counting characters and words in text.
    
    Provides flexible counting with options to exclude whitespace,
    punctuation, and other character types.
    
    Attributes:
        text: The text to analyze.
    
    Example:
        >>> counter = TextCounter("Hello, World!")
        >>> counter.char_count()
        13
        >>> counter.char_count(ignore_spaces=True, ignore_punctuation=True)
        10
        >>> counter.word_count()
        2
    """
    
    PUNCTUATION: str = string.punctuation
    WHITESPACE: str = string.whitespace
    DIGITS: str = string.digits
    
    def __init__(self, text: str = "") -> None:
        """Initialize TextCounter with text.
        
        Args:
            text: The text to analyze. Defaults to empty string.
        
        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected string, got {type(text).__name__}")
        self._text = text
    
    @property
    def text(self) -> str:
        """Get the current text."""
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        """Set new text to analyze.
        
        Args:
            value: The new text.
        
        Raises:
            TypeError: If value is not a string.
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected string, got {type(value).__name__}")
        self._text = value
    
    def char_count(
        self,
        ignore_spaces: bool = False,
        ignore_punctuation: bool = False,
        ignore_digits: bool = False,
        ignore_newlines: bool = False,
        case_sensitive: bool = True,
        custom_ignore: Optional[str] = None,
        count_only: Optional[str] = None,
    ) -> CountResult:
        """Count characters in the text with various filtering options.
        
        Args:
            ignore_spaces: If True, spaces are not counted.
            ignore_punctuation: If True, punctuation marks are not counted.
            ignore_digits: If True, digits (0-9) are not counted.
            ignore_newlines: If True, newline characters are not counted.
            case_sensitive: If False, converts text to lowercase before counting.
            custom_ignore: String of additional characters to ignore.
            count_only: If provided, only count these specific characters.
        
        Returns:
            CountResult: Object containing the count and breakdown.
        
        Example:
            >>> tc = TextCounter("Hello World! 123")
            >>> result = tc.char_count(ignore_spaces=True, ignore_digits=True)
            >>> result.total
            11
        """
        text = self._text
        options_applied: list[str] = []
        
        if not case_sensitive:
            text = text.lower()
            options_applied.append("case_insensitive")
        
        # Build set of characters to ignore
        ignore_chars: set[str] = set()
        
        if ignore_spaces:
            ignore_chars.add(" ")
            options_applied.append("ignore_spaces")
        
        if ignore_punctuation:
            ignore_chars.update(self.PUNCTUATION)
            options_applied.append("ignore_punctuation")
        
        if ignore_digits:
            ignore_chars.update(self.DIGITS)
            options_applied.append("ignore_digits")
        
        if ignore_newlines:
            ignore_chars.update("\n\r")
            options_applied.append("ignore_newlines")
        
        if custom_ignore:
            ignore_chars.update(custom_ignore)
            options_applied.append("custom_ignore")
        
        # Count characters
        if count_only is not None:
            count_only_set = set(count_only)
            options_applied.append("count_only")
            filtered_text = [c for c in text if c in count_only_set]
        else:
            filtered_text = [c for c in text if c not in ignore_chars]
        
        # Create breakdown
        breakdown: dict[str, int] = {}
        for char in filtered_text:
            breakdown[char] = breakdown.get(char, 0) + 1
        
        return CountResult(
            total=len(filtered_text),
            breakdown=breakdown,
            text_length=len(self._text),
            options_applied=options_applied,
        )
    
    def word_count(
        self,
        ignore_punctuation: bool = True,
        ignore_numbers: bool = False,
        min_length: int = 1,
        max_length: Optional[int] = None,
        unique_only: bool = False,
        case_sensitive: bool = True,
    ) -> CountResult:
        """Count words in the text with various filtering options.
        
        Args:
            ignore_punctuation: If True, strips punctuation from words.
            ignore_numbers: If True, words that are purely numeric are not counted.
            min_length: Minimum word length to count.
            max_length: Maximum word length to count (None for no limit).
            unique_only: If True, count only unique words.
            case_sensitive: If False, treats 'Word' and 'word' as the same.
        
        Returns:
            CountResult: Object containing the count and word frequency breakdown.
        
        Example:
            >>> tc = TextCounter("Hello world hello")
            >>> result = tc.word_count(unique_only=True, case_sensitive=False)
            >>> result.total
            2
        """
        text = self._text
        options_applied: list[str] = []
        
        if not case_sensitive:
            text = text.lower()
            options_applied.append("case_insensitive")
        
        # Split into words
        words = text.split()
        
        if ignore_punctuation:
            # Strip punctuation from words
            words = [w.strip(self.PUNCTUATION) for w in words]
            options_applied.append("ignore_punctuation")
        
        # Filter out empty strings
        words = [w for w in words if w]
        
        if ignore_numbers:
            words = [w for w in words if not w.isdigit()]
            options_applied.append("ignore_numbers")
        
        if min_length > 1:
            words = [w for w in words if len(w) >= min_length]
            options_applied.append(f"min_length={min_length}")
        
        if max_length is not None:
            words = [w for w in words if len(w) <= max_length]
            options_applied.append(f"max_length={max_length}")
        
        # Create breakdown (word frequency)
        breakdown: dict[str, int] = {}
        for word in words:
            breakdown[word] = breakdown.get(word, 0) + 1
        
        if unique_only:
            total = len(breakdown)
            options_applied.append("unique_only")
        else:
            total = len(words)
        
        return CountResult(
            total=total,
            breakdown=breakdown,
            text_length=len(self._text),
            options_applied=options_applied,
        )
    
    def line_count(
        self,
        ignore_empty: bool = False,
        ignore_whitespace_only: bool = False,
    ) -> CountResult:
        """Count lines in the text.
        
        Args:
            ignore_empty: If True, empty lines are not counted.
            ignore_whitespace_only: If True, lines with only whitespace are not counted.
        
        Returns:
            CountResult: Object containing the line count.
        
        Example:
            >>> tc = TextCounter("Hello\\nWorld\\n\\nTest")
            >>> tc.line_count().total
            4
            >>> tc.line_count(ignore_empty=True).total
            3
        """
        options_applied: list[str] = []
        lines = self._text.split("\n")
        
        if ignore_whitespace_only:
            lines = [line for line in lines if line.strip()]
            options_applied.append("ignore_whitespace_only")
        elif ignore_empty:
            lines = [line for line in lines if line]
            options_applied.append("ignore_empty")
        
        # Breakdown by line length
        breakdown: dict[str, int] = {}
        for i, line in enumerate(lines, 1):
            breakdown[f"line_{i}"] = len(line)
        
        return CountResult(
            total=len(lines),
            breakdown=breakdown,
            text_length=len(self._text),
            options_applied=options_applied,
        )
    
    def sentence_count(self) -> CountResult:
        """Count sentences in the text.
        
        Sentences are detected by common ending punctuation: . ! ?
        
        Returns:
            CountResult: Object containing the sentence count.
        
        Example:
            >>> tc = TextCounter("Hello! How are you? I'm fine.")
            >>> tc.sentence_count().total
            3
        """
        import re
        
        # Split by sentence-ending punctuation
        sentences = re.split(r'[.!?]+', self._text)
        # Filter out empty strings and whitespace-only
        sentences = [s.strip() for s in sentences if s.strip()]
        
        breakdown: dict[str, int] = {}
        for i, sentence in enumerate(sentences, 1):
            breakdown[f"sentence_{i}"] = len(sentence.split())
        
        return CountResult(
            total=len(sentences),
            breakdown=breakdown,
            text_length=len(self._text),
            options_applied=[],
        )
    
    def paragraph_count(self) -> CountResult:
        """Count paragraphs in the text.
        
        Paragraphs are detected by double newlines.
        
        Returns:
            CountResult: Object containing the paragraph count.
        
        Example:
            >>> tc = TextCounter("Para 1\\n\\nPara 2\\n\\nPara 3")
            >>> tc.paragraph_count().total
            3
        """
        import re
        
        # Split by double newlines (paragraph breaks)
        paragraphs = re.split(r'\n\s*\n', self._text)
        # Filter out empty strings and whitespace-only
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        breakdown: dict[str, int] = {}
        for i, para in enumerate(paragraphs, 1):
            breakdown[f"paragraph_{i}"] = len(para.split())
        
        return CountResult(
            total=len(paragraphs),
            breakdown=breakdown,
            text_length=len(self._text),
            options_applied=[],
        )
    
    def summary(self) -> dict[str, int]:
        """Get a quick summary of all counts.
        
        Returns:
            dict: Summary with characters, words, lines, sentences, paragraphs.
        
        Example:
            >>> tc = TextCounter("Hello World!")
            >>> tc.summary()
            {'characters': 12, 'characters_no_spaces': 10, 'words': 2, 'lines': 1, 'sentences': 1, 'paragraphs': 1}
        """
        return {
            "characters": self.char_count().total,
            "characters_no_spaces": self.char_count(ignore_spaces=True).total,
            "words": self.word_count().total,
            "lines": self.line_count().total,
            "sentences": self.sentence_count().total,
            "paragraphs": self.paragraph_count().total,
        }
    
    def __len__(self) -> int:
        """Return the character count of the text."""
        return len(self._text)
    
    def __repr__(self) -> str:
        """String representation of the TextCounter."""
        preview = self._text[:50] + "..." if len(self._text) > 50 else self._text
        return f"TextCounter(text={preview!r})"
