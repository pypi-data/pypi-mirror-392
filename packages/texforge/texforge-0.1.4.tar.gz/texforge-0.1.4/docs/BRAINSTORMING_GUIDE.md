# Brainstorming Guide

TexForge includes a powerful **Multi-Agent Brainstorming System** that simulates expert discussions to help you develop and refine research ideas before writing your paper.

## Overview

The brainstorming system simulates a discussion between **6 expert personas** who evaluate your research idea from different perspectives:

1. **Dr. Theory** - Theoretical Physicist (mathematical rigor and foundations)
2. **Dr. Experiment** - Experimental Physicist (practical implementation)
3. **Dr. Computation** - Computational Physicist (numerical methods)
4. **Dr. Impact** - Research Strategist (significance and publication potential)
5. **Dr. Skeptic** - Critical Reviewer (finding flaws and weaknesses)
6. **Dr. Literature** - Literature & Reference Specialist (connecting to existing research)

## How It Works

### Three-Round Discussion

1. **Round 1: Initial Reactions**
   - Each expert provides 2-3 sentence reaction to your idea
   - Dr. Literature specifically connects your idea to references in `library/`

2. **Round 2: Probing Questions**
   - Each expert asks 3-5 critical questions
   - Dr. Literature focuses on how to leverage existing references

3. **Round 3: Synthesis & Recommendation**
   - Senior advisor synthesizes all input
   - Provides GO/NO-GO/REVISE recommendation

## Usage

### Basic Command

```bash
cd your-paper-project/
texforge brainstorm --idea "Your research idea here" --journal "Physical Review A"
```

### Using Project Goals from README

If you've filled out the "Project Goals" section in your `README.md`, you can omit the `--idea` parameter:

```bash
texforge brainstorm
```

The system will automatically use your project goals as the research idea.

## Input Requirements

### 1. Project Goals (README.md)

Add this section to your project's `README.md`:

```markdown
## Project Goals

**Research Question:**
What is the main question this paper addresses?

**Objectives:**
- Objective 1
- Objective 2

**Expected Contributions:**
- What novel insights or methods does this work provide?
```

### 2. Library References

Place reference materials in the `library/` folder:
- PDF files (`.pdf`)
- HTML files (`.html`, `.htm`)
- LaTeX source folders (from arXiv downloads)
- Flat structure (no subdirectories needed)

**Easy way to add references from arXiv:**

```bash
# Download papers directly from arXiv in any format
texforge arxiv-download 2301.12345                    # LaTeX source
texforge arxiv-download 2302.98765 --format pdf       # PDF version
texforge arxiv-download 2303.45678 --format html      # HTML version

# Or copy existing files
cp ~/papers/reference.pdf library/
```

The **Dr. Literature** agent will:
- Identify relevant references for your research
- Propose novel connections between references
- Suggest how to build on existing work
- Identify gaps in the literature

## Output Files

After a brainstorming session, you'll get **three output files**:

### 1. Brainstorming Session (`brainstorming_session.md`)

**Location:** Project root

**Contents:**
- Timestamp and target journal
- Full research idea
- All three rounds of expert discussion
- Next steps checklist

**Use for:** Quick review of the session

### 2. Detailed Log (`library/brainstorm_log_YYYY-MM-DD_HH-MM-SS.md`)

**Location:** `library/` folder

**Contents:**
- Session overview with participant count
- Complete expert reactions with perspectives
- All questions and synthesis
- Action items checklist
- Links to references

**Features:**
- **Timestamped filename** for easy chronological organization
- **Stored in library/** alongside your reference materials
- **Historical record** of all brainstorming sessions
- **Future reference** when reviewing past ideas

**Use for:** Detailed review, historical tracking, comparing sessions over time

### 3. Manuscript Outline (`content/manuscript_outline.md`)

**Location:** `content/` folder

**Contents:**
- Detailed outline for Introduction, Methods, Results, Discussion, Conclusion
- 2-3 bullet points per section
- References to relevant library files

**Use for:** Starting point for writing your paper sections

### 4. Updated README.md

The system automatically adds/updates a section in your `README.md`:

```markdown
## Latest Brainstorming Session

**Date:** 2025-11-16 14:30
**Status:** ✓ GO - Proceed with research

### Key Outcomes

- Strong theoretical foundation with clear experimental path
- Novel computational approach addresses key limitations
- High publication potential for Physical Review A

### Next Steps

See `brainstorming_session.md` and `library/brainstorm_log_2025-11-16_14-30-00.md` for complete discussion.
```

## Example Workflow

### 1. Setup Project

```bash
texforge init quantum-research --template pra
cd projects/quantum-research
```

### 2. Add References

```bash
# Download from arXiv (recommended)
texforge arxiv-download 2301.12345 --format pdf
texforge arxiv-download 2302.98765

# Or copy existing files
cp ~/papers/reference1.pdf library/
cp ~/papers/reference2.pdf library/
```

### 3. Define Project Goals

Edit `README.md`:

```markdown
## Project Goals

**Research Question:**
Can we use machine learning to optimize quantum gate sequences?

**Objectives:**
- Develop ML model for quantum circuit optimization
- Benchmark against classical optimization methods
- Demonstrate speedup on real quantum hardware

**Expected Contributions:**
- Novel ML-quantum hybrid optimization algorithm
- Performance analysis on NISQ devices
```

### 4. Run Brainstorming

```bash
texforge brainstorm
```

### 5. Review Outputs

```bash
# Quick review
cat brainstorming_session.md

# Detailed review with all expert perspectives
cat library/brainstorm_log_2025-11-16_14-30-00.md

# See manuscript structure
cat content/manuscript_outline.md

# Check summary
head -50 README.md
```

### 6. Iterate if Needed

Based on expert feedback, you might:
- Add more references to `library/`
- Revise project goals in README.md
- Re-run brainstorming: `texforge brainstorm`

Each session creates a new timestamped log in `library/` so you can compare how your idea evolved.

## The Dr. Literature Agent

### What Makes Dr. Literature Special?

Unlike other experts who focus on theoretical, experimental, or computational aspects, **Dr. Literature**:

- **Actively reads** the filenames and types of references in `library/`
- **Proposes new ideas** based on combinations of existing references
- **Identifies gaps** in the current literature
- **Suggests connections** between different papers/resources
- **Ensures proper context** for your research

### Example Dr. Literature Response

Given references like:
- `quantum_ml_review_2023.pdf`
- `nisq_optimization_methods.pdf`
- `gate_synthesis_algorithms.html`

Dr. Literature might say:

> "This idea bridges the quantum ML review with NISQ optimization methods in a novel way. The gap between theoretical ML approaches and practical NISQ constraints is well-documented in quantum_ml_review_2023.pdf. By combining insights from gate_synthesis_algorithms.html with the optimization framework in nisq_optimization_methods.pdf, we could develop a hybrid approach that hasn't been explored. I'd recommend adding references on reinforcement learning for circuit optimization to strengthen the ML methodology."

### Round 2 Questions from Dr. Literature

In Round 2, Dr. Literature asks questions like:

1. "Which specific ML architectures from quantum_ml_review_2023.pdf are most compatible with the hardware constraints discussed in nisq_optimization_methods.pdf?"
2. "Are there successful hybrid classical-quantum algorithms in our library that could inform our approach?"
3. "What benchmarking methodologies from the existing references should we adopt?"

## Tips for Effective Brainstorming

### 1. Populate Library First

Add relevant papers **before** brainstorming:
```bash
# Good: References available for Dr. Literature
texforge arxiv-download 2301.12345 --format pdf
texforge arxiv-download 2302.98765
cp references/*.pdf library/
texforge brainstorm

# Less effective: No context for Dr. Literature
texforge brainstorm  # with empty library/
```

### 2. Write Clear Project Goals

Be specific in README.md:
```markdown
# Good
**Research Question:** How does entanglement entropy scale in 2D topological phases?

# Too vague
**Research Question:** Study quantum systems
```

### 3. Use Specific Journal Names

```bash
# Good: Helps Dr. Impact assess publication fit
texforge brainstorm --journal "Physical Review A"
texforge brainstorm --journal "Nature Physics"

# Less helpful
texforge brainstorm --journal "a physics journal"
```

### 4. Review All Three Outputs

- `brainstorming_session.md` → Quick decisions
- `library/brainstorm_log_*.md` → Deep analysis
- `content/manuscript_outline.md` → Writing structure

### 5. Track Sessions Over Time

The timestamped logs in `library/` create a history:

```bash
library/
├── brainstorm_log_2025-11-15_10-00-00.md  # First idea
├── brainstorm_log_2025-11-15_15-30-00.md  # After adding references
├── brainstorm_log_2025-11-16_09-00-00.md  # Revised approach
└── reference_paper.pdf
```

Compare sessions to see how your thinking evolved.

## Interpreting Recommendations

### ✓ GO - Proceed with Research

The experts believe:
- Core idea is sound
- Feasible with available resources
- Novel contribution likely
- Good publication potential

**Action:** Start writing based on `manuscript_outline.md`

### ⚠ REVISE - Modify Approach

The experts identified:
- Significant concerns that need addressing
- Modifications to strengthen the work
- Alternative approaches to consider

**Action:**
1. Review Round 2 questions carefully
2. Address major concerns in synthesis
3. Revise project goals
4. Re-run brainstorming

### ✗ NO-GO - Reconsider Approach

The experts found:
- Fundamental flaws in the approach
- Insurmountable practical barriers
- Insufficient novelty or impact

**Action:**
1. Read synthesis carefully
2. Consider alternative angles
3. Revise research question
4. Start new brainstorming session

## Advanced Usage

### Custom Journal Targeting

```bash
texforge brainstorm --journal "Nature"          # High-impact
texforge brainstorm --journal "PRL"             # Physical Review Letters
texforge brainstorm --journal "J. Chem. Phys."  # Specialized
```

Dr. Impact will adjust publication strategy accordingly.

### Multiple Iterations

```bash
# Initial brainstorming
texforge brainstorm

# Add more references based on Dr. Literature's suggestions
texforge arxiv-download 2304.11111 --format pdf
texforge arxiv-download 2305.22222
cp new_references/*.pdf library/

# Re-run with refined idea
texforge brainstorm --idea "Revised research question based on feedback"
```

Each run creates a new timestamped log for comparison.

## Troubleshooting

### No references found

```
⚠ No references found in library/
```

**Solution:** Add `.pdf`, `.html`, or `.htm` files to `library/`

### No project goals found

```
⚠ No project goals found in README.md
```

**Solution:** Either:
1. Add "## Project Goals" section to README.md
2. Use `--idea "..."` parameter

### Dr. Literature provides generic responses

**Problem:** Library references aren't being utilized

**Solution:**
- Ensure reference filenames are descriptive
- Add more references (3-5 minimum recommended)
- References should be topically relevant

## Integration with Writing Workflow

```bash
# 1. Brainstorm
texforge brainstorm

# 2. Review and iterate if needed
cat library/brainstorm_log_*.md
texforge brainstorm  # with revised goals

# 3. When you get GO recommendation:
cat content/manuscript_outline.md

# 4. Start writing sections
vim content/intro.tex
vim content/methods.tex

# 5. Compile
texforge compile

# 6. Later reference past sessions
ls library/brainstorm_log_*.md
```

## Files Generated

Summary of all files:

| File | Location | Purpose | When Created |
|------|----------|---------|--------------|
| `brainstorming_session.md` | Project root | Quick session review | Every session |
| `brainstorm_log_YYYY-MM-DD_HH-MM-SS.md` | `library/` | Detailed historical log | Every session |
| `manuscript_outline.md` | `content/` | Writing structure | Every session |
| `README.md` | Project root | Updated with latest status | Every session |

## See Also

- [CLI Guide](../CLI_GUIDE.md) - All TexForge commands
- [Project Structure](STRUCTURE.md) - Understanding project layout
- [Quick Start](QUICKSTART.md) - Getting started with TexForge

---

**Pro Tip:** Use `git` to track your brainstorming evolution:

```bash
git add brainstorming_session.md library/ content/ README.md
git commit -m "Brainstorming session: quantum ML optimization"
```

This creates a permanent record of each brainstorming iteration in your project history.
