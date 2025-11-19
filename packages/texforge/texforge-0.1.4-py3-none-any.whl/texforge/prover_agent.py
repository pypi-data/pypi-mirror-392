#!/usr/bin/env python3
"""
Theorem Prover Agent with Checker
Specialized for rigorous mathematical proofs in:
- Theoretical Computer Science
- Quantum Information Theory
- Quantum Computation
"""
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import logging

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic SDK not available. Install with: pip install anthropic")

from .config import PaperMaintenanceConfig
from .exceptions import (
    APIError,
    ParseError,
    VerificationError,
    ConfigurationError,
    TimeoutError as TexForgeTimeoutError
)


@dataclass
class ProofStep:
    """Single step in a proof"""
    step_number: int
    statement: str
    justification: str
    relies_on: List[int]  # Previous steps this depends on
    verified: bool = False
    issues: List[str] = None


@dataclass
class Theorem:
    """Theorem to be proven"""
    name: str
    statement: str
    assumptions: List[str]
    context: str  # Domain context (quantum info, complexity theory, etc.)
    label: Optional[str] = None  # LaTeX label (e.g., thm:main)
    tex_file: Optional[Path] = None  # Source file
    start_line: Optional[int] = None  # Line where theorem starts
    end_line: Optional[int] = None  # Line where theorem ends


class ProverAgent:
    """AI-powered theorem prover with verification"""

    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.proofs_dir = self.project_dir / "proofs"
        self.proofs_dir.mkdir(exist_ok=True)

        # Initialize Anthropic client
        if not ANTHROPIC_AVAILABLE:
            raise ConfigurationError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            )

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY environment variable not set"
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest model

        # Get timeouts from config
        self.timeout = config.advanced.claude_timeout
        self.max_retries = config.advanced.max_retries
        self.retry_delay = config.advanced.retry_delay

        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG if config.advanced.verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def find_theorem_by_label(self, label: str, tex_file: Optional[Path] = None) -> Optional[Theorem]:
        """Find theorem in LaTeX file(s) by label"""
        print(f"🔍 Searching for theorem with label: {label}")

        # Determine which files to search
        if tex_file:
            tex_files = [tex_file]
        else:
            # Search all .tex files in project and content/
            tex_files = list(self.project_dir.glob("*.tex"))
            content_dir = self.project_dir / "content"
            if content_dir.exists():
                tex_files.extend(content_dir.glob("*.tex"))

        for file_path in tex_files:
            theorem = self._parse_theorem_from_file(file_path, label)
            if theorem:
                print(f"  ✓ Found in {file_path.name}")
                return theorem

        print(f"  ✗ Label '{label}' not found in any .tex files")
        return None

    def _parse_theorem_from_file(self, tex_file: Path, label: str) -> Optional[Theorem]:
        """
        Parse theorem with given label from LaTeX file

        Args:
            tex_file: Path to the .tex file
            label: LaTeX label to search for (e.g., 'thm:main')

        Returns:
            Theorem object if found, None otherwise

        Raises:
            ParseError: If file cannot be read or parsed
        """
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise ParseError(f"File not found: {tex_file}")
        except Exception as e:
            raise ParseError(f"Could not read {tex_file}: {e}")

        # Pattern to match theorem environments with labels
        # Matches: \begin{theorem}, \begin{lemma}, \begin{proposition}, \begin{corollary}
        env_pattern = r'\\begin\{(theorem|lemma|proposition|corollary)\}(\[.*?\])?'
        label_pattern = r'\\label\{([^}]+)\}'

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this line starts a theorem environment
            env_match = re.search(env_pattern, line)
            if env_match:
                env_type = env_match.group(1)
                optional_name = env_match.group(2)  # e.g., [Main Result]

                # Look for label in next few lines
                start_line = i
                found_label = None
                statement_lines = []

                # Search within the environment for the label and content
                j = i
                depth = 1
                while j < len(lines) and depth > 0:
                    current = lines[j]

                    # Check for label
                    label_match = re.search(label_pattern, current)
                    if label_match and not found_label:
                        found_label = label_match.group(1)

                    # Track environment depth
                    if f'\\begin{{{env_type}}}' in current and j > i:
                        depth += 1
                    if f'\\end{{{env_type}}}' in current:
                        depth -= 1
                        if depth == 0:
                            end_line = j
                            break

                    # Collect statement (skip label and comments)
                    clean_line = re.sub(label_pattern, '', current)
                    clean_line = re.sub(r'%.*$', '', clean_line)
                    clean_line = re.sub(env_pattern, '', clean_line)
                    clean_line = clean_line.strip()
                    if clean_line and j > i:
                        statement_lines.append(clean_line)

                    j += 1

                # Check if this is the theorem we're looking for
                if found_label == label:
                    statement = ' '.join(statement_lines).strip()

                    # Extract name from optional argument or use environment type
                    if optional_name:
                        name = optional_name.strip('[]')
                    else:
                        name = env_type.capitalize()

                    # Try to infer context from surrounding text
                    context = self._infer_context(tex_file)

                    return Theorem(
                        name=name,
                        statement=statement,
                        assumptions=[],  # Can be extracted from surrounding text if needed
                        context=context,
                        label=label,
                        tex_file=tex_file,
                        start_line=start_line,
                        end_line=end_line if 'end_line' in locals() else j
                    )

            i += 1

        return None

    def _infer_context(self, tex_file: Path) -> str:
        """Infer mathematical context from file content and name"""
        try:
            content = tex_file.read_text().lower()

            # Check for domain-specific keywords
            if any(word in content for word in ['quantum', 'qubit', 'entanglement', 'density matrix', 'unitary']):
                return 'quantum information theory'
            elif any(word in content for word in ['complexity', 'np-hard', 'reduction', 'oracle', 'circuit']):
                return 'computational complexity theory'
            elif any(word in content for word in ['entropy', 'mutual information', 'channel capacity']):
                return 'information theory'
            elif any(word in content for word in ['graph', 'vertex', 'edge', 'coloring']):
                return 'graph theory'
            else:
                return 'theoretical computer science'
        except:
            return 'theoretical computer science'

    def write_proof_to_latex(self, theorem: Theorem, proof_latex: str) -> bool:
        """
        Write proof back to the original LaTeX file

        Args:
            theorem: Theorem object with source file information
            proof_latex: LaTeX proof content to write

        Returns:
            True if successful, False otherwise

        Raises:
            ParseError: If file cannot be read or written
        """
        if not theorem.tex_file:
            raise ParseError("Theorem has no source file specified")

        if not theorem.tex_file.exists():
            raise ParseError(f"Source file not found: {theorem.tex_file}")

        print(f"\n📝 Writing proof to {theorem.tex_file.name}...")

        try:
            with open(theorem.tex_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find the end of the theorem environment
            env_type = None
            for line in lines[theorem.start_line:theorem.end_line + 1]:
                match = re.search(r'\\begin\{(theorem|lemma|proposition|corollary)\}', line)
                if match:
                    env_type = match.group(1)
                    break

            if not env_type:
                print(f"  ✗ Could not determine theorem environment type")
                return False

            # Check if there's already a proof environment
            has_proof = False
            proof_start = None
            proof_end = None

            i = theorem.end_line + 1
            # Look ahead a few lines for existing proof
            while i < min(len(lines), theorem.end_line + 10):
                if '\\begin{proof}' in lines[i]:
                    has_proof = True
                    proof_start = i
                    # Find end of proof
                    j = i + 1
                    while j < len(lines):
                        if '\\end{proof}' in lines[j]:
                            proof_end = j
                            break
                        j += 1
                    break
                # Stop if we hit another theorem or section
                if re.search(r'\\(section|subsection|begin\{(theorem|lemma|proposition)', lines[i]):
                    break
                i += 1

            # Extract just the proof content from the generated LaTeX
            proof_content = self._extract_proof_content(proof_latex)

            # Create backup
            backup_file = theorem.tex_file.with_suffix('.tex.backup')
            with open(backup_file, 'w') as f:
                f.writelines(lines)
            print(f"  ✓ Created backup: {backup_file.name}")

            # Insert or replace proof
            if has_proof and proof_start is not None and proof_end is not None:
                # Replace existing proof
                print(f"  → Replacing existing proof at lines {proof_start + 1}-{proof_end + 1}")
                new_lines = (
                    lines[:proof_start] +
                    ['\\begin{proof}\n'] +
                    [proof_content + '\n'] +
                    ['\\end{proof}\n'] +
                    lines[proof_end + 1:]
                )
            else:
                # Insert new proof after theorem
                print(f"  → Inserting new proof after line {theorem.end_line + 1}")
                insert_pos = theorem.end_line + 1
                new_lines = (
                    lines[:insert_pos] +
                    ['\n', '\\begin{proof}\n'] +
                    [proof_content + '\n'] +
                    ['\\end{proof}\n', '\n'] +
                    lines[insert_pos:]
                )

            # Write back
            with open(theorem.tex_file, 'w') as f:
                f.writelines(new_lines)

            print(f"  ✓ Proof written to {theorem.tex_file.name}")
            print(f"  ✓ Backup saved to {backup_file.name}")
            return True

        except Exception as e:
            print(f"  ✗ Error writing proof: {e}")
            return False

    def _extract_proof_content(self, latex_proof: str) -> str:
        """Extract just the proof content from generated LaTeX"""
        # Remove \begin{proof} and \end{proof} tags
        content = re.sub(r'\\begin\{proof\}', '', latex_proof)
        content = re.sub(r'\\end\{proof\}', '', content)

        # Remove theorem environment if present
        content = re.sub(r'\\begin\{theorem\}.*?\\end\{theorem\}', '', content, flags=re.DOTALL)
        content = re.sub(r'\\begin\{lemma\}.*?\\end\{lemma\}', '', content, flags=re.DOTALL)

        # Clean up extra whitespace but preserve structure
        lines = content.split('\n')
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned.append('  ' + stripped)  # Indent for proof environment

        return '\n'.join(cleaned)

    def _call_claude(self, prompt: str, timeout: Optional[int] = None) -> str:
        """
        Call Claude API with retry logic and proper error handling

        Args:
            prompt: The prompt to send to Claude
            timeout: Optional timeout override (uses config default if not specified)

        Returns:
            Claude's response text

        Raises:
            APIError: If API call fails after all retries
            TexForgeTimeoutError: If operation times out
        """
        if timeout is None:
            timeout = self.timeout

        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"API call attempt {attempt + 1}/{self.max_retries}")

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8000,
                    temperature=0.2,  # Lower temperature for more focused responses
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    timeout=float(timeout)
                )

                # Extract text from response
                if response.content and len(response.content) > 0:
                    text = response.content[0].text
                    self.logger.debug(f"API call successful, response length: {len(text)}")
                    return text
                else:
                    raise APIError("Empty response from API")

            except anthropic.APITimeoutError as e:
                self.logger.warning(f"API timeout on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise TexForgeTimeoutError(f"API timeout after {self.max_retries} attempts")
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

            except anthropic.APIError as e:
                self.logger.warning(f"API error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise APIError(f"API error after {self.max_retries} attempts: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))

            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise APIError(f"Unexpected error: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))

        raise APIError(f"Failed after {self.max_retries} attempts")

    def prove_theorem(self, theorem: Theorem) -> Dict:
        """Generate rigorous proof for a theorem"""
        print(f"\n{'='*70}")
        print(f"🔬 Theorem Prover Agent")
        print(f"{'='*70}")
        print(f"\nTheorem: {theorem.name}")
        print(f"Statement: {theorem.statement}")
        print(f"Context: {theorem.context}")

        # Step 1: Generate proof outline
        print(f"\n{'─'*70}")
        print("Step 1: Generating proof strategy...")
        print(f"{'─'*70}")
        outline = self._generate_proof_outline(theorem)
        print(f"\n✓ Proof strategy generated")

        # Step 2: Generate detailed proof
        print(f"\n{'─'*70}")
        print("Step 2: Constructing detailed proof...")
        print(f"{'─'*70}")
        proof_steps = self._generate_detailed_proof(theorem, outline)
        print(f"\n✓ Generated {len(proof_steps)} proof steps")

        # Step 3: Verify proof with checker agent
        print(f"\n{'─'*70}")
        print("Step 3: Verifying proof with checker agent...")
        print(f"{'─'*70}")
        verification = self._verify_proof(theorem, proof_steps)

        # Step 4: Iterate on issues if any
        iteration = 0
        max_iterations = 3
        while verification['issues_found'] and iteration < max_iterations:
            iteration += 1
            print(f"\n{'─'*70}")
            print(f"Step 4.{iteration}: Addressing verification issues...")
            print(f"{'─'*70}")
            proof_steps = self._fix_proof_issues(theorem, proof_steps, verification)
            verification = self._verify_proof(theorem, proof_steps)

        # Step 5: Generate LaTeX formatted proof
        print(f"\n{'─'*70}")
        print("Step 5: Generating LaTeX proof...")
        print(f"{'─'*70}")
        latex_proof = self._generate_latex_proof(theorem, proof_steps, verification)

        # Save proof
        proof_file = self.proofs_dir / f"{theorem.name.lower().replace(' ', '_')}.tex"
        proof_file.write_text(latex_proof)

        # Save detailed notes
        notes_file = self.proofs_dir / f"{theorem.name.lower().replace(' ', '_')}_notes.md"
        notes = self._generate_proof_notes(theorem, outline, proof_steps, verification)
        notes_file.write_text(notes)

        # Write proof back to original LaTeX file if source is known
        wrote_to_source = False
        if theorem.tex_file:
            print(f"\n{'─'*70}")
            print("Step 6: Writing proof to original LaTeX file...")
            print(f"{'─'*70}")
            wrote_to_source = self.write_proof_to_latex(theorem, latex_proof)

        print(f"\n{'='*70}")
        print(f"✅ Proof complete!")
        print(f"{'='*70}")
        print(f"\nGenerated files:")
        print(f"  - {proof_file.name} (LaTeX proof)")
        print(f"  - {notes_file.name} (detailed notes)")
        if wrote_to_source:
            print(f"  - {theorem.tex_file.name} (updated with proof)")

        if verification['is_rigorous']:
            print(f"\n✓ Proof verified as RIGOROUS by checker agent")
        else:
            print(f"\n⚠ Proof has {len(verification['remaining_issues'])} unresolved issues")
            for issue in verification['remaining_issues'][:3]:
                print(f"    - {issue}")

        return {
            'theorem': theorem,
            'outline': outline,
            'proof_steps': proof_steps,
            'verification': verification,
            'latex_file': proof_file,
            'notes_file': notes_file
        }

    def _generate_proof_outline(self, theorem: Theorem) -> str:
        """Generate high-level proof strategy"""
        assumptions_text = "\n".join([f"  - {a}" for a in theorem.assumptions])

        prompt = f"""You are a theorem prover specializing in {theorem.context}.

Theorem to prove:
{theorem.statement}

Assumptions:
{assumptions_text}

Generate a HIGH-LEVEL PROOF STRATEGY. Identify:

1. **Proof Technique**: What's the best approach?
   - Direct proof
   - Proof by contradiction
   - Proof by induction
   - Constructive proof
   - Probabilistic method
   - Information-theoretic argument
   - Other (specify)

2. **Key Lemmas Needed**: What auxiliary results would help?

3. **Main Steps**: Outline the major steps (3-7 steps)

4. **Potential Challenges**: What are the tricky parts?

5. **Mathematical Tools**: What frameworks/theorems to use?
   - For quantum: density matrices, POVM, quantum entropy, etc.
   - For complexity: reductions, oracle separation, circuit bounds, etc.
   - For information theory: mutual information, data processing, etc.

Be specific to {theorem.context}. Think carefully about rigor."""

        return self._call_claude(prompt)

    def _generate_detailed_proof(self, theorem: Theorem, outline: str) -> List[ProofStep]:
        """Generate step-by-step detailed proof"""
        assumptions_text = "\n".join([f"  - {a}" for a in theorem.assumptions])

        prompt = f"""You are a theorem prover specializing in {theorem.context}.

Theorem: {theorem.statement}

Assumptions:
{assumptions_text}

Proof Strategy:
{outline}

Now generate a DETAILED, RIGOROUS PROOF as a sequence of logical steps.

For each step, provide:
1. Step number
2. Clear statement of what is claimed in this step
3. Detailed justification (which assumptions, lemmas, or previous steps justify this)
4. Mathematical reasoning

Format each step as:
---
STEP N:
CLAIM: [what you're claiming]
JUSTIFICATION: [why this follows]
RELIES ON: [step numbers, or "assumptions", or "lemma X"]
---

Be extremely rigorous. Every claim must be justified. Use precise mathematical language.
Pay special attention to:
- Quantum states are unit vectors (or density matrices)
- Probability distributions sum to 1
- Complexity class separations need proper oracles/barriers
- Information-theoretic inequalities (subadditivity, etc.)
- Computational assumptions vs unconditional results

Generate 5-15 detailed steps."""

        response = self._call_claude(prompt)

        # Parse steps
        proof_steps = []
        step_blocks = re.split(r'---+', response)

        for block in step_blocks:
            block = block.strip()
            if not block or 'STEP' not in block:
                continue

            # Extract step number
            step_match = re.search(r'STEP\s+(\d+)', block)
            if not step_match:
                continue
            step_num = int(step_match.group(1))

            # Extract claim
            claim_match = re.search(r'CLAIM:\s*(.+?)(?=JUSTIFICATION:|RELIES ON:|$)', block, re.DOTALL)
            claim = claim_match.group(1).strip() if claim_match else ""

            # Extract justification
            just_match = re.search(r'JUSTIFICATION:\s*(.+?)(?=RELIES ON:|$)', block, re.DOTALL)
            justification = just_match.group(1).strip() if just_match else ""

            # Extract dependencies
            relies_match = re.search(r'RELIES ON:\s*(.+?)$', block, re.DOTALL)
            relies_text = relies_match.group(1).strip() if relies_match else ""

            # Parse step numbers from dependencies
            relies_on = []
            for num in re.findall(r'\d+', relies_text):
                relies_on.append(int(num))

            proof_steps.append(ProofStep(
                step_number=step_num,
                statement=claim,
                justification=justification,
                relies_on=relies_on,
                verified=False,
                issues=[]
            ))

        return proof_steps

    def _verify_proof(self, theorem: Theorem, proof_steps: List[ProofStep]) -> Dict:
        """Verify proof with checker agent"""
        print("  🔍 Checker agent analyzing proof...")

        # Format proof for checking
        proof_text = self._format_proof_for_checking(theorem, proof_steps)

        prompt = f"""You are a PROOF CHECKER specializing in {theorem.context}.

Your job is to rigorously verify this proof and find ANY logical gaps, errors, or lack of rigor.

{proof_text}

Analyze each step carefully and check:

1. **Logical Validity**: Does each step logically follow from its dependencies?
2. **Completeness**: Are there hidden assumptions or gaps?
3. **Mathematical Rigor**: Are all claims properly justified?
4. **Domain-Specific Issues**:
   - Quantum: normalization, Hermiticity, trace preservation
   - Complexity: proper reductions, oracle access model
   - Information: chain rules, conditioning, mutual information properties

For EACH step, either:
- ✓ VERIFIED: Step is rigorous
- ⚠ ISSUE: Describe the specific problem

Then provide:

**OVERALL ASSESSMENT**:
- Is this proof RIGOROUS? (Yes/No)
- Rigor score: (0-10)
- Major gaps or errors (if any)
- Suggestions for improvement

Be harsh. Better to flag potential issues than miss errors."""

        response = self._call_claude(prompt)

        # Parse verification results
        is_rigorous = "is rigorous? yes" in response.lower() or "rigorous: yes" in response.lower()

        # Extract rigor score
        score_match = re.search(r'rigor score:?\s*(\d+)', response, re.IGNORECASE)
        rigor_score = int(score_match.group(1)) if score_match else 5

        # Extract issues
        issues_found = []
        issue_pattern = r'⚠\s*ISSUE.*?:(.*?)(?=⚠|✓|OVERALL|$)'
        for match in re.finditer(issue_pattern, response, re.DOTALL | re.IGNORECASE):
            issue_text = match.group(1).strip()
            if issue_text:
                issues_found.append(issue_text)

        # Also look for "major gaps" section
        gaps_match = re.search(r'major gaps.*?:(.*?)(?=suggestions|$)', response, re.DOTALL | re.IGNORECASE)
        if gaps_match:
            gaps_text = gaps_match.group(1).strip()
            if gaps_text and gaps_text.lower() not in ['none', 'n/a', 'no']:
                issues_found.append(f"Major gap: {gaps_text}")

        print(f"  → Rigor score: {rigor_score}/10")
        print(f"  → Issues found: {len(issues_found)}")

        return {
            'is_rigorous': is_rigorous,
            'rigor_score': rigor_score,
            'issues_found': len(issues_found) > 0,
            'all_issues': issues_found,
            'remaining_issues': issues_found,
            'checker_report': response
        }

    def _fix_proof_issues(self, theorem: Theorem, proof_steps: List[ProofStep],
                         verification: Dict) -> List[ProofStep]:
        """Address issues found by checker"""
        print(f"  🔧 Addressing {len(verification['all_issues'])} issues...")

        proof_text = self._format_proof_for_checking(theorem, proof_steps)
        issues_text = "\n".join([f"  - {issue}" for issue in verification['all_issues']])

        prompt = f"""You are fixing a proof that has verification issues.

Original Proof:
{proof_text}

Issues Found by Checker:
{issues_text}

Generate an IMPROVED PROOF that addresses these issues.

Make the proof more rigorous by:
1. Adding missing justifications
2. Filling logical gaps
3. Being more explicit about assumptions
4. Adding intermediate steps if needed

Use the same format as before (STEP N, CLAIM, JUSTIFICATION, RELIES ON)."""

        response = self._call_claude(prompt)

        # Parse improved steps (reuse parsing logic)
        improved_steps = []
        step_blocks = re.split(r'---+', response)

        for block in step_blocks:
            block = block.strip()
            if not block or 'STEP' not in block:
                continue

            step_match = re.search(r'STEP\s+(\d+)', block)
            if not step_match:
                continue
            step_num = int(step_match.group(1))

            claim_match = re.search(r'CLAIM:\s*(.+?)(?=JUSTIFICATION:|RELIES ON:|$)', block, re.DOTALL)
            claim = claim_match.group(1).strip() if claim_match else ""

            just_match = re.search(r'JUSTIFICATION:\s*(.+?)(?=RELIES ON:|$)', block, re.DOTALL)
            justification = just_match.group(1).strip() if just_match else ""

            relies_match = re.search(r'RELIES ON:\s*(.+?)$', block, re.DOTALL)
            relies_text = relies_match.group(1).strip() if relies_match else ""

            relies_on = []
            for num in re.findall(r'\d+', relies_text):
                relies_on.append(int(num))

            improved_steps.append(ProofStep(
                step_number=step_num,
                statement=claim,
                justification=justification,
                relies_on=relies_on,
                verified=False,
                issues=[]
            ))

        if improved_steps:
            return improved_steps
        else:
            return proof_steps  # Keep original if parsing failed

    def _format_proof_for_checking(self, theorem: Theorem, proof_steps: List[ProofStep]) -> str:
        """Format proof as text for checker"""
        assumptions_text = "\n".join([f"  - {a}" for a in theorem.assumptions])

        lines = [
            f"THEOREM: {theorem.statement}",
            "",
            "ASSUMPTIONS:",
            assumptions_text,
            "",
            "PROOF:",
            ""
        ]

        for step in proof_steps:
            lines.extend([
                "---",
                f"STEP {step.step_number}:",
                f"CLAIM: {step.statement}",
                f"JUSTIFICATION: {step.justification}",
                f"RELIES ON: {', '.join(map(str, step.relies_on)) if step.relies_on else 'assumptions'}",
            ])

        lines.append("---")

        return "\n".join(lines)

    def _generate_latex_proof(self, theorem: Theorem, proof_steps: List[ProofStep],
                             verification: Dict) -> str:
        """Generate publication-ready LaTeX proof"""
        proof_text = self._format_proof_for_checking(theorem, proof_steps)

        prompt = f"""Convert this proof to publication-ready LaTeX.

{proof_text}

Generate LaTeX code suitable for inclusion in a paper. Use:
- \\begin{{theorem}}...\\end{{theorem}}
- \\begin{{proof}}...\\end{{proof}}
- Proper math mode for all formulas
- \\cite{{}} for any standard results referenced
- Clear, professional mathematical writing
- \\qed at the end

Make it publication-ready for journals like Physical Review or QIP."""

        latex = self._call_claude(prompt)

        # Clean up and ensure proper structure
        if "\\begin{theorem}" not in latex:
            latex = f"\\begin{{theorem}}\n{theorem.statement}\n\\end{{theorem}}\n\n" + latex

        return latex

    def _generate_proof_notes(self, theorem: Theorem, outline: str,
                            proof_steps: List[ProofStep], verification: Dict) -> str:
        """Generate markdown notes about the proof"""
        lines = [
            f"# Proof Notes: {theorem.name}",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Context**: {theorem.context}",
            "",
            "---",
            "",
            "## Theorem Statement",
            "",
            theorem.statement,
            "",
            "## Assumptions",
            ""
        ]

        for assumption in theorem.assumptions:
            lines.append(f"- {assumption}")

        lines.extend([
            "",
            "---",
            "",
            "## Proof Strategy",
            "",
            outline,
            "",
            "---",
            "",
            "## Proof Steps",
            ""
        ])

        for step in proof_steps:
            lines.extend([
                f"### Step {step.step_number}",
                "",
                f"**Claim**: {step.statement}",
                "",
                f"**Justification**: {step.justification}",
                "",
                f"**Dependencies**: {', '.join(map(str, step.relies_on)) if step.relies_on else 'None (from assumptions)'}",
                ""
            ])

        lines.extend([
            "---",
            "",
            "## Verification Results",
            "",
            f"**Rigorous**: {'✓ Yes' if verification['is_rigorous'] else '✗ No'}",
            f"**Rigor Score**: {verification['rigor_score']}/10",
            ""
        ])

        if verification['remaining_issues']:
            lines.extend([
                "### Remaining Issues",
                ""
            ])
            for issue in verification['remaining_issues']:
                lines.append(f"- {issue}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Checker Report",
            "",
            "```",
            verification['checker_report'],
            "```"
        ])

        return "\n".join(lines)


def main():
    """CLI for theorem prover"""
    import argparse
    from .config import PaperMaintenanceConfig

    parser = argparse.ArgumentParser(description='Prove theorems with AI assistance')
    parser.add_argument('--theorem', required=True, help='Theorem statement')
    parser.add_argument('--name', required=True, help='Theorem name')
    parser.add_argument('--assumptions', nargs='+', default=[], help='Assumptions')
    parser.add_argument('--context', default='quantum information theory',
                       help='Mathematical context (default: quantum information theory)')
    parser.add_argument('-c', '--config', type=Path, help='Config file')

    args = parser.parse_args()

    # Load config
    if args.config and args.config.exists():
        config = PaperMaintenanceConfig.load(args.config)
    else:
        config = PaperMaintenanceConfig()
        config.paper_directory = Path.cwd()

    # Create theorem
    theorem = Theorem(
        name=args.name,
        statement=args.theorem,
        assumptions=args.assumptions,
        context=args.context
    )

    # Prove
    prover = ProverAgent(config)
    result = prover.prove_theorem(theorem)

    return 0 if result['verification']['is_rigorous'] else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
