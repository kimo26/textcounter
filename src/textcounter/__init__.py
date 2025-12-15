"""
TextCounter - A powerful text analysis library.

A comprehensive library for counting characters, words, and performing
data analysis on text with flexible options.

Example:
    >>> from textcounter import TextCounter
    >>> tc = TextCounter("Hello, World!")
    >>> tc.char_count()
    13
    >>> tc.char_count(ignore_spaces=True)
    12
    >>> tc.word_count()
    2
"""

from textcounter.analyzer import TextAnalyzer
from textcounter.counter import TextCounter

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "TextCounter",
    "TextAnalyzer",
    "__version__",
]
