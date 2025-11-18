#!/usr/bin/env python3
"""
Peer Review Simulation System
Simulates rigorous peer review before submission
"""
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass

from .config import PaperMaintenanceConfig


@dataclass
class ReviewerProfile:
    """Peer reviewer persona"""
    name: str
    expertise: str
    known_for: str
    review_style: str
    typical_concerns: List[str]


@dataclass
class Review:
    """A peer review"""
    reviewer: str
    recommendation: str  # Accept, Minor Revision, Major Revision, Reject
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    detailed_comments: List[str]
    questions_for_authors: List[str]
    rating_novelty: int  # 1-5
    rating_rigor: int
    rating_clarity: int
    rating_significance: int


class PeerReviewSimulation:
    """Simulate peer review process"""
    
    REVIEWERS = [
        ReviewerProfile(
            name="Reviewer 1",
            expertise="Quantum information theory",
            known_for="Mathematical rigor",
            review_style="Thorough, focuses on proofs and technical details",
            typical_concerns=[
                "Mathematical rigor",
                "Proof completeness",
                "Technical accuracy",
                "Formal definitions"
            ]
        ),
        ReviewerProfile(
            name="Reviewer 2",
            expertise="Quantum computation and simulation",
            known_for="Practical implementation",
            review_style="Critical of claims, wants experimental validation",
            typical_concerns=[
                "Experimental feasibility",
                "Practical applications",
                "Comparison with existing methods",
                "Realistic assumptions"
            ]
        ),
        ReviewerProfile(
            name="Reviewer 3",
            expertise="Many-body quantum systems",
            known_for="Broad perspective",
            review_style="Evaluates significance and impact",
            typical_concerns=[
                "Novelty and originality",
                "Broader significance",
                "Connection to literature",
                "Impact on the field"
            ]
        ),
    ]
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.review_file = self.project_dir / "peer_reviews.md"
    
    def simulate_review(self, paper_file: Path, target_journal: str = "Physical Review A") -> List[Review]:
        """Simulate full peer review process"""
        
        if not paper_file.exists():
            print(f"Error: Paper not found: {paper_file}")
            return []
        
        print("📝 Simulating peer review process...")
        print(f"Journal: {target_journal}")
        print(f"Reviewers: {len(self.REVIEWERS)}\n")
        
        # Read paper content
        paper_content = paper_file.read_text()
        
        reviews = []
        for reviewer_profile in self.REVIEWERS:
            print(f"Getting review from {reviewer_profile.name}...")
            review = self._get_review(paper_content, reviewer_profile, target_journal)
            reviews.append(review)
            print(f"  → {review.recommendation}")
        
        # Generate meta-review (editor decision)
        print("\nGenerating editorial decision...")
        meta_review = self._generate_meta_review(reviews, target_journal)
        
        # Save reviews
        report = self._generate_report(reviews, meta_review, target_journal)
        self.review_file.write_text(report)
        print(f"\n✓ Reviews saved to: {self.review_file}")
        
        # Print summary
        self._print_summary(reviews, meta_review)
        
        return reviews
    
    def _get_review(self, paper_content: str, profile: ReviewerProfile, 
                   journal: str) -> Review:
        """Get review from one reviewer"""
        
        prompt = f"""You are {profile.name}, an expert peer reviewer for {journal}.

Your expertise: {profile.expertise}
Known for: {profile.known_for}
Review style: {profile.review_style}

You are reviewing the following paper:

{paper_content[:8000]}  # Limit to avoid token limits

Provide a COMPREHENSIVE PEER REVIEW following this structure:

1. **SUMMARY** (3-4 sentences): What is this paper about? What are the main claims?

2. **RECOMMENDATION**: Choose ONE:
   - Accept as is
   - Accept with minor revisions
   - Major revisions required
   - Reject

3. **STRENGTHS** (3-5 points): What does this paper do well?

4. **WEAKNESSES** (3-5 points): What are the significant problems?

5. **DETAILED COMMENTS** (5-10 specific points):
   - Technical issues
   - Missing references
   - Clarity problems
   - Questionable claims
   
6. **QUESTIONS FOR AUTHORS** (3-5 questions they must address)

7. **RATINGS** (1-5 scale):
   - Novelty:
   - Technical rigor:
   - Clarity:
   - Significance:

Be thorough, critical, and constructive. Focus on {', '.join(profile.typical_concerns)}."""
        
        response = self._call_claude(prompt)
        
        # Parse response
        return self._parse_review(response, profile.name)
    
    def _call_claude(self, prompt: str) -> str:
        """Call Claude for review"""
        try:
            result = subprocess.run(
                ["claude", "--dangerously-skip-permissions", "-p", prompt],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=180
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def _parse_review(self, response: str, reviewer_name: str) -> Review:
        """Parse review from Claude response"""
        import re
        
        # Extract recommendation
        rec_match = re.search(r'RECOMMENDATION.*?:?\s*(Accept|Major|Minor|Reject[^\\n]*)', 
                             response, re.IGNORECASE)
        recommendation = rec_match.group(1) if rec_match else "Unknown"
        
        # Extract summary
        summary_match = re.search(r'SUMMARY.*?:?\s*(.+?)(?=RECOMMENDATION|STRENGTHS|\n\n)', 
                                 response, re.DOTALL | re.IGNORECASE)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        # Extract strengths
        strengths = self._extract_list_section(response, "STRENGTHS")
        
        # Extract weaknesses
        weaknesses = self._extract_list_section(response, "WEAKNESSES")
        
        # Extract detailed comments
        comments = self._extract_list_section(response, "DETAILED COMMENTS")
        
        # Extract questions
        questions = self._extract_list_section(response, "QUESTIONS")
        
        # Extract ratings
        ratings = self._extract_ratings(response)
        
        return Review(
            reviewer=reviewer_name,
            recommendation=recommendation,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            detailed_comments=comments,
            questions_for_authors=questions,
            rating_novelty=ratings.get('novelty', 3),
            rating_rigor=ratings.get('rigor', 3),
            rating_clarity=ratings.get('clarity', 3),
            rating_significance=ratings.get('significance', 3),
        )
    
    def _extract_list_section(self, text: str, section_name: str) -> List[str]:
        """Extract bulleted/numbered list from section"""
        import re
        
        pattern = f'{section_name}.*?:?\\s*(.+?)(?=\\n\\n[A-Z]|\\Z)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return []
        
        content = match.group(1)
        items = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Remove numbering/bullets
                item = re.sub(r'^[\d\-\*\.\)]+\s*', '', line)
                items.append(item)
        
        return items
    
    def _extract_ratings(self, text: str) -> Dict[str, int]:
        """Extract numerical ratings"""
        import re
        
        ratings = {}
        rating_types = ['novelty', 'rigor', 'clarity', 'significance']
        
        for rating_type in rating_types:
            pattern = f'{rating_type}.*?:?\\s*(\\d)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ratings[rating_type] = int(match.group(1))
        
        return ratings
    
    def _generate_meta_review(self, reviews: List[Review], journal: str) -> Dict:
        """Generate editor's decision based on reviews"""
        
        # Compile all reviews
        review_summary = "\n\n".join([
            f"REVIEWER {i+1}:\n"
            f"Recommendation: {r.recommendation}\n"
            f"Strengths: {', '.join(r.strengths[:3])}\n"
            f"Weaknesses: {', '.join(r.weaknesses[:3])}\n"
            f"Ratings: Novel={r.rating_novelty}, Rigor={r.rating_rigor}, "
            f"Clarity={r.rating_clarity}, Significance={r.rating_significance}"
            for i, r in enumerate(reviews)
        ])
        
        prompt = f"""You are the editor of {journal}.

You have received {len(reviews)} peer reviews:

{review_summary}

Provide an EDITORIAL DECISION:

1. **DECISION**: Accept / Minor Revision / Major Revision / Reject
2. **JUSTIFICATION** (2-3 sentences)
3. **REQUIRED CHANGES** (if revisions needed, list 3-5 critical items)
4. **TIMELINE** (if revisions: realistic time needed)
5. **ADVICE TO AUTHORS** (how to address concerns)

Be fair but maintain high standards for {journal}."""
        
        response = self._call_claude(prompt)
        
        return {
            'decision': response,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_report(self, reviews: List[Review], meta_review: Dict, 
                        journal: str) -> str:
        """Generate markdown report"""
        lines = [
            "# Peer Review Simulation",
            "",
            f"**Journal:** {journal}",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Reviewers:** {len(reviews)}",
            "",
            "---",
            ""
        ]
        
        # Individual reviews
        for i, review in enumerate(reviews, 1):
            lines.extend([
                f"## Reviewer {i}",
                "",
                f"**Recommendation:** {review.recommendation}",
                "",
                f"**Ratings:**",
                f"- Novelty: {review.rating_novelty}/5",
                f"- Technical Rigor: {review.rating_rigor}/5",
                f"- Clarity: {review.rating_clarity}/5",
                f"- Significance: {review.rating_significance}/5",
                "",
                f"### Summary",
                "",
                review.summary,
                "",
                f"### Strengths",
                ""
            ])
            
            for strength in review.strengths:
                lines.append(f"- {strength}")
            
            lines.extend([
                "",
                "### Weaknesses",
                ""
            ])
            
            for weakness in review.weaknesses:
                lines.append(f"- {weakness}")
            
            if review.detailed_comments:
                lines.extend([
                    "",
                    "### Detailed Comments",
                    ""
                ])
                for comment in review.detailed_comments:
                    lines.append(f"- {comment}")
            
            if review.questions_for_authors:
                lines.extend([
                    "",
                    "### Questions for Authors",
                    ""
                ])
                for question in review.questions_for_authors:
                    lines.append(f"- {question}")
            
            lines.extend(["", "---", ""])
        
        # Meta-review
        lines.extend([
            "## Editorial Decision",
            "",
            meta_review['decision'],
            "",
            "---",
            "",
            "## Response Strategy",
            "",
            "### Critical Issues to Address",
            ""
        ])
        
        # Compile common concerns
        all_weaknesses = []
        for review in reviews:
            all_weaknesses.extend(review.weaknesses)
        
        from collections import Counter
        common_themes = Counter([w[:50] for w in all_weaknesses])
        
        lines.append("Most mentioned concerns:")
        for theme, count in common_themes.most_common(5):
            lines.append(f"- {theme}... (mentioned by {count} reviewers)")
        
        lines.extend([
            "",
            "### Action Items",
            "",
            "- [ ] Address all questions from reviewers",
            "- [ ] Revise sections with identified weaknesses",
            "- [ ] Expand discussion where requested",
            "- [ ] Add missing references",
            "- [ ] Improve figures/tables if criticized",
            "- [ ] Strengthen claims with more evidence",
            ""
        ])
        
        return "\n".join(lines)
    
    def _print_summary(self, reviews: List[Review], meta_review: Dict) -> None:
        """Print summary to console"""
        print("\n" + "=" * 60)
        print("PEER REVIEW SUMMARY")
        print("=" * 60)
        
        recommendations = [r.recommendation for r in reviews]
        print(f"\nRecommendations: {', '.join(recommendations)}")
        
        avg_ratings = {
            'Novelty': sum(r.rating_novelty for r in reviews) / len(reviews),
            'Rigor': sum(r.rating_rigor for r in reviews) / len(reviews),
            'Clarity': sum(r.rating_clarity for r in reviews) / len(reviews),
            'Significance': sum(r.rating_significance for r in reviews) / len(reviews),
        }
        
        print("\nAverage Ratings (out of 5):")
        for category, score in avg_ratings.items():
            print(f"  {category}: {score:.1f}")
        
        print("\nMost Common Weaknesses:")
        all_weaknesses = []
        for review in reviews:
            all_weaknesses.extend(review.weaknesses[:2])
        
        from collections import Counter
        for weakness, count in Counter(all_weaknesses).most_common(3):
            print(f"  - {weakness}")
        
        print("\n" + "=" * 60)


def main():
    """Peer review simulation CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Peer Review Simulation")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--paper",
        type=Path,
        help="Path to paper .tex file (default: main.tex)"
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
    simulator = PeerReviewSimulation(config)
    
    # Find paper
    if args.paper:
        paper_file = args.paper
    else:
        paper_file = config.paper_directory / "main.tex"
    
    if not paper_file.exists():
        print(f"Paper not found: {paper_file}")
        return 1
    
    reviews = simulator.simulate_review(paper_file, args.journal)
    
    if not reviews:
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
