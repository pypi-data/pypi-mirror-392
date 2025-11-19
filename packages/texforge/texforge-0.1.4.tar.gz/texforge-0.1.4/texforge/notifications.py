#!/usr/bin/env python3
"""
Notification handlers for paper maintenance system
Supports: Email (SMTP), Slack, Telegram, ntfy.sh, Discord
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import subprocess
import requests
from pathlib import Path

from .config import (
    PaperMaintenanceConfig,
    EmailConfig,
    SlackConfig,
    TelegramConfig,
    NtfyConfig,
    DiscordConfig
)


class NotificationError(Exception):
    """Base exception for notification errors"""
    pass


class EmailNotifier:
    """Send notifications via email"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
    
    def send(self, subject: str, body: str, html: bool = False) -> bool:
        """Send email notification"""
        if not self.config.enabled:
            return False
        
        try:
            if self.config.method == "smtp":
                return self._send_smtp(subject, body, html)
            elif self.config.method == "sendmail":
                return self._send_sendmail(subject, body)
            elif self.config.method == "mailx":
                return self._send_mailx(subject, body)
            else:
                raise NotificationError(f"Unknown email method: {self.config.method}")
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
    
    def _send_smtp(self, subject: str, body: str, html: bool) -> bool:
        """Send via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{self.config.subject_prefix} {subject}"
        msg['From'] = self.config.from_addr
        msg['To'] = self.config.to
        
        if html:
            part = MIMEText(body, 'html')
        else:
            part = MIMEText(body, 'plain')
        msg.attach(part)
        
        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            if self.config.smtp_use_tls:
                server.starttls()
            if self.config.smtp_user and self.config.smtp_password:
                server.login(self.config.smtp_user, self.config.smtp_password)
            server.send_message(msg)
        
        return True
    
    def _send_sendmail(self, subject: str, body: str) -> bool:
        """Send via sendmail"""
        message = f"Subject: {self.config.subject_prefix} {subject}\n\n{body}"
        
        result = subprocess.run(
            ["sendmail", self.config.to],
            input=message.encode(),
            capture_output=True
        )
        
        return result.returncode == 0
    
    def _send_mailx(self, subject: str, body: str) -> bool:
        """Send via mailx"""
        result = subprocess.run(
            ["mail", "-s", f"{self.config.subject_prefix} {subject}", self.config.to],
            input=body.encode(),
            capture_output=True
        )
        
        return result.returncode == 0


class SlackNotifier:
    """Send notifications to Slack via webhook"""
    
    def __init__(self, config: SlackConfig):
        self.config = config
    
    def send(self, message: str, title: Optional[str] = None) -> bool:
        """Send Slack notification"""
        if not self.config.enabled or not self.config.webhook_url:
            return False
        
        try:
            payload = {
                "username": self.config.username,
                "icon_emoji": self.config.icon_emoji,
            }
            
            if title:
                payload["text"] = f"*{title}*\n{message}"
            else:
                payload["text"] = message
            
            if self.config.channel:
                payload["channel"] = self.config.channel
            
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False


class TelegramNotifier:
    """Send notifications via Telegram bot"""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
    
    def send(self, message: str) -> bool:
        """Send Telegram notification"""
        if not self.config.enabled or not self.config.bot_token:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.config.chat_id,
                "text": message,
                "parse_mode": self.config.parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Telegram notification failed: {e}")
            return False


class NtfyNotifier:
    """Send notifications via ntfy.sh"""
    
    def __init__(self, config: NtfyConfig):
        self.config = config
    
    def send(self, message: str, title: Optional[str] = None, 
             priority: Optional[str] = None, tags: Optional[list] = None) -> bool:
        """Send ntfy notification"""
        if not self.config.enabled or not self.config.topic:
            return False
        
        try:
            url = f"{self.config.server}/{self.config.topic}"
            
            headers = {}
            if title:
                headers["Title"] = title
            if priority:
                headers["Priority"] = priority
            else:
                headers["Priority"] = self.config.priority_default
            if tags:
                headers["Tags"] = ",".join(tags)
            
            response = requests.post(
                url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"ntfy notification failed: {e}")
            return False


class DiscordNotifier:
    """Send notifications to Discord via webhook"""
    
    def __init__(self, config: DiscordConfig):
        self.config = config
    
    def send(self, message: str, title: Optional[str] = None) -> bool:
        """Send Discord notification"""
        if not self.config.enabled or not self.config.webhook_url:
            return False
        
        try:
            payload = {
                "username": self.config.username,
            }
            
            if self.config.avatar_url:
                payload["avatar_url"] = self.config.avatar_url
            
            if title:
                # Use embed for titled messages
                payload["embeds"] = [{
                    "title": title,
                    "description": message,
                    "color": 3447003  # Blue
                }]
            else:
                payload["content"] = message
            
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=10
            )
            
            return response.status_code in (200, 204)
            
        except Exception as e:
            print(f"Discord notification failed: {e}")
            return False


class NotificationManager:
    """Manage all notification methods"""
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.email = EmailNotifier(config.notifications.email)
        self.slack = SlackNotifier(config.notifications.slack)
        self.telegram = TelegramNotifier(config.notifications.telegram)
        self.ntfy = NtfyNotifier(config.notifications.ntfy)
        self.discord = DiscordNotifier(config.notifications.discord)
    
    def send_all(self, title: str, message: str, 
                 priority: str = "default") -> dict:
        """
        Send notification via all enabled methods
        
        Returns dict with status for each method
        """
        results = {}
        
        # Email
        if self.config.notifications.email.enabled:
            results['email'] = self.email.send(title, message)
        
        # Slack
        if self.config.notifications.slack.enabled:
            results['slack'] = self.slack.send(message, title)
        
        # Telegram
        if self.config.notifications.telegram.enabled:
            # Format for Telegram Markdown
            telegram_msg = f"*{title}*\n\n{message}"
            results['telegram'] = self.telegram.send(telegram_msg)
        
        # ntfy
        if self.config.notifications.ntfy.enabled:
            # Determine tags based on priority
            tags = []
            if "passed" in title.lower():
                tags = ["white_check_mark"]
            elif "failed" in title.lower():
                tags = ["x", "warning"]
            
            results['ntfy'] = self.ntfy.send(
                message,
                title=title,
                priority=priority,
                tags=tags
            )
        
        # Discord
        if self.config.notifications.discord.enabled:
            results['discord'] = self.discord.send(message, title)
        
        return results
    
    def send_summary(self, summary) -> dict:
        """Send notification for a RunSummary"""
        from auto_maintain_paper import RunSummary
        
        # Determine priority
        if summary.checks_total == 0:
            priority = "default"
            emoji = "ℹ️"
        elif summary.success_rate >= 0.8:
            priority = "default"
            emoji = "✅"
        else:
            priority = "high"
            emoji = "⚠️"
        
        # Create title
        title = f"{emoji} Paper Maintenance: {summary.checks_passed}/{summary.checks_total} checks passed"
        
        # Create message
        message = summary.to_markdown()
        
        # Send via all methods
        return self.send_all(title, message, priority)


# Testing functions
def test_notifications(config: PaperMaintenanceConfig) -> None:
    """Test all enabled notification methods"""
    manager = NotificationManager(config)
    
    test_title = "Test Notification"
    test_message = "This is a test notification from the LaTeX paper automation system."
    
    print("Testing notification methods...")
    print()
    
    results = manager.send_all(test_title, test_message)
    
    for method, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{method:12} {status}")
    
    print()
    print("Check your notification channels!")


if __name__ == "__main__":
    # Test notifications
    from pathlib import Path
    import sys
    
    config_path = Path.home() / ".paper-automation-config.yaml"
    
    if not config_path.exists():
        print("Configuration file not found.")
        print("Run setup-automation.py first.")
        sys.exit(1)
    
    config = PaperMaintenanceConfig.load(config_path)
    test_notifications(config)
