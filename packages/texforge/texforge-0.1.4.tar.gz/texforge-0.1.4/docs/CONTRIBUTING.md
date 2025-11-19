# Contributing to LaTeX Paper Automation

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists in [GitHub Issues](https://github.com/jue-xu/latex-paper-automation/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, LaTeX distribution)
   - Relevant logs or error messages

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and motivation
   - Proposed implementation (optional)

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages: `git commit -m "Add amazing feature"`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/jue-xu/latex-paper-automation.git
cd latex-paper-automation

# Install for development (uses symlinks)
./install.sh

# Make changes to files in bin/ and lib/
# Changes are immediately reflected

# Test your changes
~/.local/bin/latex-paper-tools/bin/auto-maintain-paper.sh
```

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings for functions and classes
- Keep functions focused and testable
- Maximum line length: 120 characters

Example:
```python
def validate_citations(paper_dir: Path) -> Tuple[str, str]:
    """
    Check that all \cite commands match BibTeX entries.
    
    Args:
        paper_dir: Path to paper directory
        
    Returns:
        Tuple of (status, message)
    """
    # Implementation here
    pass
```

### Shell Scripts

- Use bash (not sh)
- Include shebang: `#!/bin/bash`
- Set strict mode: `set -euo pipefail`
- Quote variables: `"$VARIABLE"`
- Use meaningful variable names
- Add comments for complex logic

Example:
```bash
#!/bin/bash
set -euo pipefail

# Validate paper directory
PAPER_DIR="${1:-$PWD}"
if [ ! -d "$PAPER_DIR" ]; then
    echo "Error: Directory not found: $PAPER_DIR" >&2
    exit 1
fi
```

## Testing

### Manual Testing

Test your changes with the example paper:

```bash
cd examples/example-paper

# Test validation
python3 ../../lib/validate_paper.py --dir .

# Test notifications (use your own credentials)
python3 ../../lib/notification_cli.py \
    --subject "Test" \
    --body "Testing notifications" \
    --ntfy

# Test full automation
~/.local/bin/latex-paper-tools/bin/auto-maintain-paper.sh
```

### Automated Testing

We use GitHub Actions for CI. Tests run automatically on pull requests.

To run tests locally:

```bash
# Lint Python code
flake8 lib/*.py --max-line-length=120

# Check shell scripts
bash -n bin/*.sh

# Run integration tests
# (requires LaTeX installation)
cd examples/example-paper
python3 ../../lib/validate_paper.py --dir .
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update CHANGELOG.md (if exists)

## Commit Messages

Use clear, descriptive commit messages:

- Use present tense: "Add feature" not "Added feature"
- Use imperative mood: "Fix bug" not "Fixes bug"
- First line: brief summary (50 chars)
- Optional body: detailed explanation

Examples:
```
Add support for Overleaf integration

Implement sync with Overleaf using their API. This allows
automatic upload of changes to Overleaf projects.

Closes #123
```

```
Fix citation validation for multi-file papers

The citation checker now correctly scans all .tex files
in the directory, not just the main file.
```

## Release Process

(For maintainers)

1. Update version number
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will create release

## Questions?

- Open a [Discussion](https://github.com/jue-xu/latex-paper-automation/discussions)
- Check the [Wiki](https://github.com/jue-xu/latex-paper-automation/wiki)
- Create an issue for bugs or features

Thank you for contributing! 🎉
