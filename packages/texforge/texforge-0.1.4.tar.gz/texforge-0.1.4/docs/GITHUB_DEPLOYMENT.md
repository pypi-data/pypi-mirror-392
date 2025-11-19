# GitHub Deployment Guide

This guide walks you through deploying LaTeX Paper Automation to GitHub and setting up automated workflows.

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Repository Configuration](#repository-configuration)
3. [GitHub Actions Setup](#github-actions-setup)
4. [Release Management](#release-management)
5. [Advanced Workflows](#advanced-workflows)

## Initial Setup

### 1. Create GitHub Repository

```bash
# Create new repository on GitHub (via web interface or CLI)
gh repo create latex-paper-automation --public --description "Automated LaTeX paper maintenance"

# Or use the web interface:
# https://github.com/new
```

### 2. Push Code to GitHub

```bash
# Navigate to your local repository
cd latex-paper-automation

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: LaTeX Paper Automation system"

# Add remote
git remote add origin https://github.com/jue-xu/latex-paper-automation.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Repository Configuration

### 1. Enable Issues and Discussions

Go to Settings → Features and enable:
- ☑ Issues
- ☑ Discussions
- ☑ Projects (optional)
- ☑ Wiki (optional)

### 2. Add Repository Topics

Add topics for discoverability:
- `latex`
- `automation`
- `claude-code`
- `research`
- `academic-writing`
- `python`
- `bash`

### 3. Configure Branch Protection

Settings → Branches → Add rule:

**Branch name pattern**: `main`

Enable:
- ☑ Require a pull request before merging
- ☑ Require status checks to pass before merging
  - Select: `Test Scripts`, `Integration Test`
- ☑ Require branches to be up to date before merging

### 4. Add Repository Description

Settings → General → Description:
```
Automated maintenance and quality control for LaTeX research papers using Claude Code
```

Website: `https://yourusername.github.io/latex-paper-automation` (if you create docs site)

## GitHub Actions Setup

GitHub Actions are configured in `.github/workflows/ci.yml`. They run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Release creation

### Required Secrets (Optional)

For Docker Hub deployment (optional):

Settings → Secrets and variables → Actions → New repository secret:

1. `DOCKER_USERNAME`: Your Docker Hub username
2. `DOCKER_PASSWORD`: Your Docker Hub access token

## Release Management

### Creating a Release

#### Via GitHub Web Interface

1. Go to Releases → Draft a new release
2. Click "Choose a tag" → Create new tag: `v1.0.0`
3. Set release title: `v1.0.0 - Initial Release`
4. Add release notes (see template below)
5. Click "Publish release"

GitHub Actions will automatically:
- Run all tests
- Create release tarball
- Upload assets

#### Via Command Line

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Create release using GitHub CLI
gh release create v1.0.0 \
  --title "v1.0.0 - Initial Release" \
  --notes-file RELEASE_NOTES.md
```

### Release Notes Template

```markdown
## 🎉 LaTeX Paper Automation v1.0.0

### Features
- Automated LaTeX validation (compilation, references, citations)
- Claude Code integration for intelligent checks
- Multi-channel notifications (Email, Slack, Telegram, Discord, ntfy.sh)
- Git automation with smart commits
- Cron-based scheduling
- Interactive installation wizard

### Installation

```bash
# Download and install
curl -L https://github.com/jue-xu/latex-paper-automation/archive/v1.0.0.tar.gz | tar xz
cd latex-paper-automation-1.0.0
./install.sh
```

### What's Changed
- Initial public release

### Requirements
- Python 3.8+
- LaTeX (texlive)
- Git
- Claude Code (optional)

**Full Changelog**: https://github.com/jue-xu/latex-paper-automation/commits/v1.0.0
```

## Advanced Workflows

### Automated Version Bumping

Create `.github/workflows/version-bump.yml`:

```yaml
name: Version Bump

on:
  push:
    branches: [ main ]
    paths-ignore:
      - 'VERSION'
      - 'CHANGELOG.md'

jobs:
  bump:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Bump version
        id: bump
        uses: anothrNick/github-tag-action@1.36.0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          WITH_V: true
          DEFAULT_BUMP: patch
```

### Documentation Site

Create GitHub Pages site:

1. Create `docs/` directory with documentation
2. Settings → Pages → Source: `main` branch, `/docs` folder
3. Add custom domain (optional)

### Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. See error

**Expected behavior**
What you expected to happen.

**System Information:**
 - OS: [e.g. Ubuntu 22.04]
 - Python version: [e.g. 3.10]
 - LaTeX distribution: [e.g. TeX Live 2023]

**Logs**
```
Paste relevant logs here
```

**Additional context**
Any other information.
```

Create `.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature request
about: Suggest an idea
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution**
What you want to happen.

**Describe alternatives**
Alternative solutions considered.

**Additional context**
Any other context or screenshots.
```

### Pull Request Template

Create `.github/pull_request_template.md`:

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code cleanup

## Testing
- [ ] Tested manually
- [ ] Added/updated tests
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
```

## Monitoring and Analytics

### GitHub Insights

Monitor your repository:
- Traffic: Views and clones
- Community: Issues and PRs
- Commits: Activity over time
- Dependency graph: Security alerts

### Badges

Add status badges to README.md:

```markdown
[![CI Status](https://github.com/jue-xu/latex-paper-automation/workflows/CI%2FCD/badge.svg)](https://github.com/jue-xu/latex-paper-automation/actions)
[![License](https://img.shields.io/github/license/yourusername/latex-paper-automation)](LICENSE)
[![Release](https://img.shields.io/github/v/release/yourusername/latex-paper-automation)](https://github.com/jue-xu/latex-paper-automation/releases)
```

## Security

### Dependabot

GitHub automatically monitors dependencies. Configure in Settings → Security → Dependabot.

### Code Scanning

Enable CodeQL analysis:

Settings → Security → Code security → Set up code scanning

### Security Policy

Create `SECURITY.md`:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

Email: security@example.com

We'll respond within 48 hours.
```

## Continuous Deployment

For advanced users, set up automatic deployment:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Add deployment steps here
      # e.g., publish to PyPI, update docs, etc.
```

## Support

- **Issues**: Bug reports and feature requests
- **Discussions**: General questions and community support
- **Wiki**: Detailed documentation and guides
- **Projects**: Track development roadmap

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Next Steps**: After deployment, announce your project on:
- Reddit: r/LaTeX, r/compsci
- Twitter/X with relevant hashtags
- Academic mailing lists
- Your institution's tech community
