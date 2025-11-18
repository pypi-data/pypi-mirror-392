#!/usr/bin/env python3
"""
Daily Digest System - Aggregate all runs and send once per day
"""
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict
from dataclasses import dataclass

from .config import PaperMaintenanceConfig
from .notifications import NotificationManager


@dataclass
class DailyDigest:
    """Daily summary of all maintenance runs"""
    date: date
    total_runs: int
    total_checks: int
    checks_passed: int
    total_changes: int
    commits: int
    issues_found: List[str]
    improvements_made: List[str]
    run_summaries: List[Dict]
    
    @property
    def success_rate(self) -> float:
        return self.checks_passed / self.total_checks if self.total_checks > 0 else 0
    
    def to_markdown(self) -> str:
        """Generate markdown digest"""
        lines = [
            f"# Daily Paper Maintenance Digest",
            f"**Date:** {self.date.strftime('%A, %B %d, %Y')}",
            "",
            "---",
            "",
            "## Summary",
            f"- **Runs today:** {self.total_runs}",
            f"- **Total checks:** {self.total_checks}",
            f"- **Checks passed:** {self.checks_passed} ({self.success_rate*100:.1f}%)",
            f"- **Lines changed:** {self.total_changes}",
            f"- **Commits:** {self.commits}",
            "",
        ]
        
        # Success indicator
        if self.success_rate >= 0.95:
            emoji = "✅"
            status = "Excellent"
        elif self.success_rate >= 0.80:
            emoji = "🟢"
            status = "Good"
        elif self.success_rate >= 0.60:
            emoji = "🟡"
            status = "Needs Attention"
        else:
            emoji = "🔴"
            status = "Issues Found"
        
        lines.append(f"**Overall Status:** {emoji} {status}")
        lines.append("")
        
        # Issues
        if self.issues_found:
            lines.extend([
                "## Issues Found",
                "",
            ])
            for issue in self.issues_found[:10]:  # Top 10
                lines.append(f"- {issue}")
            if len(self.issues_found) > 10:
                lines.append(f"- ... and {len(self.issues_found) - 10} more")
            lines.append("")
        
        # Improvements
        if self.improvements_made:
            lines.extend([
                "## Improvements Made",
                "",
            ])
            for improvement in self.improvements_made[:10]:
                lines.append(f"- {improvement}")
            if len(self.improvements_made) > 10:
                lines.append(f"- ... and {len(self.improvements_made) - 10} more")
            lines.append("")
        
        # Activity timeline
        if self.run_summaries:
            lines.extend([
                "## Activity Timeline",
                "",
            ])
            for summary in self.run_summaries:
                time = summary.get('timestamp', 'Unknown')
                status = "✓" if summary.get('success_rate', 0) == 1.0 else "⚠"
                changes = summary.get('changes', 0)
                lines.append(
                    f"- **{time}** {status} "
                    f"{summary.get('checks_passed', 0)}/{summary.get('checks_total', 0)} checks, "
                    f"{changes} lines changed"
                )
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "💡 **Tip:** Review issues and plan tomorrow's work.",
        ])
        
        return "\n".join(lines)


class DigestManager:
    """Manage daily digest notifications"""
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.log_dir = config.advanced.log_dir
        self.digest_file = self.log_dir / "last_digest_sent.json"
    
    def get_last_digest_date(self) -> date:
        """Get date of last digest sent"""
        if self.digest_file.exists():
            with open(self.digest_file, 'r') as f:
                data = json.load(f)
                return date.fromisoformat(data['date'])
        return date.min
    
    def mark_digest_sent(self, digest_date: date) -> None:
        """Mark that digest was sent"""
        self.digest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.digest_file, 'w') as f:
            json.dump({'date': digest_date.isoformat()}, f)
    
    def should_send_digest(self) -> bool:
        """Check if we should send digest (once per day)"""
        last_sent = self.get_last_digest_date()
        today = date.today()
        return last_sent < today
    
    def collect_today_summaries(self) -> List[Dict]:
        """Collect all summaries from today"""
        today = date.today()
        summaries = []
        
        for summary_file in self.log_dir.glob("summary_*.md"):
            try:
                # Parse run ID: summary_20250115_143022.md
                run_id = summary_file.stem.replace("summary_", "")
                run_date = datetime.strptime(run_id, "%Y%m%d_%H%M%S")
                
                if run_date.date() != today:
                    continue
                
                # Parse summary
                content = summary_file.read_text()
                summary = self._parse_summary(content, run_date)
                summaries.append(summary)
                
            except Exception as e:
                print(f"Warning: Could not parse {summary_file.name}: {e}")
        
        return sorted(summaries, key=lambda x: x['timestamp'])
    
    def _parse_summary(self, content: str, timestamp: datetime) -> Dict:
        """Parse summary markdown"""
        import re
        
        # Extract checks
        checks_match = re.search(r"(\d+)/(\d+) checks passed", content)
        if checks_match:
            checks_passed = int(checks_match.group(1))
            checks_total = int(checks_match.group(2))
        else:
            checks_passed = 0
            checks_total = 0
        
        # Extract changes
        changes_match = re.search(r"(\d+) lines changed", content)
        changes = int(changes_match.group(1)) if changes_match else 0
        
        # Git status
        git_committed = "Changes committed" in content
        
        # Extract individual check results
        issues = []
        improvements = []
        
        for line in content.split('\n'):
            if '✗' in line and 'FAILED' in line:
                # Extract issue
                match = re.search(r'- ✗ (.+?): FAILED', line)
                if match:
                    issues.append(match.group(1))
            elif '✓' in line and 'PASSED' in line:
                # Extract improvement (if message follows)
                match = re.search(r'- ✓ (.+?): PASSED', line)
                if match:
                    improvements.append(match.group(1))
        
        return {
            'timestamp': timestamp.strftime('%H:%M'),
            'checks_passed': checks_passed,
            'checks_total': checks_total,
            'success_rate': checks_passed / checks_total if checks_total > 0 else 0,
            'changes': changes,
            'git_committed': git_committed,
            'issues': issues,
            'improvements': improvements,
        }
    
    def generate_digest(self) -> DailyDigest:
        """Generate today's digest"""
        summaries = self.collect_today_summaries()
        
        if not summaries:
            return DailyDigest(
                date=date.today(),
                total_runs=0,
                total_checks=0,
                checks_passed=0,
                total_changes=0,
                commits=0,
                issues_found=[],
                improvements_made=[],
                run_summaries=[],
            )
        
        # Aggregate statistics
        total_checks = sum(s['checks_total'] for s in summaries)
        checks_passed = sum(s['checks_passed'] for s in summaries)
        total_changes = sum(s['changes'] for s in summaries)
        commits = sum(1 for s in summaries if s['git_committed'])
        
        # Collect unique issues and improvements
        all_issues = []
        all_improvements = []
        for s in summaries:
            all_issues.extend(s['issues'])
            all_improvements.extend(s['improvements'])
        
        # Deduplicate while preserving order
        issues_found = list(dict.fromkeys(all_issues))
        improvements_made = list(dict.fromkeys(all_improvements))
        
        return DailyDigest(
            date=date.today(),
            total_runs=len(summaries),
            total_checks=total_checks,
            checks_passed=checks_passed,
            total_changes=total_changes,
            commits=commits,
            issues_found=issues_found,
            improvements_made=improvements_made,
            run_summaries=summaries,
        )
    
    def send_digest(self, force: bool = False) -> bool:
        """Send daily digest if due"""
        if not force and not self.should_send_digest():
            print("Digest already sent today")
            return False
        
        digest = self.generate_digest()
        
        if digest.total_runs == 0:
            print("No runs today, skipping digest")
            return False
        
        # Send via all enabled notification methods
        notifier = NotificationManager(self.config)
        
        title = f"📊 Daily Paper Digest - {digest.date.strftime('%b %d')}"
        message = digest.to_markdown()
        
        # Determine priority
        priority = "high" if digest.success_rate < 0.8 else "default"
        
        results = notifier.send_all(title, message, priority)
        
        # Mark as sent
        self.mark_digest_sent(digest.date)
        
        # Save digest
        digest_file = self.log_dir / f"digest_{digest.date.isoformat()}.md"
        digest_file.write_text(message)
        
        print(f"✓ Digest sent via {len([r for r in results.values() if r])} method(s)")
        print(f"  Saved to: {digest_file}")
        
        return True


def main():
    """Send daily digest"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Digest Manager")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force send digest even if already sent today"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview digest without sending"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Config not found: {args.config}")
        return 1
    
    config = PaperMaintenanceConfig.load(args.config)
    manager = DigestManager(config)
    
    if args.preview:
        # Just show digest
        digest = manager.generate_digest()
        print(digest.to_markdown())
    else:
        # Send digest
        success = manager.send_digest(force=args.force)
        return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
