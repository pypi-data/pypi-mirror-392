# APS Journal Review Guide

TexForge includes an **APS Journal Peer Review Agent** that simulates the peer review process for American Physical Society (APS) journals. Get expert feedback on your paper before submission.

## Overview

The APS reviewer acts as a complete peer review panel, providing:
- **3 Expert Reviewers** with different perspectives
- **Automated Compliance Checks** for APS standards
- **Editorial Decision** (Accept, Minor/Major Revision, Reject)
- **Detailed Review Report** (1-3 pages) saved as markdown

## Supported Journals

The agent supports all major APS journals:

| Code | Journal | Scope | Typical Length |
|------|---------|-------|----------------|
| `pra` | Physical Review A | Atomic, molecular, and optical physics | 8-12 pages |
| `prb` | Physical Review B | Condensed matter and materials physics | 8-15 pages |
| `prl` | Physical Review Letters | High impact short papers (all physics) | 4 pages max |
| `prx` | Physical Review X | Exceptional significance (all physics) | No limit |
| `prxquantum` | PRX Quantum | Quantum information science | No limit |
| `prr` | Physical Review Research | Open access (all physics) | No limit |

## The Three Reviewers

### Dr. Rigorous Theorist
**Role:** Theory and Methods Specialist

**Focus Areas:**
- Mathematical correctness and rigor
- Theoretical foundations and assumptions
- Model validity and applicability
- Analytical derivations and proofs
- Comparison with existing theories

### Dr. Experimental Validator
**Role:** Experimental and Computational Expert

**Focus Areas:**
- Experimental methodology and controls
- Data quality and statistical analysis
- Computational methods and validation
- Error analysis and uncertainty quantification
- Reproducibility of results

### Dr. Field Connector
**Role:** Broader Impact and Context Specialist

**Focus Areas:**
- Novelty and originality
- Significance to the field
- Literature review completeness
- Clarity of presentation
- Broader impact and applications

## Usage

### Basic Review

```bash
cd your-paper-project/
texforge review                    # Default: Physical Review A
```

### Review for Specific Journal

```bash
texforge review --journal prl      # Physical Review Letters
texforge review --journal prx      # Physical Review X
texforge review --journal prb      # Physical Review B
```

### Strict Review Mode

Apply more rigorous editorial standards:

```bash
texforge review --journal prl --strict
```

Use strict mode when:
- Targeting high-impact journals (PRL, PRX)
- Want maximum critical feedback
- Preparing for challenging submission

### Review Existing PDF

```bash
texforge review --input paper.pdf --journal pra
```

## What Happens During Review

### Step 1: Paper Preparation
- Compiles LaTeX to PDF (if needed)
- Extracts paper content for review
- Verifies file exists and is readable

```
🔨 Compiling LaTeX paper...
✓ Compiled successfully: main.pdf
```

### Step 2: Compliance Checks

Automated checks for APS standards:

**REVTeX Class Check**
- Verifies use of REVTeX4-2 document class
- Required by all APS journals

**Page Limit Check (PRL)**
- PRL papers must be ≤4 pages
- Automatically measured from compiled PDF

**Abstract Check**
- Ensures abstract section exists
- Required by APS editorial policy

**Bibliography Check**
- Verifies bibliography section present
- Ensures proper citation format

```
📋 Running automated compliance checks...
```

### Step 3: Multi-Reviewer Evaluation

Each reviewer reads your paper and provides:

1. **Brief Assessment** (2-3 sentences)
2. **Detailed Comments** (organized by focus areas)
3. **Specific Issues** (concrete problems to address)
4. **Individual Recommendation**

```
👥 Initiating peer review process...
   [1/3] Dr. Rigorous Theorist reviewing...
   [2/3] Dr. Experimental Validator reviewing...
   [3/3] Dr. Field Connector reviewing...
```

### Step 4: Editorial Synthesis

The editor synthesizes all reviews into:

- **Summary** (4-6 sentences)
- **Strengths** (3-5 major positive aspects)
- **Weaknesses** (3-5 major concerns)
- **Decision** (Accept / Minor Revision / Major Revision / Reject)
- **Rationale** (explanation for decision)

```
📊 Synthesizing reviews...
```

### Step 5: Report Generation

Two files are created:

**Main Report:** `aps_review.md`
- Current review (always overwritten)

**Archived Report:** `aps_review_20251116_143000.md`
- Timestamped historical record
- Track review iterations over time

```
✅ Review complete! Decision: Minor Revision
📄 Full report saved to: aps_review.md
```

## Understanding Review Decisions

### ✓ Accept
**What it means:**
- Paper meets journal standards
- Only minor editorial changes needed
- High likelihood of acceptance

**Next Steps:**
1. Address any minor suggestions
2. Prepare final submission
3. Write cover letter

### ⚠ Minor Revision
**What it means:**
- Strong paper with addressable issues
- Revisions likely to lead to acceptance
- Re-review may not be required

**Next Steps:**
1. Address all specific issues listed
2. Revise paper accordingly
3. Re-run review: `texforge review`
4. Submit when decision improves

### ⚠ Major Revision
**What it means:**
- Significant concerns need addressing
- Substantial changes required
- Re-review will be needed
- May require additional experiments/analysis

**Next Steps:**
1. Carefully review all weaknesses
2. Make substantial revisions
3. Consider if changes are feasible
4. Re-run review after major changes
5. May need to target different journal

### ✗ Reject
**What it means:**
- Fundamental flaws or unsuitable for journal
- Scope mismatch or insufficient novelty
- Major methodology issues

**Next Steps:**
1. Review weaknesses carefully
2. Consider fundamental restructuring
3. Target different journal tier
4. Address core issues before resubmission

## Review Report Structure

The generated `aps_review.md` contains:

```markdown
# APS Journal Review Report

**Journal:** Physical Review A
**Date:** 2025-11-16 14:30:00
**Decision:** Minor Revision

======================================================================

## Summary

[4-6 sentence synthesis of all reviewer feedback]

## Strengths

1. [Major strength 1]
2. [Major strength 2]
3. [Major strength 3]
...

## Weaknesses

1. [Major concern 1]
2. [Major concern 2]
3. [Major concern 3]
...

## APS Compliance Issues

1. [Any compliance violations]
...

## Detailed Reviewer Comments

### Dr. Rigorous Theorist

[Full theoretical review]

### Dr. Experimental Validator

[Full experimental/computational review]

### Dr. Field Connector

[Full context and impact review]

## Editorial Decision

**Decision:** Minor Revision

**Rationale:** [Explanation for decision]
```

## Example Workflow

### Pre-Submission Review

```bash
# 1. Finish writing your paper
texforge compile

# 2. Get peer review feedback
texforge review --journal pra

# 3. Read review report
cat aps_review.md

# 4. Address weaknesses
# ... edit paper based on feedback ...

# 5. Re-compile and re-review
texforge compile
texforge review --journal pra

# 6. When you get "Accept" or "Minor Revision"
texforge cover-letter pra
```

### Testing Different Journals

```bash
# See how paper fares for different journals
texforge review --journal pra         # Standard journal
texforge review --journal prl --strict # High-impact short paper
texforge review --journal prx --strict # Flagship journal

# Compare archived reviews
ls aps_review_*.md
```

### Iterative Improvement

```bash
# Initial review
texforge review --journal prl
# Decision: Major Revision

# Make changes based on feedback
# ... edit paper ...

# Second review
texforge review --journal prl
# Decision: Minor Revision

# Final tweaks
# ... edit paper ...

# Third review
texforge review --journal prl
# Decision: Accept

# Ready to submit!
```

## Integration with Other Agents

### Complete Workflow

```bash
# 1. Brainstorm research idea
texforge brainstorm

# 2. Write paper based on outline
# ... write sections ...

# 3. Get peer review
texforge review --journal pra

# 4. Iterate based on feedback
# ... revise paper ...
texforge review --journal pra

# 5. Generate cover letter when ready
texforge cover-letter pra

# 6. Submit!
```

## Tips for Getting Better Reviews

### 1. Use Proper APS Format

Ensure your paper uses REVTeX4-2:

```latex
\documentclass[aps,pra,reprint,superscriptaddress]{revtex4-2}
```

### 2. Include Complete Abstract

```latex
\begin{abstract}
Your abstract here...
\end{abstract}
```

### 3. Proper Bibliography

```latex
\bibliography{references}
```

Or use `thebibliography` environment.

### 4. Compile Before Reviewing

```bash
# Ensure paper compiles cleanly
texforge compile

# Then review
texforge review
```

### 5. Use Strict Mode for High-Impact

When targeting PRL, PRX, or Nature Physics:

```bash
texforge review --journal prl --strict
```

### 6. Track Review History

Keep timestamped reviews:

```bash
# Review generates:
aps_review.md                    # Latest
aps_review_20251115_100000.md   # First review
aps_review_20251116_140000.md   # After revisions

# Compare progress
diff aps_review_20251115_100000.md aps_review_20251116_140000.md
```

## Interpreting Compliance Issues

### "Paper does not use REVTeX4 document class"

**Problem:** Using wrong LaTeX class

**Fix:**
```latex
% Change from:
\documentclass{article}

% To:
\documentclass[aps,pra,reprint]{revtex4-2}
```

### "PRL papers must be ≤4 pages"

**Problem:** Exceeds page limit for Physical Review Letters

**Solutions:**
1. Trim content to fit 4 pages
2. Target PRA/PRB instead (longer format)
3. Move details to supplementary material

### "Abstract section not found"

**Problem:** Missing abstract

**Fix:**
```latex
\begin{document}
\title{Your Title}
\author{Your Name}

\begin{abstract}
Your abstract content here.
\end{abstract}

\maketitle
```

### "No bibliography found"

**Problem:** Missing citations

**Fix:**
```latex
% End of document
\bibliography{references}
\end{document}
```

## Advanced Usage

### Reviewing Specific File

```bash
# Review specific PDF (skip compilation)
texforge review --input submitted_paper.pdf

# Review specific TeX file
texforge review --input alternative_version.tex
```

### Custom Configuration

If using non-standard file structure:

```bash
# Create/edit .paper-config.yaml
texforge review -c custom-config.yaml
```

### Comparing Journal Standards

Generate reviews for multiple journals:

```bash
# See same paper through different lenses
for journal in pra prb prl prx; do
    texforge review --journal $journal
    mv aps_review.md review_${journal}.md
done

# Compare standards
cat review_pra.md  # Standard review
cat review_prl.md  # Stricter (4 pages)
```

## Troubleshooting

### Review says "compilation failed"

**Solution:**
```bash
# Fix compilation first
texforge compile

# Then review
texforge review
```

### Review is too generic

**Problem:** Paper content not detailed enough

**Solution:**
- Ensure paper has substantial content
- Include methodology, results, discussion
- Add proper citations and references

### "Claude CLI not found"

**Problem:** Claude CLI not installed

**Solution:**
```bash
pip install claude-cli
```

### Review times out

**Problem:** Paper too long or complex

**Solution:**
- Review will timeout after 120 seconds per reviewer
- Simplify paper or break into sections
- Report issue if persistent

## Understanding Reviewer Perspectives

### When Dr. Rigorous Theorist Says...

**"Mathematical rigor is lacking"**
- Add formal proofs or derivations
- State assumptions explicitly
- Show convergence/consistency checks

**"Model validity unclear"**
- Justify theoretical framework
- Explain approximations used
- Compare with established models

### When Dr. Experimental Validator Says...

**"Error analysis insufficient"**
- Add uncertainty quantification
- Show systematic vs. statistical errors
- Include error bars on plots

**"Reproducibility concerns"**
- Provide more implementation details
- Share code or data repositories
- Specify experimental parameters

### When Dr. Field Connector Says...

**"Novelty not clear"**
- Clarify what's new vs. prior work
- Highlight unique contributions
- Strengthen literature comparison

**"Limited broader impact"**
- Explain applications or implications
- Connect to ongoing research challenges
- Discuss future directions

## Files Generated

| File | Purpose | Persistence |
|------|---------|-------------|
| `aps_review.md` | Latest review | Overwritten each review |
| `aps_review_YYYYMMDD_HHMMSS.md` | Timestamped archive | Permanent historical record |

## See Also

- [Brainstorming Guide](BRAINSTORMING_GUIDE.md) - Develop research ideas
- [Cover Letter Guide](COVER_LETTER_GUIDE.md) - Generate submission letters
- [CLI Guide](../CLI_GUIDE.md) - All TexForge commands

---

**Pro Tip:** Combine brainstorming, review, and cover letter for complete workflow:

```bash
# 1. Develop idea
texforge brainstorm

# 2. Write paper (based on manuscript_outline.md)
# ...

# 3. Self-review
texforge review --journal pra

# 4. Revise until satisfied
# ...

# 5. Generate cover letter
texforge cover-letter pra

# 6. Submit with confidence!
```

This ensures your paper is rigorously vetted before submission.
