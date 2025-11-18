#!/usr/bin/env python3
"""
Multi-Agent Brainstorming System
Simulates discussion between multiple experts at paper inception
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass
import subprocess

from .config import PaperMaintenanceConfig


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
    ]
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.session_file = self.project_dir / "brainstorming_session.md"
    
    def run_session(self, initial_idea: str, target_journal: str = "Physical Review A") -> Dict:
        """Run brainstorming session on initial idea"""
        
        print("🧠 Starting multi-agent brainstorming session...")
        print(f"Participants: {len(self.EXPERTS)} experts\n")
        
        # Round 1: Initial reactions
        print("Round 1: Initial Reactions")
        print("=" * 60)
        round1 = self._round_1_initial_reactions(initial_idea)
        
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
            'round1_reactions': round1,
            'round2_questions': round2,
            'round3_synthesis': round3,
        }
        
        # Save session
        report = self._generate_report(session)
        self.session_file.write_text(report)
        print(f"\n✓ Session saved to: {self.session_file}")
        
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
    
    def _round_1_initial_reactions(self, idea: str) -> Dict[str, str]:
        """Each expert gives initial reaction"""
        reactions = {}
        
        for expert in self.EXPERTS:
            print(f"  {expert.name} ({expert.role})...")
            
            prompt = f"""You are {expert.name}, a {expert.role} with expertise in {expert.perspective}.

A colleague presents this research idea:
"{idea}"

Give your INITIAL REACTION (2-3 sentences):
- Is this interesting?
- What's your first thought?
- What immediately concerns you?

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
        ]
        
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
