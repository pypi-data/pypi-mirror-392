#!/usr/bin/env python3
"""
Autonomous Paper Writing System
Claude Code writes paper content based on outline and human feedback
"""
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

from .config import PaperMaintenanceConfig
from progressive_writer import ProgressiveWriter, PaperStage


@dataclass
class WritingTask:
    """A section writing task"""
    section: str  # e.g., "introduction", "methods", "results"
    status: str   # "pending", "in_progress", "needs_revision", "complete"
    content: str = ""
    human_feedback: str = ""
    revision_count: int = 0
    word_count: int = 0


class AutonomousWriter:
    """Claude Code writes paper content autonomously"""
    
    MAX_RETRIES = 3
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.outline_file = self.project_dir / "OUTLINE.md"
        self.feedback_file = self.project_dir / "HUMAN_FEEDBACK.md"
        self.tasks_file = self.project_dir / ".writing_tasks.json"
        
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> Dict[str, WritingTask]:
        """Load writing tasks"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                data = json.load(f)
                return {
                    k: WritingTask(**v) for k, v in data.items()
                }
        return {}
    
    def _save_tasks(self) -> None:
        """Save writing tasks"""
        data = {k: v.__dict__ for k, v in self.tasks.items()}
        with open(self.tasks_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _call_claude(self, prompt: str, timeout: int = 300) -> Tuple[bool, str]:
        """Call Claude Code with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                print(f"  Attempt {attempt + 1}/{self.MAX_RETRIES}...")
                
                result = subprocess.run(
                    ["claude", "--dangerously-skip-permissions", "-p", prompt],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    return True, result.stdout.strip()
                
                print(f"    Failed: Empty or error response")
                
            except subprocess.TimeoutExpired:
                print(f"    Timeout after {timeout}s")
            except Exception as e:
                print(f"    Error: {e}")
        
        # All retries failed - escalate to human
        return False, f"ESCALATION NEEDED: Failed after {self.MAX_RETRIES} attempts"
    
    def write_section(self, section: str, outline: str, 
                     previous_sections: str = "", 
                     human_feedback: str = "") -> Tuple[bool, str]:
        """Write a complete section"""
        
        print(f"\n📝 Writing section: {section}")
        
        # Read any human feedback
        if self.feedback_file.exists():
            feedback_content = self.feedback_file.read_text()
            if feedback_content.strip():
                human_feedback += f"\n\n{feedback_content}"
        
        # Construct prompt
        prompt = self._construct_writing_prompt(
            section, outline, previous_sections, human_feedback
        )
        
        success, content = self._call_claude(prompt, timeout=600)
        
        if not success:
            # Escalate to human
            self._escalate_to_human(section, content)
            return False, content
        
        # Save section
        section_file = self.project_dir / f"{section}.tex"
        section_file.write_text(content)
        
        print(f"  ✓ Wrote {len(content.split())} words to {section_file}")
        
        return True, content
    
    def _construct_writing_prompt(self, section: str, outline: str,
                                  previous_sections: str, feedback: str) -> str:
        """Construct prompt for section writing"""
        
        prompts = {
            "introduction": f"""Write the INTRODUCTION section for a physics research paper.

OUTLINE:
{outline}

PREVIOUS SECTIONS:
{previous_sections if previous_sections else "None - this is the first section"}

HUMAN FEEDBACK:
{feedback if feedback else "None"}

Write a complete, publication-ready introduction that:
1. Motivates the problem with clear physical context
2. Reviews relevant literature (cite as [1], [2], etc.)
3. Identifies the gap this work fills
4. States main contributions clearly
5. Outlines paper structure

Target length: 800-1200 words for PRA, 300-500 for PRL main text.
Use LaTeX formatting.
Include proper citations as \\cite{{key}}.
Define notation as you introduce concepts.

Write ONLY the LaTeX content (no explanations, no markdown wrappers).
Start directly with the section content.""",

            "theory": f"""Write the THEORY/METHODS section.

OUTLINE:
{outline}

INTRODUCTION WRITTEN:
{previous_sections}

HUMAN FEEDBACK:
{feedback if feedback else "None"}

Write a complete theory section that:
1. Presents mathematical framework rigorously
2. Defines all notation clearly
3. States assumptions explicitly
4. Derives key results step-by-step
5. Connects to physical intuition

For PRL: Keep main text concise, defer proofs to appendix
For PRA: Full derivations in main text

Use proper LaTeX math:
- Display equations: \\begin{{equation}}...\\end{{equation}}
- Inline math: $...$
- Multi-line: \\begin{{align}}...\\end{{align}}

Include equation labels: \\label{{eq:name}}

Write ONLY LaTeX content.""",

            "results": f"""Write the RESULTS section.

OUTLINE:
{outline}

PREVIOUS SECTIONS:
{previous_sections}

HUMAN FEEDBACK:
{feedback if feedback else "None"}

Write a complete results section that:
1. Presents numerical/simulation results
2. References figures: Fig.~\\ref{{fig:name}}
3. Quantifies findings with numbers
4. Compares with theory/predictions
5. Discusses implications of each result

Structure:
- Subsection per main result
- Clear figure descriptions
- Quantitative comparisons
- Statistical significance where relevant

For PRL: Most impactful results only
For PRA: Comprehensive results

Write ONLY LaTeX content.""",

            "discussion": f"""Write the DISCUSSION section.

OUTLINE:
{outline}

PAPER SO FAR:
{previous_sections}

HUMAN FEEDBACK:
{feedback if feedback else "None"}

Write a discussion that:
1. Interprets results in broader context
2. Compares with existing literature
3. Discusses limitations honestly
4. Explores implications
5. Suggests future directions

Be balanced:
- Acknowledge what worked well
- Be honest about limitations
- Don't overclaim
- Connect to big picture

Write ONLY LaTeX content.""",

            "conclusion": f"""Write the CONCLUSION section.

FULL PAPER:
{previous_sections}

OUTLINE:
{outline}

HUMAN FEEDBACK:
{feedback if feedback else "None"}

Write a concise conclusion that:
1. Summarizes main findings (2-3 sentences)
2. States broader significance
3. Points to future work
4. Ends with impact statement

Keep it brief: 200-300 words.
No new information - synthesis only.

Write ONLY LaTeX content.""",

            "abstract": f"""Write the ABSTRACT.

COMPLETE PAPER:
{previous_sections}

OUTLINE:
{outline}

HUMAN FEEDBACK:
{feedback if feedback else "None"}

Write an abstract following this structure:
1. Motivation (1 sentence): Why does this matter?
2. Gap (1 sentence): What's missing?
3. Approach (2 sentences): What did we do?
4. Results (2-3 sentences): What did we find? (quantitative!)
5. Impact (1 sentence): What does it mean?

Length:
- PRL: 600 characters max
- PRA: 150-200 words

Write ONLY the abstract content in LaTeX.
Use \\begin{{abstract}}...\\end{{abstract}}."""
        }
        
        return prompts.get(section, f"Write the {section} section based on the outline.")
    
    def _escalate_to_human(self, section: str, issue: str) -> None:
        """Escalate issue to human via daily digest"""
        escalation_file = self.project_dir / "ESCALATIONS.md"
        
        content = f"""# Escalation: {section}

**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Issue:** {issue}

**What I tried:**
- Attempted {self.MAX_RETRIES} times to write {section}
- Each attempt failed or produced insufficient content

**What I need:**
- Human guidance on how to proceed
- Clarification on expectations for this section
- Or: human writes this section manually

**To resolve:**
1. Add feedback to HUMAN_FEEDBACK.md
2. Re-run: python3 autonomous_writer.py --section {section}

**Or write section manually:**
{section}.tex
"""
        
        if escalation_file.exists():
            existing = escalation_file.read_text()
            content = existing + "\n\n---\n\n" + content
        
        escalation_file.write_text(content)
        print(f"\n⚠️  ESCALATED to human: {escalation_file}")
    
    def write_full_paper(self, outline_file: Optional[Path] = None) -> bool:
        """Write entire paper from outline"""
        
        if outline_file:
            self.outline_file = outline_file
        
        if not self.outline_file.exists():
            print(f"Error: Outline not found: {self.outline_file}")
            print("Run: python3 progressive_writer.py --create-outline")
            return False
        
        outline = self.outline_file.read_text()
        
        # Define writing order
        sections_order = [
            "introduction",
            "theory",      # or "methods"
            "results",
            "discussion",
            "conclusion",
            "abstract"     # Write last, when paper is complete
        ]
        
        print("🚀 Starting autonomous paper writing...")
        print(f"Sections to write: {len(sections_order)}")
        print(f"Max retries per section: {self.MAX_RETRIES}")
        print()
        
        accumulated_content = ""
        failed_sections = []
        
        for section in sections_order:
            # Check if human wants to skip
            if self._check_skip_section(section):
                print(f"⏭️  Skipping {section} (human will write)")
                continue
            
            # Write section
            success, content = self.write_section(
                section, outline, accumulated_content
            )
            
            if success:
                accumulated_content += f"\n\n% {section.upper()}\n{content}"
                
                # Save task status
                self.tasks[section] = WritingTask(
                    section=section,
                    status="complete",
                    content=content,
                    word_count=len(content.split())
                )
                self._save_tasks()
            else:
                failed_sections.append(section)
                self.tasks[section] = WritingTask(
                    section=section,
                    status="needs_revision",
                    content=content
                )
                self._save_tasks()
        
        # Generate main.tex that includes all sections
        self._generate_main_tex(sections_order)
        
        # Summary
        print("\n" + "="*60)
        print("WRITING SUMMARY")
        print("="*60)
        print(f"Completed: {len(sections_order) - len(failed_sections)}/{len(sections_order)}")
        
        if failed_sections:
            print(f"\n⚠️  Failed sections (need human input):")
            for section in failed_sections:
                print(f"  - {section}")
            print(f"\nSee ESCALATIONS.md for details")
            return False
        else:
            print("\n✅ All sections complete!")
            print(f"\nGenerated: main.tex")
            print("Next: python3 pdf_compiler.py --compile")
            return True
    
    def _check_skip_section(self, section: str) -> bool:
        """Check if human wants to skip this section"""
        skip_file = self.project_dir / ".skip_sections.txt"
        if skip_file.exists():
            skip_list = skip_file.read_text().strip().split('\n')
            return section in skip_list
        return False
    
    def _generate_main_tex(self, sections: List[str]) -> None:
        """Generate main.tex that includes all sections"""
        
        # Read template if exists
        template_file = self.project_dir / "template.tex"
        if template_file.exists():
            template = template_file.read_text()
            
            # Replace placeholder with includes
            includes = "\n".join([f"\\input{{{s}}}" for s in sections])
            
            # Try to find where to insert
            if "% INCLUDE SECTIONS HERE" in template:
                main_content = template.replace("% INCLUDE SECTIONS HERE", includes)
            else:
                # Insert before \bibliography
                main_content = template.replace(
                    "\\bibliography{references}",
                    f"{includes}\n\n\\bibliography{{references}}"
                )
        else:
            # Create simple main.tex
            main_content = r"""\documentclass[aps,pra,twocolumn,superscriptaddress]{revtex4-2}

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{braket}

\input{macros}

\begin{document}

\title{Your Title}
\author{Your Name}
\affiliation{Your Institution}
\date{\today}

""" + "\n".join([f"\\input{{{s}}}" for s in sections]) + r"""

\bibliography{references}

\end{document}
"""
        
        main_file = self.project_dir / "main.tex"
        main_file.write_text(main_content)
        print(f"  ✓ Generated {main_file}")
    
    def revise_section(self, section: str, feedback: str) -> bool:
        """Revise a section based on feedback"""
        
        print(f"\n✏️  Revising {section} with feedback...")
        
        # Read current content
        section_file = self.project_dir / f"{section}.tex"
        if not section_file.exists():
            print(f"Error: Section file not found: {section_file}")
            return False
        
        current_content = section_file.read_text()
        
        prompt = f"""Revise this {section} section based on feedback.

CURRENT CONTENT:
{current_content}

HUMAN FEEDBACK:
{feedback}

Provide REVISED version that addresses the feedback.
Keep good parts, improve weak parts.

Write ONLY the revised LaTeX content."""
        
        success, revised_content = self._call_claude(prompt, timeout=600)
        
        if success:
            # Backup old version
            backup = section_file.with_suffix('.tex.bak')
            backup.write_text(current_content)
            
            # Save revised
            section_file.write_text(revised_content)
            print(f"  ✓ Revised {section} (backup: {backup.name})")
            
            # Update task
            if section in self.tasks:
                self.tasks[section].revision_count += 1
                self.tasks[section].human_feedback = feedback
                self.tasks[section].content = revised_content
                self._save_tasks()
            
            return True
        else:
            self._escalate_to_human(f"{section}_revision", revised_content)
            return False


def main():
    """Autonomous writer CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Paper Writer")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--write-full",
        action="store_true",
        help="Write entire paper from outline"
    )
    parser.add_argument(
        "--section",
        type=str,
        help="Write specific section (introduction, theory, results, etc.)"
    )
    parser.add_argument(
        "--revise",
        type=str,
        help="Revise section with feedback from HUMAN_FEEDBACK.md"
    )
    parser.add_argument(
        "--outline",
        type=Path,
        help="Path to outline file (default: OUTLINE.md)"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Config not found: {args.config}")
        return 1
    
    config = PaperMaintenanceConfig.load(args.config)
    writer = AutonomousWriter(config)
    
    if args.write_full:
        success = writer.write_full_paper(args.outline)
        return 0 if success else 1
    
    elif args.section:
        outline = writer.outline_file.read_text() if writer.outline_file.exists() else ""
        success, content = writer.write_section(args.section, outline)
        return 0 if success else 1
    
    elif args.revise:
        if not writer.feedback_file.exists():
            print(f"Error: Feedback file not found: {writer.feedback_file}")
            print("Create HUMAN_FEEDBACK.md with your feedback")
            return 1
        
        feedback = writer.feedback_file.read_text()
        success = writer.revise_section(args.revise, feedback)
        return 0 if success else 1
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
