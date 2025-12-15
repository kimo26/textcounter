# Contributing to TextCounter

Thank you for your interest in contributing to TextCounter! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/kimo26/textcounter/issues)
2. If not, create a new issue with:
   - A clear, descriptive title
   - Steps to reproduce the bug
   - Expected behavior
   - Actual behavior
   - Python version and OS
   - Minimal code example if possible

### Suggesting Features

1. Check if the feature has been suggested in [Issues](https://github.com/kimo26/textcounter/issues)
2. Create a new issue with:
   - A clear, descriptive title
   - Detailed description of the proposed feature
   - Use cases and examples
   - Any potential implementation ideas

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Add tests for new functionality
5. Run the test suite:
   ```bash
   pytest
   ```
6. Run code quality checks:
   ```bash
   black src tests
   isort src tests
   ruff check src tests
   mypy src
   ```
7. Commit your changes with a descriptive message
8. Push to your fork
9. Create a Pull Request

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/kimo26/textcounter.git
   cd textcounter
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Code Style

- Follow PEP 8 guidelines
- Use Black for formatting (line length: 88)
- Use isort for import sorting
- Add type hints to all functions
- Write docstrings for all public methods (Google style)
- Keep functions focused and small

## Testing

- Write tests for all new functionality
- Maintain test coverage above 90%
- Use descriptive test names
- Group related tests in classes

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Update CHANGELOG.md for notable changes

## Questions?

Feel free to open an issue or start a discussion if you have questions!


