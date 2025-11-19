# TexForge Command-Line Tool Guide

## Installation

```bash
# From the repository root
pip install -e .

# Or for system-wide installation (when published to PyPI)
pip install texforge
```

## Quick Start

### 1. Initialize a New Paper

```bash
# Create a new paper project with Physical Review A template
texforge init quantum-dynamics --template pra

# Or with a custom directory
texforge init quantum-dynamics --template pra --dir ~/research/papers/
```

This creates:
```
quantum-dynamics/
├── .paper-config.yaml   # Configuration file
├── template.tex         # LaTeX template (rename to main.tex)
├── macros.tex          # Custom LaTeX macros (empty, ready for your macros)
├── references.bib      # Bibliography file
├── README.md           # Project documentation
├── content/            # Section content files
│   ├── intro.tex       # Introduction section
│   ├── methods.tex     # Methods section
│   ├── results.tex     # Results section
│   └── conclusion.tex  # Conclusion section
├── figs/               # Figures directory
├── data/               # Data files
└── code/               # Analysis code
```

**Note:** The project is created directly as `quantum-dynamics/` (no `projects/` parent folder).

### 2. Compile Your Paper

```bash
# Simple compilation (auto-detects main.tex)
cd quantum-dynamics
mv template.tex main.tex
texforge compile

# Compile specific file
texforge compile paper.tex

# Compile with configuration
texforge compile -c .paper-config.yaml

# Keep auxiliary files
texforge compile --no-clean
```

### 3. Advanced Compilation Features

```bash
# Setup macros file
texforge compile --setup-macros

# Analyze and suggest macro definitions
texforge compile --suggest-macros

# Attempt to fix common errors
texforge compile --fix-errors

# Setup journal template
texforge compile --setup-template pra
```

### 4. Compile with Notifications

Send compilation results to Slack automatically:

```bash
# Send notification on compilation (requires webhook setup)
texforge compile --notify

# Provide webhook directly
texforge compile --notify --slack-webhook "https://hooks.slack.com/services/..."

# Or use environment variable
export SLACK_WEBHOOK="https://hooks.slack.com/services/..."
texforge compile --notify

# Auto-fix errors and notify on success
texforge compile --fix-errors --notify

# Note: --fix-errors automatically sends notification on FAILURE
# even without --notify flag
texforge compile --fix-errors
```

**Notification behavior:**
- **`--notify`**: Sends notification for all compilation results (success or failure)
- **`--fix-errors`**: Automatically sends notification if error fixing fails (no `--notify` needed)
- **`--fix-errors --notify`**: Sends notification for both success and failure

## All Commands

### `texforge compile`

Compile LaTeX documents to PDF.

```bash
texforge compile [OPTIONS] [TEX_FILE]

Options:
  -c, --config PATH       Configuration file (YAML)
  --clean / --no-clean    Clean/keep auxiliary files (default: clean)
  --setup-template JOURNAL   Create journal template (pra/prl/ns/tcs/generic)
  --setup-macros          Create macros.tex file
  --suggest-macros        Analyze and suggest macro definitions
  --fix-errors            Fix common LaTeX errors (auto-notifies on failure)
  --notify                Send compilation result to Slack
  --slack-webhook URL     Slack webhook URL (or use SLACK_WEBHOOK env var)

Examples:
  texforge compile                           # Compile main.tex in current dir
  texforge compile paper.tex                 # Compile specific file
  texforge compile -c config.yaml           # Use configuration
  texforge compile --no-clean               # Keep .aux, .log files
  texforge compile --suggest-macros         # Get macro suggestions
  texforge compile --notify                 # Send Slack notification
  texforge compile --fix-errors --notify    # Fix errors and notify on success
```

### `texforge init`

Initialize a new paper project with complete folder structure.

```bash
texforge init PROJECT_NAME [OPTIONS]

Options:
  --template TEMPLATE    LaTeX template (pra/prl/ns/tcs/generic, default: generic)
  --dir PATH             Project directory (default: ./PROJECT_NAME)

Available Templates:
  - pra:     Physical Review A (two-column, revtex4-2)
  - prl:     Physical Review Letters (two-column, revtex4-2)
  - ns:      Nature/Science journals (intro, setup, results, discussion, refs, methods, appendix)
  - tcs:     Theoretical Computer Science (detailed intro with Preliminaries/Previous Work/Contributions)
  - generic: Standard article class

Examples:
  texforge init my-paper                      # Generic template in ./my-paper/
  texforge init my-paper --template pra       # Physical Review A
  texforge init my-paper --template ns        # Nature/Science structure
  texforge init my-paper --template tcs       # Theoretical CS structure
  texforge init my-paper --dir ~/papers/      # Custom parent directory

Project Structure:
  Creates PROJECT_NAME/ with:
  - template.tex (rename to main.tex)
  - macros.tex (empty, ready for custom macros)
  - references.bib
  - content/ folder with section files (depends on template)
    - PRA/PRL/Generic: intro.tex, methods.tex, results.tex, conclusion.tex
    - NS (Nature/Science): intro.tex, setup.tex, results.tex, discussion.tex, methods.tex, appendix.tex
    - TCS: intro.tex (with Preliminaries/Previous Work/Contributions subsections), methods.tex, results.tex, conclusion.tex
  - .paper-config.yaml (with default Slack webhook)
  - figs/, data/, code/ directories
  - library/ folder for key references (PDF/HTML)
  - README.md
```

### `texforge prove`

Generate rigorous mathematical proofs with AI verification.

```bash
texforge prove [OPTIONS]

Options:
  --label LABEL           LaTeX label of theorem to prove (e.g., "thm:main")
  --file PATH             Specific .tex file to search (optional)
  --theorem TEXT          Theorem statement (alternative to --label)
  --name TEXT             Theorem name (required with --theorem)
  --assumptions TEXT...   List of assumptions (optional)
  --context TEXT          Mathematical context (default: quantum information theory)
  -c, --config PATH       Configuration file

Examples:
  # Prove theorem from LaTeX label (recommended)
  texforge prove --label thm:main
  texforge prove --label lem:bound --file content/methods.tex

  # Provide theorem directly
  texforge prove --name "Main Theorem" --theorem "For any k-local Hamiltonian..."

  # With assumptions and context
  texforge prove --label thm:main \
    --assumptions "H is 2-local" "n >= 2" \
    --context "quantum information theory"

Workflow:
  1. Reads theorem from LaTeX file (or command line)
  2. Generates proof strategy
  3. Constructs detailed proof steps
  4. Verifies with checker agent (rigor score 0-10)
  5. Iteratively fixes issues (up to 3 rounds)
  6. Writes proof back to original .tex file

Output:
  - proofs/theorem_name.tex (standalone LaTeX proof)
  - proofs/theorem_name_notes.md (detailed notes with rigor score)
  - Original .tex file updated with proof (if --label used)
  - .tex.backup (automatic backup before modification)

Supported Contexts:
  - quantum information theory (default)
  - computational complexity theory
  - information theory
  - theoretical computer science
  - graph theory

See docs/PROVER_GUIDE.md for full documentation.
```

### `texforge arxiv-download`

Download arXiv papers in multiple formats for your research library.

```bash
texforge arxiv-download ARXIV_ID [OPTIONS]

Options:
  --format {latex,pdf,html}   Download format (default: latex)
                              - latex: LaTeX source code (default)
                              - pdf: PDF document
                              - html: HTML version from ar5iv.labs.arxiv.org
  --library PATH              Library directory (default: ./library)
  --name NAME                 Custom folder/file name for downloaded content
  --list                      List all downloaded arXiv sources

Arguments:
  ARXIV_ID                    ArXiv ID or URL (e.g., '2301.12345' or
                              'https://arxiv.org/abs/2301.12345')

Examples:
  # Download LaTeX source (default) - extracts to folder
  texforge arxiv-download 2301.12345

  # Download PDF version
  texforge arxiv-download 2301.12345 --format pdf

  # Download HTML version (from ar5iv)
  texforge arxiv-download 2301.12345 --format html

  # Download from arXiv URL
  texforge arxiv-download https://arxiv.org/abs/2301.12345

  # Custom name for downloaded content
  texforge arxiv-download 2301.12345 --name quantum_ml_paper
  texforge arxiv-download 2301.12345 --format pdf --name reference_paper

  # Use with custom library directory
  texforge arxiv-download 2301.12345 --library ~/my-project/references/

  # List all downloaded arXiv sources
  texforge arxiv-download --list

Workflow:
  1. Automatically extracts arXiv ID from various URL formats
  2. Downloads in specified format (LaTeX source, PDF, or HTML)
  3. Saves to library/ directory (default) or custom location
  4. LaTeX source: Extracts .tex, .bib, and .bbl files to folder
  5. PDF/HTML: Downloads single file with appropriate extension
  6. Prompts before overwriting existing files

Output Locations:
  - LaTeX format: library/arxiv_XXXXX/ (folder with source files)
  - PDF format:   library/arxiv_XXXXX.pdf (single PDF file)
  - HTML format:  library/arxiv_XXXXX.html (single HTML file)

Error Handling:
  - Raises error if LaTeX source not available (some papers PDF-only)
  - Raises error if HTML version not available on ar5iv
  - Validates downloaded files (PDF header check, HTML content check)
  - Automatically cleans up invalid downloads

Integration with Brainstorming:
  Download references before brainstorming to enable Dr. Literature agent:

  texforge arxiv-download 2301.12345
  texforge arxiv-download 2302.98765 --format pdf
  texforge brainstorm

  The Dr. Literature agent will read and reference these papers during
  the brainstorming discussion.

Tip: Use LaTeX format for papers you want to study in detail (see source code),
     PDF format for quick references, and HTML format for web-readable versions.
```

### `texforge validate`

Run quality validation on your paper.

```bash
texforge validate [OPTIONS] [TEX_FILE]

Options:
  -c, --config PATH       Configuration file (YAML)

Examples:
  texforge validate                         # Validate main.tex
  texforge validate -c config.yaml         # With configuration
```

### `texforge maintain`

Run automated paper maintenance.

```bash
texforge maintain -c CONFIG [OPTIONS]

Options:
  -c, --config PATH       Configuration file (YAML, required)
  -v, --verbose           Verbose output
  --paper-dir PATH        Paper directory (overrides config)

Examples:
  texforge maintain -c .paper-config.yaml
  texforge maintain -c config.yaml -v
  texforge maintain -c config.yaml --paper-dir ~/papers/quantum/
```

### `texforge notify`

Send notifications via configured channels.

```bash
texforge notify MESSAGE [OPTIONS]

Options:
  --subject TEXT          Notification subject (default: "TexForge Notification")
  -c, --config PATH       Configuration file (default: ~/.paper-automation-config.yaml)
  --priority LEVEL        Priority: min/low/default/high/urgent
  --email                 Send via email
  --slack                 Send via Slack
  --telegram              Send via Telegram
  --discord               Send via Discord
  --ntfy                  Send via ntfy.sh

  # Direct credential options (override config file)
  --slack-webhook URL     Slack webhook URL
  --telegram-token TOKEN  Telegram bot token
  --telegram-chat-id ID   Telegram chat ID
  --discord-webhook URL   Discord webhook URL
  --ntfy-topic TOPIC      ntfy.sh topic

Examples:
  # Using config file
  texforge notify "Build complete" --slack
  texforge notify "Paper updated" --email --telegram

  # Without config file (using direct credentials)
  texforge notify --slack --slack-webhook "https://hooks.slack.com/..." "Done"
  texforge notify --ntfy --ntfy-topic "my-paper" "Compilation complete"

  # Using environment variables
  export SLACK_WEBHOOK="https://hooks.slack.com/services/..."
  texforge notify --slack "Build complete"

  export NTFY_TOPIC="my-paper-updates"
  texforge notify --ntfy "New version ready"

  # Multiple channels with priority
  texforge notify --subject "Critical" --priority urgent \
    --slack --telegram "Error detected"
```

**Environment Variables:**
- `SLACK_WEBHOOK` - Slack webhook URL
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Telegram chat ID
- `DISCORD_WEBHOOK` - Discord webhook URL
- `NTFY_TOPIC` - ntfy.sh topic

These environment variables are used if no config file exists or if credentials are not provided via command-line arguments.

## Configuration File

The `.paper-config.yaml` file controls all aspects of paper maintenance:

```yaml
# Paper Settings
paper_directory: /path/to/paper
main_tex_file: main.tex
target_journal: Physical Review A

# Schedule
schedule:
  run_interval_hours: 6
  quiet_hours_start: "23:00"
  quiet_hours_end: "07:00"

# Checks to Run
checks:
  compile_check: true
  citation_check: true
  math_check: true
  consistency_check: false

# Git Integration
git:
  remote: "origin"
  branch: "main"
  commit_prefix: "paper: "
  auto_push: false

# Notifications
notifications:
  email:
    enabled: false
  slack:
    enabled: false
    webhook_url: ""
  ntfy:
    enabled: true
    topic: "my-paper-updates"
```

## Templates

### Physical Review A (pra)

```latex
\documentclass[aps,pra,twocolumn,superscriptaddress]{revtex4-2}
```

Features:
- Two-column layout
- APS bibliography style
- Superscript affiliations
- Includes common physics packages

### Physical Review Letters (prl)

```latex
\documentclass[aps,prl,twocolumn,superscriptaddress]{revtex4-2}
```

Features:
- Two-column layout (4 page limit)
- APS bibliography style
- Compact format

### Generic (generic)

```latex
\documentclass[11pt,a4paper]{article}
```

Features:
- Single-column layout
- Standard article class
- Flexible formatting

## Workflow Example

```bash
# 1. Create new project
texforge init quantum-entanglement --template pra

# 2. Setup
cd projects/quantum-entanglement
mv template.tex main.tex

# 3. Edit your paper
# ... edit main.tex, add references.bib ...

# 4. Compile
texforge compile

# 5. Validate
texforge validate

# 6. Setup automated maintenance
texforge maintain -c .paper-config.yaml -v

# 7. Get notifications
texforge notify "Paper compilation successful" --slack
```

## Tips

1. **Use editable installation during development:**
   ```bash
   pip install -e .
   ```
   This allows you to edit the code and immediately see changes.

2. **Use config files for reproducibility:**
   Store `.paper-config.yaml` in each project for consistent settings.

3. **Combine with Git hooks:**
   Add `texforge compile` to your pre-commit hook for automatic validation.

4. **Macro management:**
   Run `texforge compile --suggest-macros` periodically to optimize repeated expressions.

5. **Python API usage:**
   You can also use TexForge as a Python library:
   ```python
   from texforge import PDFCompiler, PaperMaintenanceConfig

   config = PaperMaintenanceConfig.load("config.yaml")
   compiler = PDFCompiler(config)
   result = compiler.compile()
   ```

## Troubleshooting

### Command not found: texforge

```bash
# Reinstall package
pip install -e .

# Check installation
pip list | grep texforge

# Verify entry point
which texforge
```

### Import errors

```bash
# Make sure you're using the texforge package, not direct imports
# Instead of: from config import PaperMaintenanceConfig
# Use: from texforge.config import PaperMaintenanceConfig

# Or in CLI context, texforge handles imports automatically
```

### Compilation fails

```bash
# Try fixing common errors first
texforge compile --fix-errors

# Check the log
cat *.log

# Validate paper structure
texforge validate
```

## Getting Help

```bash
# General help
texforge --help

# Command-specific help
texforge compile --help
texforge init --help
texforge validate --help
texforge maintain --help
texforge notify --help

# Version
texforge --version
```
