# Quick Start Guide

Get LaTeX Paper Automation running in 5 minutes!

## Prerequisites

Ensure you have:
- ✓ Python 3.8+
- ✓ LaTeX (texlive)
- ✓ Git
- ✓ [Claude Code](https://docs.claude.com/en/docs/claude-code) (optional but recommended)

## Installation (3 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/jue-xu/latex-paper-automation.git
cd latex-paper-automation
```

### 2. Run Interactive Installer

```bash
./install.sh
```

The installer will:
1. Check dependencies ✓
2. Install files to `~/.local/bin/latex-paper-tools/`
3. Guide you through configuration
4. Optionally set up cron job
5. Offer a test run

**Just follow the prompts!** It's that easy.

## Quick Test (1 minute)

### Test with Example Paper

```bash
# Navigate to example
cd examples/example-paper

# Run validation
python3 ../../lib/validate_paper.py --dir .

# Expected output:
# ✓ Compilation: PDF generated successfully
# ✓ References: All 15 references valid
# ✓ Citations: All 5 citations valid
# ✓ TODOs: No TODO comments found
#
# SUMMARY: 4 passed, 0 failed
```

### Test Full Automation

```bash
# Run complete automation pipeline
~/.local/bin/latex-paper-tools/bin/auto-maintain-paper.sh

# Check generated summary
cat $(ls -t ~/.latex-paper-automation/logs/summary_*.md | head -1)
```

## Your First Paper (1 minute)

### Set Up Your Paper

1. **Navigate to your paper directory:**
   ```bash
   cd /path/to/your/paper
   ```

2. **Update configuration:**
   ```bash
   nano ~/.paper-automation-config.yaml
   
   # Update PAPER_DIR to your paper path:
   PAPER_DIR="/path/to/your/paper"
   ```

3. **Run maintenance:**
   ```bash
   ~/.local/bin/latex-paper-tools/bin/auto-maintain-paper.sh
   ```

That's it! Your paper is now being automatically maintained.

## Common Workflows

### Scenario 1: Daily Maintenance

**Goal**: Check paper once per day, notify via ntfy.sh

```bash
# Edit config
nano ~/.paper-automation-config.yaml
```

Set:
```bash
RUN_INTERVAL_HOURS=24
ENABLE_QUICK_CHECK=true
ENABLE_CONSISTENCY_CHECK=true
ENABLE_NOTIFICATIONS=true
ENABLE_NTFY=true
NTFY_TOPIC="my-paper"
```

Cron runs automatically! Get mobile notifications via [ntfy.sh app](https://ntfy.sh).

### Scenario 2: Pre-Submission Check

**Goal**: Comprehensive review before submitting to journal

```bash
# Edit config temporarily
nano ~/.paper-automation-config.yaml
```

Enable:
```bash
ENABLE_MATH_CHECK=true
ENABLE_FULL_REVIEW=true  # Uses more tokens!
ENABLE_CITATION_CHECK=true
```

Run manually:
```bash
~/.local/bin/latex-paper-tools/bin/auto-maintain-paper.sh
```

Review the detailed summary in logs.

### Scenario 3: Collaborative Writing

**Goal**: Auto-commit improvements, notify team

```bash
nano ~/.paper-automation-config.yaml
```

Set:
```bash
ENABLE_GIT_COMMIT=true
ENABLE_GIT_PUSH=true
ENABLE_SLACK=true
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Team gets Slack updates on every automated improvement!

## Notifications Setup

### ntfy.sh (Recommended - No Signup!)

```bash
ENABLE_NTFY=true
NTFY_TOPIC="my-unique-topic"
```

Install [ntfy app](https://ntfy.sh) and subscribe to your topic. Done!

### Email

```bash
ENABLE_EMAIL=true
EMAIL_TO="you@example.com"
```

Requires working system mail.

### Slack

```bash
ENABLE_SLACK=true
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK"
```

Create webhook at: https://api.slack.com/messaging/webhooks

### Telegram

```bash
ENABLE_TELEGRAM=true
TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
TELEGRAM_CHAT_ID="123456789"
```

Create bot with [@BotFather](https://t.me/botfather).

## Monitoring

### View Recent Activity

```bash
# Latest run log
tail ~/.latex-paper-automation/logs/run_$(ls -t ~/.latex-paper-automation/logs/run_*.log | head -1)

# Latest summary
cat $(ls -t ~/.latex-paper-automation/logs/summary_*.md | head -1)

# Watch cron execution
tail -f ~/.latex-paper-automation/cron.log
```

### Check Cron Status

```bash
# View installed cron job
crontab -l | grep auto-maintain-paper

# Should show something like:
# 0 */6 * * * /home/user/.local/bin/latex-paper-tools/bin/auto-maintain-paper.sh
```

## Customization

### Enable/Disable Checks

Edit `~/.paper-automation-config.yaml`:

```bash
# Fast checks (low token usage)
ENABLE_QUICK_CHECK=true
ENABLE_CONSISTENCY_CHECK=true

# Moderate checks
ENABLE_CITATION_CHECK=true
ENABLE_MATH_CHECK=false

# Expensive check (uses many tokens)
ENABLE_FULL_REVIEW=false
```

### Adjust Frequency

```bash
# Check every N hours
RUN_INTERVAL_HOURS=6    # Every 6 hours
RUN_INTERVAL_HOURS=12   # Twice daily
RUN_INTERVAL_HOURS=24   # Once daily
```

## Troubleshooting

### "Configuration not found"

```bash
# Re-run installer
./install.sh

# Or create config manually
cp examples/example-config.yaml ~/.paper-automation-config.yaml
nano ~/.paper-automation-config.yaml
```

### "Claude Code not found"

Claude Code is optional. Either:
1. Install it: https://docs.claude.com/en/docs/claude-code
2. Disable it in config:
   ```bash
   ENABLE_CLAUDE_CODE=false
   ```

### "Permission denied"

```bash
# Fix script permissions
chmod +x ~/.local/bin/latex-paper-tools/bin/*.sh
chmod +x ~/.local/bin/latex-paper-tools/lib/*.py
```

### "LaTeX compilation failed"

```bash
# Check your LaTeX installation
pdflatex --version

# Test compilation manually
cd /path/to/paper
pdflatex main.tex
```

## Next Steps

### 1. Customize Checks

Read about available checks in the [README](README.md#features).

### 2. Set Up Notifications

Configure your preferred notification channel.

### 3. Explore Advanced Features

- Git integration for version control
- Multiple notification channels
- Token-conscious operation modes
- Custom check configurations

### 4. Join the Community

- [Report issues](https://github.com/jue-xu/latex-paper-automation/issues)
- [Request features](https://github.com/jue-xu/latex-paper-automation/discussions)
- [Contribute](CONTRIBUTING.md)

## Get Help

- **Documentation**: See [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/jue-xu/latex-paper-automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jue-xu/latex-paper-automation/discussions)
- **GitHub Deployment**: See [GitHub Deployment Guide](docs/GITHUB_DEPLOYMENT.md)

---

**You're all set! Happy writing! 📄✨**
