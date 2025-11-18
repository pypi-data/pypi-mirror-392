# Notification Setup Guide

This guide provides detailed instructions for setting up notifications for your LaTeX paper automation system.

## Table of Contents

- [Overview](#overview)
- [Email Setup](#email-setup)
- [Slack Setup](#slack-setup)
- [Telegram Setup](#telegram-setup)
- [Discord Setup](#discord-setup)
- [ntfy.sh Setup (Recommended)](#ntfysh-setup-recommended)
- [Configuration File](#configuration-file)
- [Testing Notifications](#testing-notifications)
- [Troubleshooting](#troubleshooting)

## Overview

The LaTeX paper automation system supports five notification methods:

| Method | Pros | Cons | Recommended For |
|--------|------|------|-----------------|
| **Email** | Universal, reliable | Requires system mail setup | Individual researchers |
| **Slack** | Great for teams | Requires workspace access | Collaborative projects |
| **Telegram** | Mobile-friendly, instant | Requires bot setup | Personal notifications |
| **Discord** | Rich formatting, team-friendly | Requires server access | Team communication |
| **ntfy.sh** | No signup, instant, mobile apps | Public topics unless paid | Quick setup, personal use |

You can enable multiple notification methods simultaneously.

## Email Setup

### Requirements

- Working system mail setup (`sendmail` or `mailx`)
- Or configured SMTP server

### Configuration

Edit `~/.paper-automation-config.yaml`:

```bash
# Email
ENABLE_EMAIL=true
EMAIL_TO="you@example.com"
EMAIL_FROM="paper-automation@example.com"  # Optional
```

### System Mail Setup

**For Ubuntu/Debian:**

```bash
# Install sendmail
sudo apt-get install sendmail

# Or install mailutils
sudo apt-get install mailutils
```

**For macOS:**

macOS includes `mail` command by default. Just configure your email settings:

```bash
# Test email
echo "Test" | mail -s "Test Subject" you@example.com
```

**For advanced SMTP configuration:**

Configure `sendmail` or use `msmtp`:

```bash
# Install msmtp
sudo apt-get install msmtp msmtp-mta

# Configure ~/.msmtprc
cat > ~/.msmtprc << EOF
defaults
auth           on
tls            on
tls_trust_file /etc/ssl/certs/ca-certificates.crt

account        gmail
host           smtp.gmail.com
port           587
from           your-email@gmail.com
user           your-email@gmail.com
password       your-app-password

account default : gmail
EOF

chmod 600 ~/.msmtprc
```

### Testing

```bash
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test Email" \
    --body "Testing email notifications" \
    --email
```

## Slack Setup

### Requirements

- Slack workspace access
- Permission to create incoming webhooks

### Step-by-Step Setup

1. **Create Incoming Webhook:**
   - Go to https://api.slack.com/messaging/webhooks
   - Click "Create your Slack app"
   - Choose "From scratch"
   - Name your app (e.g., "LaTeX Paper Automation")
   - Select your workspace
   - Click "Create App"

2. **Enable Incoming Webhooks:**
   - In your app settings, click "Incoming Webhooks"
   - Toggle "Activate Incoming Webhooks" to **On**
   - Click "Add New Webhook to Workspace"
   - Select the channel where notifications should appear
   - Click "Allow"

3. **Copy Webhook URL:**
   - Copy the webhook URL (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`)

### Configuration

Edit `~/.paper-automation-config.yaml`:

```bash
# Slack
ENABLE_SLACK=true
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Message Format

Slack notifications will appear as:

```
LaTeX Paper Automation - Status Update

Validation Results:
✓ Compilation: PASSED
✓ References: PASSED
✓ Citations: PASSED
```

### Testing

**From your local machine:**

```bash
# Test with curl first
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Hello, World!"}' \
  YOUR_WEBHOOK_URL

# Test with Python script
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test Slack Notification" \
    --body "Testing Slack integration" \
    --slack
```

**Note about testing environments:**
- Some sandboxed/cloud environments may be blocked by Slack's security policies
- If testing from Docker, CI/CD, or cloud IDEs fails, test from your local machine
- The webhook will work fine in production on your actual machine

### Troubleshooting Slack

**Error: HTTP 403 Forbidden / Access Denied**

This error can occur in two scenarios:

1. **Invalid webhook:**
   - The webhook URL may be expired or revoked
   - Create a new webhook following the steps above
   - Verify you copied the complete URL including all characters

2. **IP/Environment blocked:**
   - Slack blocks requests from certain cloud/shared IPs for security
   - Test with `curl` from the same environment to verify
   - If curl also fails, test from your local machine instead
   - The webhook will work in production on your actual machine

**Error: HTTP 404 Not Found**
- The webhook URL is malformed
- Check for any missing characters or extra spaces
- The URL should start with `https://hooks.slack.com/services/`

**Messages not appearing:**
- Check the channel where you installed the webhook
- The app may have been removed from the workspace
- Reinstall the webhook to the correct channel

## Telegram Setup

### Requirements

- Telegram account
- Mobile or desktop Telegram app

### Step-by-Step Setup

1. **Create Bot:**
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Start a chat and send `/newbot`
   - Follow prompts to choose a name and username
   - Copy the bot token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

2. **Get Your Chat ID:**
   - Start a chat with your new bot (send any message)
   - Search for [@userinfobot](https://t.me/userinfobot)
   - Start a chat and it will reply with your user ID
   - Copy your chat ID (numeric, e.g., `123456789`)

   **Alternative method:**
   ```bash
   # Send a message to your bot first, then:
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   # Look for "chat":{"id": YOUR_CHAT_ID in the response
   ```

3. **Send Test Message:**
   ```bash
   curl -X POST \
     "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
     -d "chat_id=<YOUR_CHAT_ID>" \
     -d "text=Test message"
   ```

### Configuration

Edit `~/.paper-automation-config.yaml`:

```bash
# Telegram
ENABLE_TELEGRAM=true
TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
TELEGRAM_CHAT_ID="123456789"
```

### Testing

```bash
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test Telegram Notification" \
    --body "Testing Telegram integration" \
    --telegram
```

## Discord Setup

### Requirements

- Discord server where you have "Manage Webhooks" permission

### Step-by-Step Setup

1. **Create Webhook:**
   - Open Discord and go to your server
   - Right-click the channel where you want notifications
   - Click "Edit Channel"
   - Go to "Integrations" → "Webhooks"
   - Click "New Webhook"
   - Name it (e.g., "LaTeX Paper Automation")
   - Click "Copy Webhook URL"

2. **Webhook URL Format:**
   - The URL looks like: `https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN`

### Configuration

Edit `~/.paper-automation-config.yaml`:

```bash
# Discord
ENABLE_DISCORD=true
DISCORD_WEBHOOK="https://discord.com/api/webhooks/YOUR/WEBHOOK"
```

### Testing

```bash
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test Discord Notification" \
    --body "Testing Discord integration" \
    --discord
```

## ntfy.sh Setup (Recommended!)

### Why ntfy.sh?

- **No signup required** - Just choose a topic name
- **Free** - Unlimited notifications
- **Mobile apps** - Available for Android and iOS
- **Simple** - Easiest to set up
- **Fast** - Instant notifications
- **Privacy** - Can self-host if desired

### Step-by-Step Setup

1. **Choose a Topic Name:**
   - Pick a unique topic name (e.g., `my-paper-automation-xyz123`)
   - More unique = better (prevents others from seeing your notifications)
   - Can use random string for privacy

2. **Install Mobile App (Optional but Recommended):**
   - **Android:** https://play.google.com/store/apps/details?id=io.heckel.ntfy
   - **iOS:** https://apps.apple.com/us/app/ntfy/id1625396347
   - Open app and subscribe to your topic name

3. **Or Use Web Interface:**
   - Go to https://ntfy.sh/your-topic-name
   - Keep the tab open to receive notifications

### Configuration

Edit `~/.paper-automation-config.yaml`:

```bash
# ntfy.sh
ENABLE_NTFY=true
NTFY_TOPIC="my-paper-automation-xyz123"  # Your unique topic
```

### Testing

```bash
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test ntfy Notification" \
    --body "Testing ntfy.sh integration" \
    --ntfy
```

### Advanced ntfy.sh Features

**Priority Levels:**
The system automatically sets priority based on results:
- `high` - If checks fail
- `default` - If all checks pass

**Self-Hosting:**
You can run your own ntfy server:
```bash
# Install
sudo snap install ntfy

# Run
ntfy serve

# Configure custom server
NTFY_SERVER="https://your-server.com"
```

## Configuration File

Your notification settings are stored in `~/.paper-automation-config.yaml`:

```bash
# ========== Notification Settings ==========
ENABLE_NOTIFICATIONS=true

# Email
ENABLE_EMAIL=false
EMAIL_TO=""
EMAIL_FROM=""

# Slack
ENABLE_SLACK=true
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Telegram
ENABLE_TELEGRAM=false
TELEGRAM_BOT_TOKEN=""
TELEGRAM_CHAT_ID=""

# Discord
ENABLE_DISCORD=false
DISCORD_WEBHOOK=""

# ntfy.sh
ENABLE_NTFY=true
NTFY_TOPIC="my-unique-topic"
```

**Security Note:**
- Config file permissions are automatically set to `600` (owner read/write only)
- Contains sensitive tokens and webhooks
- Never commit this file to version control
- It's in `.gitignore` by default

## Testing Notifications

### Test Individual Channels

```bash
# Test email
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test" --body "Test message" --email

# Test Slack
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test" --body "Test message" --slack

# Test Telegram
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test" --body "Test message" --telegram

# Test Discord
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test" --body "Test message" --discord

# Test ntfy
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test" --body "Test message" --ntfy
```

### Test All Enabled Channels

```bash
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "Test All Channels" \
    --body "Testing all enabled notification methods" \
    --all
```

### Test Different Priority Levels

```bash
python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py \
    --subject "High Priority Test" \
    --body "Testing high priority notification" \
    --priority high \
    --ntfy
```

Priority levels: `min`, `low`, `default`, `high`, `urgent`

## Troubleshooting

### General Issues

**No notifications received:**
1. Check `ENABLE_NOTIFICATIONS=true` in config
2. Verify specific channel is enabled (e.g., `ENABLE_SLACK=true`)
3. Test the channel individually using the commands above
4. Check system logs: `~/.latex-paper-automation/logs/`

**Checking configuration:**
```bash
# View notification settings
grep -A 20 "Notification Settings" ~/.paper-automation-config.yaml

# Verify config file permissions
ls -l ~/.paper-automation-config.yaml
# Should show: -rw------- (600)
```

### Email Issues

**Mail command not found:**
```bash
# Install mail utilities
sudo apt-get install mailutils
```

**Emails not sending:**
```bash
# Check system mail log
tail -f /var/log/mail.log

# Test mail command
echo "Test" | mail -s "Test" your@email.com
```

### Slack Issues

**403 Forbidden / Access Denied:**
- Webhook URL is invalid or revoked
- Create a new webhook in Slack
- Verify the complete URL was copied

**404 Not Found:**
- Webhook URL is malformed
- Check for spaces or missing characters

### Telegram Issues

**Bot not responding:**
- Verify bot token is correct
- Make sure you've sent at least one message to the bot
- Check chat ID is correct (should be numeric)

**Wrong chat:**
- Verify chat ID using [@userinfobot](https://t.me/userinfobot)
- For groups, get ID using `getUpdates` API call

### Discord Issues

**Webhook not working:**
- Verify webhook wasn't deleted in Discord
- Check you have "Manage Webhooks" permission
- Recreate webhook if necessary

### ntfy.sh Issues

**Not receiving notifications:**
- Verify topic name matches in app and config
- Check mobile app is subscribed to correct topic
- Try web interface: https://ntfy.sh/your-topic-name
- Check topic isn't too common (someone else might be using it)

**Rate limiting:**
- Free tier has rate limits
- Consider self-hosting for unlimited notifications

## Best Practices

1. **Use Multiple Channels:**
   - Enable both immediate (Slack, Telegram) and archival (Email) methods
   - Redundancy ensures you don't miss important updates

2. **Secure Your Credentials:**
   - Never commit config file to git
   - Use strong, unique topic names for ntfy.sh
   - Regenerate webhooks if accidentally exposed

3. **Test Regularly:**
   - Test notifications after any config changes
   - Verify all channels before relying on automation

4. **Priority Levels:**
   - System automatically uses `high` priority for failures
   - This helps filter important notifications

5. **Team Notifications:**
   - Use Slack or Discord for team projects
   - Use Telegram or ntfy.sh for personal projects
   - Email for formal records

## Quick Reference

| Action | Command |
|--------|---------|
| Test all notifications | `python3 ~/.local/bin/latex-paper-tools/lib/notification_cli.py --subject "Test" --body "Test" --all` |
| View config | `cat ~/.paper-automation-config.yaml` |
| Edit config | `nano ~/.paper-automation-config.yaml` |
| Check last notification | `tail ~/.latex-paper-automation/logs/run_*.log` |
| Verify permissions | `ls -l ~/.paper-automation-config.yaml` |

---

For more information, see the main [README.md](../README.md) or open an issue on GitHub.
