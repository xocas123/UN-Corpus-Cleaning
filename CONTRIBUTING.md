# Contributing to UN Speech Boilerplate Cleaner

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Provide a clear description of the problem
- Include sample text that demonstrates the issue
- Specify your Python version and OS

### Suggesting Enhancements

- Open an issue with the tag "enhancement"
- Clearly describe the proposed feature
- Explain why it would be useful
- Provide examples if possible

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add some AmazingFeature'`)
6. Push to your branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/un-speech-cleaner.git
cd un-speech-cleaner

# Install dependencies
pip install -r requirements.txt

# Run tests
python src/clean_un_text_ngram.py
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Comment complex logic

## Areas for Contribution

### High Priority

- [ ] Machine learning-based boilerplate detection
- [ ] Multi-language support (French, Spanish, Arabic, etc.)
- [ ] Unit tests and test coverage
- [ ] Performance optimization for large datasets

### Medium Priority

- [ ] Web interface for interactive cleaning
- [ ] Additional document types (Security Council, ECOSOC)
- [ ] Better handling of tables and structured data
- [ ] Batch processing improvements

### Low Priority

- [ ] Additional output formats (JSON, XML)
- [ ] Visualization of cleaning statistics
- [ ] Integration with existing NLP pipelines
- [ ] Docker containerization

## Adding New Boilerplate Patterns

To add new regex patterns:

1. Edit `n-grams and cleaning data/config_boilerplate.json`
2. Add your pattern to the appropriate category
3. Test on sample speeches
4. Document the pattern's purpose

Example:

```json
{
  "your_category": {
    "enabled": true,
    "description": "What this removes",
    "patterns": [
      "(?i)your_regex_pattern_here"
    ]
  }
}
```

## Testing

Before submitting:

1. Test on at least 10 sample speeches
2. Verify text reduction is reasonable (10-30%)
3. Manually review cleaned outputs
4. Check that substantive content is preserved

## Documentation

- Update README.md for new features
- Add examples for new functionality
- Update docstrings
- Include inline comments for complex code

## Questions?

Open an issue with the "question" tag or reach out to maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
