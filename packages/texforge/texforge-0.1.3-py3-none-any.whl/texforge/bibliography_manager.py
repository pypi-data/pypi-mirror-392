#!/usr/bin/env python3
"""
Smart Bibliography Manager
- Generate .bib entries from paper titles/DOIs
- Verify citations are real and accessible
- Check citation impact (highly-cited papers)
- Identify recent relevant work
- Suggest missing key papers in the field
"""
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import requests
from datetime import datetime

from .config import PaperMaintenanceConfig


@dataclass
class BibEntry:
    """Bibliography entry with metadata"""
    key: str
    title: str
    authors: List[str]
    year: int
    venue: str
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    citation_count: int = 0
    bib_text: str = ""
    
    @property
    def is_recent(self) -> bool:
        """Check if paper is recent (within 3 years)"""
        current_year = datetime.now().year
        return (current_year - self.year) <= 3
    
    @property
    def is_influential(self) -> bool:
        """Check if paper is highly cited"""
        # Thresholds vary by field
        # For physics: 100+ citations is influential
        # For very recent papers (< 1 year): 10+ is good
        if self.is_recent and (datetime.now().year - self.year) < 1:
            return self.citation_count >= 10
        return self.citation_count >= 100
    
    @property
    def quality_score(self) -> float:
        """Overall quality score (0-1)"""
        score = 0.0
        
        # Citation count (0-0.5)
        if self.citation_count >= 1000:
            score += 0.5
        elif self.citation_count >= 100:
            score += 0.3 + (self.citation_count - 100) / 900 * 0.2
        elif self.citation_count >= 10:
            score += 0.1 + (self.citation_count - 10) / 90 * 0.2
        else:
            score += self.citation_count / 10 * 0.1
        
        # Recency (0-0.3)
        years_old = datetime.now().year - self.year
        if years_old <= 1:
            score += 0.3
        elif years_old <= 3:
            score += 0.2
        elif years_old <= 5:
            score += 0.1
        
        # Venue quality (0-0.2)
        high_quality_venues = [
            'Physical Review Letters', 'PRL', 'Nature', 'Science',
            'Physical Review A', 'Physical Review B', 'Physical Review X',
            'Nature Physics', 'Nature Quantum Information'
        ]
        if any(venue in self.venue for venue in high_quality_venues):
            score += 0.2
        
        return min(score, 1.0)


class BibliographyManager:
    """Manage bibliography with verification and suggestions"""
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.paper_dir = config.paper_directory
        self.bib_file = self._find_bib_file()
    
    def _find_bib_file(self) -> Optional[Path]:
        """Find the .bib file in the paper directory"""
        bib_files = list(self.paper_dir.glob("*.bib"))
        if bib_files:
            return bib_files[0]
        return self.paper_dir / "references.bib"
    
    def extract_citations(self) -> List[str]:
        """Extract all citation keys from .tex files"""
        citations = set()
        
        for tex_file in self.paper_dir.glob("*.tex"):
            content = tex_file.read_text()
            
            # Find \cite{key}, \citep{key}, \citet{key}, etc.
            matches = re.findall(r'\\cite[tp]?\{([^}]+)\}', content)
            for match in matches:
                # Handle multiple citations: \cite{key1,key2}
                keys = [k.strip() for k in match.split(',')]
                citations.update(keys)
        
        return sorted(citations)
    
    def parse_bib_file(self) -> Dict[str, BibEntry]:
        """Parse existing .bib file"""
        if not self.bib_file.exists():
            return {}
        
        entries = {}
        content = self.bib_file.read_text()
        
        # Simple parsing (could use bibtexparser library for robustness)
        entry_pattern = r'@(\w+)\{([^,]+),([^@]*?)(?=\n@|\Z)'
        
        for match in re.finditer(entry_pattern, content, re.DOTALL):
            entry_type = match.group(1)
            key = match.group(2).strip()
            fields_text = match.group(3)
            
            # Extract fields
            title = self._extract_field(fields_text, 'title')
            authors_str = self._extract_field(fields_text, 'author')
            year_str = self._extract_field(fields_text, 'year')
            venue = self._extract_field(fields_text, 'journal') or \
                   self._extract_field(fields_text, 'booktitle') or ""
            doi = self._extract_field(fields_text, 'doi')
            
            # Parse authors
            authors = [a.strip() for a in authors_str.split(' and ')] if authors_str else []
            year = int(year_str) if year_str and year_str.isdigit() else 0
            
            entries[key] = BibEntry(
                key=key,
                title=title or "",
                authors=authors,
                year=year,
                venue=venue,
                doi=doi,
                bib_text=match.group(0)
            )
        
        return entries
    
    def _extract_field(self, text: str, field: str) -> Optional[str]:
        """Extract field value from BibTeX text"""
        pattern = rf'{field}\s*=\s*[{{""]([^}}"]+)[}}""]'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def verify_citation_exists(self, key: str, entry: BibEntry) -> Tuple[bool, str]:
        """Verify citation is real using Semantic Scholar API"""
        try:
            # Try DOI first
            if entry.doi:
                response = requests.get(
                    f"https://api.semanticscholar.org/v1/paper/{entry.doi}",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    return True, f"Verified via DOI ({data.get('citationCount', 0)} citations)"
            
            # Try title search
            if entry.title:
                response = requests.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params={"query": entry.title, "limit": 1},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        paper = data['data'][0]
                        citations = paper.get('citationCount', 0)
                        return True, f"Verified by title ({citations} citations)"
            
            return False, "Could not verify citation"
            
        except Exception as e:
            return False, f"Verification error: {e}"
    
    def get_citation_metrics(self, entry: BibEntry) -> Dict:
        """Get citation metrics from Semantic Scholar"""
        try:
            # Search by DOI or title
            if entry.doi:
                response = requests.get(
                    f"https://api.semanticscholar.org/graph/v1/paper/{entry.doi}",
                    params={"fields": "citationCount,influentialCitationCount,year,venue"},
                    timeout=10
                )
            elif entry.title:
                response = requests.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params={"query": entry.title, "limit": 1, 
                           "fields": "citationCount,influentialCitationCount,year,venue"},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        response_data = data['data'][0]
                    else:
                        return {}
                else:
                    return {}
            else:
                return {}
            
            if response.status_code == 200:
                data = response.json() if not isinstance(response, dict) else response_data
                return {
                    'citation_count': data.get('citationCount', 0),
                    'influential_citations': data.get('influentialCitationCount', 0),
                    'year': data.get('year', entry.year),
                    'venue': data.get('venue', {}).get('name', entry.venue)
                }
            
        except Exception as e:
            print(f"Warning: Could not fetch metrics for {entry.key}: {e}")
        
        return {}
    
    def generate_bib_entry(self, title: str = None, doi: str = None, 
                          arxiv: str = None) -> Optional[str]:
        """Generate BibTeX entry from DOI, arXiv ID, or title"""
        try:
            # Try DOI first (most reliable)
            if doi:
                response = requests.get(
                    f"https://doi.org/{doi}",
                    headers={"Accept": "application/x-bibtex"},
                    timeout=10
                )
                if response.status_code == 200:
                    return response.text
            
            # Try arXiv
            if arxiv:
                # arXiv to BibTeX conversion
                response = requests.get(
                    f"https://arxiv.org/bibtex/{arxiv}",
                    timeout=10
                )
                if response.status_code == 200:
                    return response.text
            
            # Try Semantic Scholar by title
            if title:
                response = requests.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params={"query": title, "limit": 1,
                           "fields": "title,authors,year,venue,externalIds"},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        paper = data['data'][0]
                        return self._format_bibtex(paper)
            
        except Exception as e:
            print(f"Error generating bib entry: {e}")
        
        return None
    
    def _format_bibtex(self, paper_data: Dict) -> str:
        """Format paper data as BibTeX"""
        # Generate key from first author + year
        authors = paper_data.get('authors', [])
        first_author = authors[0]['name'].split()[-1] if authors else 'Unknown'
        year = paper_data.get('year', 'n.d.')
        key = f"{first_author}{year}"
        
        # Format authors
        author_str = " and ".join(a['name'] for a in authors)
        
        # Get DOI if available
        external_ids = paper_data.get('externalIds', {})
        doi = external_ids.get('DOI', '')
        
        bib = f"""@article{{{key},
    title = {{{paper_data.get('title', 'Untitled')}}},
    author = {{{author_str}}},
    year = {{{year}}},
    journal = {{{paper_data.get('venue', {}).get('name', '')}}},"""
        
        if doi:
            bib += f"\n    doi = {{{doi}}},"
        
        bib += "\n}\n"
        
        return bib
    
    def suggest_missing_papers(self, field_keywords: List[str]) -> List[Dict]:
        """Suggest influential papers in the field that might be missing"""
        suggestions = []
        
        for keyword in field_keywords[:3]:  # Limit to avoid API rate limits
            try:
                response = requests.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params={
                        "query": keyword,
                        "limit": 5,
                        "fields": "title,authors,year,citationCount,venue,externalIds",
                        "sort": "citationCount:desc"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for paper in data.get('data', []):
                        # Only suggest highly cited papers
                        if paper.get('citationCount', 0) >= 100:
                            suggestions.append({
                                'title': paper.get('title'),
                                'authors': [a['name'] for a in paper.get('authors', [])],
                                'year': paper.get('year'),
                                'citations': paper.get('citationCount', 0),
                                'venue': paper.get('venue', {}).get('name', ''),
                                'doi': paper.get('externalIds', {}).get('DOI'),
                                'keyword': keyword
                            })
            
            except Exception as e:
                print(f"Warning: Could not fetch suggestions for '{keyword}': {e}")
        
        # Sort by citation count and deduplicate
        suggestions.sort(key=lambda x: x['citations'], reverse=True)
        seen_titles = set()
        unique_suggestions = []
        for s in suggestions:
            if s['title'] not in seen_titles:
                seen_titles.add(s['title'])
                unique_suggestions.append(s)
        
        return unique_suggestions[:10]  # Top 10
    
    def generate_report(self) -> str:
        """Generate comprehensive bibliography report"""
        citations = self.extract_citations()
        bib_entries = self.parse_bib_file()
        
        lines = ["# Bibliography Analysis Report", ""]
        lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Total citations:** {len(citations)}")
        lines.append(f"**Bibliography entries:** {len(bib_entries)}")
        lines.append("")
        
        # Missing entries
        missing = [c for c in citations if c not in bib_entries]
        if missing:
            lines.extend([
                "## ⚠️ Missing Bibliography Entries",
                "",
                "These citations are used but have no .bib entry:",
                ""
            ])
            for key in missing:
                lines.append(f"- `{key}`")
            lines.append("")
        
        # Verify existing entries
        lines.extend(["## Citation Verification", ""])
        
        unverified = []
        low_impact = []
        old_papers = []
        
        for key in citations:
            if key not in bib_entries:
                continue
            
            entry = bib_entries[key]
            
            # Get metrics
            metrics = self.get_citation_metrics(entry)
            if metrics:
                entry.citation_count = metrics.get('citation_count', 0)
            
            # Check quality
            if not entry.is_influential and entry.year < datetime.now().year - 5:
                low_impact.append((key, entry))
            
            if entry.year < datetime.now().year - 10:
                old_papers.append((key, entry))
        
        if low_impact:
            lines.extend([
                "## 📊 Low-Impact Citations",
                "",
                "These papers have low citation counts. Verify they're necessary:",
                ""
            ])
            for key, entry in low_impact[:10]:
                lines.append(f"- `{key}`: {entry.title} ({entry.year}, {entry.citation_count} citations)")
            lines.append("")
        
        if old_papers:
            lines.extend([
                "## 📅 Older References",
                "",
                "Consider supplementing with recent work (within 3 years):",
                ""
            ])
            for key, entry in old_papers[:10]:
                lines.append(f"- `{key}`: {entry.year}")
            lines.append("")
        
        # Quality summary
        lines.extend([
            "## Quality Summary",
            ""
        ])
        
        total_with_metrics = sum(1 for entry in bib_entries.values() if entry.citation_count > 0)
        avg_citations = sum(e.citation_count for e in bib_entries.values()) / len(bib_entries) if bib_entries else 0
        recent_count = sum(1 for e in bib_entries.values() if e.is_recent)
        influential_count = sum(1 for e in bib_entries.values() if e.is_influential)
        
        lines.append(f"- Average citations: {avg_citations:.1f}")
        lines.append(f"- Recent papers (≤3 years): {recent_count}/{len(bib_entries)}")
        lines.append(f"- Influential papers (100+ citations): {influential_count}/{len(bib_entries)}")
        lines.append("")
        
        return "\n".join(lines)


def main():
    """Bibliography manager CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Bibliography Manager")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate bibliography report"
    )
    parser.add_argument(
        "--generate",
        type=str,
        help="Generate bib entry from DOI or title"
    )
    parser.add_argument(
        "--suggest",
        nargs="+",
        help="Suggest papers for keywords (e.g., 'quantum entanglement' 'OTOC')"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify all citations"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Config not found: {args.config}")
        return 1
    
    config = PaperMaintenanceConfig.load(args.config)
    manager = BibliographyManager(config)
    
    if args.report:
        print(manager.generate_report())
    
    elif args.generate:
        # Try as DOI first, then title
        if '/' in args.generate:
            bib = manager.generate_bib_entry(doi=args.generate)
        else:
            bib = manager.generate_bib_entry(title=args.generate)
        
        if bib:
            print(bib)
        else:
            print("Could not generate bib entry")
    
    elif args.suggest:
        suggestions = manager.suggest_missing_papers(args.suggest)
        print(f"\nTop influential papers for: {', '.join(args.suggest)}\n")
        for i, paper in enumerate(suggestions, 1):
            print(f"{i}. {paper['title']}")
            print(f"   {', '.join(paper['authors'][:3])} ({paper['year']})")
            print(f"   {paper['venue']} - {paper['citations']} citations")
            if paper['doi']:
                print(f"   DOI: {paper['doi']}")
            print()
    
    elif args.verify:
        citations = manager.extract_citations()
        entries = manager.parse_bib_file()
        
        print(f"Verifying {len(citations)} citations...\n")
        for key in citations:
            if key in entries:
                verified, msg = manager.verify_citation_exists(key, entries[key])
                status = "✓" if verified else "✗"
                print(f"{status} {key}: {msg}")
            else:
                print(f"✗ {key}: Missing .bib entry")
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
