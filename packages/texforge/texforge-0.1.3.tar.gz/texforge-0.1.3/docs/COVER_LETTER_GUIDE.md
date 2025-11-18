# Cover Letter Writer Guide

TexForge includes a **Cover Letter Writer Agent** that generates professional, journal-specific cover letters for your paper submissions. Save time and ensure proper formatting for each journal's expectations.

## Overview

The cover letter writer:
- **Analyzes Your Paper** content automatically
- **Extracts Key Information** (title, contributions, citations)
- **Generates Professional Letters** tailored to journal standards
- **Supports Major Journals** with pre-configured profiles
- **Outputs Multiple Formats** (plain text `.txt` and markdown `.md`)

## Supported Journals

Pre-configured profiles for major physics journals:

| Code | Journal | Tone | Key Emphasis |
|------|---------|------|--------------|
| `prl` | Physical Review Letters | Concise, confident | Novelty and broad impact |
| `pra` | Physical Review A | Technical, detailed | Rigor and completeness |
| `prb` | Physical Review B | Technical, materials-focused | Applications and phenomena |
| `prx` | Physical Review X | Confident, innovative | Quality and interdisciplinary impact |
| `nature` | Nature | Compelling, accessible | Paradigm-shifting significance |
| `science` | Science | Clear, compelling | Innovation and societal impact |

**Custom journals** are also supported - the agent will generate appropriate letters for any journal name you provide.

## Usage

### Basic Usage

```bash
cd your-paper-project/
texforge cover-letter prl
```

This generates:
- `cover_letter.txt` - Plain text version (ready to copy-paste)
- `cover_letter.md` - Markdown version (with metadata)

### Specify Journal

```bash
# Pre-configured journals
texforge cover-letter prl          # Physical Review Letters
texforge cover-letter nature       # Nature
texforge cover-letter science      # Science
texforge cover-letter pra          # Physical Review A
texforge cover-letter prb          # Physical Review B
texforge cover-letter prx          # Physical Review X

# Custom journal
texforge cover-letter "Nature Physics"
texforge cover-letter "Journal of Chemical Physics"
```

### Add Additional Information

Include extra context that should appear in the letter:

```bash
texforge cover-letter prl -i "This work was funded by NSF Grant XYZ. We suggest Dr. Jane Smith as a potential reviewer."
```

### With Configuration File

```bash
texforge cover-letter pra -c .paper-config.yaml
```

## What the Agent Does

### Step 1: Paper Analysis

Reads your LaTeX file and extracts:
- **Paper Title** from `\title{...}`
- **Abstract** content
- **Introduction** and motivation
- **Key Results** and conclusions
- **Bibliography** and citations

```
📄 Reading paper content...
🔍 Extracting paper information...
```

### Step 2: Content Generation

Uses Claude AI to generate:
1. **Opening Statement** - Paper title and journal name
2. **Motivation Paragraph** - Research context and influential works
3. **Contributions Paragraph** - Novel findings and significance
4. **Journal Match Paragraph** - Why this journal is appropriate

```
🤖 Generating cover letter with Claude AI...
```

### Step 3: Output Files

Creates two files:

**cover_letter.txt** - Ready to use
```
Dear Editor,

We are pleased to submit our manuscript entitled "Quantum Entanglement
in Topological Systems" for consideration for publication in Physical
Review Letters.

[Full letter content...]

Sincerely,
[Your signature]
```

**cover_letter.md** - With metadata
```markdown
# Cover Letter for Physical Review Letters

**Generated:** 2025-11-16 14:30:00
**Paper Title:** Quantum Entanglement in Topological Systems

## Cover Letter Text

[Full letter...]

## Key Contributions Highlighted

1. Novel theoretical framework...
2. Experimental validation...

## Influential Works Cited

1. Smith et al., Nature 2023
2. Jones et al., PRL 2024
```

```
💾 Saving cover letter to cover_letter.txt and cover_letter.md...
✅ Cover letter generation complete!
```

## Cover Letter Structure

Every generated letter follows this professional structure:

### 1. Opening Statement (1 sentence)
- States paper title in quotes
- Names the target journal
- Formal submission request

**Example:**
> We are pleased to submit our manuscript entitled "Quantum Error Correction in NISQ Devices" for consideration for publication in Physical Review Letters.

### 2. Motivation Paragraph (3-5 sentences)
- Broader context and importance
- Research gap being addressed
- 2-4 influential previous works cited
- Clear problem statement

**Example:**
> Quantum error correction is essential for fault-tolerant quantum computing. Recent advances in NISQ devices (Smith et al., Nature 2023) have demonstrated promise, but scalability remains challenging. Building on the theoretical framework of Jones et al. (PRL 2024) and experimental methods from Chen et al. (PRX 2024), we address this gap...

### 3. Contributions Paragraph (3-5 sentences)
- Key findings and results
- Novel methodology or insights
- Quantitative improvements (if applicable)
- Significance and implications

**Example:**
> Our work makes three key contributions. First, we develop a novel error correction code that reduces qubit overhead by 40%. Second, we demonstrate experimental validation on a 20-qubit system. Third, we provide scaling analysis showing feasibility for 1000+ qubit systems...

### 4. Journal Match Paragraph (2-3 sentences)
- Why this journal is appropriate
- Matches journal's scope and criteria
- Expected readership and impact

**Example:**
> We believe this manuscript is well-suited for Physical Review Letters because it represents a fundamental advance in quantum error correction with broad interest to the quantum computing community. The experimental demonstration and theoretical analysis align with PRL's emphasis on high-impact physics discoveries...

### 5. Closing (1-2 sentences)
- Standard submission statement
- No prior publication assertion
- Thank you to editor

## Example Workflow

### Standard Submission

```bash
# 1. Finish and compile paper
texforge compile

# 2. Get peer review (optional but recommended)
texforge review --journal prl

# 3. Generate cover letter
texforge cover-letter prl

# 4. Review generated letter
cat cover_letter.txt

# 5. Copy to submission system
# Use cover_letter.txt for journal submission
```

### Multiple Journal Versions

```bash
# Generate letters for different journals
texforge cover-letter prl
mv cover_letter.txt cover_letter_prl.txt

texforge cover-letter pra
mv cover_letter.txt cover_letter_pra.txt

texforge cover-letter nature
mv cover_letter.txt cover_letter_nature.txt

# Use appropriate version based on submission decision
```

### With Additional Context

```bash
# Include funding, conflicts of interest, suggested reviewers
texforge cover-letter prl -i "This work was supported by NSF Grant PHY-1234567. The authors declare no conflicts of interest. We suggest Dr. Alice Smith (MIT) and Dr. Bob Jones (Caltech) as potential reviewers."
```

## Customizing Generated Letters

The generated letters are **starting points**. You should:

### 1. Review Content
- Verify accuracy of extracted title
- Check that contributions are correctly summarized
- Ensure cited works are appropriate

### 2. Add Personal Details
```
Sincerely,

Dr. Jane Doe
Assistant Professor
Department of Physics
University Example
jane.doe@example.edu
```

### 3. Add Journal-Specific Elements

Some journals require:
- Suggested reviewers
- Conflicts of interest
- Data availability statements
- Funding information

Add these after the main letter content.

### 4. Adjust Tone if Needed

For different journals:
- **Nature/Science**: More accessible, emphasize broad impact
- **PRL**: Concise and confident, stress novelty
- **PRA/PRB**: More technical detail, emphasize rigor

## Journal-Specific Guidance

### Physical Review Letters (PRL)

**Key Criteria:**
- Fundamental advance in physics
- Broad interest to physics community
- Novel methodology or surprising result
- Clear and compelling presentation

**Cover Letter Should Emphasize:**
- Breakthrough nature of results
- Why findings are surprising or unexpected
- Broad implications across subfields
- Conciseness (PRL is 4 pages max)

**Example Opening:**
> We are pleased to submit our manuscript entitled "Observation of Quantum Entanglement in Macroscopic Systems" for consideration as a Letter in Physical Review Letters. This work reports the first observation of quantum entanglement at room temperature in a macroscopic mechanical oscillator...

### Physical Review A (PRA)

**Key Criteria:**
- Significant contribution to AMO or quantum physics
- Rigorous theoretical or experimental work
- Comprehensive treatment

**Cover Letter Should Emphasize:**
- Technical rigor and completeness
- Detailed methodology
- Comprehensive analysis
- Connection to AMO/quantum physics community

### Nature

**Key Criteria:**
- Exceptional novelty and importance
- Paradigm-shifting results
- Broad interest across disciplines
- Accessible presentation

**Cover Letter Should Emphasize:**
- Transformative potential
- Multidisciplinary impact
- Accessibility to broad scientific audience
- Potential for high citation impact

### Science

**Key Criteria:**
- Major advance in the field
- Broad scientific interest
- Innovative methodology
- Clear societal or scientific impact

**Cover Letter Should Emphasize:**
- Innovation in approach
- Societal relevance
- Cross-disciplinary appeal
- Clear significance statement

## Integration with Other Agents

### Complete Pre-Submission Workflow

```bash
# 1. Develop research idea
texforge brainstorm --journal "Physical Review Letters"

# 2. Write paper based on outline
# ... write sections using content/manuscript_outline.md ...

# 3. Compile paper
texforge compile

# 4. Get peer review
texforge review --journal prl

# 5. Revise based on feedback
# ... make changes ...
texforge compile

# 6. Review again if needed
texforge review --journal prl
# (Repeat until decision is "Accept" or "Minor Revision")

# 7. Generate cover letter
texforge cover-letter prl

# 8. Review letter and customize
vim cover_letter.txt

# 9. Submit!
```

## Understanding Output Files

### cover_letter.txt

**Purpose:** Direct submission use

**Format:** Plain text, ready to copy-paste

**Use Case:**
- Copy into journal submission system
- Attach as separate document
- Email to editor

**Editing:** Open in any text editor

### cover_letter.md

**Purpose:** Documentation and metadata

**Format:** Markdown with structured metadata

**Contains:**
- Generation timestamp
- Paper title
- Full letter text
- Extracted contributions list
- Cited works list

**Use Case:**
- Project documentation
- Version control
- Tracking letter iterations

## Tips for Better Cover Letters

### 1. Write Complete Paper First

The agent needs:
- Full abstract
- Complete introduction
- Results and conclusions
- Bibliography

Incomplete papers produce generic letters.

### 2. Use Descriptive Title

```latex
% Good
\title{Observation of Topological Phase Transitions in Quantum Simulators}

% Less helpful
\title{Quantum Systems}
```

### 3. Include Key Citations

Ensure your bibliography includes:
- Seminal works in the field
- Recent relevant papers (last 2-3 years)
- Direct competitors or related work

The agent will reference these in the motivation section.

### 4. Choose Appropriate Journal

```bash
# Match paper length and impact to journal
texforge cover-letter prl   # Short (4 pages), high impact
texforge cover-letter pra   # Longer (8-12 pages), technical depth
texforge cover-letter prx   # Any length, exceptional quality
```

### 5. Customize After Generation

**Always:**
- Add author names and affiliations
- Review and adjust content
- Add journal-specific requirements

**Never:**
- Submit generated letter without review
- Copy-paste without verification
- Use for multiple journals without modification

### 6. Use Additional Info Wisely

```bash
# Good uses of -i flag
texforge cover-letter prl -i "Funded by NSF Grant ABC-123. Data available at DOI:xyz."

# Avoid
texforge cover-letter prl -i "Please accept our paper because we worked very hard."
```

## Troubleshooting

### "Could not find TeX file"

**Problem:** Can't locate main LaTeX file

**Solution:**
```bash
# Ensure file exists
ls main.tex

# Or specify in config
echo "main_tex_file: paper.tex" >> .paper-config.yaml
texforge cover-letter prl -c .paper-config.yaml
```

### Letter is too generic

**Problem:** Generated content lacks specificity

**Causes:**
- Paper content incomplete
- Missing abstract or introduction
- No bibliography

**Solution:**
1. Complete paper first
2. Ensure all sections present
3. Add comprehensive bibliography
4. Re-generate: `texforge cover-letter prl`

### "Claude API call timed out"

**Problem:** Generation taking too long

**Solution:**
- Paper may be very long (>15,000 chars)
- Try again (usually transient)
- Simplify paper structure
- Report persistent issues

### Wrong journal profile

**Problem:** Using wrong journal code

**Solution:**
```bash
# Check supported codes
texforge cover-letter --help

# Use exact code
texforge cover-letter prl  # not "PRL" or "phys-rev-lett"
```

### Title extraction failed

**Problem:** Shows "Untitled Manuscript"

**Solution:**
Ensure proper LaTeX format:
```latex
\title{Your Title Here}
```

Not:
```latex
\title{
  Your Title Here  % Multi-line may cause issues
}
```

## Advanced Usage

### Custom Journal Profile

For journals not in the database:

```bash
# Agent will create generic profile
texforge cover-letter "Custom Journal Name"
```

The letter will be professional but may lack journal-specific details. Add these manually.

### Multiple Authors

Add author information after generation:

```
Sincerely,

Dr. Jane Doe¹*, Dr. John Smith², Dr. Alice Johnson¹

¹Department of Physics, University A
²Institute of Quantum Science, University B
*Corresponding author: jane.doe@example.edu
```

### Resubmission Letters

For revised submissions:

```bash
# Generate initial letter
texforge cover-letter prl

# Edit to add response to reviewers
vim cover_letter.txt
```

Add section like:
```
We appreciate the reviewers' constructive feedback. Below we address
each point raised:

Reviewer 1, Comment 1: ...
Response: ...
```

## Files Generated

| File | Format | Purpose | Overwritten |
|------|--------|---------|-------------|
| `cover_letter.txt` | Plain text | Submission-ready letter | Yes |
| `cover_letter.md` | Markdown | Documentation with metadata | Yes |

**Note:** Files are overwritten each time. Save important versions:

```bash
# Save version for specific journal
texforge cover-letter prl
cp cover_letter.txt cover_letter_prl_v1.txt

# After revisions
texforge cover-letter prl
cp cover_letter.txt cover_letter_prl_v2.txt
```

## See Also

- [APS Review Guide](APS_REVIEW_GUIDE.md) - Get peer review before submission
- [Brainstorming Guide](BRAINSTORMING_GUIDE.md) - Develop research ideas
- [CLI Guide](../CLI_GUIDE.md) - All TexForge commands

---

**Pro Tip:** Complete submission workflow:

```bash
# 1. Quality check your paper
texforge review --journal prl

# 2. Address any major weaknesses
# ... revise paper ...

# 3. Generate cover letter when ready
texforge cover-letter prl

# 4. Customize with your details
vim cover_letter.txt

# 5. Do final compile
texforge compile

# 6. Submit paper + cover letter!
```

This ensures both your paper and cover letter are polished and professional.
