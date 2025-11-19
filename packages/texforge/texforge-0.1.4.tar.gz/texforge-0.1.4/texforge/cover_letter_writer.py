#!/usr/bin/env python3
"""
Cover Letter Writer Agent
Generates professional cover letters for journal submissions based on finished papers.
"""
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import subprocess
import re

from .config import PaperMaintenanceConfig


@dataclass
class JournalProfile:
    """Journal-specific requirements and characteristics"""
    journal_code: str
    full_name: str
    scope: str
    typical_tone: str
    key_criteria: List[str]
    typical_length: str = "one page"


@dataclass
class CoverLetterResult:
    """Result of cover letter generation"""
    journal: str
    cover_letter_text: str
    paper_title: str
    key_contributions: List[str]
    cited_works: List[str]
    timestamp: datetime

    def to_markdown(self) -> str:
        """Generate markdown version of the cover letter"""
        lines = []
        lines.append(f"# Cover Letter for {self.journal}")
        lines.append(f"\n**Generated:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n**Paper Title:** {self.paper_title}")
        lines.append(f"\n## Cover Letter Text\n")
        lines.append(self.cover_letter_text)

        lines.append(f"\n\n## Key Contributions Highlighted\n")
        for i, contrib in enumerate(self.key_contributions, 1):
            lines.append(f"{i}. {contrib}")

        lines.append(f"\n\n## Influential Works Cited\n")
        for i, work in enumerate(self.cited_works, 1):
            lines.append(f"{i}. {work}")

        return "\n".join(lines)

    def save(self, output_path: Path) -> None:
        """Save cover letter to file"""
        # Save plain text version
        txt_path = output_path.with_suffix('.txt')
        txt_path.write_text(self.cover_letter_text)

        # Save markdown version
        md_path = output_path.with_suffix('.md')
        md_path.write_text(self.to_markdown())


class CoverLetterWriter:
    """Generate professional cover letters for journal submissions"""

    # Common journal profiles
    JOURNAL_PROFILES = {
        'prl': JournalProfile(
            journal_code='prl',
            full_name='Physical Review Letters',
            scope='High-impact physics discoveries with broad significance',
            typical_tone='Concise, confident, emphasizing novelty and impact',
            key_criteria=[
                'Fundamental advance in physics',
                'Broad interest to physics community',
                'Novel methodology or surprising result',
                'Clear and compelling presentation'
            ]
        ),
        'pra': JournalProfile(
            journal_code='pra',
            full_name='Physical Review A',
            scope='Atomic, molecular, and optical physics, quantum information',
            typical_tone='Technical, detailed, emphasizing rigor and completeness',
            key_criteria=[
                'Significant contribution to AMO or quantum physics',
                'Rigorous theoretical or experimental work',
                'Clear advancement of the field',
                'Comprehensive treatment of the topic'
            ]
        ),
        'prb': JournalProfile(
            journal_code='prb',
            full_name='Physical Review B',
            scope='Condensed matter and materials physics',
            typical_tone='Technical, emphasizing material impact and applications',
            key_criteria=[
                'Advances in condensed matter theory or experiment',
                'Novel materials or phenomena',
                'Rigorous methodology',
                'Relevance to broader materials science'
            ]
        ),
        'nature': JournalProfile(
            journal_code='nature',
            full_name='Nature',
            scope='Breakthrough research across all sciences',
            typical_tone='Compelling, accessible, emphasizing broad significance',
            key_criteria=[
                'Exceptional novelty and importance',
                'Paradigm-shifting results',
                'Broad interest across disciplines',
                'Clear and accessible presentation'
            ]
        ),
        'science': JournalProfile(
            journal_code='science',
            full_name='Science',
            scope='Breakthrough research across all sciences',
            typical_tone='Clear, compelling, emphasizing innovation and impact',
            key_criteria=[
                'Major advance in the field',
                'Broad scientific interest',
                'Innovative methodology',
                'Clear societal or scientific impact'
            ]
        ),
        'prx': JournalProfile(
            journal_code='prx',
            full_name='Physical Review X',
            scope='Outstanding physics research with high impact',
            typical_tone='Confident, emphasizing innovation and broad impact',
            key_criteria=[
                'Exceptional quality and innovation',
                'Strong potential for high impact',
                'Interdisciplinary appeal',
                'Outstanding clarity and presentation'
            ]
        ),
    }

    def __init__(self, config: PaperMaintenanceConfig):
        """Initialize the cover letter writer"""
        self.config = config
        self.project_dir = config.paper_directory
        self.output_file = self.project_dir / "cover_letter"

    def generate_cover_letter(
        self,
        journal: str,
        additional_info: Optional[str] = None,
        custom_profile: Optional[JournalProfile] = None
    ) -> CoverLetterResult:
        """
        Generate a cover letter for journal submission

        Args:
            journal: Journal code (e.g., 'prl', 'nature') or custom name
            additional_info: Additional information to include
            custom_profile: Custom journal profile if journal not in database

        Returns:
            CoverLetterResult with the generated cover letter
        """
        print(f"📝 Generating cover letter for {journal.upper()}...")

        # Get journal profile
        journal_lower = journal.lower()
        if journal_lower in self.JOURNAL_PROFILES:
            profile = self.JOURNAL_PROFILES[journal_lower]
            journal_name = profile.full_name
        elif custom_profile:
            profile = custom_profile
            journal_name = custom_profile.full_name
        else:
            # Use generic profile
            profile = JournalProfile(
                journal_code=journal,
                full_name=journal,
                scope='General scientific research',
                typical_tone='Professional and clear',
                key_criteria=['Scientific rigor', 'Novel contributions', 'Clear presentation']
            )
            journal_name = journal

        # Read paper content
        print("📄 Reading paper content...")
        paper_content = self._read_paper_content()

        # Extract paper title
        print("🔍 Extracting paper information...")
        paper_title = self._extract_title(paper_content)

        # Generate cover letter using Claude
        print("🤖 Generating cover letter with Claude AI...")
        cover_letter_data = self._generate_with_claude(
            paper_content=paper_content,
            paper_title=paper_title,
            journal_name=journal_name,
            profile=profile,
            additional_info=additional_info
        )

        # Create result object
        result = CoverLetterResult(
            journal=journal_name,
            cover_letter_text=cover_letter_data['cover_letter'],
            paper_title=cover_letter_data['title'],
            key_contributions=cover_letter_data['contributions'],
            cited_works=cover_letter_data['cited_works'],
            timestamp=datetime.now()
        )

        # Save the cover letter
        print(f"💾 Saving cover letter to {self.output_file}.txt and {self.output_file}.md...")
        result.save(self.output_file)

        print("✅ Cover letter generation complete!")
        return result

    def _read_paper_content(self) -> str:
        """Read the main TeX file and extract content"""
        tex_file = self.project_dir / self.config.main_tex_file

        if not tex_file.exists():
            # Try to find main.tex or paper.tex
            candidates = ['main.tex', 'paper.tex', 'manuscript.tex']
            for candidate in candidates:
                candidate_path = self.project_dir / candidate
                if candidate_path.exists():
                    tex_file = candidate_path
                    break
            else:
                raise FileNotFoundError(
                    f"Could not find TeX file. Looked for: {self.config.main_tex_file}, "
                    f"{', '.join(candidates)}"
                )

        return tex_file.read_text(encoding='utf-8', errors='ignore')

    def _extract_title(self, paper_content: str) -> str:
        """Extract paper title from TeX content"""
        # Look for \title{...}
        title_match = re.search(r'\\title\{([^}]+)\}', paper_content)
        if title_match:
            title = title_match.group(1)
            # Clean up LaTeX commands
            title = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', title)
            title = re.sub(r'\\[a-zA-Z]+', '', title)
            return title.strip()

        return "Untitled Manuscript"

    def _generate_with_claude(
        self,
        paper_content: str,
        paper_title: str,
        journal_name: str,
        profile: JournalProfile,
        additional_info: Optional[str]
    ) -> Dict:
        """Generate cover letter using Claude CLI"""

        prompt = f"""You are an expert academic writing assistant tasked with generating a professional cover letter for a journal submission.

**Journal Information:**
- Journal: {journal_name}
- Scope: {profile.scope}
- Tone: {profile.typical_tone}
- Key Criteria: {', '.join(profile.key_criteria)}

**Paper Content:**
```
{paper_content[:15000]}  # Limit to avoid too long prompts
```

**Additional Information:**
{additional_info or 'None provided'}

**Task:**
Generate a professional cover letter for submitting this paper to {journal_name}. The cover letter should be approximately one page long and follow this structure:

1. **First Paragraph (1 sentence):** State the paper title in quotes and the journal name you are submitting to.

2. **Second Paragraph:** Describe the motivation for this research. Explain the broader context and identify 2-4 influential previous works that are relevant to this research. Use proper citations if available in the paper.

3. **Third Paragraph:** Summarize the key contributions and significance of this work. Highlight what makes this research novel and important. Focus on the main findings and their implications.

4. **Fourth Paragraph:** Explain why this paper is a good match for {journal_name}. Reference the journal's scope and criteria: {', '.join(profile.key_criteria)}.

**Output Format:**
Provide your response as a JSON object with the following structure:
{{
    "title": "extracted paper title",
    "cover_letter": "the complete cover letter text, ready to use",
    "contributions": ["contribution 1", "contribution 2", "contribution 3"],
    "cited_works": ["work 1", "work 2", "work 3"]
}}

Make the cover letter professional, concise, and compelling. Use formal academic language appropriate for {journal_name}.
"""

        try:
            result = subprocess.run(
                ["claude", "--dangerously-skip-permissions", "-p", prompt],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=180
            )

            output = result.stdout.strip()

            # Try to extract JSON from the output
            import json

            # Look for JSON block
            json_match = re.search(r'\{[^{}]*"title"[^{}]*"cover_letter"[^{}]*\}', output, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    return data
                except json.JSONDecodeError:
                    pass

            # If JSON extraction fails, try to parse the structured output
            return self._parse_claude_output(output, paper_title, journal_name)

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude API call timed out")
        except Exception as e:
            raise RuntimeError(f"Error calling Claude API: {e}")

    def _parse_claude_output(self, output: str, paper_title: str, journal_name: str) -> Dict:
        """Parse Claude output when JSON parsing fails"""
        # Fallback: try to extract the cover letter from the output
        # This is a simple heuristic-based approach

        lines = output.split('\n')
        cover_letter_lines = []
        in_letter = False

        for line in lines:
            # Skip JSON markers and code blocks
            if line.strip().startswith('{') or line.strip().startswith('}'):
                continue
            if '```' in line:
                in_letter = not in_letter
                continue
            if '"title"' in line or '"cover_letter"' in line or '"contributions"' in line:
                continue

            if line.strip() and not line.strip().startswith('#'):
                cover_letter_lines.append(line)

        cover_letter_text = '\n'.join(cover_letter_lines).strip()

        # If we couldn't extract a good cover letter, create a basic template
        if len(cover_letter_text) < 200:
            cover_letter_text = self._create_basic_template(paper_title, journal_name)

        return {
            'title': paper_title,
            'cover_letter': cover_letter_text,
            'contributions': ['Key contribution (extracted from paper)'],
            'cited_works': ['Referenced works (see paper bibliography)']
        }

    def _create_basic_template(self, paper_title: str, journal_name: str) -> str:
        """Create a basic cover letter template as fallback"""
        return f"""Dear Editor,

We are pleased to submit our manuscript entitled "{paper_title}" for consideration for publication in {journal_name}.

[This is a template. Please review and customize based on your paper content.]

This research addresses [key problem/question] and builds upon influential previous works in the field. Our work makes significant contributions to [research area] through [brief description of approach/methodology].

The key contributions of this work include: [1) contribution one, 2) contribution two, 3) contribution three]. These findings have important implications for [impact/significance].

We believe this manuscript is well-suited for {journal_name} because [reasons why paper matches journal scope and criteria].

We confirm that this manuscript has not been published elsewhere and is not under consideration by another journal. All authors have approved the manuscript and agree with its submission to {journal_name}.

Thank you for considering our manuscript.

Sincerely,
[Author names]
"""


def main():
    """CLI entry point for standalone usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate cover letters for journal submissions')
    parser.add_argument('journal', help='Journal code (e.g., prl, nature) or custom name')
    parser.add_argument('-c', '--config', type=Path, help='Configuration file path')
    parser.add_argument('-i', '--info', help='Additional information to include')

    args = parser.parse_args()

    # Load config
    if args.config and args.config.exists():
        config = PaperMaintenanceConfig.load(args.config)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = Path.cwd()
        config.main_tex_file = 'main.tex'

    # Create writer and generate
    writer = CoverLetterWriter(config)
    result = writer.generate_cover_letter(
        journal=args.journal,
        additional_info=args.info
    )

    print("\n" + "="*60)
    print(result.cover_letter_text)
    print("="*60)


if __name__ == '__main__':
    main()
