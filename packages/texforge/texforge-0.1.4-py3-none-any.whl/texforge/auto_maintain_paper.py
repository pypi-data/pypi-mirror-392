#!/usr/bin/env python3
"""
Automated LaTeX Paper Maintenance Script
Main automation engine for running checks, committing, and notifying
"""
import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import List, Optional, Tuple
import json
import time

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: Install 'rich' for better output: pip install rich")

from .config import PaperMaintenanceConfig


@dataclass
class CheckResult:
    """Result of a single check"""
    name: str
    passed: bool
    duration: float
    message: str = ""
    error: Optional[str] = None


@dataclass
class RunSummary:
    """Summary of an entire maintenance run"""
    run_id: str
    timestamp: datetime
    project_name: str
    changes_detected: int
    checks: List[CheckResult]
    git_committed: bool
    git_pushed: bool
    git_commit_hash: Optional[str] = None
    errors: List[str] = None
    
    @property
    def checks_passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)
    
    @property
    def checks_total(self) -> int:
        return len(self.checks)
    
    @property
    def success_rate(self) -> float:
        return self.checks_passed / self.checks_total if self.checks_total > 0 else 0.0
    
    def to_markdown(self) -> str:
        """Generate markdown summary"""
        lines = [
            f"# Paper Maintenance Summary",
            f"**Run ID:** {self.run_id}",
            f"**Date:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project:** {self.project_name}",
            "",
            "---",
            "",
        ]
        
        if self.changes_detected > 0:
            lines.extend([
                "## Changes Detected",
                f"{self.changes_detected} lines changed in .tex/.bib files",
                "",
            ])
        else:
            lines.extend([
                "## Status: No Changes",
                "No changes detected in LaTeX or bibliography files.",
                "",
            ])
            return "\n".join(lines)
        
        lines.extend([
            "## Checks Performed",
            "",
        ])
        
        for check in self.checks:
            status = "✓" if check.passed else "✗"
            lines.append(f"- {status} {check.name}: {'PASSED' if check.passed else 'FAILED'}")
            if check.message:
                lines.append(f"  {check.message}")
        
        lines.extend([
            "",
            f"**Summary:** {self.checks_passed}/{self.checks_total} checks passed",
            "",
        ])
        
        if self.git_committed:
            lines.extend([
                "## Git Status",
                f"Changes committed: `{self.git_commit_hash}`",
            ])
            if self.git_pushed:
                lines.append("Pushed to remote")
        else:
            lines.extend([
                "## Git Status",
                "No changes to commit",
            ])
        
        if self.errors:
            lines.extend([
                "",
                "## Errors",
                "",
            ])
            for error in self.errors:
                lines.append(f"- {error}")
        
        return "\n".join(lines)


class PaperMaintenance:
    """Main paper maintenance automation class"""
    
    def __init__(self, config: PaperMaintenanceConfig, verbose: bool = False):
        self.config = config
        self.verbose = verbose or config.advanced.verbose
        self.console = Console() if RICH_AVAILABLE else None
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = config.advanced.log_dir / f"run_{self.run_id}.log"
        self.summary_file = config.advanced.log_dir / f"summary_{self.run_id}.md"
        
        # Ensure log directory exists
        config.advanced.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file
        with open(self.log_file, 'w') as f:
            f.write(f"Paper Maintenance Run: {self.run_id}\n")
            f.write(f"Started: {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message to file and optionally console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_line)
        
        if self.verbose:
            if self.console:
                if level == "ERROR":
                    self.console.print(f"[red]✗ {message}[/red]")
                elif level == "SUCCESS":
                    self.console.print(f"[green]✓ {message}[/green]")
                elif level == "WARNING":
                    self.console.print(f"[yellow]⚠ {message}[/yellow]")
                else:
                    self.console.print(f"  {message}")
            else:
                print(f"{log_line.strip()}")
    
    def check_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours"""
        now = datetime.now().time()
        start = datetime.strptime(self.config.schedule.quiet_hours_start, "%H:%M").time()
        end = datetime.strptime(self.config.schedule.quiet_hours_end, "%H:%M").time()
        
        if start <= end:
            in_quiet = start <= now <= end
        else:  # Crosses midnight
            in_quiet = now >= start or now <= end
        
        if in_quiet:
            self.log(f"In quiet hours ({self.config.schedule.quiet_hours_start} - {self.config.schedule.quiet_hours_end})")
            return True
        
        return False
    
    def check_git_repo(self) -> bool:
        """Verify we're in a git repository"""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.config.paper_directory,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            self.log("Not a git repository", "ERROR")
            return False
    
    def get_uncommitted_changes(self) -> int:
        """Count lines changed in .tex and .bib files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat", "HEAD", "--", "*.tex", "*.bib"],
                cwd=self.config.paper_directory,
                capture_output=True,
                text=True
            )
            
            output = result.stdout.strip()
            if not output:
                return 0
            
            # Parse last line: "2 files changed, 127 insertions(+), 43 deletions(-)"
            last_line = output.split('\n')[-1]
            
            insertions = 0
            deletions = 0
            
            if "insertion" in last_line:
                parts = last_line.split(',')
                for part in parts:
                    if "insertion" in part:
                        insertions = int(part.split()[0])
                    elif "deletion" in part:
                        deletions = int(part.split()[0])
            
            return insertions + deletions
            
        except Exception as e:
            self.log(f"Error counting changes: {e}", "ERROR")
            return 0
    
    def run_claude_check(self, command: str, description: str) -> CheckResult:
        """Run a Claude Code check"""
        self.log(f"Running: {description}")
        start_time = time.time()
        
        try:
            cmd = ["claude", "-p", command]
            if self.config.advanced.skip_permissions:
                cmd = ["claude", "--dangerously-skip-permissions", "-p", command]
            
            result = subprocess.run(
                cmd,
                cwd=self.config.paper_directory,
                capture_output=True,
                text=True,
                timeout=self.config.advanced.claude_timeout
            )
            
            duration = time.time() - start_time
            
            # Log output
            with open(self.log_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Check: {description}\n")
                f.write(f"{'='*80}\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write("\nSTDERR:\n")
                    f.write(result.stderr)
                f.write(f"\n{'='*80}\n\n")
            
            if result.returncode == 0:
                self.log(f"✓ {description} completed ({duration:.1f}s)", "SUCCESS")
                return CheckResult(
                    name=description,
                    passed=True,
                    duration=duration
                )
            else:
                self.log(f"✗ {description} failed", "ERROR")
                return CheckResult(
                    name=description,
                    passed=False,
                    duration=duration,
                    error=result.stderr
                )
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log(f"⚠ {description} timed out after {duration:.1f}s", "WARNING")
            return CheckResult(
                name=description,
                passed=False,
                duration=duration,
                error="Timeout"
            )
        except Exception as e:
            duration = time.time() - start_time
            self.log(f"✗ {description} error: {e}", "ERROR")
            return CheckResult(
                name=description,
                passed=False,
                duration=duration,
                error=str(e)
            )
    
    def git_pull(self) -> bool:
        """Pull latest changes from remote"""
        try:
            self.log("Pulling latest changes...")
            subprocess.run(
                ["git", "pull", self.config.git.remote, self.config.git.branch],
                cwd=self.config.paper_directory,
                check=True,
                capture_output=True
            )
            self.log("✓ Pulled latest changes", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"⚠ Pull had issues: {e}", "WARNING")
            return False
    
    def git_commit_and_push(self, summary: RunSummary) -> Tuple[bool, bool, Optional[str]]:
        """Commit and push changes if any"""
        try:
            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "diff", "--quiet", "HEAD", "--", "*.tex", "*.bib"],
                cwd=self.config.paper_directory
            )
            
            if result.returncode == 0:
                # No changes
                self.log("No changes to commit")
                return False, False, None
            
            # Add changed files
            subprocess.run(
                ["git", "add", "-u", "*.tex", "*.bib"],
                cwd=self.config.paper_directory,
                check=True
            )
            
            # Create commit message
            commit_msg = (
                f"{self.config.git.commit_prefix} "
                f"Auto-maintenance: {summary.checks_passed}/{summary.checks_total} checks passed - "
                f"{self.run_id}"
            )
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.config.paper_directory,
                check=True,
                capture_output=True
            )
            
            # Get commit hash
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.config.paper_directory,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = result.stdout.strip()
            
            self.log(f"✓ Changes committed: {commit_hash}", "SUCCESS")
            
            # Push if enabled
            if self.config.git.auto_push:
                self.log("Pushing to remote...")
                subprocess.run(
                    ["git", "push", self.config.git.remote, "HEAD"],
                    cwd=self.config.paper_directory,
                    check=True,
                    capture_output=True
                )
                self.log("✓ Pushed to remote", "SUCCESS")
                return True, True, commit_hash
            
            return True, False, commit_hash
            
        except subprocess.CalledProcessError as e:
            self.log(f"✗ Git operation failed: {e}", "ERROR")
            return False, False, None
    
    def run(self) -> RunSummary:
        """Run the main maintenance process"""
        if self.console:
            self.console.print(Panel.fit(
                f"[bold blue]Paper Maintenance Run[/bold blue]\n"
                f"Run ID: {self.run_id}\n"
                f"Project: {self.config.project_name or 'Unknown'}",
                border_style="blue"
            ))
        else:
            self.log("=" * 80)
            self.log(f"Paper Maintenance Run: {self.run_id}")
            self.log("=" * 80)
        
        # Check quiet hours
        if self.check_quiet_hours():
            summary = RunSummary(
                run_id=self.run_id,
                timestamp=datetime.now(),
                project_name=self.config.project_name,
                changes_detected=0,
                checks=[],
                git_committed=False,
                git_pushed=False,
                errors=["Skipped: in quiet hours"]
            )
            return summary
        
        # Check git repo
        if not self.check_git_repo():
            summary = RunSummary(
                run_id=self.run_id,
                timestamp=datetime.now(),
                project_name=self.config.project_name,
                changes_detected=0,
                checks=[],
                git_committed=False,
                git_pushed=False,
                errors=["Not a git repository"]
            )
            return summary
        
        # Pull latest changes
        self.git_pull()
        
        # Check for changes
        changes = self.get_uncommitted_changes()
        self.log(f"Changes detected: {changes} lines")
        
        if changes == 0:
            self.log("No changes detected")
            summary = RunSummary(
                run_id=self.run_id,
                timestamp=datetime.now(),
                project_name=self.config.project_name,
                changes_detected=0,
                checks=[],
                git_committed=False,
                git_pushed=False
            )
            return summary
        
        # Run checks
        checks: List[CheckResult] = []
        
        if self.config.checks.compile_check:
            checks.append(self.run_claude_check("/compile-check", "Compilation check"))
        
        if self.config.checks.consistency_check:
            checks.append(self.run_claude_check("/check-consistency", "Consistency check"))
        
        if self.config.checks.math_check:
            checks.append(self.run_claude_check("/check-math", "Math notation check"))
        
        if self.config.checks.citation_check:
            checks.append(self.run_claude_check("/check-citations", "Citation check"))
        
        if self.config.checks.figure_check:
            checks.append(self.run_claude_check("/check-figures", "Figure check"))
        
        if self.config.checks.proofread:
            checks.append(self.run_claude_check("/proofread *.tex", "Proofreading"))
        
        # Full review if major changes
        if self.config.checks.full_review_on_major_changes and \
           changes >= self.config.checks.major_change_threshold:
            self.log(f"Major changes detected ({changes} lines) - running full review")
            checks.append(self.run_claude_check("/review-paper", "Full paper review"))
        
        # Create summary
        summary = RunSummary(
            run_id=self.run_id,
            timestamp=datetime.now(),
            project_name=self.config.project_name,
            changes_detected=changes,
            checks=checks,
            git_committed=False,
            git_pushed=False
        )
        
        # Commit and push
        committed, pushed, commit_hash = self.git_commit_and_push(summary)
        summary.git_committed = committed
        summary.git_pushed = pushed
        summary.git_commit_hash = commit_hash
        
        # Save summary
        with open(self.summary_file, 'w') as f:
            f.write(summary.to_markdown())
        
        # Display results
        if self.console:
            self._display_summary_rich(summary)
        else:
            self._display_summary_plain(summary)
        
        return summary
    
    def _display_summary_rich(self, summary: RunSummary) -> None:
        """Display summary using rich"""
        # Create results table
        table = Table(title="Check Results", show_header=True)
        table.add_column("Check", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Duration", justify="right")
        
        for check in summary.checks:
            status = "[green]✓ PASSED[/green]" if check.passed else "[red]✗ FAILED[/red]"
            table.add_row(check.name, status, f"{check.duration:.1f}s")
        
        self.console.print(table)
        
        # Summary panel
        success_rate = summary.success_rate * 100
        color = "green" if success_rate >= 80 else "yellow" if success_rate >= 60 else "red"
        
        summary_text = f"[{color}]{summary.checks_passed}/{summary.checks_total} checks passed ({success_rate:.0f}%)[/{color}]\n"
        
        if summary.git_committed:
            summary_text += f"\n[green]✓[/green] Changes committed"
            if summary.git_pushed:
                summary_text += f" and pushed"
        
        self.console.print(Panel(summary_text, title="Summary", border_style=color))
        self.console.print(f"\n[dim]Full log: {self.log_file}[/dim]")
        self.console.print(f"[dim]Summary: {self.summary_file}[/dim]")
    
    def _display_summary_plain(self, summary: RunSummary) -> None:
        """Display summary in plain text"""
        print("\n" + "=" * 80)
        print("CHECK RESULTS")
        print("=" * 80)
        
        for check in summary.checks:
            status = "✓ PASSED" if check.passed else "✗ FAILED"
            print(f"{status:10} {check.name:30} ({check.duration:.1f}s)")
        
        print("\n" + "=" * 80)
        print(f"SUMMARY: {summary.checks_passed}/{summary.checks_total} checks passed")
        if summary.git_committed:
            print(f"Git: Changes committed{' and pushed' if summary.git_pushed else ''}")
        print("=" * 80)
        print(f"\nFull log: {self.log_file}")
        print(f"Summary: {self.summary_file}")


def main():
    parser = argparse.ArgumentParser(description="Automated LaTeX Paper Maintenance")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml",
        help="Configuration file path"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run checks but don't commit/push"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if not args.config.exists():
        print(f"Error: Configuration file not found: {args.config}")
        print("Run setup-automation.py first to create configuration")
        sys.exit(1)
    
    config = PaperMaintenanceConfig.load(args.config)
    
    if args.dry_run:
        config.git.auto_push = False
        print("DRY RUN MODE: No commits will be pushed")
    
    # Run maintenance
    maintenance = PaperMaintenance(config, verbose=args.verbose)
    summary = maintenance.run()
    
    # Exit with appropriate code
    if summary.checks_total == 0:
        sys.exit(0)
    elif summary.checks_passed == summary.checks_total:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
