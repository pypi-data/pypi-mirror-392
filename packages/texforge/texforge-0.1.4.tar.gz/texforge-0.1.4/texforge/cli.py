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
  texforge review --journal prl                # Review paper as APS referee
  texforge cover-letter prl                    # Generate cover letter for PRL
  texforge brainstorm --journal "Nature"       # Brainstorm manuscript outline
  texforge polish main.tex                     # Check grammar and word flow
  texforge arxiv-download 2301.12345           # Download arXiv source to library/
  texforge bib-merge                           # Merge .bib files from library/
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
        choices=['pra', 'prl', 'ns', 'tcs', 'generic'],
        default='generic',
        help='LaTeX template to use (pra=Physical Review A, prl=Physical Review Letters, ns=Nature/Science journals, tcs=Theoretical Computer Science, generic=Standard article)'
    )
    init_parser.add_argument(
        '--dir',
        type=Path,
        help='Project directory (default: ./projects/<project_name>)'
    )

    # === BRAINSTORM command ===
    brainstorm_parser = subparsers.add_parser(
        'brainstorm',
        help='Generate manuscript outline from project goals and references',
        description='AI-powered brainstorming session to create manuscript outline'
    )
    brainstorm_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file (default: .paper-config.yaml in current directory)'
    )
    brainstorm_parser.add_argument(
        '--idea',
        type=str,
        help='Research idea (default: uses Project Goals from README.md)'
    )
    brainstorm_parser.add_argument(
        '--journal',
        type=str,
        default='Physical Review A',
        help='Target journal (default: Physical Review A)'
    )

    # === PROVE command ===
    prove_parser = subparsers.add_parser(
        'prove',
        help='Generate rigorous proof for a theorem with verification',
        description='AI-powered theorem prover with checker agent for rigorous proofs'
    )
    prove_parser.add_argument(
        '--label',
        type=str,
        help='LaTeX label of theorem to prove (e.g., "thm:main" or "lem:bound")'
    )
    prove_parser.add_argument(
        '--file',
        type=Path,
        help='Specific .tex file to search (default: search all .tex files)'
    )
    prove_parser.add_argument(
        '--theorem',
        type=str,
        help='Theorem statement to prove (alternative to --label)'
    )
    prove_parser.add_argument(
        '--name',
        type=str,
        help='Theorem name (e.g., "Main Theorem" or "Lemma 3.2")'
    )
    prove_parser.add_argument(
        '--assumptions',
        nargs='+',
        default=[],
        help='List of assumptions (e.g., "H is Hermitian" "n >= 2")'
    )
    prove_parser.add_argument(
        '--context',
        type=str,
        default='quantum information theory',
        help='Mathematical context (default: quantum information theory)'
    )
    prove_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file (default: .paper-config.yaml)'
    )

    # === REVIEW command ===
    review_parser = subparsers.add_parser(
        'review',
        help='APS journal peer review simulation',
        description='Review paper as an APS journal referee (PRR, PRA, PRB, PRL, PRX, PRX Quantum)'
    )
    review_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file (default: .paper-config.yaml in current directory)'
    )
    review_parser.add_argument(
        '--journal',
        type=str,
        default='pra',
        choices=['pra', 'prb', 'prl', 'prx', 'prxquantum', 'prr'],
        help='Target APS journal (default: pra)'
    )
    review_parser.add_argument(
        '--input',
        type=Path,
        help='PDF file to review (default: compile from LaTeX)'
    )
    review_parser.add_argument(
        '--strict',
        action='store_true',
        help='Apply strict journal-specific criteria'
    )

    # === COVER-LETTER command ===
    cover_letter_parser = subparsers.add_parser(
        'cover-letter',
        help='Generate cover letter for journal submission',
        description='Generate a professional cover letter for submitting your paper to a journal'
    )
    cover_letter_parser.add_argument(
        'journal',
        type=str,
        help='Target journal (e.g., prl, nature, pra) or custom journal name'
    )
    cover_letter_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file (default: .paper-config.yaml in current directory)'
    )
    cover_letter_parser.add_argument(
        '-i', '--info',
        type=str,
        help='Additional information to include in the cover letter'
    )

    # === POLISH command ===
    polish_parser = subparsers.add_parser(
        'polish',
        help='Check grammar and word flow',
        description='Polish LaTeX paper for grammar, clarity, and flow while preserving terminology'
    )
    polish_parser.add_argument(
        'tex_file',
        type=Path,
        help='LaTeX file to polish'
    )
    polish_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file (default: .paper-config.yaml in current directory)'
    )
    polish_parser.add_argument(
        '--mode',
        type=str,
        choices=['report', 'inline'],
        default='report',
        help='Output mode: report (markdown) or inline (tex comments) (default: report)'
    )
    polish_parser.add_argument(
        '--severity',
        type=str,
        choices=['critical', 'major', 'minor'],
        help='Filter by severity level'
    )
    polish_parser.add_argument(
        '--preserve',
        type=str,
        help='Comma-separated list of additional terms to preserve'
    )
    polish_parser.add_argument(
        '--setup-macros',
        action='store_true',
        help='Setup LaTeX macros for inline comments'
    )
    polish_parser.add_argument(
        '--output',
        type=Path,
        help='Output file for report (default: polish_report.md)'
    )

    # === ARXIV-DOWNLOAD command ===
    arxiv_parser = subparsers.add_parser(
        'arxiv-download',
        help='Download arXiv LaTeX source for references',
        description='Download LaTeX source code from arXiv papers to library/ folder'
    )
    arxiv_parser.add_argument(
        'arxiv_id',
        nargs='?',
        help="ArXiv ID or URL (e.g., '2301.12345' or 'https://arxiv.org/abs/2301.12345')"
    )
    arxiv_parser.add_argument(
        '--library',
        type=Path,
        help='Library directory path (default: ./library)'
    )
    arxiv_parser.add_argument(
        '--name',
        type=str,
        help='Custom folder name for extracted source'
    )
    arxiv_parser.add_argument(
        '--list',
        action='store_true',
        help='List all downloaded arXiv sources'
    )

    # === BIB-MERGE command ===
    bib_merge_parser = subparsers.add_parser(
        'bib-merge',
        help='Merge bibliography files from library/',
        description='Merge all .bib and .bbl files from library/ into references.bib'
    )
    bib_merge_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file (default: .paper-config.yaml in current directory)'
    )
    bib_merge_parser.add_argument(
        '--output',
        type=Path,
        help='Output file for merged bibliography (default: references.bib)'
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
    (project_dir / 'library').mkdir(exist_ok=True)

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

## Project Goals

<!-- Describe your research objectives, main questions, and expected contributions here.
     The brainstorming agent will use this section to understand your paper's purpose. -->

**Research Question:**
[What is the main question this paper addresses?]

**Objectives:**
- [Objective 1]
- [Objective 2]
- [Objective 3]

**Expected Contributions:**
- [What novel insights or methods does this work provide?]

**Target Audience:**
[Who is the intended audience? What background should they have?]

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
├── library/          # Key references (PDF/HTML)
├── figs/             # Figures
├── data/             # Data files
└── code/             # Analysis code
```

## Quick Start

```bash
cd {project_dir}

# 1. Add key references to library/
# 2. Update "Project Goals" section above
# 3. Generate manuscript outline:
#    texforge brainstorm

# 4. Edit content files in content/
# 5. Compile:
texforge compile template.tex
```

## Maintenance

```bash
texforge maintain -c .paper-config.yaml
```
"""
    (project_dir / 'README.md').write_text(readme_content)

    # Dynamic content description based on template
    if args.template == 'ns':
        content_desc = "content/ (intro, setup, results, discussion, methods, appendix)"
    elif args.template == 'tcs':
        content_desc = "content/ (intro with subsections: preliminaries, previous_work, contributions; then methods, results, conclusion)"
    else:
        content_desc = "content/ (intro, methods, results, conclusion)"

    print(f"\n✅ Project initialized successfully!")
    print(f"\nCreated:")
    print(f"  - {config_path.name}")
    print(f"  - template.tex")
    print(f"  - references.bib")
    print(f"  - README.md (with project goals template)")
    print(f"  - macros.tex (empty)")
    print(f"  - {content_desc}")
    print(f"  - Directory structure (figs/, data/, code/, library/)")

    print(f"\nNext steps:")
    print(f"  1. cd {project_dir}")
    print(f"  2. Add key references to library/ folder")
    print(f"  3. Fill out 'Project Goals' section in README.md")
    print(f"  4. Run: texforge brainstorm (to generate manuscript outline)")
    print(f"  5. Edit section files in content/")
    print(f"  6. texforge compile template.tex")

    print(f"\n💡 Tip: Configure notifications in {config_path.name}:")
    print(f"   Edit 'slack.webhook_url' or use SLACK_WEBHOOK env var")

    return 0


def cmd_brainstorm(args):
    """Handle the brainstorm command."""
    from .brainstorming import BrainstormingSession
    from .config import PaperMaintenanceConfig

    # Load config
    config_path = args.config or (Path.cwd() / '.paper-config.yaml')
    if config_path.exists():
        config = PaperMaintenanceConfig.load(config_path)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = Path.cwd()

    # Create brainstorming session
    session_manager = BrainstormingSession(config)

    # Run session
    try:
        session = session_manager.run_session(
            initial_idea=args.idea,
            target_journal=args.journal
        )

        print(f"\n{'='*70}")
        print(f"✅ Brainstorming session complete!")
        print(f"\nGenerated files:")
        print(f"  - {session_manager.session_file.name} (full session notes)")
        print(f"  - {session_manager.manuscript_outline.relative_to(config.paper_directory)} (manuscript outline)")
        print(f"\nNext steps:")
        print(f"  1. Review the manuscript outline")
        print(f"  2. Edit section files in content/ based on the outline")
        print(f"  3. Add references to references.bib")
        print(f"  4. Run: texforge compile")

        return 0

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print(f"\nPlease either:")
        print(f"  1. Fill out the 'Project Goals' section in README.md")
        print(f"  2. Or provide an idea with: texforge brainstorm --idea 'Your research idea'")
        return 1
    except Exception as e:
        print(f"\n❌ Error during brainstorming session: {e}")
        return 1


def cmd_prove(args):
    """Handle the prove command."""
    from .prover_agent import ProverAgent, Theorem
    from .config import PaperMaintenanceConfig

    # Load config
    config_path = args.config or (Path.cwd() / '.paper-config.yaml')
    if config_path.exists():
        config = PaperMaintenanceConfig.load(config_path)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = Path.cwd()

    # Run prover
    prover = ProverAgent(config)

    try:
        # Option 1: Find theorem by label in LaTeX files
        if args.label:
            theorem = prover.find_theorem_by_label(args.label, args.file)
            if not theorem:
                print(f"\n❌ Theorem with label '{args.label}' not found")
                print(f"\nMake sure your LaTeX file contains:")
                print(f"  \\begin{{theorem}}[Optional Name]")
                print(f"  \\label{{{args.label}}}")
                print(f"  Your theorem statement here...")
                print(f"  \\end{{theorem}}")
                return 1

            print(f"\n📍 Found theorem: {theorem.name}")
            print(f"   Statement: {theorem.statement[:100]}...")
            print(f"   File: {theorem.tex_file.name}")
            print(f"   Context: {theorem.context}")

        # Option 2: Create theorem from command-line arguments
        elif args.theorem and args.name:
            theorem = Theorem(
                name=args.name,
                statement=args.theorem,
                assumptions=args.assumptions if args.assumptions else [],
                context=args.context
            )
        else:
            print(f"\n❌ Error: Must provide either --label or both --theorem and --name")
            print(f"\nUsage:")
            print(f"  # Prove theorem from LaTeX file:")
            print(f"  texforge prove --label thm:main")
            print(f"\n  # Or provide theorem directly:")
            print(f"  texforge prove --name 'Main Theorem' --theorem 'Statement here'")
            return 1

        # Generate proof
        result = prover.prove_theorem(theorem)

        print(f"\nNext steps:")
        print(f"  1. Review proof in: {result['latex_file'].name}")
        print(f"  2. Check detailed notes: {result['notes_file'].name}")
        if theorem.tex_file:
            print(f"  3. Proof has been written to: {theorem.tex_file.name}")
            print(f"     (Backup saved as {theorem.tex_file.with_suffix('.tex.backup').name})")
        if not result['verification']['is_rigorous']:
            print(f"  4. Address remaining issues and re-run")

        return 0 if result['verification']['is_rigorous'] else 1

    except Exception as e:
        print(f"\n❌ Error during proof generation: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_review(args):
    """Handle the review command."""
    from .aps_reviewer import APSReviewer
    from .config import PaperMaintenanceConfig

    # Load config
    config_path = args.config or (Path.cwd() / '.paper-config.yaml')
    if config_path.exists():
        config = PaperMaintenanceConfig.load(config_path)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = Path.cwd()

    # Create reviewer
    reviewer = APSReviewer(config)

    # Run review
    try:
        result = reviewer.review_paper(
            journal=args.journal,
            input_file=args.input if hasattr(args, 'input') else None,
            strict=args.strict
        )

        # Print summary
        print(f"\n{'='*70}")
        print(f"📊 Review Summary")
        print(f"{'='*70}")
        print(f"\n{result.summary}\n")

        print(f"**Decision:** {result.decision}")
        print(f"\n**Strengths:** {len(result.strengths)} identified")
        print(f"**Weaknesses:** {len(result.weaknesses)} identified")

        if result.compliance_issues:
            print(f"**Compliance Issues:** {len(result.compliance_issues)} found")

        print(f"\n📄 Full review report saved to:")
        print(f"   {reviewer.output_file}")

        # Return exit code based on decision
        decision_codes = {
            'Accept': 0,
            'Minor Revision': 0,
            'Major Revision': 1,
            'Reject': 2
        }
        return decision_codes.get(result.decision, 1)

    except Exception as e:
        print(f"\n❌ Error during review: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_cover_letter(args):
    """Handle the cover-letter command."""
    from .cover_letter_writer import CoverLetterWriter
    from .config import PaperMaintenanceConfig

    # Load config
    config_path = args.config or (Path.cwd() / '.paper-config.yaml')
    if config_path.exists():
        config = PaperMaintenanceConfig.load(config_path)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = Path.cwd()
        config.main_tex_file = 'main.tex'

    # Create writer
    writer = CoverLetterWriter(config)

    # Generate cover letter
    try:
        result = writer.generate_cover_letter(
            journal=args.journal,
            additional_info=args.info if hasattr(args, 'info') else None
        )

        # Print the cover letter
        print(f"\n{'='*70}")
        print(f"📧 Cover Letter for {result.journal}")
        print(f"{'='*70}\n")
        print(result.cover_letter_text)
        print(f"\n{'='*70}")

        print(f"\n✅ Cover letter saved to:")
        print(f"   {writer.output_file}.txt (plain text)")
        print(f"   {writer.output_file}.md (markdown with metadata)")

        print(f"\n💡 Next steps:")
        print(f"   1. Review and customize the cover letter")
        print(f"   2. Add author names and affiliations")
        print(f"   3. Submit to {result.journal}")

        return 0

    except Exception as e:
        print(f"\n❌ Error generating cover letter: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_polish(args):
    """Handle the polish command."""
    from .polish_agent import PolishAgent
    from .config import PaperMaintenanceConfig

    # Load config
    config_path = args.config or (Path.cwd() / '.paper-config.yaml')
    if config_path.exists():
        config = PaperMaintenanceConfig.load(config_path)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = args.tex_file.parent if args.tex_file.parent != Path('.') else Path.cwd()

    # Create polish agent
    agent = PolishAgent(config)

    # Handle setup-macros
    if args.setup_macros:
        macros_file = agent.setup_latex_macros()
        print(f"\n✅ LaTeX macros created: {macros_file}")
        print(f"\nAdd to your LaTeX preamble:")
        print(f"  \\input{{polish_macros}}")
        print(f"\nMacros available:")
        print(f"  \\polishcomment{{...}}  - Blue comment for minor issues")
        print(f"  \\grammarfix{{...}}     - Red comment for critical issues")
        print(f"  \\flowsuggestion{{...}} - Orange comment for flow issues")
        return 0

    # Override output file if specified
    if hasattr(args, 'output') and args.output:
        agent.output_file = args.output

    # Parse preserve terms
    preserve_terms = None
    if args.preserve:
        preserve_terms = [t.strip() for t in args.preserve.split(',')]

    # Run polish check
    try:
        result = agent.polish_paper(
            args.tex_file,
            mode=args.mode,
            preserve_terms=preserve_terms,
            severity_filter=args.severity
        )

        # Print summary
        print(f"\n{'='*70}")
        print(f"📊 Polish Summary")
        print(f"{'='*70}")
        print(f"Word Flow Score: {result.word_flow_score:.1f}/10")
        print(f"Total Issues: {result.total_issues}")
        print(f"  - Critical: {result.critical_count}")
        print(f"  - Major: {result.major_count}")
        print(f"  - Minor: {result.minor_count}")

        if args.mode == "report":
            print(f"\n📄 Full report saved to:")
            print(f"   {agent.output_file}")
        else:
            print(f"\n📝 Inline comments added to:")
            print(f"   {args.tex_file}")
            print(f"   (Backup: {args.tex_file.with_suffix('.tex.backup')})")

        print(f"\n💡 Next steps:")
        if result.critical_count > 0:
            print(f"   1. Review and fix {result.critical_count} critical issues")
        if args.mode == "report":
            print(f"   2. Run with --mode inline to add comments to file")
        else:
            print(f"   2. Search for \\polishcomment, \\grammarfix in your .tex file")
            print(f"   3. Address comments and remove macro calls when done")

        # Return exit code based on critical issues
        return 0 if result.critical_count == 0 else 1

    except Exception as e:
        print(f"\n❌ Error during polish check: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_arxiv_download(args):
    """Handle the arxiv-download command."""
    from .arxiv_downloader import ArXivDownloader

    # Determine library directory
    library_dir = args.library if hasattr(args, 'library') and args.library else Path.cwd() / "library"

    downloader = ArXivDownloader(library_dir)

    if args.list:
        downloaded = downloader.list_downloaded()
        if not downloaded:
            print(f"No arXiv sources found in {library_dir}")
        else:
            print(f"\n📚 Downloaded arXiv sources in {library_dir}:\n")
            for folder in downloaded:
                tex_count = len(list(folder.glob("*.tex")))
                bib_count = len(list(folder.glob("*.bib")))
                bbl_count = len(list(folder.glob("*.bbl")))
                print(f"  • {folder.name}/")
                print(f"    {tex_count} .tex, {bib_count} .bib, {bbl_count} .bbl files")
        return 0

    if not args.arxiv_id:
        print("Error: arxiv_id is required (unless using --list)")
        return 1

    result = downloader.download_source(args.arxiv_id, args.name)

    if result:
        print(f"\n💡 Tip: Run 'texforge brainstorm' to use this reference in your brainstorming session")
        print(f"💡 Tip: Run 'texforge bib-merge' to merge bibliographies into references.bib")
        return 0
    else:
        return 1


def cmd_bib_merge(args):
    """Handle the bib-merge command."""
    from .bibliography_manager import BibliographyManager
    from .config import PaperMaintenanceConfig

    # Load config
    config_path = args.config or (Path.cwd() / '.paper-config.yaml')
    if config_path.exists():
        config = PaperMaintenanceConfig.load(config_path)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = Path.cwd()

    # Create bibliography manager
    manager = BibliographyManager(config)

    # Merge bibliographies
    output_file = args.output if hasattr(args, 'output') and args.output else None
    result = manager.merge_library_bibliographies(output_file)

    if result['total'] > 0:
        print("\n📊 Merge Summary:")
        print(f"   Sources: {len(result['sources'])}")
        for src in result['sources']:
            print(f"     - {src}")
        if result['duplicates']:
            print(f"\n   Duplicates found: {len(result['duplicates'])}")
            for dup in result['duplicates'][:5]:  # Show first 5
                print(f"     - '{dup['key']}' in {dup['duplicate_source']} (kept from {dup['first_source']})")
            if len(result['duplicates']) > 5:
                print(f"     ... and {len(result['duplicates']) - 5} more")

        print(f"\n💡 Tip: Use \\cite{{key}} in your LaTeX to cite these references")
        return 0
    else:
        print("\n⚠️  No bibliography entries found to merge")
        print(f"Add .bib or .bbl files to {manager.library_dir}")
        return 1


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
        'brainstorm': cmd_brainstorm,
        'prove': cmd_prove,
        'review': cmd_review,
        'cover-letter': cmd_cover_letter,
        'polish': cmd_polish,
        'arxiv-download': cmd_arxiv_download,
        'bib-merge': cmd_bib_merge,
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
