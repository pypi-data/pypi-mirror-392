#!/usr/bin/env python3
"""
Multi-Agent Brainstorming System
Simulates discussion between multiple experts at paper inception
Reads project goals from README and references from library/ folder
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import subprocess

from .config import PaperMaintenanceConfig
from .bibliography_manager import BibliographyManager


@dataclass
class Expert:
    """Expert persona for brainstorming"""
    name: str
    role: str
    perspective: str
    typical_concerns: List[str]


class BrainstormingSession:
    """Simulate multi-expert discussion"""
    
    EXPERTS = [
        Expert(
            name="Dr. Theory",
            role="Theoretical Physicist",
            perspective="Mathematical rigor and theoretical foundations",
            typical_concerns=[
                "Mathematical soundness",
                "Theoretical implications",
                "Connection to existing theory",
                "Hidden assumptions",
                "Fundamental insights"
            ]
        ),
        Expert(
            name="Dr. Experiment",
            role="Experimental Physicist",
            perspective="Practical implementation and verification",
            typical_concerns=[
                "Experimental verifiability",
                "Practical constraints",
                "Measurement feasibility",
                "Error analysis",
                "Current technology limits"
            ]
        ),
        Expert(
            name="Dr. Computation",
            role="Computational Physicist",
            perspective="Numerical methods and simulations",
            typical_concerns=[
                "Simulation feasibility",
                "Computational complexity",
                "Numerical verification",
                "Algorithm stability",
                "Parameter space"
            ]
        ),
        Expert(
            name="Dr. Impact",
            role="Research Strategist",
            perspective="Significance and publication potential",
            typical_concerns=[
                "Scientific significance",
                "Novel contribution",
                "Target audience",
                "Publication venue",
                "Broader impact"
            ]
        ),
        Expert(
            name="Dr. Skeptic",
            role="Critical Reviewer",
            perspective="Finding flaws and weaknesses",
            typical_concerns=[
                "Potential flaws",
                "Unstated assumptions",
                "Alternative explanations",
                "Limitations",
                "Competing approaches"
            ]
        ),
        Expert(
            name="Dr. Literature",
            role="Literature & Reference Specialist",
            perspective="Connecting ideas to existing research and references",
            typical_concerns=[
                "Related work in library",
                "Novel connections between references",
                "Gap identification in literature",
                "Reference-inspired ideas",
                "Building on existing knowledge"
            ]
        ),
    ]
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.session_file = self.project_dir / "brainstorming_session.md"
        self.manuscript_outline = self.project_dir / "content" / "manuscript_outline.md"
        self.library_dir = self.project_dir / "library"

    def _read_project_goals(self) -> Optional[str]:
        """Extract project goals from README.md"""
        readme_path = self.project_dir / "README.md"
        if not readme_path.exists():
            return None

        readme_content = readme_path.read_text()

        # Extract Project Goals section
        match = re.search(r'## Project Goals\s*\n(.*?)(?=\n##|\Z)', readme_content, re.DOTALL)
        if match:
            goals = match.group(1).strip()
            # Remove HTML comments
            goals = re.sub(r'<!--.*?-->', '', goals, flags=re.DOTALL)
            return goals.strip()
        return None

    def _read_library_references(self) -> List[Dict[str, str]]:
        """Read references from library/ folder"""
        library_dir = self.project_dir / "library"
        references = []

        if not library_dir.exists():
            return references

        # Find all PDF and HTML files
        for file_path in library_dir.glob("*"):
            if file_path.suffix.lower() in ['.pdf', '.html', '.htm']:
                references.append({
                    'filename': file_path.name,
                    'type': file_path.suffix[1:].upper(),
                    'path': str(file_path.relative_to(self.project_dir))
                })

        return references

    def _save_detailed_log(self, session: Dict) -> Path:
        """Save detailed brainstorming log with timestamp to library/"""
        # Ensure library directory exists
        self.library_dir.mkdir(exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"brainstorm_log_{timestamp}.md"
        log_path = self.library_dir / log_filename

        # Generate comprehensive log
        log_content = self._generate_detailed_log(session)

        # Write log file
        log_path.write_text(log_content)
        print(f"✓ Detailed log saved to: {log_path}")

        return log_path

    def _generate_detailed_log(self, session: Dict) -> str:
        """Generate detailed log content with full session information"""
        lines = [
            "# Detailed Brainstorming Session Log",
            "",
            f"**Session Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Target Journal:** {session['target_journal']}",
            "",
            "---",
            "",
            "## Session Overview",
            "",
            f"- **Participants:** {len(self.EXPERTS)} expert personas",
            f"- **References Available:** {len(session['references'])}",
            f"- **Discussion Rounds:** 3",
            "",
            "---",
            "",
            "## Research Idea",
            "",
            session['initial_idea'],
            "",
            "---",
            "",
            "## Available References",
            ""
        ]

        if session['references']:
            for ref in session['references']:
                lines.append(f"- **{ref['filename']}** ({ref['type']}) - `{ref['path']}`")
        else:
            lines.append("_(No references available)_")

        lines.extend([
            "",
            "---",
            "",
            "## Round 1: Initial Expert Reactions",
            "",
            "_Each expert provides their first impression of the research idea._",
            ""
        ])

        for expert in self.EXPERTS:
            name = expert.name
            if name in session['round1_reactions']:
                lines.extend([
                    f"### {name} ({expert.role})",
                    "",
                    f"**Perspective:** {expert.perspective}",
                    "",
                    session['round1_reactions'][name],
                    ""
                ])

        lines.extend([
            "---",
            "",
            "## Round 2: Probing Questions",
            "",
            "_Each expert asks critical questions that need answers._",
            ""
        ])

        for expert in self.EXPERTS:
            name = expert.name
            if name in session['round2_questions']:
                lines.extend([
                    f"### {name}",
                    ""
                ])
                for q in session['round2_questions'][name]:
                    lines.append(f"{q}")
                lines.append("")

        lines.extend([
            "---",
            "",
            "## Round 3: Synthesis & Strategic Recommendation",
            "",
            "### Expert Synthesis",
            "",
            session['round3_synthesis']['synthesis'],
            "",
            "### Final Recommendation",
            "",
            session['round3_synthesis']['recommendation'],
            "",
            "---",
            "",
            "## Action Items",
            "",
            "Based on this brainstorming session:",
            "",
            "- [ ] Address major concerns identified by experts",
            "- [ ] Answer critical questions from Round 2",
            "- [ ] Refine research plan based on synthesis",
            "- [ ] Review relevant references in library/",
            "- [ ] Update manuscript outline as needed",
            "",
            "---",
            "",
            f"_Log generated by TexForge Multi-Agent Brainstorming System_",
            f"_Timestamp: {session['timestamp']}_",
            ""
        ])

        return "\n".join(lines)

    def _update_readme_outline(self, session: Dict) -> None:
        """Update README.md with brainstorming session summary"""
        readme_path = self.project_dir / "README.md"

        if not readme_path.exists():
            print("⚠ README.md not found, skipping update")
            return

        readme_content = readme_path.read_text()

        # Create brainstorming summary section
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        summary_section = f"""

## Latest Brainstorming Session

**Date:** {timestamp}
**Status:** {self._extract_recommendation_status(session['round3_synthesis']['recommendation'])}

### Key Outcomes

{self._extract_key_points(session['round3_synthesis']['synthesis'])}

### Next Steps

See `brainstorming_session.md` and `library/brainstorm_log_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.md` for complete discussion.

---
"""

        # Check if brainstorming section already exists
        if "## Latest Brainstorming Session" in readme_content:
            # Replace existing section
            readme_content = re.sub(
                r'## Latest Brainstorming Session.*?(?=\n##|\Z)',
                summary_section.strip(),
                readme_content,
                flags=re.DOTALL
            )
        else:
            # Add new section before Project Goals or at end
            if "## Project Goals" in readme_content:
                readme_content = readme_content.replace(
                    "## Project Goals",
                    f"{summary_section}\n## Project Goals"
                )
            else:
                readme_content += "\n" + summary_section

        readme_path.write_text(readme_content)
        print(f"✓ README.md updated with brainstorming summary")

    def _extract_recommendation_status(self, recommendation: str) -> str:
        """Extract GO/NO-GO/REVISE status from recommendation"""
        recommendation_upper = recommendation.upper()
        if "GO" in recommendation_upper and "NO-GO" not in recommendation_upper:
            return "✓ GO - Proceed with research"
        elif "NO-GO" in recommendation_upper:
            return "✗ NO-GO - Reconsider approach"
        elif "REVISE" in recommendation_upper:
            return "⚠ REVISE - Modify approach recommended"
        else:
            return "Under review"

    def _extract_key_points(self, synthesis: str, max_points: int = 3) -> str:
        """Extract key bullet points from synthesis"""
        # Try to find existing bullet points or numbered lists
        lines = synthesis.split('\n')
        key_points = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('-', '*', '•')) or (stripped and stripped[0].isdigit() and '.' in stripped[:3]):
                key_points.append(f"- {stripped.lstrip('-*•0123456789. ')}")
                if len(key_points) >= max_points:
                    break

        if key_points:
            return '\n'.join(key_points)
        else:
            # If no bullets found, take first few sentences
            sentences = synthesis.split('. ')[:max_points]
            return '\n'.join([f"- {s.strip()}" for s in sentences if s.strip()])

    def _merge_library_bibliographies(self) -> None:
        """Merge all .bib and .bbl files from library/ into references.bib"""
        try:
            bib_manager = BibliographyManager(self.config)
            result = bib_manager.merge_library_bibliographies()

            if result['total'] > 0:
                print(f"  ✓ Merged {result['total']} bibliography entries from {len(result['sources'])} file(s)")
                if result['duplicates']:
                    print(f"  ⚠️  Removed {len(result['duplicates'])} duplicate entries")
            else:
                print("  ℹ️  No bibliography files found in library/")
        except Exception as e:
            print(f"  ⚠️  Could not merge bibliographies: {e}")

    def run_session(self, initial_idea: str = None, target_journal: str = "Physical Review A") -> Dict:
        """Run brainstorming session on initial idea"""

        print("🧠 Starting multi-agent brainstorming session...")
        print(f"Participants: {len(self.EXPERTS)} experts\n")

        # Read project goals and references
        print("📖 Reading project context...")
        project_goals = self._read_project_goals()
        references = self._read_library_references()

        if project_goals:
            print(f"  ✓ Found project goals in README.md")
        else:
            print(f"  ⚠ No project goals found in README.md")

        if references:
            print(f"  ✓ Found {len(references)} reference(s) in library/:")
            for ref in references:
                print(f"    - {ref['filename']} ({ref['type']})")
        else:
            print(f"  ⚠ No references found in library/")

        # Use project goals as initial idea if not provided
        if not initial_idea and project_goals:
            initial_idea = project_goals
            print(f"\n  Using project goals as research idea")
        elif not initial_idea:
            raise ValueError("No initial idea provided and no project goals found in README.md")

        print()

        # Round 1: Initial reactions
        print("Round 1: Initial Reactions")
        print("=" * 60)
        round1 = self._round_1_initial_reactions(initial_idea, references)
        
        # Round 2: Deep dive questions
        print("\nRound 2: Deep Dive Questions")
        print("=" * 60)
        round2 = self._round_2_deep_questions(initial_idea, round1)
        
        # Round 3: Synthesis and recommendations
        print("\nRound 3: Synthesis & Recommendations")
        print("=" * 60)
        round3 = self._round_3_synthesis(initial_idea, round1, round2, target_journal)
        
        # Compile full session
        session = {
            'timestamp': datetime.now().isoformat(),
            'initial_idea': initial_idea,
            'target_journal': target_journal,
            'project_goals': project_goals,
            'references': references,
            'round1_reactions': round1,
            'round2_questions': round2,
            'round3_synthesis': round3,
        }

        # Save session
        report = self._generate_report(session)
        self.session_file.write_text(report)
        print(f"\n✓ Session saved to: {self.session_file}")

        # Generate manuscript outline
        outline = self.generate_manuscript_outline(session, references)

        # Save detailed log with timestamp to library/
        print("\n📋 Saving detailed brainstorming log...")
        log_path = self._save_detailed_log(session)

        # Update README.md with brainstorming summary
        print("\n📝 Updating README.md with session summary...")
        self._update_readme_outline(session)

        # Merge bibliographies from library/ references
        print("\n📚 Merging bibliographies from library/...")
        self._merge_library_bibliographies()

        print("\n✅ Brainstorming session complete!")
        print(f"   - Full session: {self.session_file}")
        print(f"   - Detailed log: {log_path}")
        print(f"   - Manuscript outline: {self.manuscript_outline}")

        return session
    
    def _call_claude(self, prompt: str) -> str:
        """Call Claude for expert response"""
        try:
            result = subprocess.run(
                ["claude", "--dangerously-skip-permissions", "-p", prompt],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def _round_1_initial_reactions(self, idea: str, references: List[Dict]) -> Dict[str, str]:
        """Each expert gives initial reaction"""
        reactions = {}

        # Format references for context
        refs_context = ""
        if references:
            refs_list = "\n".join([f"  - {ref['filename']} ({ref['type']})" for ref in references])
            refs_context = f"\n\nAvailable reference materials in library/:\n{refs_list}\n\nNote: You may reference these materials in your response."

        for expert in self.EXPERTS:
            print(f"  {expert.name} ({expert.role})...")

            # Special prompt for Dr. Literature to actively engage with references
            if expert.name == "Dr. Literature":
                prompt = f"""You are {expert.name}, a {expert.role} with expertise in {expert.perspective}.

A colleague presents this research idea:
"{idea}"

Available reference materials in library/:
{refs_list if references else "  (No references available)"}

As the Literature & Reference Specialist, give your INITIAL REACTION focusing on:
- How does this idea connect to or build upon the available references?
- What gaps in the current literature (based on library/) does this address?
- What new ideas or approaches could emerge from combining insights from these references?
- If there are references, which ones seem most relevant and why?

Provide 2-3 sentences connecting the research idea to the existing knowledge base."""
            else:
                prompt = f"""You are {expert.name}, a {expert.role} with expertise in {expert.perspective}.

A colleague presents this research idea:
"{idea}"{refs_context}

Give your INITIAL REACTION (2-3 sentences):
- Is this interesting?
- What's your first thought?
- What immediately concerns you?
- If relevant, what references would help validate or inform this work?

Respond as {expert.name} would, from their perspective. Be direct and honest."""

            response = self._call_claude(prompt)
            reactions[expert.name] = response
            print(f"    → {response[:100]}...")

        return reactions
    
    def _round_2_deep_questions(self, idea: str, round1: Dict) -> Dict[str, List[str]]:
        """Each expert asks probing questions"""
        questions = {}

        for expert in self.EXPERTS:
            print(f"  {expert.name}...")

            # Compile what others said
            other_reactions = "\n".join([
                f"- {name}: {reaction}"
                for name, reaction in round1.items()
                if name != expert.name
            ])

            # Special prompt for Dr. Literature
            if expert.name == "Dr. Literature":
                prompt = f"""You are {expert.name}, a {expert.role}.

Research idea: "{idea}"

Your initial reaction: {round1[expert.name]}

Others' reactions:
{other_reactions}

As the Literature & Reference Specialist, ask 3-5 PROBING QUESTIONS that need answers before moving forward.
Focus on:
- What specific insights from the library references should inform this work?
- Are there related methodologies or results in the references that could be leveraged?
- What novel combinations or extensions of existing work are possible?
- What reference materials are missing that would strengthen this research?
- How can we ensure this work properly builds on and cites the existing literature?

List only the questions, numbered 1-5."""
            else:
                prompt = f"""You are {expert.name}, a {expert.role}.

Research idea: "{idea}"

Your initial reaction: {round1[expert.name]}

Others' reactions:
{other_reactions}

Now ask 3-5 PROBING QUESTIONS that need to be answered before moving forward.
Focus on {expert.perspective}.

List only the questions, numbered 1-5."""

            response = self._call_claude(prompt)

            # Parse questions
            question_list = []
            for line in response.split('\n'):
                if line.strip() and (line[0].isdigit() or line.startswith('-')):
                    question_list.append(line.strip())

            questions[expert.name] = question_list
            print(f"    → Asked {len(question_list)} questions")

        return questions
    
    def _round_3_synthesis(self, idea: str, round1: Dict, round2: Dict, 
                          target_journal: str) -> Dict:
        """Synthesize discussion and provide recommendations"""
        
        print("  Synthesizing discussion...")
        
        # Compile full discussion
        discussion = f"""Initial idea: {idea}

Round 1 reactions:
{self._format_dict(round1)}

Round 2 questions:
{self._format_questions(round2)}
"""
        
        prompt = f"""You are a senior research advisor facilitating this brainstorming session.

{discussion}

Target venue: {target_journal}

Provide a SYNTHESIS including:

1. **Core Strengths** (2-3 key strengths of this idea)
2. **Major Concerns** (2-3 critical issues that must be addressed)
3. **Research Plan** (suggested order of tasks)
4. **Success Criteria** (how to know if this will work)
5. **Publication Strategy** (is {target_journal} appropriate? why/why not?)

Be strategic and actionable."""
        
        synthesis = self._call_claude(prompt)
        
        # Also get recommendation
        prompt2 = f"""Based on this brainstorming session:

{discussion}

And synthesis:
{synthesis}

Give a clear GO/NO-GO/REVISE recommendation:
- GO: Proceed with this idea as planned
- NO-GO: Abandon this approach
- REVISE: Modify the approach (specify how)

Justify your recommendation in 2-3 sentences."""
        
        recommendation = self._call_claude(prompt2)
        
        return {
            'synthesis': synthesis,
            'recommendation': recommendation
        }
    
    def _format_dict(self, d: Dict) -> str:
        """Format dictionary for display"""
        return "\n".join([f"- {k}: {v}" for k, v in d.items()])

    def _format_questions(self, q: Dict[str, List[str]]) -> str:
        """Format questions for display"""
        lines = []
        for expert, questions in q.items():
            lines.append(f"\n{expert}:")
            for question in questions:
                lines.append(f"  {question}")
        return "\n".join(lines)

    def generate_manuscript_outline(self, session: Dict, references: List[Dict]) -> str:
        """Generate a detailed manuscript outline based on brainstorming session"""
        print("\n📝 Generating manuscript outline...")

        # Format references
        refs_list = ""
        if references:
            refs_list = "\n".join([f"  - {ref['filename']}" for ref in references])

        # Compile session context
        context = f"""Research Idea:
{session['initial_idea']}

Expert Synthesis:
{session['round3_synthesis']['synthesis']}

Recommendation:
{session['round3_synthesis']['recommendation']}

Available References in library/:
{refs_list if refs_list else "  (None)"}
"""

        prompt = f"""Based on this brainstorming session, create a DETAILED MANUSCRIPT OUTLINE.

{context}

Generate a comprehensive outline with the following sections:

## Introduction
- Motivation (why is this important?)
- Background (what's been done before?)
- Research question
- Our approach (high-level)
- Contributions (what's new?)

## Methods
- Theoretical framework
- Key equations/algorithms
- Implementation details
- Parameters and assumptions

## Results
- Main findings (list 3-5 key results)
- Validation approach
- Comparison with baselines/theory

## Discussion
- Interpretation of results
- Limitations
- Future work

## Conclusion
- Summary of contributions
- Broader impact

For each section, provide:
1. 2-3 bullet points of what should be covered
2. If references from library/ are relevant, mention which ones

Format as clean markdown with clear hierarchy."""

        outline = self._call_claude(prompt)

        # Save outline
        self.manuscript_outline.write_text(outline)
        print(f"✓ Manuscript outline saved to: {self.manuscript_outline}")

        return outline

    def _generate_report(self, session: Dict) -> str:
        """Generate markdown report of session"""
        lines = [
            "# Multi-Agent Brainstorming Session",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Target Journal:** {session['target_journal']}",
            "",
            "---",
            "",
            "## Initial Research Idea",
            "",
            session['initial_idea'],
            "",
            "---",
            "",
            "## Round 1: Initial Reactions",
            ""
        ]
        
        for expert in self.EXPERTS:
            name = expert.name
            if name in session['round1_reactions']:
                lines.extend([
                    f"### {name} ({expert.role})",
                    "",
                    session['round1_reactions'][name],
                    ""
                ])
        
        lines.extend([
            "---",
            "",
            "## Round 2: Probing Questions",
            ""
        ])
        
        for expert in self.EXPERTS:
            name = expert.name
            if name in session['round2_questions']:
                lines.extend([
                    f"### {name}",
                    ""
                ])
                for q in session['round2_questions'][name]:
                    lines.append(f"- {q}")
                lines.append("")
        
        lines.extend([
            "---",
            "",
            "## Round 3: Synthesis & Recommendation",
            "",
            "### Synthesis",
            "",
            session['round3_synthesis']['synthesis'],
            "",
            "### Recommendation",
            "",
            session['round3_synthesis']['recommendation'],
            "",
            "---",
            "",
            "## Next Steps",
            "",
            "Based on this discussion:",
            "- [ ] Address major concerns identified",
            "- [ ] Answer critical questions from experts",
            "- [ ] Refine research plan based on synthesis",
            "- [ ] Create detailed OUTLINE.md",
            ""
        ])

        return "\n".join(lines)


def main():
    """Brainstorming CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent Brainstorming")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--idea",
        type=str,
        required=True,
        help="Initial research idea (quote-wrapped)"
    )
    parser.add_argument(
        "--journal",
        type=str,
        default="Physical Review A",
        help="Target journal"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Config not found: {args.config}")
        return 1
    
    config = PaperMaintenanceConfig.load(args.config)
    session = BrainstormingSession(config)
    
    session.run_session(args.idea, args.journal)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
