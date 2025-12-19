"""
Contributing to Sports AI Bettor

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/sports-ai-bettor.git
cd sports-ai-bettor
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Code Style

We follow PEP 8 and use these tools:

```bash
# Format code
black src/ config/ tests/

# Check style
flake8 src/ config/ tests/

# Type checking
mypy src/ config/
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov=config --cov-report=html

# Specific test file
pytest tests/test_predictor.py -v
```

## Making Changes

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add tests for new functionality
4. Run tests to ensure everything passes
5. Commit with clear messages: `git commit -m "Add feature: description"`
6. Push and create a pull request

## Pull Request Guidelines

- Describe what your PR does
- Include any related issue numbers
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

## Reporting Issues

When reporting bugs, please include:
- Python version and OS
- Error messages and stack traces
- Steps to reproduce
- Expected vs actual behavior

## Code of Conduct

Be respectful and constructive. We're all here to learn and improve!

---

Thank you for contributing! 🎯
"""