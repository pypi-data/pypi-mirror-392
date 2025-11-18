#!/usr/bin/env python3
"""
Figure Generation Agent
Creates illustrative figures at 50% paper progress
Uses matplotlib for plots and diagrams
"""
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

from .config import PaperMaintenanceConfig
from progressive_writer import ProgressiveWriter


class FigureGenerationAgent:
    """Generate illustrative figures for paper"""
    
    MAX_RETRIES = 3
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.figures_dir = self.project_dir / "figures"
        self.figures_dir.mkdir(exist_ok=True)
        
        self.figure_script_dir = self.project_dir / "figure_scripts"
        self.figure_script_dir.mkdir(exist_ok=True)
    
    def check_progress(self) -> float:
        """Check paper progress percentage"""
        writer = ProgressiveWriter(self.config)
        
        # Count completed milestones
        completed = sum(1 for m in writer.milestones if m.completed)
        total = len(writer.milestones)
        
        return completed / total if total > 0 else 0.0
    
    def should_generate_figures(self) -> bool:
        """Check if we're at 50% progress"""
        progress = self.check_progress()
        return 0.45 <= progress <= 0.60  # 45-60% range
    
    def generate_illustrative_figure(self, figure_description: str,
                                    figure_name: str = "main_idea") -> Tuple[bool, Optional[Path]]:
        """
        Generate illustrative figure for main paper idea
        
        Args:
            figure_description: What the figure should show
            figure_name: Filename (without extension)
        
        Returns:
            (success, figure_path)
        """
        
        print(f"\n🎨 Generating figure: {figure_name}")
        print(f"Description: {figure_description[:100]}...")
        
        # Read paper content for context
        context = self._read_paper_context()
        
        # Generate plotting code
        success, plot_code = self._generate_plot_code(
            figure_description, context
        )
        
        if not success:
            print(f"  ❌ Failed to generate code")
            return False, None
        
        # Save script
        script_file = self.figure_script_dir / f"plot_{figure_name}.py"
        script_file.write_text(plot_code)
        print(f"  ✓ Generated script: {script_file}")
        
        # Execute script
        print(f"  Running script...")
        success = self._execute_plot_script(script_file, figure_name)
        
        if success:
            figure_path = self.figures_dir / f"{figure_name}.pdf"
            print(f"  ✅ Generated: {figure_path}")
            return True, figure_path
        else:
            print(f"  ❌ Failed to execute script")
            return False, None
    
    def _read_paper_context(self) -> str:
        """Read written sections for context"""
        context_parts = []
        
        # Try to read existing sections
        for section in ["introduction.tex", "theory.tex", "methods.tex"]:
            section_file = self.project_dir / section
            if section_file.exists():
                content = section_file.read_text()
                context_parts.append(f"--- {section} ---\n{content[:1000]}")
        
        # Try OUTLINE.md
        outline_file = self.project_dir / "OUTLINE.md"
        if outline_file.exists():
            context_parts.append(f"--- OUTLINE ---\n{outline_file.read_text()}")
        
        return "\n\n".join(context_parts)
    
    def _generate_plot_code(self, description: str, context: str) -> Tuple[bool, str]:
        """Generate matplotlib plotting code"""
        
        prompt = f"""Generate Python code to create an illustrative figure for a physics paper.

PAPER CONTEXT:
{context[:3000]}

FIGURE DESCRIPTION:
{description}

Requirements:
1. Use matplotlib for plotting
2. Create publication-quality figure
3. Use physics-appropriate style (serif fonts, etc.)
4. Include clear labels, legend if needed
5. Save as both PDF and PNG
6. Figure should be self-contained

Generate a complete Python script that:
- Imports necessary libraries (matplotlib, numpy, etc.)
- Creates the figure
- Saves to 'figures/{description.split()[0]}.pdf' and '.png'
- Can be run standalone

Example structure:
```python
import matplotlib.pyplot as plt
import numpy as np

# Set publication style
plt.rcParams.update({{
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'legend.fontsize': 10
}})

# Create figure
fig, ax = plt.subplots(figsize=(6, 4))

# Your plotting code here
# ...

# Labels and formatting
ax.set_xlabel('...')
ax.set_ylabel('...')
ax.legend()

# Save
plt.tight_layout()
plt.savefig('figures/{description.split()[0]}.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figures/{description.split()[0]}.png', dpi=300, bbox_inches='tight')
plt.close()

print("Figure saved")
```

Write ONLY the Python code (no explanations)."""
        
        for attempt in range(self.MAX_RETRIES):
            try:
                result = subprocess.run(
                    ["claude", "--dangerously-skip-permissions", "-p", prompt],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    code = result.stdout.strip()
                    # Extract code from markdown if present
                    if "```python" in code:
                        code = code.split("```python")[1].split("```")[0].strip()
                    return True, code
                    
            except Exception as e:
                print(f"    Attempt {attempt + 1} failed: {e}")
        
        return False, ""
    
    def _execute_plot_script(self, script_file: Path, figure_name: str) -> bool:
        """Execute the plotting script"""
        
        try:
            result = subprocess.run(
                ["python3", str(script_file)],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Check if figure was created
                pdf_file = self.figures_dir / f"{figure_name}.pdf"
                return pdf_file.exists()
            else:
                print(f"    Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"    Exception: {e}")
            return False
    
    def generate_all_figures(self, figure_specs: dict) -> dict:
        """
        Generate all required figures from specifications
        
        Args:
            figure_specs: Dict of {figure_name: description}
        
        Returns:
            Dict of {figure_name: (success, path)}
        """
        
        print("\n" + "="*60)
        print("FIGURE GENERATION")
        print("="*60)
        print(f"Figures to generate: {len(figure_specs)}")
        print()
        
        results = {}
        
        for name, description in figure_specs.items():
            success, path = self.generate_illustrative_figure(description, name)
            results[name] = (success, path)
        
        # Summary
        successful = sum(1 for s, _ in results.values() if s)
        print(f"\n{'='*60}")
        print(f"Generated: {successful}/{len(figure_specs)} figures")
        print(f"{'='*60}")
        
        return results


def main():
    """Figure generation CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Figure Generation Agent")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--figure",
        type=str,
        help="Figure description"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="main_idea",
        help="Figure name"
    )
    parser.add_argument(
        "--check-progress",
        action="store_true",
        help="Check if it's time to generate figures"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Config not found: {args.config}")
        return 1
    
    config = PaperMaintenanceConfig.load(args.config)
    agent = FigureGenerationAgent(config)
    
    if args.check_progress:
        progress = agent.check_progress()
        should_generate = agent.should_generate_figures()
        
        print(f"Paper progress: {progress*100:.1f}%")
        print(f"Should generate figures: {'YES' if should_generate else 'NO'}")
        
        return 0
    
    elif args.figure:
        success, path = agent.generate_illustrative_figure(args.figure, args.name)
        return 0 if success else 1
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
