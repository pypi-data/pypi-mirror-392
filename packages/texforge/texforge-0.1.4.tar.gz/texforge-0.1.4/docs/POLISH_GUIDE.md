# Polish Agent Guide

**Grammar and Word Flow Checker for LaTeX Papers**

The Polish Agent checks your LaTeX papers for grammar errors, word flow issues, and clarity problems while **strictly preserving technical terminology**. It's designed specifically for academic physics and mathematics papers.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [What It Checks](#what-it-checks)
3. [Two Modes](#two-modes)
4. [Terminology Preservation](#terminology-preservation)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Understanding Results](#understanding-results)
8. [Workflow Integration](#workflow-integration)
9. [Tips & Best Practices](#tips--best-practices)

---

## Quick Start

```bash
# Basic usage - generates markdown report
texforge polish main.tex

# With inline LaTeX comments
texforge polish main.tex --mode inline

# Filter by severity
texforge polish main.tex --severity critical

# Setup LaTeX macros for inline mode
texforge polish --setup-macros
```

---

## What It Checks

### Grammar Issues (Critical)
- **Subject-verb agreement**: "The quantum state are evolving" → "is evolving"
- **Tense consistency**: Mixed past/present tense in sections
- **Article usage**: Missing or incorrect "a/an/the"
- **Pronoun agreement**: Singular/plural mismatches

### Word Flow Issues (Major)
- **Awkward phrasing**: Unnecessarily complex constructions
- **Unclear sentences**: Ambiguous or confusing statements
- **Redundancy**: Repetitive phrases or ideas
- **Paragraph transitions**: Poor flow between ideas

### Clarity Issues (Major/Minor)
- **Ambiguous pronouns**: "It" or "this" without clear referent
- **Confusing constructions**: Nested clauses, run-on sentences
- **Jargon overload**: Too many technical terms in one sentence
- **Readability**: Overly long sentences

### Style Issues (Minor)
- **Passive voice overuse**: "The experiment was performed" → "We performed"
- **Wordiness**: "In order to" → "To", "Due to the fact that" → "Because"
- **Weak verbs**: "Make use of" → "Use"

---

## Two Modes

### 1. Report Mode (Default)

Generates a detailed markdown report without modifying your files.

```bash
texforge polish main.tex
# Creates: polish_report.md
```

**Output structure:**
```markdown
# Grammar & Word Flow Report

**Summary:**
- Total Issues: 15
- Critical: 3
- Major: 7
- Minor: 5
- Word Flow Score: 7.2/10

## Critical Issues (3)

### 1. Line 45: Grammar
**Original:** "The quantum state are evolving..."
**Issue:** Subject-verb agreement
**Suggestion:** "The quantum state is evolving..."
```

**Best for:**
- First-time review
- Understanding all issues before making changes
- Team discussions
- Tracking improvements over time

### 2. Inline Mode

Adds colored LaTeX comments directly in your .tex file.

```bash
texforge polish main.tex --mode inline
# Modifies: main.tex (backup created)
```

**Example output in .tex:**
```latex
The quantum state are evolving\grammarfix{GRAMMAR: should be "is evolving" (subject-verb agreement)}

This approach is useful\polishcomment{FLOW: Consider "This approach helps..." for clarity}
```

**Best for:**
- Reviewing issues in context
- Making corrections while writing
- Seeing suggestions alongside original text

---

## Terminology Preservation

**Critical feature:** The Polish Agent **NEVER changes or suggests changes to technical terminology**.

### Default Protected Terms

**Physics:** qubit, entanglement, decoherence, Hamiltonian, Hilbert space, Bell state, CNOT gate, density matrix, von Neumann entropy, quantum supremacy, NISQ device, wave function...

**Math:** eigenvalue, eigenvector, isomorphism, theorem, lemma, corollary, proof, bijection, topology...

### Auto-Detection

The agent automatically preserves:
- Terms in `\texttt{}`, `\mathbf{}`, `\emph{}`
- Custom `\newcommand` definitions
- Capitalized mid-sentence words (proper nouns)
- LaTeX math mode expressions

### Custom Terminology

Add your own terms via:

**1. Command line:**
```bash
texforge polish main.tex --preserve "quantum supremacy,NISQ,VQE"
```

**2. Configuration file:**
Create `.polish-config.yaml`:
```yaml
preserve_terms:
  - "quantum supremacy"
  - "variational quantum eigensolver"
  - "VQE"
  - "your-custom-term"
```

---

## Usage Examples

### Basic Grammar Check
```bash
# Generate report for main.tex
texforge polish main.tex

# Review polish_report.md
less polish_report.md
```

### Check Specific Section
```bash
# Polish introduction only
texforge polish introduction.tex

# Polish multiple sections
texforge polish intro.tex methods.tex results.tex
```

### Inline Comments Mode
```bash
# Setup macros first (one time)
texforge polish --setup-macros

# Add \input{polish_macros} to your preamble

# Run polish with inline mode
texforge polish main.tex --mode inline

# Review and fix issues in your editor
# Search for: \polishcomment, \grammarfix, \flowsuggestion
```

### Severity Filtering
```bash
# Only critical issues
texforge polish main.tex --severity critical

# Only major issues
texforge polish main.tex --severity major

# Only minor style suggestions
texforge polish main.tex --severity minor
```

### With Custom Configuration
```bash
# Create config (copy from example)
cp .polish-config.yaml.example .polish-config.yaml

# Edit to add your terminology
vim .polish-config.yaml

# Run with config
texforge polish main.tex -c .paper-config.yaml
```

### Custom Output Location
```bash
# Save report to custom location
texforge polish main.tex --output reviews/grammar_check.md
```

---

## Configuration

### `.polish-config.yaml` Structure

```yaml
# Additional technical terms to preserve
preserve_terms:
  - "quantum supremacy"
  - "NISQ device"
  - "VQE"

# Grammar check settings
grammar:
  check_critical: true
  check_major: true
  check_minor: true
  check_passive_voice: true
  check_wordiness: true

# Output settings
output:
  default_mode: "report"
  report_file: "polish_report.md"
  critical_color: "red"
  major_color: "orange"
  minor_color: "blue"
```

### LaTeX Macros

When using `--mode inline`, first run:
```bash
texforge polish --setup-macros
```

This creates `polish_macros.tex`:
```latex
\usepackage{xcolor}
\newcommand{\polishcomment}[1]{\textcolor{blue}{[\textbf{POLISH:} #1]}}
\newcommand{\grammarfix}[1]{\textcolor{red}{[\textbf{GRAMMAR:} #1]}}
\newcommand{\flowsuggestion}[1]{\textcolor{orange}{[\textbf{FLOW:} #1]}}
```

Add to your preamble:
```latex
\documentclass{article}
\input{polish_macros}  % <-- Add this
\begin{document}
...
```

**To hide comments** (e.g., for submission), add to `polish_macros.tex`:
```latex
\renewcommand{\polishcomment}[1]{}
\renewcommand{\grammarfix}[1]{}
\renewcommand{\flowsuggestion}[1]{}
```

---

## Understanding Results

### Word Flow Score

**Scale:** 0-10 (higher is better)

- **9-10:** Excellent - Very few issues
- **7-9:** Good - Minor improvements needed
- **5-7:** Fair - Several issues to address
- **3-5:** Poor - Significant rewriting needed
- **0-3:** Critical - Major grammar/flow problems

**Calculation:** Based on issues per 100 lines of text.

### Severity Levels

**Critical:**
- Grammar errors that affect comprehension
- Subject-verb disagreement, wrong tense
- **Action:** Fix immediately

**Major:**
- Flow issues that hinder readability
- Awkward phrasing, unclear meaning
- **Action:** Review and improve

**Minor:**
- Style suggestions, not errors
- Passive voice, wordiness
- **Action:** Consider improving

---

## Workflow Integration

### During Writing (Iterative)

```bash
# 1. Write section
vim introduction.tex

# 2. Quick polish check
texforge polish introduction.tex --severity critical

# 3. Fix critical issues

# 4. Full polish before moving on
texforge polish introduction.tex

# 5. Repeat for each section
```

### Pre-Review Polish

```bash
# 1. Complete draft
texforge compile

# 2. Polish all sections
texforge polish main.tex

# 3. Review report, fix issues
vim polish_report.md

# 4. Re-polish to verify
texforge polish main.tex

# 5. Proceed to peer review
texforge review --journal pra
```

### Pre-Submission Final Check

```bash
# 1. Polish check
texforge polish main.tex --severity critical

# 2. Must have 0 critical issues
# Word Flow Score should be > 7.0

# 3. Compile and validate
texforge compile
texforge validate

# 4. Ready for submission
```

### CI/CD Integration

```yaml
# .github/workflows/paper-quality.yml
- name: Grammar Check
  run: |
    pip install texforge
    texforge polish main.tex --severity critical
    # Fail if critical issues found (exit code 1)
```

---

## Tips & Best Practices

### 1. **Run Early and Often**
- Polish section by section as you write
- Don't wait until the end
- Easier to fix small batches of issues

### 2. **Start with Report Mode**
- Review all issues first
- Understand patterns in your writing
- Then use inline mode for targeted fixes

### 3. **Prioritize Critical Issues**
- Always fix critical grammar errors
- Major flow issues next
- Minor style suggestions last (time permitting)

### 4. **Preserve Your Voice**
- Polish Agent suggests, you decide
- Don't blindly accept all suggestions
- Technical writing has different style than general writing

### 5. **Use Severity Filtering**
```bash
# Quick check before commit
texforge polish main.tex --severity critical

# Full review before submission
texforge polish main.tex
```

### 6. **Track Improvements**
```bash
# Save reports with dates
texforge polish main.tex --output polish_$(date +%Y%m%d).md

# Compare over time
diff polish_20250101.md polish_20250115.md
```

### 7. **Domain-Specific Terms**
- Maintain `.polish-config.yaml` in your repo
- Add new terminology as you introduce it
- Share config with collaborators

### 8. **Combine with Other Agents**
```bash
# 1. Polish for grammar
texforge polish main.tex

# 2. Validate references/citations
texforge validate

# 3. Peer review simulation
texforge review --journal pra

# 4. Generate cover letter
texforge cover-letter pra
```

---

## Troubleshooting

### "No issues found" but you know there are problems

**Possible causes:**
- Content is in math mode (intentionally skipped)
- Content is in comments (intentionally skipped)
- Issues are too minor to flag

**Try:**
```bash
# Check with all severity levels
texforge polish main.tex

# Check specific sections
texforge polish problematic_section.tex
```

### Too many minor issues overwhelming report

**Solution:**
```bash
# Focus on critical first
texforge polish main.tex --severity critical

# Then major
texforge polish main.tex --severity major

# Minor last (if time)
texforge polish main.tex --severity minor
```

### False positives on technical terms

**Solution:**
```bash
# Add to preserved terms
texforge polish main.tex --preserve "your-term,another-term"

# Or add to .polish-config.yaml permanently
```

### Inline mode comments not showing in PDF

**Check:**
1. Did you add `\input{polish_macros}` to preamble?
2. Is `\usepackage{xcolor}` loaded?
3. Did you run `texforge polish --setup-macros` first?

---

## Comparison with Other Tools

| Feature | Polish Agent | Grammarly | LanguageTool | Overleaf |
|---------|--------------|-----------|--------------|----------|
| **LaTeX-aware** | ✅ Yes | ❌ No | ⚠️ Limited | ✅ Yes |
| **Preserves terminology** | ✅ Yes | ❌ No | ❌ No | N/A |
| **Inline comments** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Report mode** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Offline** | ✅ Yes | ❌ No | ⚠️ Limited | ❌ No |
| **Academic focus** | ✅ Physics/Math | ❌ General | ⚠️ General | ✅ Yes |
| **Configurable** | ✅ Yes | ⚠️ Limited | ⚠️ Limited | ❌ No |

---

## Advanced Usage

### Batch Processing
```bash
# Polish all .tex files
for file in *.tex; do
  texforge polish "$file" --severity critical
done

# Collect all critical issues
grep -r "SEVERITY: critical" polish_report_*.md
```

### Integration with Git Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash
texforge polish main.tex --severity critical || {
  echo "❌ Critical grammar issues found!"
  echo "Run: texforge polish main.tex"
  exit 1
}
```

### Custom Workflow Scripts
```bash
#!/bin/bash
# full-review.sh

echo "1. Compiling..."
texforge compile || exit 1

echo "2. Validating..."
texforge validate || exit 1

echo "3. Grammar check..."
texforge polish main.tex || {
  echo "⚠️  Grammar issues found, but continuing..."
}

echo "4. Peer review..."
texforge review --journal pra

echo "✅ Full review complete!"
```

---

## FAQ

**Q: Will it change my LaTeX code?**
A: Only in `--mode inline`, and it creates a backup first. Report mode never modifies files.

**Q: Does it check math equations?**
A: No, math mode is intentionally skipped to avoid false positives on mathematical notation.

**Q: Can I use it for other languages?**
A: Currently English only. The underlying AI model supports other languages, but terminology preservation is optimized for English academic writing.

**Q: How accurate is it?**
A: Very high precision for grammar errors. Flow/style suggestions are more subjective - use your judgment.

**Q: Does it require internet?**
A: Yes, it calls the Claude API via the `claude` CLI tool.

**Q: Can I run it in CI/CD?**
A: Yes! Use `--severity critical` and check exit code. Returns 0 if no critical issues, 1 otherwise.

---

## Next Steps

1. **Try it out:**
   ```bash
   texforge polish main.tex
   ```

2. **Review the report:**
   ```bash
   less polish_report.md
   ```

3. **Fix critical issues first**

4. **Integrate into your workflow:**
   - Add to your paper's Makefile
   - Create git pre-commit hook
   - Run before each compilation

5. **Combine with other agents:**
   ```bash
   texforge polish main.tex
   texforge review --journal pra
   texforge cover-letter pra
   ```

---

**Happy polishing! 🎨**

*For more help:*
- [CLI Guide](../CLI_GUIDE.md) - All commands
- [GitHub Issues](https://github.com/Jue-Xu/LaTex-paper-automation/issues) - Report bugs
- [GitHub Discussions](https://github.com/Jue-Xu/LaTex-paper-automation/discussions) - Ask questions
