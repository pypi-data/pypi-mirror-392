#!/usr/bin/env python3
"""
LaTeX Paper Validation
Performs various checks on a LaTeX paper and returns results in JSON format
"""

import sys
import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse

class PaperValidator:
    """Validates LaTeX papers for common issues"""
    
    def __init__(self, paper_dir: str = "."):
        self.paper_dir = Path(paper_dir).resolve()
        self.checks = []
        self.results = {
            'status': 'UNKNOWN',
            'passed': 0,
            'failed': 0,
            'checks': []
        }
    
    def log_check(self, name: str, status: str, message: str):
        """Log a check result"""
        check = {
            'name': name,
            'status': status,
            'message': message
        }
        self.checks.append(check)
        self.results['checks'].append(check)
        
        if status == 'PASS':
            self.results['passed'] += 1
            print(f"✓ {name}: {message}")
        elif status == 'FAIL':
            self.results['failed'] += 1
            print(f"✗ {name}: {message}")
        else:
            print(f"⚠ {name}: {message}")
    
    def find_main_tex(self) -> Path:
        """Find the main .tex file"""
        # Look for main.tex first
        candidates = ['main.tex', 'paper.tex', 'manuscript.tex']
        
        for candidate in candidates:
            path = self.paper_dir / candidate
            if path.exists():
                return path
        
        # Find any .tex file that contains \documentclass
        for tex_file in self.paper_dir.glob('*.tex'):
            content = tex_file.read_text(errors='ignore')
            if r'\documentclass' in content:
                return tex_file
        
        raise FileNotFoundError("No main .tex file found")
    
    def check_compilation(self) -> Tuple[str, str]:
        """Check if paper compiles"""
        try:
            main_tex = self.find_main_tex()
        except FileNotFoundError as e:
            self.log_check("Compilation", "FAIL", str(e))
            return "FAIL", str(e)
        
        try:
            # Run pdflatex
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', main_tex.name],
                cwd=self.paper_dir,
                capture_output=True,
                timeout=60
            )
            
            # Check for PDF output
            pdf_file = main_tex.with_suffix('.pdf')
            if pdf_file.exists():
                self.log_check("Compilation", "PASS", f"PDF generated successfully: {pdf_file.name}")
                return "PASS", f"PDF generated: {pdf_file.name}"
            else:
                error_msg = "PDF not generated"
                if result.stderr:
                    error_msg += f": {result.stderr.decode('utf-8', errors='ignore')[:200]}"
                self.log_check("Compilation", "FAIL", error_msg)
                return "FAIL", error_msg
        
        except subprocess.TimeoutExpired:
            self.log_check("Compilation", "FAIL", "Compilation timeout")
            return "FAIL", "Compilation timeout"
        except Exception as e:
            self.log_check("Compilation", "FAIL", f"Compilation error: {str(e)}")
            return "FAIL", f"Compilation error: {str(e)}"
    
    def check_references(self) -> Tuple[str, str]:
        """Check that all \ref commands point to valid \label commands"""
        try:
            main_tex = self.find_main_tex()
            
            # Find all .tex files in directory
            tex_files = list(self.paper_dir.glob('*.tex'))
            
            # Collect all labels
            labels = set()
            refs = []
            
            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                
                # Find labels
                labels.update(re.findall(r'\\label\{([^}]+)\}', content))
                
                # Find refs
                refs.extend(re.findall(r'\\ref\{([^}]+)\}', content))
                refs.extend(re.findall(r'\\eqref\{([^}]+)\}', content))
            
            # Check for undefined refs
            undefined = [ref for ref in refs if ref not in labels]
            
            if undefined:
                self.log_check("References", "FAIL", f"Undefined references: {', '.join(set(undefined))}")
                return "FAIL", f"Undefined references: {', '.join(set(undefined))}"
            elif refs:
                self.log_check("References", "PASS", f"All {len(refs)} references valid")
                return "PASS", f"All {len(refs)} references valid"
            else:
                self.log_check("References", "WARN", "No references found")
                return "WARN", "No references found"
        
        except FileNotFoundError as e:
            self.log_check("References", "FAIL", str(e))
            return "FAIL", str(e)
        except Exception as e:
            self.log_check("References", "FAIL", f"Error checking references: {str(e)}")
            return "FAIL", f"Error: {str(e)}"
    
    def check_citations(self) -> Tuple[str, str]:
        """Check that all \cite commands match BibTeX entries"""
        try:
            main_tex = self.find_main_tex()
            
            # Find all .tex files
            tex_files = list(self.paper_dir.glob('*.tex'))
            
            # Find all .bib files
            bib_files = list(self.paper_dir.glob('*.bib'))
            
            if not bib_files:
                self.log_check("Citations", "WARN", "No BibTeX files found")
                return "WARN", "No .bib files found"
            
            # Collect all BibTeX keys
            bib_keys = set()
            for bib_file in bib_files:
                content = bib_file.read_text(errors='ignore')
                bib_keys.update(re.findall(r'@\w+\{([^,\s]+)', content))
            
            # Collect all citations
            citations = []
            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                # Match \cite{key1,key2,...}
                cite_matches = re.findall(r'\\cite[tp]?\{([^}]+)\}', content)
                for match in cite_matches:
                    citations.extend([k.strip() for k in match.split(',')])
            
            # Check for undefined citations
            undefined = [cite for cite in citations if cite not in bib_keys]
            
            if undefined:
                self.log_check("Citations", "FAIL", f"Undefined citations: {', '.join(set(undefined))}")
                return "FAIL", f"Undefined: {', '.join(set(undefined))}"
            elif citations:
                self.log_check("Citations", "PASS", f"All {len(citations)} citations found in bibliography")
                return "PASS", f"All {len(citations)} citations valid"
            else:
                self.log_check("Citations", "WARN", "No citations found")
                return "WARN", "No citations found"
        
        except FileNotFoundError as e:
            self.log_check("Citations", "FAIL", str(e))
            return "FAIL", str(e)
        except Exception as e:
            self.log_check("Citations", "FAIL", f"Error checking citations: {str(e)}")
            return "FAIL", f"Error: {str(e)}"
    
    def check_todos(self) -> Tuple[str, str]:
        """Check for TODO comments"""
        try:
            tex_files = list(self.paper_dir.glob('*.tex'))
            
            todos = []
            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                        # Skip commented lines
                        if not line.strip().startswith('%'):
                            todos.append(f"{tex_file.name}:{i}")
            
            if todos:
                self.log_check("TODOs", "WARN", f"Found {len(todos)} TODO/FIXME comments")
                return "WARN", f"Found {len(todos)} TODOs"
            else:
                self.log_check("TODOs", "PASS", "No TODO comments found")
                return "PASS", "No TODOs found"
        
        except Exception as e:
            self.log_check("TODOs", "FAIL", f"Error checking TODOs: {str(e)}")
            return "FAIL", f"Error: {str(e)}"
    
    def check_spelling(self) -> Tuple[str, str]:
        """Check spelling using aspell or hunspell"""
        try:
            # Check if aspell is available
            if subprocess.run(['which', 'aspell'], capture_output=True).returncode == 0:
                spellcheck_cmd = ['aspell', 'list']
            elif subprocess.run(['which', 'hunspell'], capture_output=True).returncode == 0:
                spellcheck_cmd = ['hunspell', '-l']
            else:
                self.log_check("Spelling", "SKIP", "No spell checker found (aspell/hunspell)")
                return "SKIP", "No spell checker available"
            
            tex_files = list(self.paper_dir.glob('*.tex'))
            
            all_errors = []
            for tex_file in tex_files:
                # Use aspell/hunspell to check
                result = subprocess.run(
                    spellcheck_cmd,
                    input=tex_file.read_text(errors='ignore'),
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    errors = result.stdout.strip().split('\n')
                    all_errors.extend(errors)
            
            unique_errors = set(all_errors)
            if len(unique_errors) > 10:
                self.log_check("Spelling", "WARN", f"Found {len(unique_errors)} potential spelling errors")
                return "WARN", f"{len(unique_errors)} potential errors"
            elif unique_errors:
                self.log_check("Spelling", "WARN", f"Found potential spelling errors: {', '.join(list(unique_errors)[:5])}")
                return "WARN", f"Found some errors"
            else:
                self.log_check("Spelling", "PASS", "No spelling errors found")
                return "PASS", "No errors found"
        
        except Exception as e:
            self.log_check("Spelling", "FAIL", f"Error checking spelling: {str(e)}")
            return "FAIL", f"Error: {str(e)}"
    
    def run_all_checks(self, 
                      enable_compilation: bool = True,
                      enable_references: bool = True,
                      enable_citations: bool = True,
                      enable_todos: bool = True,
                      enable_spelling: bool = False) -> Dict[str, Any]:
        """Run all enabled checks"""
        
        print("="*60)
        print(f"Validating paper: {self.paper_dir}")
        print("="*60)
        print()
        
        if enable_compilation:
            self.check_compilation()
        
        if enable_references:
            self.check_references()
        
        if enable_citations:
            self.check_citations()
        
        if enable_todos:
            self.check_todos()
        
        if enable_spelling:
            self.check_spelling()
        
        # Determine overall status
        if self.results['failed'] > 0:
            self.results['status'] = 'FAILED'
        else:
            self.results['status'] = 'PASSED'
        
        return self.results
    
    def save_results(self, output_file: str):
        """Save results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Validate LaTeX paper')
    parser.add_argument('--dir', default='.', help='Paper directory (default: current)')
    parser.add_argument('--output', help='Output JSON file for results')
    parser.add_argument('--no-compile', action='store_true', help='Skip compilation check')
    parser.add_argument('--no-refs', action='store_true', help='Skip reference check')
    parser.add_argument('--no-cites', action='store_true', help='Skip citation check')
    parser.add_argument('--no-todos', action='store_true', help='Skip TODO check')
    parser.add_argument('--check-spelling', action='store_true', help='Enable spelling check')
    
    args = parser.parse_args()
    
    validator = PaperValidator(args.dir)
    
    results = validator.run_all_checks(
        enable_compilation=not args.no_compile,
        enable_references=not args.no_refs,
        enable_citations=not args.no_cites,
        enable_todos=not args.no_todos,
        enable_spelling=args.check_spelling
    )
    
    # Print summary
    print()
    print("="*60)
    print(f"SUMMARY: {results['passed']} passed, {results['failed']} failed")
    print("="*60)
    
    # Save results if requested
    if args.output:
        validator.save_results(args.output)
        print(f"\nResults saved to: {args.output}")
    
    # Exit with error code if any checks failed
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
