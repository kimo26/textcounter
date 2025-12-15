"""
Command-line interface for TextCounter.

Provides a CLI for counting characters, words, and analyzing text from
files or standard input.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from textcounter import TextCounter, TextAnalyzer, __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="textcounter",
        description="Count characters, words, and analyze text",
        epilog="Example: textcounter -c -w myfile.txt",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        help="Input file (reads from stdin if not provided)",
    )
    
    parser.add_argument(
        "-t", "--text",
        type=str,
        help="Direct text input (alternative to file)",
    )
    
    # Counting options
    count_group = parser.add_argument_group("Counting Options")
    
    count_group.add_argument(
        "-c", "--chars",
        action="store_true",
        help="Count characters",
    )
    
    count_group.add_argument(
        "-w", "--words",
        action="store_true",
        help="Count words",
    )
    
    count_group.add_argument(
        "-l", "--lines",
        action="store_true",
        help="Count lines",
    )
    
    count_group.add_argument(
        "-s", "--sentences",
        action="store_true",
        help="Count sentences",
    )
    
    count_group.add_argument(
        "-p", "--paragraphs",
        action="store_true",
        help="Count paragraphs",
    )
    
    count_group.add_argument(
        "-a", "--all",
        action="store_true",
        help="Show all counts (summary)",
    )
    
    # Filtering options
    filter_group = parser.add_argument_group("Filtering Options")
    
    filter_group.add_argument(
        "--no-spaces",
        action="store_true",
        help="Ignore spaces when counting characters",
    )
    
    filter_group.add_argument(
        "--no-punctuation",
        action="store_true",
        help="Ignore punctuation when counting",
    )
    
    filter_group.add_argument(
        "--no-digits",
        action="store_true",
        help="Ignore digits when counting characters",
    )
    
    filter_group.add_argument(
        "--unique",
        action="store_true",
        help="Count only unique words",
    )
    
    filter_group.add_argument(
        "--min-length",
        type=int,
        default=1,
        help="Minimum word length to count (default: 1)",
    )
    
    # Analysis options
    analysis_group = parser.add_argument_group("Analysis Options")
    
    analysis_group.add_argument(
        "--frequency",
        choices=["chars", "words"],
        help="Show frequency analysis for characters or words",
    )
    
    analysis_group.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top items in frequency analysis (default: 10)",
    )
    
    analysis_group.add_argument(
        "--readability",
        action="store_true",
        help="Show readability analysis",
    )
    
    analysis_group.add_argument(
        "--ngrams",
        type=int,
        metavar="N",
        help="Show N-gram analysis (e.g., --ngrams 2 for bigrams)",
    )
    
    analysis_group.add_argument(
        "--stats",
        action="store_true",
        help="Show comprehensive statistics",
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    
    output_group.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    output_group.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (numbers only)",
    )
    
    return parser


def get_text(args: argparse.Namespace) -> str:
    """Get text from file, argument, or stdin.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        The text to analyze.
    """
    if args.text:
        return args.text
    
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        except PermissionError:
            print(f"Error: Permission denied reading '{args.file}'.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Read from stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()
    
    print("Enter text (Ctrl+D to finish):", file=sys.stderr)
    return sys.stdin.read()


def format_output(
    label: str,
    value: int | float | str,
    quiet: bool = False,
) -> str:
    """Format output based on quiet mode.
    
    Args:
        label: Description of the value.
        value: The value to display.
        quiet: If True, only show the value.
    
    Returns:
        Formatted output string.
    """
    if quiet:
        return str(value)
    return f"{label}: {value}"


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).
    
    Returns:
        Exit code (0 for success).
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Get text to analyze
    text = get_text(args)
    
    if not text.strip():
        print("Warning: Empty text provided.", file=sys.stderr)
    
    counter = TextCounter(text)
    analyzer = TextAnalyzer(text)
    
    results: dict[str, int | float | str | dict] = {}
    
    # Determine what to count
    show_all = args.all or not any([
        args.chars, args.words, args.lines,
        args.sentences, args.paragraphs,
        args.frequency, args.readability,
        args.ngrams, args.stats,
    ])
    
    # Character count
    if args.chars or show_all:
        result = counter.char_count(
            ignore_spaces=args.no_spaces,
            ignore_punctuation=args.no_punctuation,
            ignore_digits=args.no_digits,
        )
        results["characters"] = result.total
    
    # Word count
    if args.words or show_all:
        result = counter.word_count(
            ignore_punctuation=args.no_punctuation,
            min_length=args.min_length,
            unique_only=args.unique,
        )
        results["words"] = result.total
    
    # Line count
    if args.lines or show_all:
        result = counter.line_count()
        results["lines"] = result.total
    
    # Sentence count
    if args.sentences or show_all:
        result = counter.sentence_count()
        results["sentences"] = result.total
    
    # Paragraph count
    if args.paragraphs or show_all:
        result = counter.paragraph_count()
        results["paragraphs"] = result.total
    
    # Frequency analysis
    if args.frequency:
        if args.frequency == "chars":
            freq = analyzer.char_frequency(
                ignore_spaces=args.no_spaces,
                ignore_punctuation=args.no_punctuation,
                top_n=args.top,
            )
        else:
            freq = analyzer.word_frequency(
                min_length=args.min_length,
                top_n=args.top,
            )
        results["frequency"] = {
            "most_common": freq.most_common,
            "unique_count": freq.unique_items,
            "total_count": freq.total_items,
        }
    
    # Readability analysis
    if args.readability:
        read = analyzer.readability()
        results["readability"] = {
            "flesch_reading_ease": read.flesch_reading_ease,
            "flesch_kincaid_grade": read.flesch_kincaid_grade,
            "avg_sentence_length": read.avg_sentence_length,
            "avg_word_length": read.avg_word_length,
            "complexity_rating": read.complexity_rating,
        }
    
    # N-gram analysis
    if args.ngrams:
        ngrams = analyzer.ngrams(n=args.ngrams, top_n=args.top)
        results["ngrams"] = {
            "n": args.ngrams,
            "most_common": ngrams.most_common,
            "unique_count": ngrams.unique_items,
        }
    
    # Comprehensive statistics
    if args.stats:
        stats = analyzer.statistics
        richness = analyzer.vocabulary_richness()
        results["statistics"] = {
            "char_count": stats.char_count,
            "word_count": stats.word_count,
            "sentence_count": stats.sentence_count,
            "paragraph_count": stats.paragraph_count,
            "avg_word_length": stats.avg_word_length,
            "avg_sentence_length": stats.avg_sentence_length,
            "vocabulary_richness": stats.vocabulary_richness,
            "ttr": richness["ttr"],
            "hapax_ratio": richness["hapax_ratio"],
        }
    
    # Output results
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        for key, value in results.items():
            if isinstance(value, dict):
                if not args.quiet:
                    print(f"\n{key.upper()}:")
                for k, v in value.items():
                    if isinstance(v, list):
                        if not args.quiet:
                            print(f"  {k}:")
                        for item in v:
                            if isinstance(item, tuple):
                                print(f"    {item[0]}: {item[1]}")
                            else:
                                print(f"    {item}")
                    else:
                        print(format_output(f"  {k}", v, args.quiet))
            else:
                print(format_output(key, value, args.quiet))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
