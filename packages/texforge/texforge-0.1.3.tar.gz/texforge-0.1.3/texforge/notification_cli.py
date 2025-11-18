#!/usr/bin/env python3
"""
CLI wrapper for notification system
Provides command-line interface to notifications.py
"""

import sys
import argparse
from pathlib import Path

from .config import PaperMaintenanceConfig
from .notifications import NotificationManager


def main():
    """Command-line interface for sending notifications"""
    parser = argparse.ArgumentParser(
        description='Send notifications via multiple channels',
        epilog='Example: notification_cli.py --subject "Build Complete" --body "Success!" --slack --email'
    )

    parser.add_argument('--subject', required=True,
                       help='Notification subject/title')
    parser.add_argument('--body', required=True,
                       help='Notification body/message')
    parser.add_argument('--priority', default='default',
                       choices=['min', 'low', 'default', 'high', 'urgent'],
                       help='Notification priority (default: default)')

    # Channel selection
    parser.add_argument('--email', action='store_true',
                       help='Send via email')
    parser.add_argument('--slack', action='store_true',
                       help='Send via Slack')
    parser.add_argument('--telegram', action='store_true',
                       help='Send via Telegram')
    parser.add_argument('--discord', action='store_true',
                       help='Send via Discord')
    parser.add_argument('--ntfy', action='store_true',
                       help='Send via ntfy.sh')
    parser.add_argument('--all', action='store_true',
                       help='Send via all configured channels')

    # Configuration
    parser.add_argument('--config', type=Path,
                       default=Path.home() / '.paper-automation-config.yaml',
                       help='Path to config file (default: ~/.paper-automation-config.yaml)')

    # Direct credential arguments (optional, override config)
    parser.add_argument('--slack-webhook', type=str,
                       help='Slack webhook URL (or set SLACK_WEBHOOK env var)')
    parser.add_argument('--telegram-token', type=str,
                       help='Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)')
    parser.add_argument('--telegram-chat-id', type=str,
                       help='Telegram chat ID (or set TELEGRAM_CHAT_ID env var)')
    parser.add_argument('--discord-webhook', type=str,
                       help='Discord webhook URL (or set DISCORD_WEBHOOK env var)')
    parser.add_argument('--ntfy-topic', type=str,
                       help='ntfy.sh topic (or set NTFY_TOPIC env var)')

    args = parser.parse_args()

    # Load configuration if it exists, otherwise create default
    if args.config.exists():
        try:
            config = PaperMaintenanceConfig.load(args.config)
        except Exception as e:
            print(f"Warning: Could not load configuration: {e}", file=sys.stderr)
            print("Using default configuration with environment variables", file=sys.stderr)
            config = PaperMaintenanceConfig()
    else:
        # No config file - use default config with env vars
        config = PaperMaintenanceConfig()

    # Override config with command-line arguments or environment variables
    import os

    if args.slack or args.slack_webhook or os.getenv('SLACK_WEBHOOK'):
        config.notifications.slack.enabled = True
        config.notifications.slack.webhook_url = (
            args.slack_webhook or
            os.getenv('SLACK_WEBHOOK') or
            config.notifications.slack.webhook_url
        )

    if args.telegram or args.telegram_token or os.getenv('TELEGRAM_BOT_TOKEN'):
        config.notifications.telegram.enabled = True
        config.notifications.telegram.bot_token = (
            args.telegram_token or
            os.getenv('TELEGRAM_BOT_TOKEN') or
            config.notifications.telegram.bot_token
        )
        config.notifications.telegram.chat_id = (
            args.telegram_chat_id or
            os.getenv('TELEGRAM_CHAT_ID') or
            config.notifications.telegram.chat_id
        )

    if args.discord or args.discord_webhook or os.getenv('DISCORD_WEBHOOK'):
        config.notifications.discord.enabled = True
        config.notifications.discord.webhook_url = (
            args.discord_webhook or
            os.getenv('DISCORD_WEBHOOK') or
            config.notifications.discord.webhook_url
        )

    if args.ntfy or args.ntfy_topic or os.getenv('NTFY_TOPIC'):
        config.notifications.ntfy.enabled = True
        config.notifications.ntfy.topic = (
            args.ntfy_topic or
            os.getenv('NTFY_TOPIC') or
            config.notifications.ntfy.topic
        )

    # If --all is specified, send via all enabled channels
    # Otherwise, only send via explicitly requested channels
    if args.all:
        # Use send_all which respects enabled flags in config
        manager = NotificationManager(config)
        results = manager.send_all(args.subject, args.body, args.priority)

        # Print results
        success_count = 0
        total_count = 0
        for channel, success in results.items():
            total_count += 1
            if success:
                success_count += 1
                print(f"✓ {channel.capitalize()} notification sent")
            else:
                print(f"✗ {channel.capitalize()} notification failed", file=sys.stderr)

        print(f"\nNotification summary: {success_count}/{total_count} sent successfully")
        sys.exit(0 if success_count > 0 else 1)

    else:
        # Send only via explicitly requested channels
        if not any([args.email, args.slack, args.telegram, args.discord, args.ntfy]):
            parser.print_help()
            print("\nError: No notification channels specified. Use --all or specify channels.", file=sys.stderr)
            sys.exit(1)

        manager = NotificationManager(config)
        success_count = 0
        total_requested = 0

        # Email
        if args.email:
            total_requested += 1
            if config.notifications.email.enabled:
                if manager.email.send(args.subject, args.body):
                    print("✓ Email notification sent")
                    success_count += 1
                else:
                    print("✗ Email notification failed", file=sys.stderr)
            else:
                print("Email notification skipped: not enabled in config", file=sys.stderr)

        # Slack
        if args.slack:
            total_requested += 1
            if config.notifications.slack.enabled:
                if manager.slack.send(args.body, args.subject):
                    print("✓ Slack notification sent")
                    success_count += 1
                else:
                    print("✗ Slack notification failed", file=sys.stderr)
            else:
                print("Slack notification skipped: not enabled in config", file=sys.stderr)

        # Telegram
        if args.telegram:
            total_requested += 1
            if config.notifications.telegram.enabled:
                telegram_msg = f"*{args.subject}*\n\n{args.body}"
                if manager.telegram.send(telegram_msg):
                    print("✓ Telegram notification sent")
                    success_count += 1
                else:
                    print("✗ Telegram notification failed", file=sys.stderr)
            else:
                print("Telegram notification skipped: not enabled in config", file=sys.stderr)

        # Discord
        if args.discord:
            total_requested += 1
            if config.notifications.discord.enabled:
                if manager.discord.send(args.body, args.subject):
                    print("✓ Discord notification sent")
                    success_count += 1
                else:
                    print("✗ Discord notification failed", file=sys.stderr)
            else:
                print("Discord notification skipped: not enabled in config", file=sys.stderr)

        # ntfy
        if args.ntfy:
            total_requested += 1
            if config.notifications.ntfy.enabled:
                # Determine tags based on subject
                tags = []
                subject_lower = args.subject.lower()
                if "passed" in subject_lower or "success" in subject_lower:
                    tags = ["white_check_mark"]
                elif "failed" in subject_lower or "error" in subject_lower:
                    tags = ["x", "warning"]

                if manager.ntfy.send(args.body, args.subject, args.priority, tags):
                    print("✓ ntfy notification sent")
                    success_count += 1
                else:
                    print("✗ ntfy notification failed", file=sys.stderr)
            else:
                print("ntfy notification skipped: not enabled in config", file=sys.stderr)

        print(f"\nNotification summary: {success_count}/{total_requested} sent successfully")
        sys.exit(0 if success_count > 0 else 1)


if __name__ == "__main__":
    main()
