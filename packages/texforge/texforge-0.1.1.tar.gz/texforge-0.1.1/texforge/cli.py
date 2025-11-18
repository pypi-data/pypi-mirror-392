#!/usr/bin/env python3
"""
TexForge - LaTeX Paper Forge CLI

Command-line interface for LaTeX paper automation tools.
Forge perfect papers with ease.
"""

import sys
import argparse
from pathlib import Path

from . import __version__


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog='texforge',
        description='TexForge - Forge perfect LaTeX papers with automated compilation and maintenance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  texforge compile main.tex                    # Compile LaTeX to PDF
  texforge compile -c config.yaml main.tex     # Compile with config
  texforge validate main.tex                   # Validate paper quality
  texforge maintain -c config.yaml             # Run maintenance checks
  texforge notify --slack "Build complete"     # Send notification

For more information, visit: https://github.com/Jue-Xu/LaTex-paper-automation
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'texforge {__version__}'
    )

    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # === COMPILE command ===
    compile_parser = subparsers.add_parser(
        'compile',
        help='Compile LaTeX document to PDF',
        description='Compile LaTeX documents with automatic bibliography processing'
    )
    compile_parser.add_argument(
        'tex_file',
        nargs='?',
        type=Path,
        help='LaTeX file to compile (default: main.tex)'
    )
    compile_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file (YAML)'
    )
    compile_parser.add_argument(
        '--clean',
        action='store_true',
        default=True,
        help='Clean auxiliary files after compilation (default: true)'
    )
    compile_parser.add_argument(
        '--no-clean',
        dest='clean',
        action='store_false',
        help='Keep auxiliary files after compilation'
    )
    compile_parser.add_argument(
        '--setup-template',
        type=str,
        choices=['pra', 'prl', 'generic'],
        help='Setup journal template'
    )
    compile_parser.add_argument(
        '--setup-macros',
        action='store_true',
        help='Setup macros.tex file'
    )
    compile_parser.add_argument(
        '--suggest-macros',
        action='store_true',
        help='Suggest macro definitions'
    )
    compile_parser.add_argument(
        '--fix-errors',
        action='store_true',
        help='Attempt to fix common errors'
    )
    compile_parser.add_argument(
        '--notify',
        action='store_true',
        help='Send compilation result notification to Slack'
    )
    compile_parser.add_argument(
        '--slack-webhook',
        type=str,
        help='Slack webhook URL (or use SLACK_WEBHOOK env var)'
    )

    # === VALIDATE command ===
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate paper quality and consistency',
        description='Run quality checks on LaTeX paper'
    )
    validate_parser.add_argument(
        'tex_file',
        nargs='?',
        type=Path,
        help='LaTeX file to validate (default: main.tex)'
    )
    validate_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file (YAML)'
    )

    # === MAINTAIN command ===
    maintain_parser = subparsers.add_parser(
        'maintain',
        help='Run automated paper maintenance',
        description='Perform automatic checks and improvements'
    )
    maintain_parser.add_argument(
        '-c', '--config',
        type=Path,
        required=True,
        help='Configuration file (YAML)'
    )
    maintain_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    maintain_parser.add_argument(
        '--paper-dir',
        type=Path,
        help='Paper directory (overrides config)'
    )

    # === NOTIFY command ===
    notify_parser = subparsers.add_parser(
        'notify',
        help='Send notifications',
        description='Send notifications via configured channels'
    )
    notify_parser.add_argument(
        'message',
        help='Notification message'
    )
    notify_parser.add_argument(
        '--subject',
        default='LRC Notification',
        help='Notification subject/title'
    )
    notify_parser.add_argument(
        '-c', '--config',
        type=Path,
        default=Path.home() / '.paper-automation-config.yaml',
        help='Configuration file (YAML)'
    )
    notify_parser.add_argument(
        '--priority',
        default='default',
        choices=['min', 'low', 'default', 'high', 'urgent'],
        help='Notification priority'
    )
    notify_parser.add_argument(
        '--email',
        action='store_true',
        help='Send via email'
    )
    notify_parser.add_argument(
        '--slack',
        action='store_true',
        help='Send via Slack'
    )
    notify_parser.add_argument(
        '--telegram',
        action='store_true',
        help='Send via Telegram'
    )
    notify_parser.add_argument(
        '--discord',
        action='store_true',
        help='Send via Discord'
    )
    notify_parser.add_argument(
        '--ntfy',
        action='store_true',
        help='Send via ntfy.sh'
    )
    # Direct credential arguments
    notify_parser.add_argument(
        '--slack-webhook',
        type=str,
        help='Slack webhook URL (or set SLACK_WEBHOOK env var)'
    )
    notify_parser.add_argument(
        '--telegram-token',
        type=str,
        help='Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)'
    )
    notify_parser.add_argument(
        '--telegram-chat-id',
        type=str,
        help='Telegram chat ID (or set TELEGRAM_CHAT_ID env var)'
    )
    notify_parser.add_argument(
        '--discord-webhook',
        type=str,
        help='Discord webhook URL (or set DISCORD_WEBHOOK env var)'
    )
    notify_parser.add_argument(
        '--ntfy-topic',
        type=str,
        help='ntfy.sh topic (or set NTFY_TOPIC env var)'
    )

    # === INIT command ===
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize a new paper project',
        description='Create configuration and directory structure for a new paper'
    )
    init_parser.add_argument(
        'project_name',
        help='Name of the paper project'
    )
    init_parser.add_argument(
        '--template',
        type=str,
        choices=['pra', 'prl', 'generic'],
        default='generic',
        help='LaTeX template to use'
    )
    init_parser.add_argument(
        '--dir',
        type=Path,
        help='Project directory (default: ./projects/<project_name>)'
    )

    return parser


def cmd_compile(args):
    """Handle the compile command."""
    from .pdf_compiler import PDFCompiler
    from .config import PaperMaintenanceConfig

    # Load config if provided
    if args.config:
        config = PaperMaintenanceConfig.load(args.config)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = Path.cwd()
        if args.tex_file:
            config.main_tex_file = args.tex_file.name

    # Update paper directory if tex_file is in different directory
    if args.tex_file:
        config.paper_directory = args.tex_file.parent if args.tex_file.parent != Path('.') else Path.cwd()
        config.main_tex_file = args.tex_file.name

    compiler = PDFCompiler(config)

    # Handle setup commands
    if args.setup_template:
        compiler.setup_template(args.setup_template)
        print(f"\n✓ Template created for {args.setup_template.upper()}")
        print(f"  Edit {compiler.template_file} to customize")
        return 0

    if args.setup_macros:
        compiler.setup_macros()
        print(f"\n✓ Macros file created")
        print(f"  Add your custom macros to {compiler.macros_file}")
        return 0

    if args.suggest_macros:
        print("Analyzing paper for frequently used patterns...\n")
        suggestions = compiler.analyze_macro_usage()

        if suggestions:
            print("Suggested macro definitions:")
            print("=" * 60)
            for i, sugg in enumerate(suggestions, 1):
                print(f"\n{i}. Pattern used {sugg.frequency} times:")
                print(f"   {sugg.pattern}")
                print(f"   Suggestion: {sugg.suggested_definition}")
                print(f"   Rationale: {sugg.rationale}")

            print("\n" + "=" * 60)
            print(f"\nAdd these to {compiler.macros_file}")
        else:
            print("No macro suggestions found.")
        return 0

    if args.fix_errors:
        print("Attempting to fix common errors...")
        fixes = compiler.fix_common_errors()

        if fixes:
            for fix in fixes:
                print(f"✓ {fix}")
            # Try compiling after fixes
            print("\n🔄 Compiling after fixes...")
            result = compiler.compile(clean=args.clean)
        else:
            print("No common errors found")
            result = compiler.compile(clean=args.clean)

        # If still failing, try Claude Code
        if not result.success:
            print("\n💡 Common fixes didn't resolve all errors.")
            fixed = compiler.fix_errors_with_claude(result.errors)

            # After Claude Code fixes, compile again and send notification
            if fixed:
                result = compiler.compile(clean=args.clean)
                if args.notify:
                    _send_compile_notification(args, compiler, result)
                return 0
            else:
                # Send notification about failure (always send when fix-errors fails)
                _send_compile_notification(args, compiler, result)
                return 1
        else:
            # Send notification about success
            if args.notify:
                _send_compile_notification(args, compiler, result)

            print(f"\n✅ Errors fixed! Compilation successful.")
            print(f"   PDF: {result.pdf_path}")
            return 0

    # Compile
    print(f"Compiling {compiler.main_tex}...\n")
    result = compiler.compile(clean=args.clean)

    # Prepare notification message if needed
    if args.notify:
        _send_compile_notification(args, compiler, result)

    if result.success:
        print(f"✅ Compilation successful!")
        print(f"   PDF: {result.pdf_path}")
        print(f"   Pages: {result.pages}")
        print(f"   Time: {result.compile_time:.1f}s")

        if result.warnings:
            print(f"\n⚠️  {len(result.warnings)} warnings:")
            for warning in result.warnings[:5]:
                print(f"   {warning}")
        return 0
    else:
        print(f"❌ Compilation failed")
        print(f"\nErrors:")
        for error in result.errors:
            print(f"   {error}")

        print(f"\n💡 Try: texforge compile --fix-errors")
        print(f"   This will use Claude Code to automatically fix the errors")
        return 1


def _send_compile_notification(args, compiler, result):
    """Send compilation result notification to Slack"""
    import os
    import requests

    # Get webhook URL from args or env var or default
    webhook_url = (
        args.slack_webhook or
        os.getenv('SLACK_WEBHOOK') or
        "https://hooks.slack.com/services/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"
    )

    # Build message
    if result.success:
        status_emoji = ":white_check_mark:"
        status_text = "Compilation Successful"
        color = "good"
        fields = [
            {"title": "PDF", "value": str(result.pdf_path), "short": True},
            {"title": "Pages", "value": str(result.pages), "short": True},
            {"title": "Time", "value": f"{result.compile_time:.1f}s", "short": True},
        ]
        if result.warnings:
            fields.append({
                "title": "Warnings",
                "value": f"{len(result.warnings)} warnings",
                "short": True
            })
    else:
        status_emoji = ":x:"
        status_text = "Compilation Failed"
        color = "danger"
        error_summary = "\n".join(f"• {err}" for err in result.errors[:3])
        if len(result.errors) > 3:
            error_summary += f"\n... and {len(result.errors) - 3} more errors"
        fields = [
            {"title": "Errors", "value": error_summary, "short": False}
        ]

    message = {
        "attachments": [{
            "color": color,
            "fallback": f"{status_emoji} {status_text}: {compiler.main_tex}",
            "pretext": f"{status_emoji} *{status_text}*",
            "title": str(compiler.main_tex.name),
            "fields": fields,
            "footer": "TexForge",
            "ts": int(result.compile_time) if hasattr(result, 'compile_time') else 0
        }]
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        if response.status_code == 200:
            print(f"\n📱 Notification sent to Slack")
        else:
            print(f"\n⚠️  Failed to send notification: {response.status_code}")
    except Exception as e:
        print(f"\n⚠️  Failed to send notification: {e}")


def cmd_validate(args):
    """Handle the validate command."""
    from .validate_paper import main as validate_main

    # Prepare arguments for validate_paper
    sys.argv = ['validate_paper']

    if args.tex_file:
        sys.argv.extend(['--paper-dir', str(args.tex_file.parent or Path.cwd())])

    if args.config:
        sys.argv.extend(['-c', str(args.config)])

    return validate_main()


def cmd_maintain(args):
    """Handle the maintain command."""
    from .auto_maintain_paper import main as maintain_main

    # Prepare arguments for auto_maintain_paper
    sys.argv = ['auto_maintain_paper', '-c', str(args.config)]

    if args.verbose:
        sys.argv.append('-v')

    if args.paper_dir:
        sys.argv.extend(['--paper-dir', str(args.paper_dir)])

    return maintain_main()


def cmd_notify(args):
    """Handle the notify command."""
    from .notification_cli import main as notify_main

    # Prepare arguments for notification_cli
    sys.argv = [
        'notification_cli',
        '--subject', args.subject,
        '--body', args.message,
        '--priority', args.priority,
        '--config', str(args.config)
    ]

    if args.email:
        sys.argv.append('--email')
    if args.slack:
        sys.argv.append('--slack')
    if args.telegram:
        sys.argv.append('--telegram')
    if args.discord:
        sys.argv.append('--discord')
    if args.ntfy:
        sys.argv.append('--ntfy')

    # Add credential arguments if provided
    if hasattr(args, 'slack_webhook') and args.slack_webhook:
        sys.argv.extend(['--slack-webhook', args.slack_webhook])
    if hasattr(args, 'telegram_token') and args.telegram_token:
        sys.argv.extend(['--telegram-token', args.telegram_token])
    if hasattr(args, 'telegram_chat_id') and args.telegram_chat_id:
        sys.argv.extend(['--telegram-chat-id', args.telegram_chat_id])
    if hasattr(args, 'discord_webhook') and args.discord_webhook:
        sys.argv.extend(['--discord-webhook', args.discord_webhook])
    if hasattr(args, 'ntfy_topic') and args.ntfy_topic:
        sys.argv.extend(['--ntfy-topic', args.ntfy_topic])

    return notify_main()


def cmd_init(args):
    """Handle the init command."""
    project_dir = args.dir or Path(args.project_name)
    project_dir.mkdir(parents=True, exist_ok=True)

    print(f"Initializing paper project: {args.project_name}")
    print(f"Directory: {project_dir}")

    # Create basic structure
    (project_dir / 'figs').mkdir(exist_ok=True)
    (project_dir / 'data').mkdir(exist_ok=True)
    (project_dir / 'code').mkdir(exist_ok=True)

    # Create config file
    from .config import PaperMaintenanceConfig

    config = PaperMaintenanceConfig()
    config.project_name = args.project_name
    config.paper_directory = project_dir.absolute()
    config.main_tex_file = 'main.tex'

    config_path = project_dir / '.paper-config.yaml'
    config.save(config_path)

    # Create template files
    from .pdf_compiler import PDFCompiler

    compiler = PDFCompiler(config)
    compiler.setup_template(args.template)
    compiler.setup_macros(silent=True)

    # Create empty references.bib
    (project_dir / 'references.bib').write_text("% Bibliography\n")

    # Create README
    readme_content = f"""# {args.project_name}

Research paper project initialized with TexForge.

## Structure

```
{args.project_name}/
├── template.tex       # Main LaTeX file
├── references.bib     # Bibliography
├── macros.tex         # Custom macros
├── .paper-config.yaml # TexForge configuration
├── content/          # Paper sections
│   ├── intro.tex
│   ├── methods.tex
│   ├── results.tex
│   └── conclusion.tex
├── figs/             # Figures
├── data/             # Data files
└── code/             # Analysis code
```

## Quick Start

```bash
cd {project_dir}
# Edit content files in content/
texforge compile template.tex
```

## Maintenance

```bash
texforge maintain -c .paper-config.yaml
```
"""
    (project_dir / 'README.md').write_text(readme_content)

    print(f"\n✅ Project initialized successfully!")
    print(f"\nCreated:")
    print(f"  - {config_path.name}")
    print(f"  - template.tex")
    print(f"  - references.bib")
    print(f"  - README.md")
    print(f"  - macros.tex (empty)")
    print(f"  - content/ (intro, methods, results, conclusion)")
    print(f"  - Directory structure (figs/, data/, code/)")

    print(f"\nNext steps:")
    print(f"  1. cd {project_dir}")
    print(f"  2. Edit section files in content/")
    print(f"  3. texforge compile template.tex")

    print(f"\n💡 Tip: Configure notifications in {config_path.name}:")
    print(f"   Edit 'slack.webhook_url' or use SLACK_WEBHOOK env var")

    return 0


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handler
    command_handlers = {
        'compile': cmd_compile,
        'validate': cmd_validate,
        'maintain': cmd_maintain,
        'notify': cmd_notify,
        'init': cmd_init,
    }

    handler = command_handlers.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            return 130
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
