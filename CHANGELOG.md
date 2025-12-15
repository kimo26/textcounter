# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added

- Initial release of TextCounter
- `TextCounter` class for counting characters, words, lines, sentences, and paragraphs
- Character counting with options:
  - Ignore spaces
  - Ignore punctuation
  - Ignore digits
  - Ignore newlines
  - Case sensitivity
  - Custom character ignore list
  - Count only specific characters
- Word counting with options:
  - Ignore punctuation
  - Ignore numbers
  - Minimum/maximum length filters
  - Unique words only
  - Case sensitivity
- `TextAnalyzer` class for advanced text analysis
- Character and word frequency analysis
- N-gram analysis (bigrams, trigrams, etc.)
- Readability metrics:
  - Flesch Reading Ease
  - Flesch-Kincaid Grade Level
- Vocabulary richness metrics:
  - Type-Token Ratio (TTR)
  - Hapax Ratio
  - Yule's K
- Word and sentence length distributions
- Pattern extraction:
  - Email addresses
  - URLs
  - Numbers
  - Custom regex patterns
- Text comparison functionality
- Full-featured CLI with JSON output support
- Comprehensive test suite with 95%+ coverage
- Full type hint support
- Zero runtime dependencies
