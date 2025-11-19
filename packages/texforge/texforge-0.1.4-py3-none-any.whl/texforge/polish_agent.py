#!/usr/bin/env python3
"""
Polish Agent - Grammar and Word Flow Checker
=============================================

Checks LaTeX papers for grammar, word flow, and clarity issues while preserving
technical terminology. Supports two modes:
1. Report mode: Generates markdown report with all suggestions
2. Inline mode: Writes colored comments directly in .tex files

Output: Grammar report or inline LaTeX comments
"""

import subprocess
import sys
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

from .config import PaperMaintenanceConfig


@dataclass
class GrammarIssue:
    """Single grammar/style issue"""
    line_number: int
    original_text: str
    issue_type: str  # "grammar", "flow", "clarity", "style"
    suggestion: str
    severity: str  # "critical", "major", "minor"
    preserve_terminology: bool = False  # Flag if technical term involved


@dataclass
class PolishResult:
    """Complete polish result"""
    file_path: Path
    mode: str  # "report" or "inline"
    issues: List[GrammarIssue]
    word_flow_score: float
    total_issues: int
    critical_count: int
    major_count: int
    minor_count: int
    timestamp: datetime

    def to_markdown(self) -> str:
        """Generate markdown report"""
        lines = []
        lines.append("# Grammar & Word Flow Report")
        lines.append(f"\n**File:** {self.file_path.name}")
        lines.append(f"**Date:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Mode:** {self.mode}")
        lines.append(f"\n**Summary:**")
        lines.append(f"- Total Issues: {self.total_issues}")
        lines.append(f"- Critical: {self.critical_count}")
        lines.append(f"- Major: {self.major_count}")
        lines.append(f"- Minor: {self.minor_count}")
        lines.append(f"- Word Flow Score: {self.word_flow_score:.1f}/10")
        lines.append("\n" + "="*70 + "\n")

        # Group issues by severity
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        major_issues = [i for i in self.issues if i.severity == "major"]
        minor_issues = [i for i in self.issues if i.severity == "minor"]

        # Critical Issues
        if critical_issues:
            lines.append(f"## Critical Issues ({len(critical_issues)})\n")
            for i, issue in enumerate(critical_issues, 1):
                lines.append(f"### {i}. Line {issue.line_number}: {issue.issue_type.title()}\n")
                lines.append(f"**Original:** {issue.original_text}")
                lines.append(f"**Issue:** {issue.issue_type}")
                lines.append(f"**Suggestion:** {issue.suggestion}")
                if issue.preserve_terminology:
                    lines.append(f"**Note:** Preserves technical terminology")
                lines.append("")

        # Major Issues
        if major_issues:
            lines.append(f"## Major Issues ({len(major_issues)})\n")
            for i, issue in enumerate(major_issues, 1):
                lines.append(f"### {i}. Line {issue.line_number}: {issue.issue_type.title()}\n")
                lines.append(f"**Original:** {issue.original_text}")
                lines.append(f"**Suggestion:** {issue.suggestion}")
                lines.append("")

        # Minor Issues
        if minor_issues:
            lines.append(f"## Minor Issues ({len(minor_issues)})\n")
            for i, issue in enumerate(minor_issues, 1):
                lines.append(f"### {i}. Line {issue.line_number}: {issue.issue_type.title()}\n")
                lines.append(f"**Original:** {issue.original_text}")
                lines.append(f"**Suggestion:** {issue.suggestion}")
                lines.append("")

        return "\n".join(lines)


class PolishAgent:
    """
    Grammar and Word Flow Polish Agent

    Checks papers for grammar, clarity, and flow while preserving technical terminology.
    """

    # Common physics/math terms to preserve
    DEFAULT_PHYSICS_TERMS = {
        "qubit", "qubits", "entanglement", "decoherence", "Hamiltonian",
        "Hilbert space", "Bell state", "CNOT gate", "quantum", "eigenvalue",
        "eigenvector", "eigenstate", "unitary", "Hermitian", "tensor product",
        "fidelity", "density matrix", "von Neumann entropy", "Schmidt decomposition",
        "quantum supremacy", "NISQ", "Born rule", "wave function", "superposition"
    }

    DEFAULT_MATH_TERMS = {
        "eigenvalue", "eigenvector", "isomorphism", "homomorphism", "bijection",
        "surjection", "injection", "theorem", "lemma", "corollary", "proposition",
        "proof", "QED", "iff", "onto", "one-to-one", "cardinality", "topology"
    }

    def __init__(self, config: PaperMaintenanceConfig):
        """Initialize polish agent"""
        self.config = config
        self.project_dir = config.paper_directory
        self.output_file = self.project_dir / "polish_report.md"
        self.terminology = self._load_terminology()

    def _load_terminology(self) -> set:
        """Load terminology to preserve from config"""
        default_terms = self.DEFAULT_PHYSICS_TERMS | self.DEFAULT_MATH_TERMS

        # Check for user config
        config_file = self.project_dir / ".polish-config.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
                    if user_config and 'preserve_terms' in user_config:
                        user_terms = set(user_config['preserve_terms'])
                        return default_terms | user_terms
            except Exception as e:
                print(f"⚠️  Warning: Could not load .polish-config.yaml: {e}")

        return default_terms

    def polish_paper(
        self,
        tex_file: Path,
        mode: str = "report",  # "report" or "inline"
        preserve_terms: Optional[List[str]] = None,
        severity_filter: Optional[str] = None
    ) -> PolishResult:
        """
        Polish paper for grammar and flow

        Args:
            tex_file: LaTeX file to polish
            mode: "report" (markdown output) or "inline" (tex comments)
            preserve_terms: Additional terminology to preserve
            severity_filter: Only show issues of this severity (critical/major/minor)

        Returns:
            PolishResult with all findings
        """
        print(f"\n{'='*70}")
        print(f"Polish Agent: Grammar & Word Flow Check")
        print(f"{'='*70}\n")

        if not tex_file.exists():
            raise FileNotFoundError(f"File not found: {tex_file}")

        # Read file content
        content = tex_file.read_text()

        # Extract technical terms from content
        tech_terms = self._extract_technical_terms(content)
        all_terms = tech_terms | self.terminology
        if preserve_terms:
            all_terms |= set(preserve_terms)

        print(f"📄 Analyzing: {tex_file.name}")
        print(f"🔍 Preserving {len(all_terms)} technical terms")
        print(f"📊 Mode: {mode}\n")

        # Get polish suggestions from Claude
        print("🤖 Running grammar and flow analysis...")
        issues = self._get_polish_suggestions(content, all_terms)

        # Apply severity filter if specified
        if severity_filter:
            issues = [i for i in issues if i.severity == severity_filter]

        # Calculate statistics
        critical_count = len([i for i in issues if i.severity == "critical"])
        major_count = len([i for i in issues if i.severity == "major"])
        minor_count = len([i for i in issues if i.severity == "minor"])

        # Calculate word flow score (0-10, higher is better)
        total_lines = len(content.split('\n'))
        issues_per_100_lines = (len(issues) / max(total_lines, 1)) * 100
        word_flow_score = max(0, 10 - issues_per_100_lines / 2)

        result = PolishResult(
            file_path=tex_file,
            mode=mode,
            issues=issues,
            word_flow_score=word_flow_score,
            total_issues=len(issues),
            critical_count=critical_count,
            major_count=major_count,
            minor_count=minor_count,
            timestamp=datetime.now()
        )

        # Generate output based on mode
        if mode == "report":
            self._generate_report(result)
            print(f"\n✅ Polish check complete!")
            print(f"   Issues found: {len(issues)} (Critical: {critical_count}, Major: {major_count}, Minor: {minor_count})")
            print(f"   Word flow score: {word_flow_score:.1f}/10")
            print(f"   Report saved: {self.output_file}")
        else:  # inline
            self._insert_inline_comments(tex_file, issues)
            print(f"\n✅ Inline comments added to {tex_file.name}")
            print(f"   Issues marked: {len(issues)}")
            print(f"   Backup saved: {tex_file.with_suffix('.tex.backup')}")

        return result

    def _extract_technical_terms(self, content: str) -> set:
        """Extract technical terms from LaTeX content"""
        terms = set()

        # Find terms in \texttt{}, \mathbf{}, etc.
        for pattern in [r'\\texttt\{([^}]+)\}', r'\\mathbf\{([^}]+)\}',
                       r'\\emph\{([^}]+)\}', r'\\textit\{([^}]+)\}']:
            matches = re.findall(pattern, content)
            terms.update(matches)

        # Find custom commands (likely terminology)
        custom_commands = re.findall(r'\\newcommand\{\\(\w+)\}', content)
        terms.update(custom_commands)

        # Find capitalized words mid-sentence (likely proper nouns)
        # Skip words at sentence start
        sentences = re.split(r'[.!?]\s+', content)
        for sentence in sentences:
            words = sentence.split()[1:]  # Skip first word
            for word in words:
                if word and word[0].isupper() and word.isalpha():
                    terms.add(word)

        return terms

    def _get_polish_suggestions(self, content: str, terms: set) -> List[GrammarIssue]:
        """Get polishing suggestions from Claude"""

        # Build term list for prompt (limit to first 50 for brevity)
        term_list = ', '.join(list(terms)[:50])
        if len(terms) > 50:
            term_list += f", ... and {len(terms) - 50} more"

        prompt = f"""You are a technical writing editor specializing in academic physics and mathematics papers.

**CRITICAL RULES:**
1. NEVER change technical terminology including: {term_list}
2. ONLY check: grammar, sentence flow, clarity, readability
3. Preserve ALL LaTeX commands, equations, citations, and mathematical notation
4. Focus on making sentences clearer without changing technical meaning
5. Ignore LaTeX preamble, commands, and bibliography sections

**WHAT TO CHECK:**
- Grammar errors (subject-verb agreement, tense consistency, article usage)
- Word flow issues (awkward phrasing, unclear sentences, redundancy)
- Clarity problems (confusing constructions, ambiguous pronouns)
- Style issues (passive voice overuse, wordiness)

**WHAT TO IGNORE:**
- Technical terminology and jargon
- Mathematical expressions and equations
- LaTeX commands and environments
- Citation formatting
- Bibliography entries

**PAPER CONTENT:**
```latex
{content[:20000]}
```
{"[Content truncated for length]" if len(content) > 20000 else ""}

Analyze this LaTeX content and identify grammar and flow issues. For each issue provide:
- LINE: <approximate line number>
- ORIGINAL: <exact quote of problematic text>
- TYPE: <grammar|flow|clarity|style>
- SUGGESTION: <how to improve it>
- SEVERITY: <critical|major|minor>

Use this severity guide:
- critical: Grammar errors that affect understanding (subject-verb disagreement, wrong tense)
- major: Flow issues that hinder readability (awkward phrasing, unclear meaning)
- minor: Style suggestions (passive voice, wordiness)

Output each issue in this exact format:
---
LINE: <number>
ORIGINAL: <text>
TYPE: <type>
SUGGESTION: <improvement>
SEVERITY: <severity>
---

If no issues found, output: "NO ISSUES FOUND"
"""

        try:
            response = self._call_claude(prompt)
            return self._parse_issues(response, content)
        except Exception as e:
            print(f"⚠️  Warning: Claude call failed: {e}")
            return []

    def _call_claude(self, prompt: str) -> str:
        """Call Claude API via CLI"""
        try:
            result = subprocess.run(
                ["claude", "--dangerously-skip-permissions", "-p", prompt],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=180
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude call failed: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude call timed out after 180 seconds")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude CLI not found. Please install: pip install claude-cli"
            )

    def _parse_issues(self, response: str, content: str) -> List[GrammarIssue]:
        """Parse Claude's response into structured issues"""

        if "NO ISSUES FOUND" in response:
            return []

        issues = []

        # Split by issue separator
        issue_blocks = re.split(r'\n---\n', response)

        for block in issue_blocks:
            if not block.strip():
                continue

            # Extract fields
            line_match = re.search(r'LINE:\s*(\d+)', block)
            original_match = re.search(r'ORIGINAL:\s*(.+?)(?=\nTYPE:|$)', block, re.DOTALL)
            type_match = re.search(r'TYPE:\s*(\w+)', block)
            suggestion_match = re.search(r'SUGGESTION:\s*(.+?)(?=\nSEVERITY:|$)', block, re.DOTALL)
            severity_match = re.search(r'SEVERITY:\s*(\w+)', block)

            if all([line_match, original_match, type_match, suggestion_match, severity_match]):
                issues.append(GrammarIssue(
                    line_number=int(line_match.group(1)),
                    original_text=original_match.group(1).strip(),
                    issue_type=type_match.group(1).strip().lower(),
                    suggestion=suggestion_match.group(1).strip(),
                    severity=severity_match.group(1).strip().lower()
                ))

        return issues

    def _generate_report(self, result: PolishResult):
        """Save report to markdown file"""
        markdown_content = result.to_markdown()
        self.output_file.write_text(markdown_content)

        # Also save timestamped copy
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        archive_file = self.project_dir / f"polish_report_{timestamp}.md"
        archive_file.write_text(markdown_content)

    def _insert_inline_comments(self, tex_file: Path, issues: List[GrammarIssue]):
        """Insert colored comments into LaTeX file"""

        # Create backup
        backup_file = tex_file.with_suffix('.tex.backup')
        content = tex_file.read_text()
        backup_file.write_text(content)

        lines = content.split('\n')

        # Insert comments (in reverse order to preserve line numbers)
        for issue in sorted(issues, key=lambda x: x.line_number, reverse=True):
            if 0 < issue.line_number <= len(lines):
                line_idx = issue.line_number - 1

                # Choose comment color based on severity
                if issue.severity == "critical":
                    comment_cmd = "\\grammarfix"
                    color = "red"
                elif issue.severity == "major":
                    comment_cmd = "\\flowsuggestion"
                    color = "orange"
                else:
                    comment_cmd = "\\polishcomment"
                    color = "blue"

                # Format comment
                comment_text = f"{issue.issue_type.upper()}: {issue.suggestion}"
                comment = f"{comment_cmd}{{{comment_text}}}"

                # Add comment at end of line
                lines[line_idx] = lines[line_idx].rstrip() + " " + comment

        # Write modified content
        tex_file.write_text('\n'.join(lines))

    def setup_latex_macros(self) -> Path:
        """
        Setup LaTeX macros for inline comments

        Returns path to macros file
        """
        macros_file = self.project_dir / "polish_macros.tex"

        macros_content = r"""% Polish Agent - LaTeX Macros for Inline Comments
% Include in your preamble: \input{polish_macros}

\usepackage{xcolor}

% Grammar/flow comment macros
\newcommand{\polishcomment}[1]{\textcolor{blue}{[\textbf{POLISH:} #1]}}
\newcommand{\grammarfix}[1]{\textcolor{red}{[\textbf{GRAMMAR:} #1]}}
\newcommand{\flowsuggestion}[1]{\textcolor{orange}{[\textbf{FLOW:} #1]}}

% To hide all comments, uncomment these lines:
% \renewcommand{\polishcomment}[1]{}
% \renewcommand{\grammarfix}[1]{}
% \renewcommand{\flowsuggestion}[1]{}
"""

        macros_file.write_text(macros_content)
        return macros_file


def main():
    """CLI entry point for standalone testing"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Polish Agent - Grammar & Flow Checker")
    parser.add_argument('tex_file', type=Path, help='LaTeX file to polish')
    parser.add_argument(
        '--mode',
        choices=['report', 'inline'],
        default='report',
        help='Output mode (default: report)'
    )
    parser.add_argument(
        '--severity',
        choices=['critical', 'major', 'minor'],
        help='Filter by severity'
    )
    parser.add_argument(
        '--preserve',
        type=str,
        help='Comma-separated list of additional terms to preserve'
    )
    parser.add_argument(
        '--setup-macros',
        action='store_true',
        help='Setup LaTeX macros for inline comments'
    )
    parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file'
    )

    args = parser.parse_args()

    # Load config
    if args.config and args.config.exists():
        config = PaperMaintenanceConfig.load(args.config)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = args.tex_file.parent if args.tex_file.parent != Path('.') else Path.cwd()

    agent = PolishAgent(config)

    # Setup macros if requested
    if args.setup_macros:
        macros_file = agent.setup_latex_macros()
        print(f"✓ Created {macros_file}")
        print(f"\nAdd to your LaTeX preamble:")
        print(f"  \\input{{polish_macros}}")
        return 0

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

        return 0 if result.critical_count == 0 else 1

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
