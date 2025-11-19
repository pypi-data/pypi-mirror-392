#!/usr/bin/env python3
"""
APS Journal Review Agent
========================

Acts as a peer referee for APS journals (Physical Review A, B, L, X, PRX Quantum).
Reviews papers for scientific merit, compliance with APS standards, and provides
editorial recommendations.

Output: 1-3 page review with summary, pros/cons, and decision.
"""

import subprocess
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import PaperMaintenanceConfig
from .pdf_compiler import PDFCompiler


@dataclass
class ReviewerProfile:
    """APS reviewer persona definition"""
    name: str
    role: str
    expertise: str
    focus_areas: List[str]

    def to_prompt_section(self) -> str:
        """Convert profile to prompt text"""
        return f"""
### {self.name} ({self.role})
**Expertise:** {self.expertise}
**Focus Areas:** {', '.join(self.focus_areas)}
"""


@dataclass
class APSReviewResult:
    """Complete APS review result"""
    journal: str
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    decision: str  # "Accept", "Minor Revision", "Major Revision", "Reject"
    decision_rationale: str
    detailed_reviews: Dict[str, str]  # reviewer_name -> review_text
    compliance_issues: List[str]
    timestamp: datetime

    def to_markdown(self) -> str:
        """Generate markdown review report"""
        lines = []
        lines.append("# APS Journal Review Report")
        lines.append(f"\n**Journal:** {self.journal}")
        lines.append(f"**Date:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Decision:** {self.decision}")
        lines.append("\n" + "="*70 + "\n")

        # Summary
        lines.append("## Summary\n")
        lines.append(self.summary)
        lines.append("\n")

        # Strengths
        lines.append("## Strengths\n")
        for i, strength in enumerate(self.strengths, 1):
            lines.append(f"{i}. {strength}")
        lines.append("\n")

        # Weaknesses
        lines.append("## Weaknesses\n")
        for i, weakness in enumerate(self.weaknesses, 1):
            lines.append(f"{i}. {weakness}")
        lines.append("\n")

        # Compliance Issues (if any)
        if self.compliance_issues:
            lines.append("## APS Compliance Issues\n")
            for i, issue in enumerate(self.compliance_issues, 1):
                lines.append(f"{i}. {issue}")
            lines.append("\n")

        # Detailed Reviews
        lines.append("## Detailed Reviewer Comments\n")
        for reviewer_name, review_text in self.detailed_reviews.items():
            lines.append(f"### {reviewer_name}\n")
            lines.append(review_text)
            lines.append("\n")

        # Decision and Rationale
        lines.append("## Editorial Decision\n")
        lines.append(f"**Decision:** {self.decision}\n")
        lines.append(f"**Rationale:** {self.decision_rationale}")
        lines.append("\n")

        return "\n".join(lines)


class APSReviewer:
    """
    APS Journal Peer Review Agent

    Simulates peer review process for APS journals with multiple expert reviewers.
    Provides comprehensive feedback including summary, pros/cons, and editorial decision.
    """

    # APS Journal Reviewer Personas
    REVIEWERS = [
        ReviewerProfile(
            name="Dr. Rigorous Theorist",
            role="Theory and Methods Specialist",
            expertise="Theoretical frameworks, mathematical rigor, model validity",
            focus_areas=[
                "Mathematical correctness and rigor",
                "Theoretical foundations and assumptions",
                "Model validity and applicability",
                "Analytical derivations and proofs",
                "Comparison with existing theories"
            ]
        ),
        ReviewerProfile(
            name="Dr. Experimental Validator",
            role="Experimental and Computational Expert",
            expertise="Experimental design, data analysis, computational methods",
            focus_areas=[
                "Experimental methodology and controls",
                "Data quality and statistical analysis",
                "Computational methods and validation",
                "Error analysis and uncertainty quantification",
                "Reproducibility of results"
            ]
        ),
        ReviewerProfile(
            name="Dr. Field Connector",
            role="Broader Impact and Context Specialist",
            expertise="Literature context, significance, broader implications",
            focus_areas=[
                "Novelty and originality",
                "Significance to the field",
                "Literature review completeness",
                "Clarity of presentation",
                "Broader impact and applications"
            ]
        )
    ]

    # APS Journal Specifications
    JOURNAL_SPECS = {
        'pra': {
            'full_name': 'Physical Review A',
            'scope': 'Atomic, molecular, and optical physics',
            'typical_length': '8-12 pages',
            'emphasis': 'Fundamental research in AMO physics'
        },
        'prb': {
            'full_name': 'Physical Review B',
            'scope': 'Condensed matter and materials physics',
            'typical_length': '8-15 pages',
            'emphasis': 'Condensed matter phenomena and materials'
        },
        'prl': {
            'full_name': 'Physical Review Letters',
            'scope': 'All physics - high impact short papers',
            'typical_length': '4 pages maximum',
            'emphasis': 'Significant advances with broad impact'
        },
        'prx': {
            'full_name': 'Physical Review X',
            'scope': 'All physics - exceptional significance',
            'typical_length': 'No strict limit',
            'emphasis': 'Exceptional quality and broad interest'
        },
        'prxquantum': {
            'full_name': 'PRX Quantum',
            'scope': 'Quantum information science',
            'typical_length': 'No strict limit',
            'emphasis': 'Outstanding quantum research'
        },
        'prr': {
            'full_name': 'Physical Review Research',
            'scope': 'All physics - open access',
            'typical_length': 'No strict limit',
            'emphasis': 'Solid research across all physics'
        }
    }

    def __init__(self, config: PaperMaintenanceConfig):
        """Initialize APS reviewer"""
        self.config = config
        self.project_dir = config.paper_directory
        self.output_file = self.project_dir / "aps_review.md"
        self.compiler = PDFCompiler(config)

    def review_paper(
        self,
        journal: str = "pra",
        input_file: Optional[Path] = None,
        strict: bool = False
    ) -> APSReviewResult:
        """
        Perform comprehensive APS journal review

        Args:
            journal: Target APS journal (pra, prb, prl, prx, prxquantum, prr)
            input_file: Specific PDF file to review (if None, compiles from LaTeX)
            strict: Apply strict journal-specific criteria

        Returns:
            APSReviewResult with complete review
        """
        journal = journal.lower()
        if journal not in self.JOURNAL_SPECS:
            raise ValueError(f"Unknown journal: {journal}. Must be one of {list(self.JOURNAL_SPECS.keys())}")

        journal_info = self.JOURNAL_SPECS[journal]

        print(f"\n{'='*70}")
        print(f"APS Peer Review: {journal_info['full_name']}")
        print(f"{'='*70}\n")

        # Step 1: Get paper content
        paper_content, pdf_path = self._prepare_paper(input_file)

        # Step 2: Automated compliance checks
        print("📋 Running automated compliance checks...")
        compliance_issues = self._check_aps_compliance(paper_content, pdf_path, journal)

        # Step 3: Multi-reviewer evaluation
        print("\n👥 Initiating peer review process...")
        detailed_reviews = {}

        for i, reviewer in enumerate(self.REVIEWERS, 1):
            print(f"   [{i}/{len(self.REVIEWERS)}] {reviewer.name} reviewing...")
            review_text = self._get_reviewer_feedback(
                reviewer, paper_content, journal_info, strict
            )
            detailed_reviews[reviewer.name] = review_text

        # Step 4: Extract and synthesize findings
        print("\n📊 Synthesizing reviews...")
        synthesis = self._synthesize_reviews(
            detailed_reviews, compliance_issues, journal_info, strict
        )

        # Step 5: Create review result
        result = APSReviewResult(
            journal=journal_info['full_name'],
            summary=synthesis['summary'],
            strengths=synthesis['strengths'],
            weaknesses=synthesis['weaknesses'],
            decision=synthesis['decision'],
            decision_rationale=synthesis['rationale'],
            detailed_reviews=detailed_reviews,
            compliance_issues=compliance_issues,
            timestamp=datetime.now()
        )

        # Step 6: Save report
        self._save_review(result)

        print(f"\n✅ Review complete! Decision: {result.decision}")
        print(f"📄 Full report saved to: {self.output_file}")

        return result

    def _prepare_paper(self, input_file: Optional[Path]) -> Tuple[str, Path]:
        """Prepare paper for review (compile if needed)"""
        if input_file and input_file.suffix == '.pdf':
            # PDF provided directly - extract text for review
            print(f"📄 Reading PDF: {input_file}")
            # For PDF, read associated .tex if available, otherwise use PDF metadata
            tex_file = input_file.with_suffix('.tex')
            if tex_file.exists():
                content = tex_file.read_text()
            else:
                # Use pdftotext if available, or note it's PDF-only review
                content = f"[PDF-only review for {input_file.name}]\n"
                content += "[Note: LaTeX source not available for detailed review]"
            return content, input_file

        else:
            # Compile from LaTeX
            print("🔨 Compiling LaTeX paper...")
            compile_result = self.compiler.compile(clean=False)

            if not compile_result.success:
                errors_text = "\n".join(compile_result.errors)
                raise RuntimeError(
                    f"Paper compilation failed:\n{errors_text}"
                )

            # Read LaTeX source
            main_tex = self.compiler.main_tex
            if not main_tex.exists():
                raise FileNotFoundError(f"Main TeX file not found: {main_tex}")

            content = main_tex.read_text()
            pdf_path = compile_result.pdf_path

            print(f"✓ Compiled successfully: {pdf_path}")
            return content, pdf_path

    def _check_aps_compliance(
        self, content: str, pdf_path: Path, journal: str
    ) -> List[str]:
        """Check APS-specific compliance requirements"""
        issues = []

        # Check 1: REVTeX class (if LaTeX)
        if not content.startswith("[PDF-only review"):
            if not re.search(r'\\documentclass.*revtex4', content, re.IGNORECASE):
                issues.append(
                    "Paper does not use REVTeX4 document class. "
                    "APS journals require REVTeX4-2."
                )

        # Check 2: Page limits for PRL
        if journal == 'prl':
            try:
                result = subprocess.run(
                    ['pdfinfo', str(pdf_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    pages_match = re.search(r'Pages:\s*(\d+)', result.stdout)
                    if pages_match:
                        pages = int(pages_match.group(1))
                        if pages > 4:
                            issues.append(
                                f"PRL papers must be ≤4 pages. Current: {pages} pages. "
                                f"Consider PRX, PRA, or PRR for longer papers."
                            )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # pdfinfo not available, skip check
                pass

        # Check 3: Abstract presence
        if not re.search(r'\\begin\{abstract\}', content):
            issues.append("Abstract section not found. APS requires abstracts.")

        # Check 4: Bibliography
        has_bib = (
            re.search(r'\\bibliography\{', content) or
            re.search(r'\\begin\{thebibliography\}', content)
        )
        if not has_bib:
            issues.append("No bibliography found. APS requires proper citations.")

        return issues

    def _get_reviewer_feedback(
        self,
        reviewer: ReviewerProfile,
        paper_content: str,
        journal_info: Dict,
        strict: bool
    ) -> str:
        """Get feedback from a specific reviewer using Claude"""

        # Construct review prompt
        prompt = self._build_review_prompt(
            reviewer, paper_content, journal_info, strict
        )

        # Call Claude for review
        try:
            review = self._call_claude(prompt)
            return review
        except Exception as e:
            return f"[Review unavailable: {str(e)}]"

    def _build_review_prompt(
        self,
        reviewer: ReviewerProfile,
        paper_content: str,
        journal_info: Dict,
        strict: bool
    ) -> str:
        """Build detailed review prompt for Claude"""

        strictness = "very strict" if strict else "thorough but fair"

        prompt = f"""You are {reviewer.name}, a {reviewer.role} serving as a peer reviewer for {journal_info['full_name']}.

**Your Expertise:** {reviewer.expertise}

**Your Review Focus:**
{chr(10).join(f"- {area}" for area in reviewer.focus_areas)}

**Journal Context:**
- Journal: {journal_info['full_name']}
- Scope: {journal_info['scope']}
- Typical Length: {journal_info['typical_length']}
- Emphasis: {journal_info['emphasis']}

**Review Instructions:**
Please provide a {strictness} review of the paper below. Structure your review as follows:

1. **Brief Assessment** (2-3 sentences): Overall impression
2. **Detailed Comments** (organized by your focus areas)
3. **Specific Issues** (list concrete problems to address)
4. **Recommendation** (Accept / Minor Revision / Major Revision / Reject)

Be constructive, specific, and reference particular sections/equations when relevant.

---

**PAPER CONTENT:**

{paper_content[:15000]}

{"[Content truncated for length]" if len(paper_content) > 15000 else ""}

---

Please provide your review now:"""

        return prompt

    def _call_claude(self, prompt: str) -> str:
        """Call Claude API via CLI"""
        try:
            result = subprocess.run(
                ["claude", "--dangerously-skip-permissions", "-p", prompt],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude call failed: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude call timed out after 120 seconds")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude CLI not found. Please install: pip install claude-cli"
            )

    def _synthesize_reviews(
        self,
        detailed_reviews: Dict[str, str],
        compliance_issues: List[str],
        journal_info: Dict,
        strict: bool
    ) -> Dict:
        """Synthesize multiple reviews into summary, pros/cons, and decision"""

        # Build synthesis prompt
        reviews_text = "\n\n".join(
            f"### {reviewer}:\n{review}"
            for reviewer, review in detailed_reviews.items()
        )

        compliance_text = "\n".join(
            f"- {issue}" for issue in compliance_issues
        ) if compliance_issues else "None"

        strictness = "strict" if strict else "standard"

        prompt = f"""You are the **Editor** of {journal_info['full_name']}. You have received reviews from three expert reviewers for a submitted manuscript.

**Reviewer Feedback:**

{reviews_text}

**Automated Compliance Checks:**
{compliance_text}

**Your Task as Editor:**

Based on the reviews and compliance checks, provide:

1. **SUMMARY** (one paragraph, 4-6 sentences): Synthesize the key findings from all reviewers

2. **STRENGTHS** (3-5 bullet points): Major positive aspects identified by reviewers

3. **WEAKNESSES** (3-5 bullet points): Major concerns and issues to address

4. **DECISION**: Choose ONE of:
   - Accept (minimal changes needed)
   - Minor Revision (addressable issues, likely acceptance)
   - Major Revision (significant concerns, re-review needed)
   - Reject (fundamental flaws or unsuitable for journal)

5. **DECISION RATIONALE** (2-4 sentences): Explain why you chose this decision

Apply {strictness} editorial standards for {journal_info['full_name']}.

**Output Format:**

SUMMARY:
[Your summary paragraph]

STRENGTHS:
- [Strength 1]
- [Strength 2]
...

WEAKNESSES:
- [Weakness 1]
- [Weakness 2]
...

DECISION:
[Accept / Minor Revision / Major Revision / Reject]

RATIONALE:
[Your rationale]
"""

        try:
            synthesis_text = self._call_claude(prompt)
            return self._parse_synthesis(synthesis_text)

        except Exception as e:
            # Fallback synthesis
            return {
                'summary': f"Review synthesis unavailable ({str(e)}). See detailed reviews below.",
                'strengths': ["See individual reviewer comments"],
                'weaknesses': ["See individual reviewer comments"],
                'decision': "Major Revision",
                'rationale': "Unable to synthesize reviews automatically. Manual editorial review required."
            }

    def _parse_synthesis(self, synthesis_text: str) -> Dict:
        """Parse synthesis output into structured format"""

        result = {
            'summary': '',
            'strengths': [],
            'weaknesses': [],
            'decision': 'Major Revision',
            'rationale': ''
        }

        # Extract SUMMARY
        summary_match = re.search(
            r'SUMMARY:\s*\n(.+?)(?=\n\nSTRENGTHS:|\n\nWEAKNESSES:|\n\nDECISION:|$)',
            synthesis_text,
            re.DOTALL | re.IGNORECASE
        )
        if summary_match:
            result['summary'] = summary_match.group(1).strip()

        # Extract STRENGTHS
        strengths_match = re.search(
            r'STRENGTHS:\s*\n(.+?)(?=\n\nWEAKNESSES:|\n\nDECISION:|$)',
            synthesis_text,
            re.DOTALL | re.IGNORECASE
        )
        if strengths_match:
            strengths_text = strengths_match.group(1)
            result['strengths'] = [
                s.strip('- ').strip()
                for s in strengths_text.split('\n')
                if s.strip() and s.strip().startswith('-')
            ]

        # Extract WEAKNESSES
        weaknesses_match = re.search(
            r'WEAKNESSES:\s*\n(.+?)(?=\n\nDECISION:|$)',
            synthesis_text,
            re.DOTALL | re.IGNORECASE
        )
        if weaknesses_match:
            weaknesses_text = weaknesses_match.group(1)
            result['weaknesses'] = [
                w.strip('- ').strip()
                for w in weaknesses_text.split('\n')
                if w.strip() and w.strip().startswith('-')
            ]

        # Extract DECISION
        decision_match = re.search(
            r'DECISION:\s*\n(.+?)(?=\n\nRATIONALE:|$)',
            synthesis_text,
            re.DOTALL | re.IGNORECASE
        )
        if decision_match:
            decision_text = decision_match.group(1).strip()
            # Normalize decision
            if 'reject' in decision_text.lower():
                result['decision'] = 'Reject'
            elif 'major' in decision_text.lower():
                result['decision'] = 'Major Revision'
            elif 'minor' in decision_text.lower():
                result['decision'] = 'Minor Revision'
            elif 'accept' in decision_text.lower():
                result['decision'] = 'Accept'

        # Extract RATIONALE
        rationale_match = re.search(
            r'RATIONALE:\s*\n(.+?)$',
            synthesis_text,
            re.DOTALL | re.IGNORECASE
        )
        if rationale_match:
            result['rationale'] = rationale_match.group(1).strip()

        return result

    def _save_review(self, result: APSReviewResult):
        """Save review to markdown file"""
        markdown_content = result.to_markdown()
        self.output_file.write_text(markdown_content)

        # Also save timestamped copy
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        archive_file = self.project_dir / f"aps_review_{timestamp}.md"
        archive_file.write_text(markdown_content)


def main():
    """CLI entry point for standalone testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m texforge.aps_reviewer <journal> [--strict]")
        print("Journals: pra, prb, prl, prx, prxquantum, prr")
        sys.exit(1)

    journal = sys.argv[1].lower()
    strict = '--strict' in sys.argv

    # Create minimal config
    config = PaperMaintenanceConfig()
    config.paper_directory = Path.cwd()

    # Run review
    reviewer = APSReviewer(config)
    result = reviewer.review_paper(journal=journal, strict=strict)

    print(f"\n{'='*70}")
    print(f"Decision: {result.decision}")
    print(f"Report: {reviewer.output_file}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
