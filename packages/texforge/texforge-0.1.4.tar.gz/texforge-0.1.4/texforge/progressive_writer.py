#!/usr/bin/env python3
"""
Progressive Paper Development System
Guides paper from rough idea to submission-ready manuscript
Prevents going off-track with milestone checking
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

from .config import PaperMaintenanceConfig


class PaperStage(Enum):
    """Stages of paper development"""
    IDEA = "idea"                      # Initial concept
    OUTLINE = "outline"                # Structured outline
    DRAFT = "draft"                    # First draft
    REVISION = "revision"              # Revisions in progress
    POLISHING = "polishing"            # Final polish
    SUBMISSION_READY = "submission"    # Ready to submit


@dataclass
class Milestone:
    """Paper development milestone"""
    name: str
    stage: PaperStage
    completed: bool = False
    completion_date: Optional[datetime] = None
    notes: str = ""
    
    # Criteria for completion
    criteria: List[str] = field(default_factory=list)
    

@dataclass
class PaperOutline:
    """Structured paper outline"""
    title: str = ""
    abstract_points: List[str] = field(default_factory=list)
    
    # Main sections
    introduction_points: List[str] = field(default_factory=list)
    background_points: List[str] = field(default_factory=list)
    methods_points: List[str] = field(default_factory=list)
    results_points: List[str] = field(default_factory=list)
    discussion_points: List[str] = field(default_factory=list)
    conclusion_points: List[str] = field(default_factory=list)
    
    # Key claims and contributions
    main_claims: List[str] = field(default_factory=list)
    novel_contributions: List[str] = field(default_factory=list)
    
    # Target venue
    target_journal: str = "Physical Review A"  # or "Physical Review Letters"
    page_limit: int = 20  # PRA: 10-20, PRL: ~5


@dataclass
class DirectionCheck:
    """Check to ensure paper stays on track"""
    timestamp: datetime
    stage: PaperStage
    
    # Alignment checks
    title_matches_content: bool = True
    claims_supported: bool = True
    outline_followed: bool = True
    scope_appropriate: bool = True
    
    # Issues found
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    # Metrics
    total_sections: int = 0
    completed_sections: int = 0
    current_page_count: int = 0
    
    @property
    def is_on_track(self) -> bool:
        """Check if paper is on track"""
        return (self.title_matches_content and 
                self.claims_supported and 
                self.outline_followed and 
                self.scope_appropriate and
                len(self.issues) == 0)


class ProgressiveWriter:
    """Manage progressive paper development"""
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.progress_file = self.project_dir / ".paper-progress.json"
        self.outline_file = self.project_dir / "OUTLINE.md"
        
        self.outline = self._load_outline()
        self.milestones = self._initialize_milestones()
        self.current_stage = self._determine_current_stage()
    
    def _load_outline(self) -> PaperOutline:
        """Load or create paper outline"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                outline_data = data.get('outline', {})
                return PaperOutline(**outline_data)
        return PaperOutline()
    
    def _save_progress(self) -> None:
        """Save progress to file"""
        data = {
            'outline': self.outline.__dict__,
            'milestones': [m.__dict__ for m in self.milestones],
            'current_stage': self.current_stage.value,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _initialize_milestones(self) -> List[Milestone]:
        """Initialize paper development milestones"""
        return [
            Milestone(
                name="Define Research Question",
                stage=PaperStage.IDEA,
                criteria=[
                    "Clear research question stated",
                    "Gap in literature identified",
                    "Novelty articulated"
                ]
            ),
            Milestone(
                name="Create Detailed Outline",
                stage=PaperStage.OUTLINE,
                criteria=[
                    "All main sections outlined",
                    "Key claims identified",
                    "Main results planned",
                    "OUTLINE.md file created"
                ]
            ),
            Milestone(
                name="Complete Introduction",
                stage=PaperStage.DRAFT,
                criteria=[
                    "Motivation clear",
                    "Literature review done",
                    "Contributions stated"
                ]
            ),
            Milestone(
                name="Complete Methods/Theory",
                stage=PaperStage.DRAFT,
                criteria=[
                    "Methods clearly described",
                    "Notation defined",
                    "Approach justified"
                ]
            ),
            Milestone(
                name="Complete Results",
                stage=PaperStage.DRAFT,
                criteria=[
                    "All results presented",
                    "Figures generated",
                    "Tables completed",
                    "Main claims supported"
                ]
            ),
            Milestone(
                name="Complete Discussion/Conclusion",
                stage=PaperStage.DRAFT,
                criteria=[
                    "Results interpreted",
                    "Implications discussed",
                    "Limitations acknowledged",
                    "Future work mentioned"
                ]
            ),
            Milestone(
                name="First Complete Draft",
                stage=PaperStage.DRAFT,
                criteria=[
                    "All sections written",
                    "Compiles without errors",
                    "References complete",
                    "Abstract written"
                ]
            ),
            Milestone(
                name="Major Revisions Complete",
                stage=PaperStage.REVISION,
                criteria=[
                    "Structural issues fixed",
                    "Arguments strengthened",
                    "Gaps filled",
                    "Flow improved"
                ]
            ),
            Milestone(
                name="Content Complete",
                stage=PaperStage.POLISHING,
                criteria=[
                    "All revisions incorporated",
                    "No TODOs remaining",
                    "Length appropriate",
                    "Quality checks pass"
                ]
            ),
            Milestone(
                name="Submission Ready",
                stage=PaperStage.SUBMISSION_READY,
                criteria=[
                    "Journal format followed",
                    "All author approvals",
                    "Cover letter prepared",
                    "Meets submission requirements"
                ]
            ),
        ]
    
    def _determine_current_stage(self) -> PaperStage:
        """Determine current stage based on completed milestones"""
        if not self.progress_file.exists():
            return PaperStage.IDEA
        
        # Find highest completed stage
        completed_stages = [
            m.stage for m in self.milestones if m.completed
        ]
        
        if not completed_stages:
            return PaperStage.IDEA
        
        # Return next stage after highest completed
        stage_order = list(PaperStage)
        max_completed = max(completed_stages, key=lambda s: stage_order.index(s))
        max_index = stage_order.index(max_completed)
        
        if max_index < len(stage_order) - 1:
            return stage_order[max_index + 1]
        return PaperStage.SUBMISSION_READY
    
    def check_direction(self) -> DirectionCheck:
        """Check if paper is going in the right direction"""
        check = DirectionCheck(
            timestamp=datetime.now(),
            stage=self.current_stage
        )
        
        # Analyze paper content using Claude
        from auto_maintain_paper import PaperMaintenance
        
        maintenance = PaperMaintenance(self.config, verbose=False)
        
        # Check title alignment
        if self.outline.title:
            result = maintenance.run_claude_check(
                f"""Analyze if the paper content matches the title:
                Title: "{self.outline.title}"
                
                Check:
                1. Does the content address what the title promises?
                2. Is the scope appropriate for the title?
                3. Are we staying focused or drifting off-topic?
                
                Respond with: ALIGNED or MISALIGNED
                If misaligned, explain the discrepancy.""",
                "Title alignment check"
            )
            check.title_matches_content = "ALIGNED" in result.message if result.message else True
        
        # Check if claims are supported
        if self.outline.main_claims:
            claims_text = "\n".join(f"- {claim}" for claim in self.outline.main_claims)
            result = maintenance.run_claude_check(
                f"""Verify main claims are supported:
                
                Claimed contributions:
                {claims_text}
                
                Check:
                1. Are these claims substantiated in the Results?
                2. Is there sufficient evidence?
                3. Are claims overstated?
                
                Respond with: SUPPORTED or UNSUPPORTED
                List any unsupported claims.""",
                "Claims verification"
            )
            check.claims_supported = "SUPPORTED" in result.message if result.message else True
        
        # Check outline adherence
        if self.outline_file.exists():
            result = maintenance.run_claude_check(
                f"""Compare current draft with original outline in OUTLINE.md:
                
                Check:
                1. Are we following the planned structure?
                2. Have we deviated from the outline?
                3. Are deviations justified?
                
                Respond with: FOLLOWING or DEVIATED
                Explain any major deviations.""",
                "Outline adherence check"
            )
            check.outline_followed = "FOLLOWING" in result.message if result.message else True
        
        # Check scope
        result = maintenance.run_claude_check(
            f"""Assess paper scope for {self.outline.target_journal}:
            Target: {self.outline.target_journal} ({self.outline.page_limit} pages)
            
            Check:
            1. Is the scope appropriate for target venue?
            2. Is it too broad or too narrow?
            3. Can it fit within page limit?
            4. Is novelty sufficient for this venue?
            
            Respond with: APPROPRIATE or INAPPROPRIATE
            Provide specific concerns.""",
            "Scope check"
        )
        check.scope_appropriate = "APPROPRIATE" in result.message if result.message else True
        
        # Get section completion status
        result = maintenance.run_claude_check(
            """Count sections and their completion status:
            
            For each main section (Introduction, Methods/Theory, Results, Discussion, Conclusion):
            - Is it started?
            - Is it substantially complete?
            - What's missing?
            
            Format: COMPLETED: X/Y sections
            List incomplete sections.""",
            "Section completion check"
        )
        
        # Extract metrics from result
        if result.message:
            import re
            match = re.search(r'COMPLETED:\s*(\d+)/(\d+)', result.message)
            if match:
                check.completed_sections = int(match.group(1))
                check.total_sections = int(match.group(2))
        
        # Get page count
        try:
            import subprocess
            # Count pages from PDF if available
            pdf_files = list(self.project_dir.glob("*.pdf"))
            if pdf_files:
                result = subprocess.run(
                    ["pdfinfo", str(pdf_files[0])],
                    capture_output=True,
                    text=True
                )
                match = re.search(r'Pages:\s*(\d+)', result.stdout)
                if match:
                    check.current_page_count = int(match.group(1))
        except:
            pass
        
        # Collect issues, warnings, suggestions
        if not check.title_matches_content:
            check.issues.append("Paper content does not match title - refocus or retitle")
        
        if not check.claims_supported:
            check.issues.append("Main claims are not fully supported - add evidence or revise claims")
        
        if not check.outline_followed:
            check.warnings.append("Paper deviates from original outline - verify this is intentional")
        
        if not check.scope_appropriate:
            check.issues.append(f"Scope may not be appropriate for {self.outline.target_journal}")
        
        if check.current_page_count > self.outline.page_limit:
            check.warnings.append(
                f"Page count ({check.current_page_count}) exceeds target ({self.outline.page_limit})"
            )
        
        # Stage-specific suggestions
        if self.current_stage == PaperStage.DRAFT:
            check.suggestions.append("Focus on completing all sections before polishing")
            if check.completed_sections < check.total_sections:
                check.suggestions.append(
                    f"Complete remaining {check.total_sections - check.completed_sections} sections"
                )
        
        elif self.current_stage == PaperStage.REVISION:
            check.suggestions.append("Address structural issues before fine-tuning language")
            check.suggestions.append("Ensure all claims are well-supported")
        
        elif self.current_stage == PaperStage.POLISHING:
            check.suggestions.append("Focus on clarity, consistency, and presentation")
            check.suggestions.append("Run comprehensive quality checks")
        
        return check
    
    def generate_progress_report(self) -> str:
        """Generate progress report"""
        lines = ["# Paper Development Progress", ""]
        
        # Header
        lines.append(f"**Project:** {self.outline.title or 'Untitled'}")
        lines.append(f"**Target:** {self.outline.target_journal}")
        lines.append(f"**Current Stage:** {self.current_stage.value.title()}")
        lines.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        
        # Milestones
        lines.append("## Milestones")
        lines.append("")
        
        for milestone in self.milestones:
            status = "✅" if milestone.completed else "⬜"
            lines.append(f"### {status} {milestone.name}")
            lines.append(f"**Stage:** {milestone.stage.value}")
            
            if milestone.completed:
                lines.append(f"**Completed:** {milestone.completion_date.strftime('%Y-%m-%d')}")
            else:
                lines.append("**Status:** In Progress" if milestone.stage == self.current_stage else "Pending")
            
            lines.append("")
            lines.append("**Criteria:**")
            for criterion in milestone.criteria:
                lines.append(f"- {criterion}")
            
            if milestone.notes:
                lines.append(f"\n**Notes:** {milestone.notes}")
            
            lines.append("")
        
        # Direction check
        lines.append("## Direction Check")
        lines.append("")
        
        check = self.check_direction()
        
        if check.is_on_track:
            lines.append("✅ **Status:** On Track")
        else:
            lines.append("⚠️ **Status:** Needs Attention")
        
        lines.append("")
        lines.append(f"- Title alignment: {'✓' if check.title_matches_content else '✗'}")
        lines.append(f"- Claims supported: {'✓' if check.claims_supported else '✗'}")
        lines.append(f"- Following outline: {'✓' if check.outline_followed else '✗'}")
        lines.append(f"- Scope appropriate: {'✓' if check.scope_appropriate else '✗'}")
        lines.append("")
        
        if check.current_page_count > 0:
            lines.append(f"**Pages:** {check.current_page_count}/{self.outline.page_limit}")
        
        if check.total_sections > 0:
            lines.append(f"**Sections:** {check.completed_sections}/{check.total_sections} complete")
        
        lines.append("")
        
        # Issues
        if check.issues:
            lines.append("### 🚨 Issues")
            lines.append("")
            for issue in check.issues:
                lines.append(f"- {issue}")
            lines.append("")
        
        # Warnings
        if check.warnings:
            lines.append("### ⚠️ Warnings")
            lines.append("")
            for warning in check.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        # Suggestions
        if check.suggestions:
            lines.append("### 💡 Suggestions")
            lines.append("")
            for suggestion in check.suggestions:
                lines.append(f"- {suggestion}")
            lines.append("")
        
        # Next steps
        lines.append("## Next Steps")
        lines.append("")
        
        next_milestone = next((m for m in self.milestones if not m.completed), None)
        if next_milestone:
            lines.append(f"**Current milestone:** {next_milestone.name}")
            lines.append("")
            lines.append("**To complete:**")
            for criterion in next_milestone.criteria:
                lines.append(f"- [ ] {criterion}")
        else:
            lines.append("✅ All milestones complete!")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def create_outline_template(self) -> str:
        """Create OUTLINE.md template"""
        template = f"""# Paper Outline: {self.outline.title or '[Title]'}

**Target Venue:** {self.outline.target_journal}
**Page Limit:** {self.outline.page_limit} pages

---

## Abstract (150-200 words)

Key points to cover:
- [ ] Problem/motivation
- [ ] Approach
- [ ] Key results
- [ ] Implications

---

## Introduction

### Motivation
- Why is this problem important?
- What gap does it fill?

### Background
- Essential concepts
- Related work

### Our Contribution
Main claims:
{chr(10).join(f'- {claim}' for claim in self.outline.main_claims) if self.outline.main_claims else '- [Claim 1]\n- [Claim 2]'}

Novel aspects:
{chr(10).join(f'- {contrib}' for contrib in self.outline.novel_contributions) if self.outline.novel_contributions else '- [Novel aspect 1]\n- [Novel aspect 2]'}

---

## Methods/Theory

- Mathematical framework
- Approach description
- Justification

---

## Results

Main findings:
- Result 1: [Description]
- Result 2: [Description]
- Result 3: [Description]

Figures/Tables:
- Figure 1: [Description]
- Figure 2: [Description]

---

## Discussion

- Interpretation of results
- Comparison with literature
- Implications
- Limitations

---

## Conclusion

- Summary of findings
- Impact
- Future directions

---

## Notes

**Key References:**
- [Paper 1]
- [Paper 2]
- [Paper 3]

**Potential Issues:**
- [Issue 1]

**Open Questions:**
- [Question 1]
"""
        return template


def main():
    """Progressive paper development CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Progressive Paper Development")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize paper development tracking"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show progress status"
    )
    parser.add_argument(
        "--check-direction",
        action="store_true",
        help="Check if paper is on track"
    )
    parser.add_argument(
        "--create-outline",
        action="store_true",
        help="Create OUTLINE.md template"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Config not found: {args.config}")
        return 1
    
    config = PaperMaintenanceConfig.load(args.config)
    writer = ProgressiveWriter(config)
    
    if args.init:
        print("Initializing paper development tracking...")
        writer._save_progress()
        print(f"✓ Created {writer.progress_file}")
        
        if args.create_outline or not writer.outline_file.exists():
            outline_content = writer.create_outline_template()
            writer.outline_file.write_text(outline_content)
            print(f"✓ Created {writer.outline_file}")
        
        print("\nEdit OUTLINE.md to define your paper structure, then run:")
        print("  python3 progressive_writer.py --status")
    
    elif args.status:
        report = writer.generate_progress_report()
        print(report)
        
        # Save report
        report_file = writer.project_dir / "PROGRESS.md"
        report_file.write_text(report)
        print(f"\n✓ Saved to {report_file}")
    
    elif args.check_direction:
        check = writer.check_direction()
        
        if check.is_on_track:
            print("✅ Paper is on track!")
        else:
            print("⚠️ Paper needs attention")
        
        if check.issues:
            print("\nIssues:")
            for issue in check.issues:
                print(f"  - {issue}")
        
        if check.suggestions:
            print("\nSuggestions:")
            for suggestion in check.suggestions:
                print(f"  - {suggestion}")
    
    elif args.create_outline:
        outline_content = writer.create_outline_template()
        writer.outline_file.write_text(outline_content)
        print(f"✓ Created {writer.outline_file}")
        print("\nEdit this file to define your paper structure")
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
