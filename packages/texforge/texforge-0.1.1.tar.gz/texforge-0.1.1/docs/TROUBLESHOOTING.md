# Troubleshooting Guide

This guide covers common issues and their solutions for the LaTeX Paper Automation system.

## Table of Contents

- [Cron Job Issues](#cron-job-issues)
- [Claude Code Issues](#claude-code-issues)
- [Notification Issues](#notification-issues)
- [Permission Issues](#permission-issues)
- [Compilation Issues](#compilation-issues)
- [Git Issues](#git-issues)
- [General Debugging](#general-debugging)

## Cron Job Issues

### Cron Job Not Running

**Check if cron job exists:**

```bash
crontab -l | grep auto-maintain-paper
```

**Check cron logs:**

```bash
# View cron execution log
tail -f ~/.latex-paper-automation/cron.log

# View latest run log
tail ~/.latex-paper-automation/logs/run_*.log
```

**Test manual run:**

```bash
~/.local/bin/latex-paper-tools/bin/auto-maintain-paper.sh
```

**Common causes:**

1. **Cron service not running:**
   ```bash
   # Check cron status
   sudo systemctl status cron

   # Start cron if needed
   sudo systemctl start cron
   ```

2. **Wrong PATH in cron:**
   - Cron runs with a minimal PATH
   - The install script adds full paths to avoid this issue
   - If still having issues, add PATH to your crontab:
   ```bash
   crontab -e
   # Add at the top:
   PATH=/usr/local/bin:/usr/bin:/bin
   ```

3. **User permissions:**
   ```bash
   # Ensure config file is readable
   ls -l ~/.paper-automation-config.yaml
   # Should show: -rw------- (600)

   # Ensure scripts are executable
   ls -l ~/.local/bin/latex-paper-tools/bin/*.sh
   # Should show: -rwxr-xr-x or similar
   ```

### Cron Running but No Output

**Check if paper directory exists:**

```bash
# Check config
grep PAPER_DIR ~/.paper-automation-config.yaml

# Verify directory exists
ls -la /path/to/your/paper
```

**Check logs for errors:**

```bash
# View all recent logs
ls -lt ~/.latex-paper-automation/logs/

# View the most recent error log
cat $(ls -t ~/.latex-paper-automation/logs/run_*.log | head -1)
```

## Claude Code Issues

### Claude Code Not Installed

```bash
# Check if Claude Code is installed
which claude-code

# If not found, install it
# Follow instructions at: https://docs.claude.com/en/docs/claude-code
```

### Authentication Issues

```bash
# Re-authenticate
claude-code auth

# Test Claude Code
echo "print('Hello from Claude!')" | claude-code

# Check authentication status
claude-code --version
```

**Common authentication errors:**

1. **Token expired:**
   - Run `claude-code auth` to re-authenticate
   - Follow the browser prompts

2. **Network issues:**
   - Check internet connection
   - Verify firewall settings allow HTTPS connections

### Claude Code Checks Not Running

**Verify Claude Code is enabled in config:**

```bash
grep ENABLE_CLAUDE_CODE ~/.paper-automation-config.yaml
# Should show: ENABLE_CLAUDE_CODE=true
```

**Check token limits:**

```bash
# Review your token usage
# Adjust MAX_TOKENS_PER_RUN if needed
grep MAX_TOKENS_PER_RUN ~/.paper-automation-config.yaml
```

**Reduce token usage:**

```bash
# Edit config to disable expensive checks
nano ~/.paper-automation-config.yaml

# Set these to false to reduce token usage:
ENABLE_MATH_CHECK=false
ENABLE_FULL_REVIEW=false
```

## Notification Issues

### No Notifications Received

**Check if notifications are enabled:**

```bash
grep ENABLE_NOTIFICATIONS ~/.paper-automation-config.yaml
# Should show: ENABLE_NOTIFICATIONS=true
```

**Test notification script directly:**

```bash
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test" \
    --body "Testing notifications" \
    --all
```

**Check specific notification settings:**

```bash
# View all notification settings
grep -A 20 "Notification Settings" ~/.paper-automation-config.yaml
```

**Verify at least one notification method is enabled:**

```bash
# Check which methods are enabled
grep "^ENABLE_" ~/.paper-automation-config.yaml | grep -E "(EMAIL|SLACK|TELEGRAM|DISCORD|NTFY)"
```

### Method-Specific Issues

For detailed troubleshooting of specific notification methods (Email, Slack, Telegram, Discord, ntfy.sh), see:

**[NOTIFICATION_SETUP.md - Troubleshooting Section](NOTIFICATION_SETUP.md#troubleshooting)**

Quick links:
- [Email troubleshooting](NOTIFICATION_SETUP.md#email-issues)
- [Slack troubleshooting](NOTIFICATION_SETUP.md#slack-issues)
- [Telegram troubleshooting](NOTIFICATION_SETUP.md#telegram-issues)
- [Discord troubleshooting](NOTIFICATION_SETUP.md#discord-issues)
- [ntfy.sh troubleshooting](NOTIFICATION_SETUP.md#ntfysh-issues)

## Permission Issues

### Script Permission Errors

```bash
# Fix script permissions
chmod +x ~/.local/bin/latex-paper-tools/bin/*.sh
chmod +x ~/.local/bin/latex-paper-tools/lib/*.py

# Fix config permissions
chmod 600 ~/.paper-automation-config.yaml
```

### Cannot Write to Log Directory

```bash
# Create log directory if it doesn't exist
mkdir -p ~/.latex-paper-automation/logs

# Fix permissions
chmod 755 ~/.latex-paper-automation
chmod 755 ~/.latex-paper-automation/logs
```

### Git Permission Issues

```bash
# Check paper directory permissions
ls -la /path/to/your/paper

# You should own the directory
# If not, you may need to change ownership or disable git features

# Disable git if needed
nano ~/.paper-automation-config.yaml
# Set: ENABLE_GIT_COMMIT=false
```

## Compilation Issues

### LaTeX Compilation Fails

**Check if LaTeX is installed:**

```bash
which pdflatex
which xelatex
which lualatex

# If not found, install LaTeX
# Ubuntu/Debian:
sudo apt-get install texlive-full

# macOS:
brew install --cask mactex
```

**Test compilation manually:**

```bash
cd /path/to/your/paper
pdflatex main.tex
```

**Check for missing packages:**

```bash
# Install additional LaTeX packages
# Ubuntu/Debian:
sudo apt-get install texlive-latex-extra texlive-fonts-extra

# Or use tlmgr:
tlmgr install <package-name>
```

**Check main tex file setting:**

```bash
grep MAIN_TEX_FILE ~/.paper-automation-config.yaml
# Verify this matches your actual main tex file name
```

### References or Citations Broken

**Run BibTeX/Biber:**

```bash
cd /path/to/your/paper

# For BibTeX:
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# For Biber:
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

**Check bibliography file exists:**

```bash
ls /path/to/your/paper/*.bib
```

## Git Issues

### Auto-commit Failing

**Check git is configured:**

```bash
git config --global user.name
git config --global user.email

# If not set:
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

**Check if directory is a git repository:**

```bash
cd /path/to/your/paper
git status

# If not a git repo, initialize:
git init
```

**Check for uncommitted changes:**

```bash
cd /path/to/your/paper
git status
```

### Auto-push Failing

**Check remote repository is configured:**

```bash
cd /path/to/your/paper
git remote -v

# Add remote if needed:
git remote add origin https://github.com/user/repo.git
```

**Check authentication:**

```bash
# Test push manually
git push origin main

# If authentication fails, set up SSH keys or personal access token
```

**Disable auto-push if not needed:**

```bash
nano ~/.paper-automation-config.yaml
# Set: ENABLE_GIT_PUSH=false
```

## General Debugging

### Enable Verbose Logging

Run the script manually with bash debugging:

```bash
bash -x ~/.local/bin/latex-paper-tools/bin/auto-maintain-paper.sh
```

### Check All Dependencies

```bash
# Python version
python3 --version

# Required: Python 3.8+
# If older, upgrade Python

# Check required Python modules
python3 -c "import json, subprocess, os, sys; print('Core modules OK')"
```

### View Recent Logs

```bash
# List all logs
ls -lt ~/.latex-paper-automation/logs/

# View the most recent run log
tail -50 $(ls -t ~/.latex-paper-automation/logs/run_*.log | head -1)

# View the most recent summary
cat $(ls -t ~/.latex-paper-automation/logs/summary_*.md | head -1)
```

### Clean Start

If all else fails, try a fresh installation:

```bash
# Backup your config
cp ~/.paper-automation-config.yaml ~/paper-automation-config-backup.sh

# Remove old installation
rm -rf ~/.local/bin/latex-paper-tools
rm -rf ~/.latex-paper-automation

# Re-run installer
cd /path/to/latex-paper-automation
./install.sh

# Restore your config if needed
cp ~/paper-automation-config-backup.sh ~/.paper-automation-config.yaml
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs:**
   ```bash
   tail -50 $(ls -t ~/.latex-paper-automation/logs/run_*.log | head -1)
   ```

2. **Search existing issues:**
   - [GitHub Issues](https://github.com/jue-xu/latex-paper-automation/issues)

3. **Create a new issue:**
   - Include your OS and version
   - Include relevant log excerpts
   - Include your config (with sensitive info removed)
   - Describe what you expected vs what happened

4. **Check documentation:**
   - [README.md](../README.md) - Main documentation
   - [QUICKSTART.md](QUICKSTART.md) - Quick start guide
   - [NOTIFICATION_SETUP.md](NOTIFICATION_SETUP.md) - Notification configuration
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development information

---

**Need more help?** Open an issue on [GitHub Issues](https://github.com/jue-xu/latex-paper-automation/issues)
