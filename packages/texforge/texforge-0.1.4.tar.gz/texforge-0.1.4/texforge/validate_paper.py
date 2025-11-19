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
    
    def parse_log_file(self, log_file: Path) -> Dict[str, List[str]]:
        """Parse LaTeX log file for errors and warnings"""
        if not log_file.exists():
            return {'errors': [], 'warnings': [], 'overfull': [], 'underfull': []}

        content = log_file.read_text(errors='ignore')
        lines = content.split('\n')

        errors = []
        warnings = []
        overfull = []
        underfull = []

        for i, line in enumerate(lines):
            # Fatal errors
            if line.startswith('!'):
                # Get context (next few lines)
                context = ' '.join(lines[i:i+3]).replace('\n', ' ')[:100]
                errors.append(context)

            # Undefined references/citations
            elif 'undefined' in line.lower() and ('reference' in line.lower() or 'citation' in line.lower()):
                warnings.append(line.strip())

            # Overfull boxes (bad layout)
            elif line.startswith('Overfull'):
                overfull.append(line.strip())

            # Underfull boxes
            elif line.startswith('Underfull'):
                underfull.append(line.strip())

        return {
            'errors': errors[:10],  # Limit to first 10
            'warnings': warnings[:10],
            'overfull': overfull[:5],
            'underfull': underfull[:5]
        }

    def check_compilation(self, full_build: bool = True) -> Tuple[str, str]:
        """Check if paper compiles with optional full build (including bibtex)"""
        try:
            main_tex = self.find_main_tex()
        except FileNotFoundError as e:
            self.log_check("Compilation", "FAIL", str(e))
            return "FAIL", str(e)

        try:
            base_name = main_tex.stem
            pdf_file = main_tex.with_suffix('.pdf')
            log_file = main_tex.with_suffix('.log')

            # Check if bibtex/biber is needed
            has_bibliography = False
            bib_files = list(self.paper_dir.glob('*.bib'))
            if bib_files:
                content = main_tex.read_text(errors='ignore')
                has_bibliography = r'\bibliography' in content or r'\addbibresource' in content

            if full_build and has_bibliography:
                # Full build: pdflatex -> bibtex -> pdflatex -> pdflatex
                steps = [
                    (['pdflatex', '-interaction=nonstopmode', main_tex.name], 'First pdflatex'),
                    (['bibtex', base_name], 'BibTeX'),
                    (['pdflatex', '-interaction=nonstopmode', main_tex.name], 'Second pdflatex'),
                    (['pdflatex', '-interaction=nonstopmode', main_tex.name], 'Third pdflatex'),
                ]
            else:
                # Single run
                steps = [
                    (['pdflatex', '-interaction=nonstopmode', main_tex.name], 'pdflatex'),
                ]

            # Run compilation steps
            for cmd, description in steps:
                result = subprocess.run(
                    cmd,
                    cwd=self.paper_dir,
                    capture_output=True,
                    timeout=60
                )
                # BibTeX failures are often non-fatal, continue
                if result.returncode != 0 and 'bibtex' not in cmd[0]:
                    # Check if PDF was still generated
                    if not pdf_file.exists():
                        break

            # Check for PDF output
            if pdf_file.exists():
                # Parse log for issues
                log_info = self.parse_log_file(log_file)

                if log_info['errors']:
                    msg = f"PDF generated but with errors: {log_info['errors'][0][:80]}"
                    self.log_check("Compilation", "WARN", msg)
                    return "WARN", "PDF generated with errors"
                elif log_info['warnings']:
                    msg = f"PDF generated successfully (with {len(log_info['warnings'])} warnings)"
                    self.log_check("Compilation", "PASS", msg)
                    return "PASS", f"PDF generated: {pdf_file.name}"
                else:
                    self.log_check("Compilation", "PASS", f"PDF generated successfully: {pdf_file.name}")
                    return "PASS", f"PDF generated: {pdf_file.name}"
            else:
                # Parse log for specific error
                log_info = self.parse_log_file(log_file)
                error_msg = "PDF not generated"
                if log_info['errors']:
                    error_msg += f": {log_info['errors'][0][:100]}"

                self.log_check("Compilation", "FAIL", error_msg)
                return "FAIL", error_msg

        except subprocess.TimeoutExpired:
            self.log_check("Compilation", "FAIL", "Compilation timeout (>60s)")
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
            ref_locations = {}  # Track where each ref is used

            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')

                # Find labels
                labels.update(re.findall(r'\\label\{([^}]+)\}', content))

                # Find refs with location tracking
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    # Find all reference commands
                    for ref_cmd in [r'\\ref\{([^}]+)\}', r'\\eqref\{([^}]+)\}', r'\\cref\{([^}]+)\}', r'\\Cref\{([^}]+)\}']:
                        for match in re.finditer(ref_cmd, line):
                            ref = match.group(1)
                            refs.append(ref)
                            if ref not in ref_locations:
                                ref_locations[ref] = []
                            ref_locations[ref].append({
                                'file': tex_file.name,
                                'line': line_num,
                                'context': line.strip()[:80]
                            })

            # Check for undefined refs
            undefined = [ref for ref in set(refs) if ref not in labels]

            if undefined:
                # Build detailed error message with locations
                error_details = []
                for ref in undefined[:5]:  # Limit to first 5 for readability
                    locations = ref_locations.get(ref, [])
                    if locations:
                        loc = locations[0]
                        error_details.append(f"{ref} at {loc['file']}:{loc['line']}")

                error_msg = f"Undefined references: {', '.join(error_details)}"
                if len(undefined) > 5:
                    error_msg += f" (and {len(undefined) - 5} more)"

                self.log_check("References", "FAIL", error_msg)
                return "FAIL", f"Undefined: {', '.join(undefined)}"
            elif refs:
                self.log_check("References", "PASS", f"All {len(refs)} references valid ({len(labels)} labels defined)")
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

            # Collect all citations with location tracking
            citations = []
            cite_locations = {}

            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    # Match various cite commands: \cite, \citep, \citet, \citealp, etc.
                    for cite_match in re.finditer(r'\\cite[a-z]*\{([^}]+)\}', line):
                        cite_keys = [k.strip() for k in cite_match.group(1).split(',')]
                        for key in cite_keys:
                            citations.append(key)
                            if key not in cite_locations:
                                cite_locations[key] = []
                            cite_locations[key].append({
                                'file': tex_file.name,
                                'line': line_num,
                                'context': line.strip()[:80]
                            })

            # Check for undefined citations
            undefined = [cite for cite in set(citations) if cite not in bib_keys]

            if undefined:
                # Build detailed error message with locations
                error_details = []
                for cite in undefined[:5]:  # Limit to first 5 for readability
                    locations = cite_locations.get(cite, [])
                    if locations:
                        loc = locations[0]
                        error_details.append(f"{cite} at {loc['file']}:{loc['line']}")

                error_msg = f"Undefined citations: {', '.join(error_details)}"
                if len(undefined) > 5:
                    error_msg += f" (and {len(undefined) - 5} more)"

                self.log_check("Citations", "FAIL", error_msg)
                return "FAIL", f"Undefined: {', '.join(undefined)}"
            elif citations:
                self.log_check("Citations", "PASS", f"All {len(citations)} citations found in {len(bib_files)} bibliography file(s)")
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
    
    def check_figures_tables(self) -> Tuple[str, str]:
        """Check that all figure/table files exist and references are valid"""
        try:
            tex_files = list(self.paper_dir.glob('*.tex'))

            issues = []
            total_figures = 0
            total_tables = 0

            # Common image extensions
            image_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.eps', '.svg']

            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    # Skip commented lines
                    if line.strip().startswith('%'):
                        continue

                    # Check \includegraphics
                    for match in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', line):
                        total_figures += 1
                        fig_path = match.group(1)

                        # Try to find the file with various extensions
                        found = False
                        for ext in [''] + image_extensions:
                            test_path = self.paper_dir / (fig_path + ext)
                            if test_path.exists():
                                found = True
                                break

                        if not found:
                            issues.append(f"Missing figure: {fig_path} at {tex_file.name}:{line_num}")

            # Count tables (just for statistics)
            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                total_tables += len(re.findall(r'\\begin\{table\}', content))

            if issues:
                self.log_check("Figures/Tables", "FAIL", f"Found {len(issues)} missing figure(s): {issues[0] if issues else ''}")
                return "FAIL", f"{len(issues)} missing figures"
            elif total_figures > 0 or total_tables > 0:
                self.log_check("Figures/Tables", "PASS", f"All figures exist ({total_figures} figures, {total_tables} tables)")
                return "PASS", f"{total_figures} figures, {total_tables} tables OK"
            else:
                self.log_check("Figures/Tables", "WARN", "No figures or tables found")
                return "WARN", "No figures/tables found"

        except Exception as e:
            self.log_check("Figures/Tables", "FAIL", f"Error checking figures/tables: {str(e)}")
            return "FAIL", f"Error: {str(e)}"

    def check_math_environments(self) -> Tuple[str, str]:
        """Check for balanced math delimiters and environments"""
        try:
            tex_files = list(self.paper_dir.glob('*.tex'))

            issues = []

            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                lines = content.split('\n')

                # Check for deprecated $$ usage
                for line_num, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('%'):
                        continue
                    if '$$' in line:
                        issues.append(f"Deprecated $$ at {tex_file.name}:{line_num} (use \\[...\\] instead)")

                # Remove comments for analysis
                content_no_comments = '\n'.join(
                    line.split('%')[0] if not line.strip().startswith('%') else ''
                    for line in lines
                )

                # Count single $ delimiters (should be even)
                dollar_count = content_no_comments.count('$')
                # Subtract $$ occurrences (already counted as 2 single $)
                dollar_count -= 2 * content_no_comments.count('$$')

                if dollar_count % 2 != 0:
                    issues.append(f"Unbalanced $ delimiters in {tex_file.name} (found {dollar_count})")

                # Check balanced environments
                math_envs = ['equation', 'align', 'gather', 'multline', 'eqnarray',
                            'equation*', 'align*', 'gather*', 'multline*']

                for env in math_envs:
                    begin_count = len(re.findall(rf'\\begin\{{{env}\}}', content_no_comments))
                    end_count = len(re.findall(rf'\\end\{{{env}\}}', content_no_comments))

                    if begin_count != end_count:
                        issues.append(f"Unbalanced {env} environment in {tex_file.name} ({begin_count} begin, {end_count} end)")

                # Check \[ and \] balance
                bracket_open = content_no_comments.count(r'\[')
                bracket_close = content_no_comments.count(r'\]')
                if bracket_open != bracket_close:
                    issues.append(f"Unbalanced \\[...\\] in {tex_file.name} ({bracket_open} open, {bracket_close} close)")

                # Check \( and \) balance
                paren_open = content_no_comments.count(r'\(')
                paren_close = content_no_comments.count(r'\)')
                if paren_open != paren_close:
                    issues.append(f"Unbalanced \\(...\\) in {tex_file.name} ({paren_open} open, {paren_close} close)")

            if issues:
                self.log_check("Math Environments", "FAIL", f"Found {len(issues)} issue(s): {issues[0] if issues else ''}")
                return "FAIL", f"{len(issues)} math issues"
            else:
                self.log_check("Math Environments", "PASS", "All math environments balanced")
                return "PASS", "All math balanced"

        except Exception as e:
            self.log_check("Math Environments", "FAIL", f"Error checking math: {str(e)}")
            return "FAIL", f"Error: {str(e)}"

    def check_todos(self) -> Tuple[str, str]:
        """Check for TODO comments in LaTeX files"""
        try:
            tex_files = list(self.paper_dir.glob('*.tex'))

            todos = []
            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    # TODOs should be in comments - check if line is commented
                    if stripped.startswith('%') and ('TODO' in stripped or 'FIXME' in stripped or 'XXX' in stripped):
                        # Extract the TODO text for better reporting
                        todo_text = stripped[1:].strip()[:50]  # Remove % and get first 50 chars
                        todos.append(f"{tex_file.name}:{i}: {todo_text}")

            if todos:
                self.log_check("TODOs", "WARN", f"Found {len(todos)} TODO/FIXME comments: {todos[0] if todos else ''}")
                return "WARN", f"Found {len(todos)} TODOs"
            else:
                self.log_check("TODOs", "PASS", "No TODO comments found")
                return "PASS", "No TODOs found"

        except Exception as e:
            self.log_check("TODOs", "FAIL", f"Error checking TODOs: {str(e)}")
            return "FAIL", f"Error: {str(e)}"
    
    def check_packages(self) -> Tuple[str, str]:
        """Check that all required LaTeX packages are available"""
        try:
            tex_files = list(self.paper_dir.glob('*.tex'))

            packages = set()
            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')
                # Find all \usepackage commands
                for match in re.finditer(r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}', content):
                    # Handle multiple packages in one command: \usepackage{pkg1,pkg2}
                    pkg_list = [pkg.strip() for pkg in match.group(1).split(',')]
                    packages.update(pkg_list)

            if not packages:
                self.log_check("Packages", "WARN", "No packages found")
                return "WARN", "No packages"

            # Check if kpsewhich is available (comes with TeX distributions)
            if subprocess.run(['which', 'kpsewhich'], capture_output=True).returncode != 0:
                self.log_check("Packages", "SKIP", "kpsewhich not found (cannot verify packages)")
                return "SKIP", "Cannot verify packages"

            # Check each package
            missing = []
            for pkg in packages:
                result = subprocess.run(
                    ['kpsewhich', f'{pkg}.sty'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    missing.append(pkg)

            if missing:
                self.log_check("Packages", "FAIL", f"Missing packages: {', '.join(missing[:5])}")
                return "FAIL", f"{len(missing)} missing packages"
            else:
                self.log_check("Packages", "PASS", f"All {len(packages)} packages available")
                return "PASS", f"{len(packages)} packages OK"

        except subprocess.TimeoutExpired:
            self.log_check("Packages", "FAIL", "Package check timeout")
            return "FAIL", "Timeout"
        except Exception as e:
            self.log_check("Packages", "FAIL", f"Error checking packages: {str(e)}")
            return "FAIL", f"Error: {str(e)}"

    def check_layout(self) -> Tuple[str, str]:
        """Check for overfull/underfull boxes in compilation log"""
        try:
            main_tex = self.find_main_tex()
            log_file = main_tex.with_suffix('.log')

            if not log_file.exists():
                self.log_check("Layout", "SKIP", "No log file found (compile first)")
                return "SKIP", "No log file"

            log_info = self.parse_log_file(log_file)

            overfull_count = len(log_info['overfull'])
            underfull_count = len(log_info['underfull'])

            # Overfull boxes are more serious than underfull
            if overfull_count > 10:
                self.log_check("Layout", "WARN", f"Found {overfull_count} overfull boxes (text extends into margins)")
                return "WARN", f"{overfull_count} overfull boxes"
            elif overfull_count > 0:
                msg = f"Found {overfull_count} overfull box(es): {log_info['overfull'][0][:60]}"
                self.log_check("Layout", "WARN", msg)
                return "WARN", f"{overfull_count} overfull boxes"
            elif underfull_count > 20:
                self.log_check("Layout", "WARN", f"Found {underfull_count} underfull boxes (poor spacing)")
                return "WARN", f"{underfull_count} underfull boxes"
            elif underfull_count > 0:
                self.log_check("Layout", "PASS", f"Minor layout issues: {underfull_count} underfull boxes")
                return "PASS", "Minor issues"
            else:
                self.log_check("Layout", "PASS", "No layout issues detected")
                return "PASS", "No layout issues"

        except FileNotFoundError as e:
            self.log_check("Layout", "SKIP", str(e))
            return "SKIP", str(e)
        except Exception as e:
            self.log_check("Layout", "FAIL", f"Error checking layout: {str(e)}")
            return "FAIL", f"Error: {str(e)}"

    def strip_latex_commands(self, content: str) -> str:
        """Remove LaTeX commands and environments to get plain text"""
        # Remove comments
        lines = content.split('\n')
        no_comments = '\n'.join(
            line.split('%')[0] if not line.strip().startswith('%') else ''
            for line in lines
        )

        # Remove common LaTeX commands (keep the text inside braces)
        text = re.sub(r'\\(?:textbf|textit|emph|underline|textrm|texttt)\{([^}]+)\}', r'\1', no_comments)

        # Remove citations and references
        text = re.sub(r'\\(?:cite|ref|eqref|label)\{[^}]+\}', '', text)

        # Remove section commands but keep titles
        text = re.sub(r'\\(?:section|subsection|subsubsection|paragraph)\*?\{([^}]+)\}', r'\1', text)

        # Remove math environments
        text = re.sub(r'\$[^$]+\$', '', text)  # Inline math
        text = re.sub(r'\\\[.*?\\\]', '', text, flags=re.DOTALL)  # Display math
        text = re.sub(r'\\begin\{(?:equation|align|gather)[^}]*\}.*?\\end\{(?:equation|align|gather)[^}]*\}', '', text, flags=re.DOTALL)

        # Remove other common commands
        text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{[^}]*\}', '', text)
        text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remove remaining commands

        # Remove special characters
        text = re.sub(r'[{}\\$]', ' ', text)

        return text

    def check_spelling(self) -> Tuple[str, str]:
        """Check spelling using aspell or hunspell with LaTeX awareness"""
        try:
            # Check if aspell is available (prefer aspell with TeX mode)
            has_aspell = subprocess.run(['which', 'aspell'], capture_output=True).returncode == 0
            has_hunspell = subprocess.run(['which', 'hunspell'], capture_output=True).returncode == 0

            if not has_aspell and not has_hunspell:
                self.log_check("Spelling", "SKIP", "No spell checker found (install aspell or hunspell)")
                return "SKIP", "No spell checker available"

            tex_files = list(self.paper_dir.glob('*.tex'))

            all_errors = []
            for tex_file in tex_files:
                content = tex_file.read_text(errors='ignore')

                if has_aspell:
                    # Use aspell in TeX mode (understands LaTeX commands)
                    result = subprocess.run(
                        ['aspell', '--mode=tex', '--list', '--lang=en'],
                        input=content,
                        capture_output=True,
                        text=True
                    )
                else:
                    # Fallback: manually strip LaTeX commands for hunspell
                    stripped_content = self.strip_latex_commands(content)
                    result = subprocess.run(
                        ['hunspell', '-l'],
                        input=stripped_content,
                        capture_output=True,
                        text=True
                    )

                if result.stdout:
                    errors = [e for e in result.stdout.strip().split('\n') if e]
                    all_errors.extend(errors)

            # Filter out common false positives
            common_terms = {'et', 'al', 'fig', 'eq', 'arxiv', 'doi', 'http', 'https', 'www'}
            filtered_errors = [e for e in all_errors if e.lower() not in common_terms and len(e) > 2]

            unique_errors = set(filtered_errors)

            if len(unique_errors) > 20:
                self.log_check("Spelling", "WARN", f"Found {len(unique_errors)} potential spelling errors")
                return "WARN", f"{len(unique_errors)} potential errors"
            elif len(unique_errors) > 10:
                self.log_check("Spelling", "WARN", f"Found {len(unique_errors)} potential errors: {', '.join(list(unique_errors)[:3])}")
                return "WARN", f"{len(unique_errors)} potential errors"
            elif unique_errors:
                self.log_check("Spelling", "PASS", f"Found {len(unique_errors)} minor spelling issues")
                return "PASS", f"{len(unique_errors)} minor issues"
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
                      enable_figures: bool = True,
                      enable_math: bool = True,
                      enable_packages: bool = True,
                      enable_layout: bool = True,
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

        if enable_figures:
            self.check_figures_tables()

        if enable_math:
            self.check_math_environments()

        if enable_packages:
            self.check_packages()

        if enable_layout:
            self.check_layout()

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
    parser.add_argument('--no-figures', action='store_true', help='Skip figure/table check')
    parser.add_argument('--no-math', action='store_true', help='Skip math environment check')
    parser.add_argument('--no-packages', action='store_true', help='Skip package dependencies check')
    parser.add_argument('--no-layout', action='store_true', help='Skip layout (overfull/underfull) check')
    parser.add_argument('--no-todos', action='store_true', help='Skip TODO check')
    parser.add_argument('--check-spelling', action='store_true', help='Enable spelling check')

    args = parser.parse_args()

    validator = PaperValidator(args.dir)

    results = validator.run_all_checks(
        enable_compilation=not args.no_compile,
        enable_references=not args.no_refs,
        enable_citations=not args.no_cites,
        enable_figures=not args.no_figures,
        enable_math=not args.no_math,
        enable_packages=not args.no_packages,
        enable_layout=not args.no_layout,
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
