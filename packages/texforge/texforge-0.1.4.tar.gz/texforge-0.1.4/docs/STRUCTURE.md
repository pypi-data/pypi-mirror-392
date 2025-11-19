# Repository Structure

Complete overview of the LaTeX Paper Automation repository structure.

```
latex-paper-automation/
│
├── README.md                      # Main documentation
├── QUICKSTART.md                  # 5-minute getting started guide
├── LICENSE                        # MIT License
├── CONTRIBUTING.md                # Contribution guidelines
├── requirements.txt               # Python dependencies
├── install.sh                     # Interactive installation script
│
├── bin/                           # Executable scripts
│   ├── auto-maintain-paper.sh     # Main automation orchestrator
│   └── uninstall.sh               # Uninstallation script
│
├── lib/                           # Python libraries
│   ├── validate_paper.py          # Paper validation logic
│   └── notification_cli.py       # Multi-channel notifications
│
├── docs/                          # Additional documentation
│   ├── GITHUB_DEPLOYMENT.md       # GitHub deployment guide
│
├── examples/                      # Example papers and configs
│   └── example-paper/             # Sample LaTeX paper
│       ├── main.tex               # Main LaTeX file
│       └── references.bib         # Bibliography
│
└── .github/                       # GitHub configuration
    └── workflows/                 # CI/CD workflows
        └── ci.yml                 # GitHub Actions CI/CD
```

## Core Components

### Installation System

**install.sh**
- Interactive installation wizard
- Dependency checking
- Configuration setup
- Cron job installation
- Test run option

**bin/uninstall.sh**
- Clean uninstallation
- Optional data preservation
- Cron job removal

### Automation Engine

**bin/auto-maintain-paper.sh**
- Main orchestration script
- Runs validation checks
- Integrates with Claude Code
- Manages git commits
- Sends notifications
- Generates detailed logs

### Validation System

**lib/validate_paper.py**
- LaTeX compilation check
- Reference validation (`\ref` → `\label`)
- Citation validation (`\cite` → `.bib`)
- TODO comment detection
- Spell checking (optional)
- JSON output for automation

### Notification System

**lib/notification_cli.py**
- Email (SMTP/sendmail)
- Slack (webhooks)
- Telegram (bot API)
- Discord (webhooks)
- ntfy.sh (push notifications)
- Configuration-driven
- Priority levels

## Documentation

### User Documentation

1. **README.md**: Complete user guide
   - Features overview
   - Installation instructions
   - Usage examples
   - Configuration reference
   - Troubleshooting

2. **QUICKSTART.md**: Fast track to working system
   - 5-minute setup
   - Common workflows
   - Quick troubleshooting

### Developer Documentation

1. **CONTRIBUTING.md**: Contribution guide
   - Development setup
   - Coding standards
   - Testing procedures
   - Pull request process

### Deployment Documentation

1. **docs/GITHUB_DEPLOYMENT.md**: GitHub-specific guide
   - Repository setup
   - GitHub Actions configuration
   - Release management
   - Security setup

   - CI/CD integration
   - Kubernetes deployment

## Configuration

### Installation Location

After installation:
```
~/.local/bin/latex-paper-tools/
├── bin/
│   ├── auto-maintain-paper.sh
│   └── uninstall.sh
└── lib/
    ├── validate_paper.py
    └── notification_cli.py
```

### User Configuration

```
~/.paper-automation-config.yaml    # Main configuration
```

Configuration sections:
- Paper settings (directory, main file, target journal)
- Automation settings (interval, token limits)
- Check configuration (enable/disable features)
- Git integration (commit, push)
- Notification settings (all channels)

### State Directory

```
~/.latex-paper-automation/
└── logs/
    ├── run_YYYYMMDD_HHMMSS.log      # Execution logs
    ├── summary_YYYYMMDD_HHMMSS.md   # Human-readable summaries
    └── cron.log                      # Cron execution log
```

## GitHub Integration

### Actions Workflows

**.github/workflows/ci.yml**
- Automated testing on push/PR
- Linting (Python and shell)
- Integration testing
- Release automation

### Issue Templates

(To be added via GitHub web interface)
- Bug report template
- Feature request template
- Pull request template

## Examples

### Example Paper

**examples/example-paper/**
- Complete LaTeX paper with RevTeX4
- Bibliography with 5 entries
- Proper structure for testing
- Used in CI/CD pipeline

### Example Configurations

(Can be added)
- Minimal configuration
- Full-featured configuration
- Token-conscious configuration
- Multi-paper configuration

## Dependencies

### System Requirements

**Required:**
- Python 3.8+
- LaTeX (texlive-latex-base, texlive-latex-extra)
- Git
- Bash (with common utilities: grep, awk, sed)

**Optional:**
- Claude Code CLI (for intelligent checks)
- aspell or hunspell (for spell checking)
- mail/sendmail (for email notifications)

### Python Libraries

**Currently none!**
- Uses only standard library
- No pip install required
- Maximizes compatibility

**Optional (for future features):**
- requests (for advanced HTTP)
- rich (for terminal UI)
- GitPython (for git integration)

## Extension Points

### Adding New Checks

1. Add check function to `lib/validate_paper.py`
2. Update `run_all_checks()` method
3. Add command-line flag
4. Document in README

### Adding New Notification Channels

1. Add method to `lib/notification_cli.py`
2. Update `send_all()` method
3. Add configuration template
4. Document setup process

### Adding New Automation Features

1. Add logic to `bin/auto-maintain-paper.sh`
2. Update configuration template
3. Add to installation wizard
4. Update documentation

## Testing

### Manual Testing

```bash
# Test validation
python3 lib/validate_paper.py --dir examples/example-paper

# Test notifications (dry run)
python3 lib/notification_cli.py --help

# Test full automation
bin/auto-maintain-paper.sh
```

### CI/CD Testing

GitHub Actions automatically tests:
- Script syntax
- Python linting
- Integration tests
- Example paper validation

## Maintenance

### Log Rotation

Automatic: Keeps last 50 logs of each type.

Manual cleanup:
```bash
# Remove old logs
find ~/.latex-paper-automation/logs -name "run_*.log" -mtime +30 -delete
```

### Updates

```bash
# Pull latest version
cd latex-paper-automation
git pull

# Re-run installer to update
./install.sh
```

### Uninstallation

```bash
# Run uninstall script
~/.local/bin/latex-paper-tools/bin/uninstall.sh

# Or manually remove
rm -rf ~/.local/bin/latex-paper-tools
rm ~/.paper-automation-config.yaml
rm -rf ~/.latex-paper-automation
crontab -l | grep -v auto-maintain-paper | crontab -
```

## Future Enhancements

Possible additions:
- Web dashboard
- Multi-paper management
- Template system
- Journal-specific checks
- Collaborative features
- Machine learning integration
- Performance analytics
- Cloud deployment options

## Version History

- **v1.0.0**: Initial release
  - Core validation system
  - Claude Code integration
  - Multi-channel notifications
  - Git automation

---

**For questions or suggestions about the structure, please open an issue!**
