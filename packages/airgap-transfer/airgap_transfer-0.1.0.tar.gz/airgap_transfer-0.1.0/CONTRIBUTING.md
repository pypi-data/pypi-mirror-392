# Contributing to Airgap Transfer

Thank you for your interest in contributing to Airgap Transfer! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/RLHQ/airgap-transfer/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with the `enhancement` label
3. Describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative solutions you've considered

### Pull Requests

1. **Fork the repository**

```bash
git clone https://github.com/RLHQ/airgap-transfer.git
cd airgap-transfer
```

2. **Create a branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

3. **Set up development environment**

```bash
# Install in development mode with all dependencies
pip install -e ".[all,dev]"
```

4. **Make your changes**

- Follow the existing code style
- Add type hints
- Write docstrings
- Update documentation if needed

5. **Test your changes**

```bash
# Run tests
pytest

# Check code formatting
black src/ tests/
ruff check src/ tests/

# Type checking (if mypy is set up)
mypy src/
```

6. **Commit your changes**

```bash
git add .
git commit -m "Add feature: your feature description"
```

Follow conventional commit messages:
- `feat: add new feature`
- `fix: bug fix`
- `docs: documentation changes`
- `test: add tests`
- `refactor: code refactoring`
- `chore: maintenance tasks`

7. **Push and create PR**

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Development Guidelines

### Code Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Add type hints (Python 3.8+ compatible)

### Documentation

- Write clear docstrings (Google style)
- Update README.md if adding features
- Add examples for new functionality
- Keep CHANGELOG.md updated

### Testing

- Write tests for new features
- Maintain >80% code coverage
- Test edge cases
- Include integration tests where appropriate

### Commit Messages

Good commit messages:
```
feat: add compression support for keyboard transfer

- Add gzip compression option
- Update CLI with --compress flag
- Add documentation for compression
```

Bad commit messages:
```
fix stuff
update code
changes
```

## Project Structure

```
airgap-transfer/
├── src/airgap_transfer/     # Main package
│   ├── keyboard/            # Keyboard transfer module
│   ├── qrcode/              # QR code transfer module
│   ├── cli/                 # Command-line interface
│   ├── utils/               # Utility functions
│   └── installer/           # Installer module (planned)
├── tests/                   # Test suite
├── examples/                # Example scripts
├── docs/                    # Documentation
└── scripts/                 # Development scripts
```

## Areas for Contribution

### High Priority

- [ ] Test coverage improvements
- [ ] Documentation improvements
- [ ] Bug fixes
- [ ] Performance optimizations

### Medium Priority

- [ ] Installer module (v0.2.0)
- [ ] Configuration file support
- [ ] Batch transfer support
- [ ] Enhanced error handling

### Low Priority

- [ ] Encryption support
- [ ] Compression support
- [ ] Resume/retry functionality
- [ ] GUI interface

## Getting Help

- Open a [Discussion](https://github.com/RLHQ/airgap-transfer/discussions)
- Ask in Issues (with the `question` label)
- Check existing documentation

## Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Mentioned in release notes
- Added to contributors list

Thank you for contributing! 🎉
