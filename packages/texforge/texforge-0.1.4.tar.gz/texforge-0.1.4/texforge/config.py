"""
Configuration for Automated LaTeX Paper Maintenance
Optimized for Claude Max Plan
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List
import yaml


@dataclass
class GitConfig:
    """Git repository configuration"""
    remote: str = "origin"
    branch: str = "main"
    commit_prefix: str = "[auto]"
    auto_push: bool = True
    use_separate_branch: bool = False
    auto_branch_name: str = "auto-improvements"


@dataclass
class CheckConfig:
    """Configuration for which checks to run"""
    # Basic checks (always recommended)
    compile_check: bool = True
    consistency_check: bool = True
    math_check: bool = True
    citation_check: bool = True
    figure_check: bool = True
    
    # Advanced checks (enabled for Claude Max)
    proofread: bool = True
    style_check: bool = True
    full_review_on_major_changes: bool = True
    major_change_threshold: int = 30  # Lower threshold for Max plan
    
    # Periodic comprehensive reviews (new for Max)
    periodic_full_review: bool = True
    full_review_interval_hours: int = 24  # Once per day


@dataclass
class EmailConfig:
    """Email notification configuration"""
    enabled: bool = False
    to: str = ""
    from_addr: str = "latex-bot@yourdomain.com"
    subject_prefix: str = "[LaTeX Paper]"
    method: str = "smtp"  # smtp, sendmail, mailx
    
    # SMTP settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True


@dataclass
class SlackConfig:
    """Slack webhook configuration"""
    enabled: bool = False
    webhook_url: str = "https://hooks.slack.com/services/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"
    channel: Optional[str] = None
    username: str = "Paper Bot"
    icon_emoji: str = ":robot_face:"


@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""
    parse_mode: str = "Markdown"


@dataclass
class NtfyConfig:
    """ntfy.sh push notification configuration"""
    enabled: bool = False
    topic: str = ""
    server: str = "https://ntfy.sh"
    priority_default: str = "default"
    priority_high: str = "high"


@dataclass
class DiscordConfig:
    """Discord webhook configuration"""
    enabled: bool = False
    webhook_url: str = ""
    username: str = "Paper Bot"
    avatar_url: Optional[str] = None


@dataclass
class NotificationConfig:
    """All notification methods"""
    email: EmailConfig = field(default_factory=EmailConfig)
    slack: SlackConfig = field(default_factory=SlackConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    ntfy: NtfyConfig = field(default_factory=NtfyConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    
    # Notification settings
    include_diff: bool = False
    max_diff_lines: int = 50
    summary_level: str = "detailed"  # brief, detailed, full


@dataclass
class ScheduleConfig:
    """Schedule and timing configuration"""
    # OPTIMIZED FOR CLAUDE MAX - More frequent runs!
    run_interval_hours: int = 2  # Every 2 hours (instead of 5)
    
    quiet_hours_start: str = "23:00"
    quiet_hours_end: str = "07:00"
    
    # Working hours boost (optional)
    working_hours_enabled: bool = False
    working_hours_start: str = "09:00"
    working_hours_end: str = "18:00"
    working_hours_interval: int = 1  # Every hour during work


@dataclass
class AdvancedConfig:
    """Advanced configuration options"""
    claude_timeout: int = 600  # 10 minutes (more time for Max)
    skip_permissions: bool = True
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    
    # Logging
    log_dir: Path = field(default_factory=lambda: Path.home() / ".latex-paper-automation" / "logs")
    max_log_files: int = 60  # Keep 60 days with more frequent runs
    verbose: bool = False
    
    # Performance
    parallel_checks: bool = False  # Run some checks in parallel
    cache_results: bool = True  # Cache check results


@dataclass
class PaperMaintenanceConfig:
    """Complete configuration for paper maintenance"""
    git: GitConfig = field(default_factory=GitConfig)
    checks: CheckConfig = field(default_factory=CheckConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    advanced: AdvancedConfig = field(default_factory=AdvancedConfig)
    
    # Project-specific settings
    project_name: str = ""
    paper_directory: Path = field(default_factory=Path.cwd)
    main_tex_file: str = "main.tex"
    
    @classmethod
    def load(cls, config_path: Path) -> "PaperMaintenanceConfig":
        """Load configuration from YAML file"""
        if not config_path.exists():
            return cls()

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Reconstruct nested dataclasses
        config = cls()
        
        if 'git' in data:
            config.git = GitConfig(**data['git'])
        if 'checks' in data:
            config.checks = CheckConfig(**data['checks'])
        if 'notifications' in data:
            notif_data = data['notifications']
            config.notifications = NotificationConfig(
                email=EmailConfig(**notif_data.get('email', {})),
                slack=SlackConfig(**notif_data.get('slack', {})),
                telegram=TelegramConfig(**notif_data.get('telegram', {})),
                ntfy=NtfyConfig(**notif_data.get('ntfy', {})),
                discord=DiscordConfig(**notif_data.get('discord', {})),
            )
            # Copy top-level notification settings
            for key in ['include_diff', 'max_diff_lines', 'summary_level']:
                if key in notif_data:
                    setattr(config.notifications, key, notif_data[key])
        if 'schedule' in data:
            config.schedule = ScheduleConfig(**data['schedule'])
        if 'advanced' in data:
            adv_data = data['advanced'].copy()
            if 'log_dir' in adv_data:
                adv_data['log_dir'] = Path(adv_data['log_dir'])
            config.advanced = AdvancedConfig(**adv_data)
        
        # Top-level settings
        for key in ['project_name', 'main_tex_file']:
            if key in data:
                setattr(config, key, data[key])
        if 'paper_directory' in data:
            config.paper_directory = Path(data['paper_directory'])
        
        return config
    
    def save(self, config_path: Path) -> None:
        """Save configuration to YAML file"""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict, handling nested dataclasses and Paths
        data = self._to_dict()

        with open(config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)
        
        # Protect file if it contains passwords
        if self.notifications.email.smtp_password or \
           self.notifications.slack.webhook_url or \
           self.notifications.telegram.bot_token:
            config_path.chmod(0o600)
    
    def _to_dict(self) -> dict:
        """Convert config to dictionary for YAML serialization"""
        def convert(obj):
            if isinstance(obj, Path):
                return str(obj)
            elif hasattr(obj, '__dataclass_fields__'):
                return {k: convert(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert(item) for item in obj]
            else:
                return obj
        
        return convert(self)


# Claude Max Preset Configuration
def get_max_plan_config() -> PaperMaintenanceConfig:
    """
    Get optimized configuration for Claude Max plan
    
    Key optimizations:
    - More frequent runs (every 2 hours)
    - All checks enabled including proofread
    - Lower threshold for full reviews (30 lines instead of 50)
    - Longer timeout (10 minutes instead of 5)
    - Periodic comprehensive reviews every 24 hours
    - Optional: hourly checks during working hours
    """
    config = PaperMaintenanceConfig()
    
    # More aggressive checking
    config.checks.proofread = True
    config.checks.style_check = True
    config.checks.major_change_threshold = 30
    config.checks.periodic_full_review = True
    config.checks.full_review_interval_hours = 24
    
    # More frequent runs
    config.schedule.run_interval_hours = 2
    
    # Longer timeout for comprehensive checks
    config.advanced.claude_timeout = 600
    config.advanced.max_log_files = 60
    
    return config


# Claude Pro Preset Configuration  
def get_pro_plan_config() -> PaperMaintenanceConfig:
    """
    Get conservative configuration for Claude Pro plan
    
    Optimized for quota management:
    - Less frequent runs (every 5 hours)
    - Proofread disabled by default
    - Higher threshold for full reviews
    - Shorter timeout
    """
    config = PaperMaintenanceConfig()
    
    # Conservative checking
    config.checks.proofread = False
    config.checks.style_check = False
    config.checks.major_change_threshold = 50
    config.checks.periodic_full_review = False
    
    # Less frequent runs
    config.schedule.run_interval_hours = 5
    
    # Standard timeout
    config.advanced.claude_timeout = 300
    
    return config


if __name__ == "__main__":
    # Example: Create and save Max plan config
    config = get_max_plan_config()
    config.project_name = "My Quantum Paper"
    config.notifications.ntfy.enabled = True
    config.notifications.ntfy.topic = "my-paper-2025"

    config_path = Path.home() / ".paper-automation-config.yaml"
    config.save(config_path)
    print(f"Configuration saved to: {config_path}")

    # Load it back
    loaded = PaperMaintenanceConfig.load(config_path)
    print(f"Run interval: {loaded.schedule.run_interval_hours} hours")
    print(f"Proofread enabled: {loaded.checks.proofread}")
