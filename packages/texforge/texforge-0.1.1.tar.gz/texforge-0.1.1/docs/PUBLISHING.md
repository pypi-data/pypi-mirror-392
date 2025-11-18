# Publishing TexForge to PyPI

This guide explains how to publish TexForge to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Token**: Generate API tokens:
   - PyPI: Account Settings → API tokens → Add API token
   - TestPyPI: Same process on TestPyPI

3. **GitHub Secrets**: Add your PyPI API token to GitHub:
   - Go to repository Settings → Secrets and variables → Actions
   - Add secret: `PYPI_API_TOKEN` with your PyPI API token value

## Publishing Methods

### Method 1: Automated (Recommended) - GitHub Actions

The repository includes a GitHub Actions workflow that automatically publishes to PyPI when you create a release.

**Steps:**

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # Increment version number
   ```

2. **Update changelog** in `texforge/__init__.py`:
   ```python
   __version__ = "0.1.1"
   ```

3. **Commit and push changes**:
   ```bash
   git add pyproject.toml texforge/__init__.py
   git commit -m "Bump version to 0.1.1"
   git push
   ```

4. **Create a git tag**:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

5. **Create GitHub Release**:
   - Go to GitHub → Releases → Draft a new release
   - Choose tag: `v0.1.1`
   - Title: `TexForge v0.1.1`
   - Describe changes in the release notes
   - Click "Publish release"

6. **Automatic publish**: GitHub Actions will automatically:
   - Build the package
   - Run tests
   - Publish to PyPI

### Method 2: Manual Publishing

If you prefer to publish manually:

**1. Install build tools:**
```bash
pip install --upgrade build twine
```

**2. Build the package:**
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/texforge-0.1.0.tar.gz` (source distribution)
- `dist/texforge-0.1.0-py3-none-any.whl` (wheel)

**3. Test on TestPyPI first (recommended):**
```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ texforge
```

**4. Publish to PyPI:**
```bash
twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (including `pypi-` prefix)

**5. Verify installation:**
```bash
# Create new virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install texforge

# Test
texforge --version
texforge --help
```

## Version Management

### Semantic Versioning

TexForge follows [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Incompatible API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Examples:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.1` → `0.2.0`: New feature
- `0.9.0` → `1.0.0`: First stable release

### Pre-release versions

For testing:
- Alpha: `0.1.0a1`, `0.1.0a2`
- Beta: `0.1.0b1`, `0.1.0b2`
- Release candidate: `0.1.0rc1`

## Pre-publish Checklist

Before publishing a new version:

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `texforge/__init__.py`
- [ ] Update `README.md` if needed
- [ ] Update `CLI_GUIDE.md` if commands changed
- [ ] Test installation locally: `pip install -e .`
- [ ] Run all commands to ensure they work
- [ ] Check that all imports work
- [ ] Review git diff to ensure no sensitive data
- [ ] Commit all changes
- [ ] Create git tag
- [ ] Test on TestPyPI first (optional but recommended)

## Troubleshooting

### Package name already exists
If "texforge" is taken on PyPI, you'll need to:
1. Choose a different name (check availability on PyPI first)
2. Update `name` in `pyproject.toml`
3. Update all documentation

### Upload fails
```bash
# Check package before uploading
twine check dist/*

# If you get authentication errors, regenerate API token
```

### Wrong files included
```bash
# Check what's in the distribution
tar -tzf dist/texforge-0.1.0.tar.gz

# Update MANIFEST.in to include/exclude files
```

## After Publishing

1. **Verify on PyPI**: Visit https://pypi.org/project/texforge/
2. **Test installation**: `pip install texforge`
3. **Update README badge** (optional):
   ```markdown
   [![PyPI version](https://badge.fury.io/py/texforge.svg)](https://badge.fury.io/py/texforge)
   ```
4. **Announce**: Share on relevant communities

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PEP 621 - pyproject.toml](https://peps.python.org/pep-0621/)
