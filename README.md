# TextCounter

[![PyPI version](https://badge.fury.io/py/textcounter.svg)](https://badge.fury.io/py/textcounter)
[![Python versions](https://img.shields.io/pypi/pyversions/textcounter.svg)](https://pypi.org/project/textcounter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/textcounter/workflows/Tests/badge.svg)](https://github.com/yourusername/textcounter/actions)
[![codecov](https://codecov.io/gh/yourusername/textcounter/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/textcounter)

A powerful, flexible Python library for counting characters, words, and performing comprehensive text analysis. Perfect for writers, developers, data scientists, and anyone working with text data.

## ✨ Features

- **Character Counting** - Count with options to ignore spaces, punctuation, digits, and more
- **Word Counting** - Count words with filters for length, uniqueness, and case sensitivity
- **Line/Sentence/Paragraph Counting** - Comprehensive text structure analysis
- **Frequency Analysis** - Character and word frequency with percentages
- **N-gram Analysis** - Generate and analyze bigrams, trigrams, and more
- **Readability Metrics** - Flesch Reading Ease, Flesch-Kincaid Grade Level
- **Vocabulary Richness** - Type-Token Ratio, Hapax Ratio, Yule's K
- **Pattern Extraction** - Extract emails, URLs, numbers using regex
- **CLI Tool** - Full-featured command-line interface
- **Zero Dependencies** - Pure Python, no external dependencies required
- **Type Hints** - Full type annotation support for better IDE integration

## 📦 Installation

```bash
pip install textcounter
```

For development:
```bash
pip install textcounter[dev]
```

## 🚀 Quick Start

### Basic Usage

```python
from textcounter import TextCounter, TextAnalyzer

# Character counting
counter = TextCounter("Hello, World!")
print(counter.char_count().total)  # 13
print(counter.char_count(ignore_spaces=True).total)  # 12
print(counter.char_count(ignore_punctuation=True).total)  # 11

# Word counting
counter = TextCounter("The quick brown fox jumps over the lazy dog")
print(counter.word_count().total)  # 9
print(counter.word_count(unique_only=True).total)  # 8 (two "the"s)
print(counter.word_count(min_length=4).total)  # 5

# Get a quick summary
print(counter.summary())
# {'characters': 43, 'characters_no_spaces': 35, 'words': 9, 'lines': 1, 'sentences': 1, 'paragraphs': 1}
```

### Advanced Character Counting

```python
from textcounter import TextCounter

text = "Hello World! 123"
counter = TextCounter(text)

# Ignore multiple character types
result = counter.char_count(
    ignore_spaces=True,
    ignore_punctuation=True,
    ignore_digits=True
)
print(result.total)  # 10

# Count only specific characters
result = counter.char_count(count_only="aeiou")
print(result.total)  # 3 (e, o, o)

# Get character breakdown
result = counter.char_count()
print(result.breakdown)  # {'H': 1, 'e': 1, 'l': 3, 'o': 2, ...}
```

### Word Counting Options

```python
from textcounter import TextCounter

text = "Hello HELLO hello World world"
counter = TextCounter(text)

# Case-insensitive unique words
result = counter.word_count(case_sensitive=False, unique_only=True)
print(result.total)  # 2 (hello, world)

# Filter by word length
counter = TextCounter("I am a Python developer")
result = counter.word_count(min_length=3, max_length=6)
print(result.total)  # 2 (Python has 6 chars, developer has 9)

# Ignore numbers
counter = TextCounter("There are 5 apples and 3 oranges")
result = counter.word_count(ignore_numbers=True)
print(result.total)  # 5
```

### Text Analysis

```python
from textcounter import TextAnalyzer

analyzer = TextAnalyzer("The quick brown fox jumps over the lazy dog. The dog barks.")

# Word frequency analysis
freq = analyzer.word_frequency()
print(freq.most_common[:3])  # [('the', 3), ('dog', 2), ('quick', 1), ...]
print(freq.percentages['the'])  # Percentage of total words

# Character frequency
char_freq = analyzer.char_frequency(ignore_spaces=True)
print(char_freq.most_common[:5])

# N-gram analysis (bigrams, trigrams, etc.)
bigrams = analyzer.ngrams(n=2, top_n=5)
print(bigrams.most_common)  # [('the quick', 1), ('quick brown', 1), ...]

trigrams = analyzer.ngrams(n=3, top_n=5)
print(trigrams.most_common)
```

### Readability Analysis

```python
from textcounter import TextAnalyzer

text = """
The implementation of sophisticated algorithms requires comprehensive 
understanding of computational complexity theory and data structures.
"""

analyzer = TextAnalyzer(text)
readability = analyzer.readability()

print(f"Flesch Reading Ease: {readability.flesch_reading_ease}")
print(f"Flesch-Kincaid Grade: {readability.flesch_kincaid_grade}")
print(f"Complexity Rating: {readability.complexity_rating}")
print(f"Avg Sentence Length: {readability.avg_sentence_length}")
print(f"Avg Word Length: {readability.avg_word_length}")
```

### Vocabulary Richness

```python
from textcounter import TextAnalyzer

analyzer = TextAnalyzer("The cat sat on the mat while the dog ran around the yard")
richness = analyzer.vocabulary_richness()

print(f"Type-Token Ratio: {richness['ttr']}")  # Unique words / Total words
print(f"Hapax Ratio: {richness['hapax_ratio']}")  # Words appearing only once
print(f"Yule's K: {richness['yules_k']}")  # Vocabulary richness measure
```

### Pattern Extraction

```python
from textcounter import TextAnalyzer

text = """
Contact us at support@example.com or sales@company.org.
Visit https://example.com for pricing starting at $19.99.
Call us at 555-1234 for 24/7 support.
"""

analyzer = TextAnalyzer(text)

# Extract emails
emails = analyzer.extract_emails()
print(emails)  # ['support@example.com', 'sales@company.org']

# Extract URLs
urls = analyzer.extract_urls()
print(urls)  # ['https://example.com']

# Extract numbers
numbers = analyzer.extract_numbers()
print(numbers)  # ['19.99', '555', '1234', '24', '7']

# Custom pattern matching
phone_patterns = analyzer.find_patterns(r'\d{3}-\d{4}')
print(phone_patterns)  # [(start, end, '555-1234')]
```

### Comprehensive Statistics

```python
from textcounter import TextAnalyzer

analyzer = TextAnalyzer("Your text here...")
stats = analyzer.statistics()

print(f"Characters: {stats.char_count}")
print(f"Words: {stats.word_count}")
print(f"Sentences: {stats.sentence_count}")
print(f"Paragraphs: {stats.paragraph_count}")
print(f"Avg Word Length: {stats.avg_word_length}")
print(f"Avg Sentence Length: {stats.avg_sentence_length}")
print(f"Vocabulary Richness: {stats.vocabulary_richness}")
```

### Comparing Texts

```python
from textcounter import TextAnalyzer

text1 = TextAnalyzer("The quick brown fox")
text2 = TextAnalyzer("The slow red fox jumps high")

comparison = text1.compare(text2)
print(comparison)
# {
#     'word_count': {'text1': 4, 'text2': 6, 'difference': 2},
#     'char_count': {...},
#     'avg_word_length': {...},
#     'vocabulary_richness': {...}
# }
```

## 💻 Command-Line Interface

TextCounter includes a powerful CLI for quick text analysis.

### Basic Usage

```bash
# Count characters and words in a file
textcounter myfile.txt

# Count only characters
textcounter -c myfile.txt

# Count words
textcounter -w myfile.txt

# Direct text input
textcounter -t "Hello World" -c -w
```

### Filtering Options

```bash
# Ignore spaces and punctuation
textcounter -c --no-spaces --no-punctuation myfile.txt

# Count unique words only
textcounter -w --unique myfile.txt

# Minimum word length
textcounter -w --min-length 4 myfile.txt
```

### Analysis Commands

```bash
# Character frequency (top 10)
textcounter --frequency chars --top 10 myfile.txt

# Word frequency
textcounter --frequency words --top 20 myfile.txt

# Readability analysis
textcounter --readability myfile.txt

# N-gram analysis
textcounter --ngrams 2 myfile.txt  # Bigrams
textcounter --ngrams 3 myfile.txt  # Trigrams

# Comprehensive statistics
textcounter --stats myfile.txt
```

### Output Options

```bash
# JSON output
textcounter --json myfile.txt

# Quiet mode (numbers only)
textcounter -w --quiet myfile.txt

# Pipe from stdin
cat myfile.txt | textcounter -c -w
echo "Hello World" | textcounter --json
```

### Full Example

```bash
$ textcounter -t "The quick brown fox jumps over the lazy dog." --stats --json
{
  "statistics": {
    "char_count": 44,
    "word_count": 9,
    "sentence_count": 1,
    "paragraph_count": 1,
    "avg_word_length": 3.89,
    "avg_sentence_length": 9.0,
    "vocabulary_richness": 0.8889,
    "ttr": 0.8889,
    "hapax_ratio": 0.7778
  }
}
```

## 📊 API Reference

### TextCounter Class

| Method | Description |
|--------|-------------|
| `char_count(...)` | Count characters with filtering options |
| `word_count(...)` | Count words with filtering options |
| `line_count(...)` | Count lines |
| `sentence_count()` | Count sentences |
| `paragraph_count()` | Count paragraphs |
| `summary()` | Get all counts as a dictionary |

### TextAnalyzer Class

| Method | Description |
|--------|-------------|
| `char_frequency(...)` | Analyze character frequency |
| `word_frequency(...)` | Analyze word frequency |
| `ngrams(n, ...)` | Generate n-gram analysis |
| `readability()` | Calculate readability metrics |
| `vocabulary_richness()` | Calculate vocabulary metrics |
| `word_length_distribution()` | Get word length distribution |
| `sentence_length_distribution()` | Get sentence length distribution |
| `statistics()` | Get comprehensive statistics |
| `find_patterns(pattern)` | Find regex patterns |
| `extract_emails()` | Extract email addresses |
| `extract_urls()` | Extract URLs |
| `extract_numbers()` | Extract numbers |
| `compare(other)` | Compare with another analyzer |

## 🧪 Development

### Setup

```bash
git clone https://github.com/yourusername/textcounter.git
cd textcounter
pip install -e .[dev]
```

### Running Tests

```bash
pytest
pytest --cov=textcounter --cov-report=html
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint
ruff check src tests

# Type checking
mypy src
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📬 Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/textcounter/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/textcounter/discussions)

## 🙏 Acknowledgments

- Inspired by classic Unix tools like `wc`
- Readability formulas based on Flesch-Kincaid research
- Built with ❤️ for the Python community
