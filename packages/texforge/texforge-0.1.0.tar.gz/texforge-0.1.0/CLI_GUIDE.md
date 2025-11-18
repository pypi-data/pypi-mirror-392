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
projects/quantum-dynamics/
├── .paper-config.yaml   # Configuration file
├── template.tex         # LaTeX template (rename to main.tex)
├── macros.tex          # Custom LaTeX macros
├── references.bib      # Bibliography file
├── README.md           # Project documentation
├── figs/               # Figures directory
├── data/               # Data files
└── code/               # Analysis code
```

### 2. Compile Your Paper

```bash
# Simple compilation (auto-detects main.tex)
cd projects/quantum-dynamics
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

## All Commands

### `texforge compile`

Compile LaTeX documents to PDF.

```bash
texforge compile [OPTIONS] [TEX_FILE]

Options:
  -c, --config PATH       Configuration file (YAML)
  --clean / --no-clean    Clean/keep auxiliary files (default: clean)
  --setup-template JOURNAL   Create journal template (pra/prl/generic)
  --setup-macros          Create macros.tex file
  --suggest-macros        Analyze and suggest macro definitions
  --fix-errors            Fix common LaTeX errors

Examples:
  texforge compile                           # Compile main.tex in current dir
  texforge compile paper.tex                 # Compile specific file
  texforge compile -c config.yaml           # Use configuration
  texforge compile --no-clean               # Keep .aux, .log files
  texforge compile --suggest-macros         # Get macro suggestions
```

### `texforge init`

Initialize a new paper project.

```bash
texforge init PROJECT_NAME [OPTIONS]

Options:
  --template TEMPLATE    LaTeX template (pra/prl/generic, default: generic)
  --dir PATH             Project directory (default: ./projects/PROJECT_NAME)

Examples:
  texforge init my-paper                    # Generic template
  texforge init my-paper --template pra     # Physical Review A
  texforge init my-paper --template prl     # Physical Review Letters
  texforge init my-paper --dir ~/papers/    # Custom directory
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
