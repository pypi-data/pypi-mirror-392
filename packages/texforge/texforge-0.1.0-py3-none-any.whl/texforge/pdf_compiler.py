#!/usr/bin/env python3
"""
Enhanced PDF Compilation System
- Supports custom templates
- Manages LaTeX macros
- Ensures error-free compilation
- Suggests macro definitions for frequently used patterns
"""
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter
from dataclasses import dataclass

from .config import PaperMaintenanceConfig


@dataclass
class CompilationResult:
    """Result of LaTeX compilation"""
    success: bool
    pdf_path: Optional[Path]
    errors: List[str]
    warnings: List[str]
    log_file: Path
    
    # Compilation metrics
    pages: int = 0
    compile_time: float = 0.0
    passes_needed: int = 0


@dataclass
class MacroSuggestion:
    """Suggested macro definition"""
    name: str
    pattern: str
    frequency: int
    suggested_definition: str
    rationale: str


class PDFCompiler:
    """Enhanced LaTeX PDF compiler"""
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.paper_dir = config.paper_directory
        self.main_tex = self._find_main_tex()
        self.macros_file = self.paper_dir / "macros.tex"
        self.template_file = self.paper_dir / "template.tex"
    
    def _find_main_tex(self) -> Optional[Path]:
        """Find main .tex file"""
        # Try config setting first
        if self.config.main_tex_file:
            main = self.paper_dir / self.config.main_tex_file
            if main.exists():
                return main
        
        # Common main file names
        for name in ["main.tex", "paper.tex", "manuscript.tex"]:
            candidate = self.paper_dir / name
            if candidate.exists():
                return candidate
        
        # Find .tex file with \documentclass
        for tex_file in self.paper_dir.glob("*.tex"):
            content = tex_file.read_text()
            if r'\documentclass' in content:
                return tex_file
        
        return None
    
    def setup_template(self, journal: str = "pra") -> Path:
        """Setup LaTeX template for target journal"""
        templates = {
            "pra": self._get_pra_template(),
            "prl": self._get_prl_template(),
            "generic": self._get_generic_template()
        }
        
        template = templates.get(journal.lower(), templates["generic"])
        
        if not self.template_file.exists():
            self.template_file.write_text(template)
            print(f"✓ Created template: {self.template_file}")
        
        return self.template_file
    
    def _get_pra_template(self) -> str:
        """Physical Review A template"""
        return r"""%% Physical Review A Template
\documentclass[aps,pra,twocolumn,superscriptaddress]{revtex4-2}

%% Essential packages
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{braket}  % For quantum notation

%% Load custom macros
\input{macros}

\begin{document}

\title{Your Title}

\author{Author Name}
\affiliation{Institution}

\date{\today}

\begin{abstract}
Your abstract here.
\end{abstract}

\maketitle

%% Include sections
\input{introduction}
\input{methods}
\input{results}
\input{conclusion}

\bibliography{references}

\end{document}
"""
    
    def _get_prl_template(self) -> str:
        """Physical Review Letters template"""
        return r"""%% Physical Review Letters Template
\documentclass[aps,prl,twocolumn,superscriptaddress]{revtex4-2}

%% Essential packages
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{braket}

%% Load custom macros
\input{macros}

\begin{document}

\title{Your Title}

\author{Author Name}
\affiliation{Institution}

\date{\today}

\begin{abstract}
Your abstract here (max 600 characters).
\end{abstract}

\maketitle

%% Main text (approximately 4 pages)
\input{main}

\bibliography{references}

\end{document}
"""
    
    def _get_generic_template(self) -> str:
        """Generic template"""
        return r"""%% Generic LaTeX Template
\documentclass[11pt,a4paper]{article}

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}

%% Load custom macros
\input{macros}

\title{Your Title}
\author{Author Name}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
Your abstract.
\end{abstract}

%% Include sections
\input{introduction}
\input{methods}
\input{results}
\input{conclusion}

\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""
    
    def setup_macros(self, include_common: bool = True) -> Path:
        """Setup macros.tex file"""
        if self.macros_file.exists():
            print(f"Macros file already exists: {self.macros_file}")
            return self.macros_file
        
        macros = []
        
        if include_common:
            macros.extend([
                "%% Common Mathematical Macros",
                "",
                "% Quantum mechanics",
                r"\newcommand{\ket}[1]{|#1\rangle}",
                r"\newcommand{\bra}[1]{\langle#1|}",
                r"\newcommand{\braket}[2]{\langle#1|#2\rangle}",
                r"\newcommand{\ketbra}[2]{|#1\rangle\langle#2|}",
                "",
                "% Operators",
                r"\newcommand{\op}[1]{\hat{#1}}",
                r"\newcommand{\Ham}{\op{H}}  % Hamiltonian",
                r"\newcommand{\identity}{\mathbb{I}}",
                "",
                "% States and vectors",
                r"\newcommand{\psi}{\psi}",
                r"\newcommand{\rho}{\rho}",
                "",
                "% Common sets",
                r"\newcommand{\R}{\mathbb{R}}",
                r"\newcommand{\C}{\mathbb{C}}",
                r"\newcommand{\N}{\mathbb{N}}",
                "",
                "% Derivatives",
                r"\newcommand{\dd}{\mathrm{d}}",
                r"\newcommand{\pd}[2]{\frac{\partial #1}{\partial #2}}",
                "",
                "% Miscellaneous",
                r"\newcommand{\abs}[1]{|#1|}",
                r"\newcommand{\norm}[1]{\|#1\|}",
                r"\newcommand{\avg}[1]{\langle#1\rangle}",
                "",
                "%%% Add your custom macros below %%%",
                "",
            ])
        else:
            macros.extend([
                "%% Custom LaTeX Macros",
                "",
                "%%% Add your macros here %%%",
                "",
            ])
        
        self.macros_file.write_text("\n".join(macros))
        print(f"✓ Created macros file: {self.macros_file}")
        
        return self.macros_file
    
    def analyze_macro_usage(self) -> List[MacroSuggestion]:
        """Analyze paper and suggest macro definitions"""
        suggestions = []
        
        # Collect all math expressions from .tex files
        math_patterns = []
        
        for tex_file in self.paper_dir.glob("*.tex"):
            content = tex_file.read_text()
            
            # Extract math mode content
            # Inline math: $...$
            inline_math = re.findall(r'\$([^\$]+)\$', content)
            math_patterns.extend(inline_math)
            
            # Display math: \[...\] or $$...$$
            display_math = re.findall(r'\\\[([^\]]+)\\\]|\$\$([^\$]+)\$\$', content)
            math_patterns.extend([m[0] or m[1] for m in display_math])
        
        # Count frequent patterns
        pattern_counter = Counter(math_patterns)
        
        # Suggest macros for frequent patterns
        for pattern, count in pattern_counter.most_common(20):
            if count >= 3:  # Used at least 3 times
                suggestion = self._suggest_macro_for_pattern(pattern, count)
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _suggest_macro_for_pattern(self, pattern: str, frequency: int) -> Optional[MacroSuggestion]:
        """Suggest macro for a specific pattern"""
        pattern = pattern.strip()
        
        # Skip simple patterns
        if len(pattern) < 5:
            return None
        
        # Common patterns
        suggestions_map = {
            r'\langle \psi |': MacroSuggestion(
                name="brapsi",
                pattern=pattern,
                frequency=frequency,
                suggested_definition=r"\newcommand{\brapsi}{\langle\psi|}",
                rationale="Frequently used bra notation"
            ),
            r'| \psi \rangle': MacroSuggestion(
                name="ketpsi",
                pattern=pattern,
                frequency=frequency,
                suggested_definition=r"\newcommand{\ketpsi}{|\psi\rangle}",
                rationale="Frequently used ket notation"
            ),
            r'\hat{H}': MacroSuggestion(
                name="Ham",
                pattern=pattern,
                frequency=frequency,
                suggested_definition=r"\newcommand{\Ham}{\hat{H}}",
                rationale="Hamiltonian operator"
            ),
        }
        
        # Check if pattern matches known suggestions
        for known_pattern, suggestion in suggestions_map.items():
            if re.search(re.escape(known_pattern), pattern):
                suggestion.frequency = frequency
                return suggestion
        
        # Generic suggestion for repeated complex expressions
        if frequency >= 5 and len(pattern) > 15:
            # Generate macro name from pattern
            name = self._generate_macro_name(pattern)
            return MacroSuggestion(
                name=name,
                pattern=pattern,
                frequency=frequency,
                suggested_definition=f"\\newcommand{{\\{name}}}{{{pattern}}}",
                rationale=f"Used {frequency} times - consider defining as macro"
            )
        
        return None
    
    def _generate_macro_name(self, pattern: str) -> str:
        """Generate reasonable macro name from pattern"""
        # Extract main command or symbol
        match = re.search(r'\\([a-zA-Z]+)', pattern)
        if match:
            return match.group(1) + "expr"
        return "customexpr"
    
    def compile(self, clean: bool = True) -> CompilationResult:
        """Compile LaTeX to PDF"""
        if not self.main_tex:
            return CompilationResult(
                success=False,
                pdf_path=None,
                errors=["No main .tex file found"],
                warnings=[],
                log_file=None
            )
        
        errors = []
        warnings = []
        
        # Compile multiple times for references
        passes = ["pdflatex", "bibtex", "pdflatex", "pdflatex"]
        
        import time
        start_time = time.time()
        
        for i, command in enumerate(passes, 1):
            try:
                if command == "bibtex":
                    # Run bibtex on .aux file
                    aux_file = self.main_tex.stem
                    result = subprocess.run(
                        ["bibtex", aux_file],
                        cwd=self.paper_dir,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                else:
                    # Run pdflatex
                    result = subprocess.run(
                        [command, "-interaction=nonstopmode", 
                         "-file-line-error", str(self.main_tex.name)],
                        cwd=self.paper_dir,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                
                # Parse output for errors and warnings
                for line in result.stdout.split('\n'):
                    # Check for warnings first (to avoid false positives from '!' in warnings)
                    if 'Warning' in line:
                        warnings.append(line.strip())
                    # Only count actual errors (lines starting with '!' or containing 'Error:')
                    elif line.strip().startswith('!') or 'Error:' in line or ') Error' in line:
                        errors.append(line.strip())
                
            except subprocess.TimeoutExpired:
                errors.append(f"{command} timed out")
                break
            except Exception as e:
                errors.append(f"{command} failed: {e}")
                break
        
        compile_time = time.time() - start_time
        
        # Check if PDF was generated
        pdf_path = self.paper_dir / self.main_tex.with_suffix('.pdf').name
        success = pdf_path.exists() and len(errors) == 0
        
        # Get page count
        pages = 0
        if success:
            try:
                result = subprocess.run(
                    ["pdfinfo", str(pdf_path)],
                    capture_output=True,
                    text=True
                )
                match = re.search(r'Pages:\s*(\d+)', result.stdout)
                if match:
                    pages = int(match.group(1))
            except:
                pass
        
        # Clean auxiliary files
        if clean:
            for ext in ['.aux', '.log', '.bbl', '.blg', '.out', '.toc']:
                aux_file = self.main_tex.with_suffix(ext)
                if aux_file.exists():
                    try:
                        aux_file.unlink()
                    except:
                        pass
        
        log_file = self.main_tex.with_suffix('.log')
        
        return CompilationResult(
            success=success,
            pdf_path=pdf_path if success else None,
            errors=errors[:10],  # Limit to first 10
            warnings=warnings[:10],
            log_file=log_file if log_file.exists() else None,
            pages=pages,
            compile_time=compile_time,
            passes_needed=len(passes)
        )
    
    def fix_common_errors(self) -> List[str]:
        """Attempt to fix common LaTeX errors"""
        fixes_applied = []
        
        if not self.main_tex:
            return fixes_applied
        
        content = self.main_tex.read_text()
        modified = False
        
        # Fix: Missing \end{document}
        if r'\begin{document}' in content and r'\end{document}' not in content:
            content += "\n\\end{document}\n"
            fixes_applied.append("Added missing \\end{document}")
            modified = True
        
        # Fix: Missing packages for common commands
        packages_needed = {
            r'\bra{': 'braket',
            r'\ket{': 'braket',
            r'\includegraphics': 'graphicx',
            r'\href{': 'hyperref',
        }
        
        for command, package in packages_needed.items():
            if command in content and f'usepackage{{{package}}}' not in content:
                # Add package after \documentclass
                content = re.sub(
                    r'(\\documentclass\{[^}]+\})',
                    f'\\1\n\\usepackage{{{package}}}',
                    content,
                    count=1
                )
                fixes_applied.append(f"Added \\usepackage{{{package}}}")
                modified = True
        
        if modified:
            # Backup original
            backup = self.main_tex.with_suffix('.tex.bak')
            backup.write_text(self.main_tex.read_text())
            
            # Write fixed version
            self.main_tex.write_text(content)
            fixes_applied.append(f"Original backed up to {backup.name}")
        
        return fixes_applied


def main():
    """PDF Compiler CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced PDF Compiler")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile LaTeX to PDF"
    )
    parser.add_argument(
        "--setup-template",
        type=str,
        choices=["pra", "prl", "generic"],
        help="Setup journal template"
    )
    parser.add_argument(
        "--setup-macros",
        action="store_true",
        help="Setup macros.tex file"
    )
    parser.add_argument(
        "--suggest-macros",
        action="store_true",
        help="Suggest macro definitions"
    )
    parser.add_argument(
        "--fix-errors",
        action="store_true",
        help="Attempt to fix common errors"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Config not found: {args.config}")
        return 1
    
    config = PaperMaintenanceConfig.load(args.config)
    compiler = PDFCompiler(config)
    
    if args.setup_template:
        compiler.setup_template(args.setup_template)
        print(f"\n✓ Template created for {args.setup_template.upper()}")
        print(f"  Edit {compiler.template_file} to customize")
    
    elif args.setup_macros:
        compiler.setup_macros()
        print(f"\n✓ Macros file created")
        print(f"  Add your custom macros to {compiler.macros_file}")
    
    elif args.suggest_macros:
        print("Analyzing paper for frequently used patterns...\n")
        suggestions = compiler.analyze_macro_usage()
        
        if suggestions:
            print("Suggested macro definitions:")
            print("=" * 60)
            for i, sugg in enumerate(suggestions, 1):
                print(f"\n{i}. Pattern used {sugg.frequency} times:")
                print(f"   {sugg.pattern}")
                print(f"   Suggestion: {sugg.suggested_definition}")
                print(f"   Rationale: {sugg.rationale}")
            
            print("\n" + "=" * 60)
            print(f"\nAdd these to {compiler.macros_file}")
        else:
            print("No macro suggestions found.")
    
    elif args.fix_errors:
        print("Attempting to fix common errors...")
        fixes = compiler.fix_common_errors()
        
        if fixes:
            for fix in fixes:
                print(f"✓ {fix}")
        else:
            print("No fixes needed")
    
    elif args.compile:
        print(f"Compiling {compiler.main_tex}...\n")
        result = compiler.compile()
        
        if result.success:
            print(f"✅ Compilation successful!")
            print(f"   PDF: {result.pdf_path}")
            print(f"   Pages: {result.pages}")
            print(f"   Time: {result.compile_time:.1f}s")
            
            if result.warnings:
                print(f"\n⚠️  {len(result.warnings)} warnings:")
                for warning in result.warnings[:5]:
                    print(f"   {warning}")
        else:
            print(f"❌ Compilation failed")
            print(f"\nErrors:")
            for error in result.errors:
                print(f"   {error}")
            
            print(f"\nTry: python3 pdf_compiler.py --fix-errors")
            return 1
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
