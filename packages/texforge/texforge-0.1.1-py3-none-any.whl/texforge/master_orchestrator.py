#!/usr/bin/env python3
"""
Master Orchestrator
Runs the complete autonomous paper writing pipeline
"""
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import time

from .config import PaperMaintenanceConfig
from brainstorming import BrainstormingSession
from autonomous_writer import AutonomousWriter
from simulation_agent import DualSimulationAgent
from figure_agent import FigureGenerationAgent
from progressive_writer import ProgressiveWriter
from peer_review import PeerReviewSimulation
from pdf_compiler import PDFCompiler
from bibliography_manager import BibliographyManager


class MasterOrchestrator:
    """Orchestrate complete paper writing pipeline"""
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.log_file = self.project_dir / "orchestrator.log"
        
        # Initialize all agents
        self.brainstormer = BrainstormingSession(config)
        self.writer = AutonomousWriter(config)
        self.simulator = DualSimulationAgent(config)
        self.figure_agent = FigureGenerationAgent(config)
        self.progress_tracker = ProgressiveWriter(config)
        self.peer_reviewer = PeerReviewSimulation(config)
        self.compiler = PDFCompiler(config)
        self.bib_manager = BibliographyManager(config)
        
        self.start_time = datetime.now()
    
    def log(self, message: str) -> None:
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        print(log_line.strip())
        
        with open(self.log_file, 'a') as f:
            f.write(log_line)
    
    def run_complete_pipeline(self, initial_idea: str, target_journal: str = "Physical Review A") -> bool:
        """
        Run complete pipeline from idea to submission-ready paper
        
        Returns: True if successful, False if human intervention needed
        """
        
        self.log("="*70)
        self.log("AUTONOMOUS PAPER WRITING PIPELINE")
        self.log("="*70)
        self.log(f"Initial idea: {initial_idea[:100]}...")
        self.log(f"Target journal: {target_journal}")
        self.log("")
        
        # PHASE 1: Brainstorming
        self.log("PHASE 1: Multi-Agent Brainstorming")
        self.log("-"*70)
        
        try:
            session = self.brainstormer.run_session(initial_idea, target_journal)
            
            # Check recommendation
            recommendation = session['round3_synthesis']['recommendation']
            
            if "NO-GO" in recommendation.upper():
                self.log("⚠️  Brainstorming recommendation: NO-GO")
                self.log("Human decision needed. See brainstorming_session.md")
                return False
            
            self.log("✓ Brainstorming complete - GO decision")
            
        except Exception as e:
            self.log(f"✗ Brainstorming failed: {e}")
            return False
        
        # PHASE 2: Setup
        self.log("\nPHASE 2: Project Setup")
        self.log("-"*70)
        
        try:
            # Initialize tracking
            self.progress_tracker._save_progress()
            self.log("✓ Initialized progress tracking")
            
            # Setup template
            journal_key = "prl" if "PRL" in target_journal or "Letters" in target_journal else "pra"
            self.compiler.setup_template(journal_key)
            self.log(f"✓ Setup {journal_key.upper()} template")
            
            # Setup macros
            self.compiler.setup_macros(include_common=True)
            self.log("✓ Setup macros.tex")
            
            # Create outline from brainstorming
            self._create_outline_from_brainstorming(session, target_journal)
            self.log("✓ Created OUTLINE.md")
            
        except Exception as e:
            self.log(f"✗ Setup failed: {e}")
            return False
        
        # PHASE 3: Content Generation
        self.log("\nPHASE 3: Autonomous Content Generation")
        self.log("-"*70)
        
        try:
            success = self.writer.write_full_paper()
            
            if not success:
                self.log("⚠️  Content generation incomplete")
                self.log("Check ESCALATIONS.md for issues needing human input")
                return False
            
            self.log("✓ All sections written")
            
        except Exception as e:
            self.log(f"✗ Content generation failed: {e}")
            return False
        
        # PHASE 4: Figure Generation (at 50% progress)
        self.log("\nPHASE 4: Figure Generation")
        self.log("-"*70)
        
        try:
            progress = self.figure_agent.check_progress()
            self.log(f"Current progress: {progress*100:.1f}%")
            
            if progress >= 0.45:
                # Read outline for figure specs
                figure_specs = self._extract_figure_specs()
                
                if figure_specs:
                    results = self.figure_agent.generate_all_figures(figure_specs)
                    successful = sum(1 for s, _ in results.values() if s)
                    self.log(f"✓ Generated {successful}/{len(figure_specs)} figures")
                else:
                    self.log("No figures specified in outline")
            else:
                self.log("Skipping (progress < 45%)")
                
        except Exception as e:
            self.log(f"⚠️  Figure generation failed: {e}")
            # Continue anyway - figures can be added manually
        
        # PHASE 5: Numerical Simulations (if specified)
        self.log("\nPHASE 5: Numerical Simulations")
        self.log("-"*70)
        
        try:
            sim_tasks = self._extract_simulation_tasks()
            
            if sim_tasks:
                all_verified = True
                
                for task_name, task_desc in sim_tasks.items():
                    self.log(f"Running: {task_name}")
                    
                    verification = self.simulator.run_dual_simulation(
                        task_desc, 
                        params={}  # Extract from paper
                    )
                    
                    if verification.match:
                        self.log(f"  ✓ Verified (diff: {verification.max_difference:.2e})")
                    else:
                        self.log(f"  ✗ Mismatch: {verification.details}")
                        all_verified = False
                
                if not all_verified:
                    self.log("⚠️  Some simulations failed verification")
                    self.log("Human review needed. See simulations/verification.log")
                    return False
                    
            else:
                self.log("No simulations specified")
                
        except Exception as e:
            self.log(f"⚠️  Simulation failed: {e}")
            # Continue - simulations can be done manually
        
        # PHASE 6: Bibliography Verification
        self.log("\nPHASE 6: Bibliography Verification")
        self.log("-"*70)
        
        try:
            report = self.bib_manager.generate_report()
            
            # Save report
            bib_report_file = self.project_dir / "bibliography_report.md"
            bib_report_file.write_text(report)
            
            # Check for issues
            if "Missing Bibliography Entries" in report:
                self.log("⚠️  Missing .bib entries detected")
            
            if "Low-Impact Citations" in report:
                self.log("⚠️  Some citations have low impact")
            
            self.log("✓ Bibliography analyzed")
            self.log(f"See: {bib_report_file}")
            
        except Exception as e:
            self.log(f"⚠️  Bibliography check failed: {e}")
        
        # PHASE 7: Compilation
        self.log("\nPHASE 7: PDF Compilation")
        self.log("-"*70)
        
        try:
            result = self.compiler.compile(clean=True)
            
            if result.success:
                self.log(f"✓ PDF compiled successfully")
                self.log(f"  Pages: {result.pages}")
                self.log(f"  Time: {result.compile_time:.1f}s")
                self.log(f"  Output: {result.pdf_path}")
            else:
                self.log("✗ Compilation failed")
                for error in result.errors[:5]:
                    self.log(f"  {error}")
                
                # Try to fix
                self.log("Attempting auto-fix...")
                fixes = self.compiler.fix_common_errors()
                
                if fixes:
                    for fix in fixes:
                        self.log(f"  Applied: {fix}")
                    
                    # Retry
                    result = self.compiler.compile(clean=True)
                    if result.success:
                        self.log("✓ Fixed and recompiled successfully")
                    else:
                        self.log("✗ Still failing - human intervention needed")
                        return False
                else:
                    return False
                    
        except Exception as e:
            self.log(f"✗ Compilation failed: {e}")
            return False
        
        # PHASE 8: Direction Check
        self.log("\nPHASE 8: Direction Check")
        self.log("-"*70)
        
        try:
            check = self.progress_tracker.check_direction()
            
            if check.is_on_track:
                self.log("✓ Paper is on track")
            else:
                self.log("⚠️  Paper has issues:")
                for issue in check.issues:
                    self.log(f"  - {issue}")
                
                self.log("Human review recommended")
                
        except Exception as e:
            self.log(f"⚠️  Direction check failed: {e}")
        
        # PHASE 9: Peer Review Simulation
        self.log("\nPHASE 9: Peer Review Simulation")
        self.log("-"*70)
        
        try:
            main_tex = self.project_dir / "main.tex"
            reviews = self.peer_reviewer.simulate_review(main_tex, target_journal)
            
            if reviews:
                avg_rating = sum(r.rating_significance for r in reviews) / len(reviews)
                self.log(f"✓ Simulated {len(reviews)} peer reviews")
                self.log(f"  Average significance: {avg_rating:.1f}/5")
                
                # Check recommendations
                recommendations = [r.recommendation for r in reviews]
                if any("Reject" in r for r in recommendations):
                    self.log("⚠️  At least one reviewer recommends rejection")
                    self.log("Major revisions needed. See peer_reviews.md")
                    return False
            else:
                self.log("✗ Peer review simulation failed")
                
        except Exception as e:
            self.log(f"⚠️  Peer review failed: {e}")
        
        # FINAL SUMMARY
        elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        
        self.log("\n" + "="*70)
        self.log("PIPELINE COMPLETE")
        self.log("="*70)
        self.log(f"Total time: {elapsed:.1f} hours")
        self.log(f"Output: {result.pdf_path if result.success else 'N/A'}")
        self.log("")
        self.log("Next steps:")
        self.log("1. Review paper manually")
        self.log("2. Address any escalations in ESCALATIONS.md")
        self.log("3. Review peer review feedback in peer_reviews.md")
        self.log("4. Make final adjustments")
        self.log("5. Submit to journal!")
        self.log("="*70)
        
        return True
    
    def _create_outline_from_brainstorming(self, session: Dict, journal: str) -> None:
        """Create OUTLINE.md from brainstorming results"""
        
        synthesis = session['round3_synthesis']['synthesis']
        
        outline_content = f"""# Paper Outline

**Generated from brainstorming session**
**Target Journal:** {journal}
**Date:** {datetime.now().strftime('%Y-%m-%d')}

---

## Initial Idea

{session['initial_idea']}

---

## Key Insights from Brainstorming

{synthesis}

---

## Paper Structure

### Abstract
[To be written - summarize motivation, approach, results, impact]

### Introduction
- Motivation and context
- Literature review
- Gap identification
- Our contributions

### Theory/Methods
- Mathematical framework
- Key assumptions
- Main theoretical results

### Results
- Numerical simulations
- Comparisons with theory
- Key findings

### Discussion
- Interpretation
- Limitations
- Future work

### Conclusion
- Summary of contributions
- Broader impact

---

## Figures Needed
1. Main idea illustration (generate at 50% progress)
2. Results plots (from simulations)
3. [Add more as needed]

---

## Notes

See full brainstorming discussion in: brainstorming_session.md
"""
        
        outline_file = self.project_dir / "OUTLINE.md"
        outline_file.write_text(outline_content)
    
    def _extract_figure_specs(self) -> Dict[str, str]:
        """Extract figure specifications from outline/paper"""
        # Simplified - in practice would parse OUTLINE.md
        return {
            "main_idea": "Illustrate the main concept of the paper"
        }
    
    def _extract_simulation_tasks(self) -> Dict[str, str]:
        """Extract simulation tasks from paper content"""
        # Simplified - in practice would parse results section
        return {}


def main():
    """Orchestrator CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Master Paper Writing Orchestrator")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--idea",
        type=str,
        required=True,
        help="Initial research idea"
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
    orchestrator = MasterOrchestrator(config)
    
    success = orchestrator.run_complete_pipeline(args.idea, args.journal)
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
