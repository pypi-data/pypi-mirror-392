# TexForge Theorem Prover Agent Guide

## Overview

The **Theorem Prover Agent** is an AI-powered system that generates rigorous mathematical proofs with automatic verification. It's specialized for:
- **Quantum Information Theory**
- **Computational Complexity Theory**
- **Theoretical Computer Science**
- **Information Theory**

## Key Features

### 🤖 Dual-Agent System
- **Prover Agent**: Generates step-by-step rigorous proofs
- **Checker Agent**: Verifies logical validity and mathematical rigor

### 📝 LaTeX Integration
- Reads theorems directly from your LaTeX files
- Writes verified proofs back automatically
- Creates backups before modifying files

### 🔍 Rigorous Verification
- Each proof step explicitly justified
- Dependency tracking between steps
- Domain-specific correctness checks
- Iterative refinement (up to 3 rounds)

### 📊 Quality Scoring
- Rigor score (0-10) for each proof
- Detailed issue identification
- Suggestions for improvement

## Installation

The prover agent is included with TexForge:

```bash
pip install texforge
```

## Usage

### Method 1: Prove from LaTeX Label (Recommended)

**Step 1: Write theorem in your LaTeX file**

```latex
% In content/methods.tex or main.tex

\begin{theorem}[Magic Growth Bound]
\label{thm:magic_bound}
For any 1D nearest-neighbor Hamiltonian $H = \sum_{i} h_{i,i+1}$ acting on $n$ qubits,
the stabilizer magic $M(\rho(t))$ of the evolved state satisfies
\[
M(\rho(t)) \leq C t^2
\]
for some constant $C > 0$ and all times $t \geq 0$.
\end{theorem}

% Proof will be inserted here automatically!
```

**Step 2: Run the prover**

```bash
# Basic usage
texforge prove --label thm:magic_bound

# Specify file if you have multiple .tex files
texforge prove --label thm:magic_bound --file content/methods.tex
```

**Step 3: Review the output**

The prover will:
1. Find the theorem in your .tex files
2. Generate a proof strategy
3. Construct detailed proof steps
4. Verify with checker agent
5. Write the proof back to your file

### Method 2: Provide Theorem Directly

For theorems not yet in LaTeX:

```bash
texforge prove \
  --name "Magic Growth Bound" \
  --theorem "For any k-local Hamiltonian H, stabilizer magic grows at most polynomially in time" \
  --assumptions "H is 2-local" "Initial state has bounded magic" \
  --context "quantum information theory"
```

## Supported Theorem Environments

The prover recognizes these LaTeX environments:
- `\begin{theorem}...\end{theorem}`
- `\begin{lemma}...\end{lemma}`
- `\begin{proposition}...\end{proposition}`
- `\begin{corollary}...\end{corollary}`

## Mathematical Contexts

The prover automatically detects context from your LaTeX content, or you can specify:

### Quantum Information Theory (default)
```bash
texforge prove --label thm:main --context "quantum information theory"
```

**Domain expertise:**
- Quantum states (density matrices, pure states)
- Quantum operations (unitaries, CPTP maps, POVMs)
- Quantum entropy (von Neumann, Rényi)
- Entanglement measures
- Quantum channels
- Stabilizer formalism

### Computational Complexity Theory
```bash
texforge prove --label thm:main --context "computational complexity theory"
```

**Domain expertise:**
- Complexity classes (P, NP, BQP, etc.)
- Reductions and hardness
- Oracle separations
- Circuit complexity
- Query complexity

### Information Theory
```bash
texforge prove --label thm:main --context "information theory"
```

**Domain expertise:**
- Shannon entropy
- Mutual information
- Channel capacity
- Data processing inequality
- Rate-distortion theory

## Output Files

For each proof, the prover generates:

### 1. `proofs/theorem_name.tex`
Publication-ready LaTeX proof with proper formatting:
```latex
\begin{proof}
  We proceed by analyzing the Hamiltonian evolution...

  \textbf{Step 1:} First, observe that...

  \textbf{Step 2:} By the Lieb-Robinson bound...

  Therefore, $M(\rho(t)) \leq Ct^2$.
\end{proof}
```

### 2. `proofs/theorem_name_notes.md`
Detailed markdown notes containing:
- Theorem statement
- Proof strategy
- Each proof step with justification
- Verification results
- Rigor score
- Checker agent report

### 3. Original `.tex` file (updated)
Your original file with the proof inserted after the theorem.

### 4. Backup file (`.tex.backup`)
Automatic backup of your original file before modification.

## Proof Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Generate Proof Strategy                             │
│ • Identify proof technique (direct, contradiction, etc.)    │
│ • List key lemmas needed                                    │
│ • Outline main steps                                        │
│ • Identify potential challenges                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Construct Detailed Proof                            │
│ • Generate 5-15 rigorous steps                              │
│ • Each step: claim + justification + dependencies           │
│ • Track logical dependencies                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Verify with Checker Agent                           │
│ • Check logical validity of each step                       │
│ • Verify completeness (no hidden assumptions)               │
│ • Domain-specific correctness checks                        │
│ • Assign rigor score (0-10)                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Issues found? ───Yes──→ ┌──────────────────┐
                            │                │ Step 4: Fix      │
                            No               │ Issues           │
                            ↓                │ (up to 3 rounds) │
┌─────────────────────────────────────────┐ └──────────────────┘
│ Step 5: Generate LaTeX Proof            │         ↓
│ • Publication-ready formatting          │    (loop back to
│ • Proper math mode                      │     verification)
│ • Citation placeholders                 │
└─────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────┐
│ Step 6: Write to Original LaTeX File   │
│ • Create backup                         │
│ • Insert or replace proof               │
│ • Preserve formatting                   │
└─────────────────────────────────────────┘
```

## Examples

### Example 1: Quantum Magic Growth

**LaTeX input:**
```latex
\begin{theorem}[Polynomial Magic Growth]
\label{thm:poly_magic}
For any $k$-local Hamiltonian $H$ on $n$ qubits with $\|H\| = O(1)$,
the stabilizer magic $M(\rho(t))$ satisfies
\[
M(\rho(t)) \leq O(n t^{2k}).
\]
\end{theorem}
```

**Command:**
```bash
texforge prove --label thm:poly_magic
```

**Output (proof automatically inserted):**
```latex
\begin{theorem}[Polynomial Magic Growth]
\label{thm:poly_magic}
For any $k$-local Hamiltonian $H$ on $n$ qubits with $\|H\| = O(1)$,
the stabilizer magic $M(\rho(t))$ satisfies
\[
M(\rho(t)) \leq O(n t^{2k}).
\]
\end{theorem}

\begin{proof}
  We prove this by bounding the growth of magic through Hamiltonian evolution.

  \textbf{Step 1: Decompose Hamiltonian.}
  Write $H = \sum_{i=1}^{N} h_i$ where each $h_i$ acts on at most $k$ qubits
  and $N = O(n)$. This is possible since $H$ is $k$-local.

  \textbf{Step 2: Apply Trotter decomposition.}
  By the Trotter-Suzuki formula, for small time steps $\delta = t/m$,
  \[
  e^{-iHt} = \prod_{j=1}^{m} e^{-ih_1\delta} \cdots e^{-ih_N\delta} + O(t^2/m).
  \]

  \textbf{Step 3: Bound magic increase per time step.}
  Each $e^{-ih_i\delta}$ acts on at most $k$ qubits. By the magic monotone
  property, the magic can increase by at most $O(k)$ per application.

  \textbf{Step 4: Count total operations.}
  The total number of operations is $N \times m = O(n) \times O(t/\delta)$.
  Choosing $\delta = O(1/t)$ to control the Trotter error, we have
  $O(nt)$ operations, each increasing magic by $O(k)$.

  \textbf{Step 5: Accumulate magic growth.}
  Therefore, the total magic satisfies
  \[
  M(\rho(t)) \leq M(\rho(0)) + O(nt \cdot k) = O(ntk) \leq O(nt^{2k}),
  \]
  where we've used that the magic growth is quadratic in the number
  of operations for $k$-local gates.
\end{proof}
```

### Example 2: Complexity Theory

**LaTeX input:**
```latex
\begin{lemma}[Oracle Separation]
\label{lem:oracle_sep}
There exists an oracle $O$ such that $\mathrm{BQP}^O \not\subseteq \mathrm{PH}^O$.
\end{lemma}
```

**Command:**
```bash
texforge prove --label lem:oracle_sep --context "computational complexity theory"
```

The prover will generate a rigorous proof using complexity-theoretic techniques.

## Advanced Features

### Specify Assumptions

If your theorem relies on specific assumptions not stated in the LaTeX:

```bash
texforge prove \
  --label thm:main \
  --assumptions "Hamiltonian is time-independent" \
                "System has finite dimension" \
                "Initial state is pure"
```

### Search Specific File

If you have many .tex files:

```bash
texforge prove --label thm:bound --file content/results.tex
```

### Override Context Detection

Force a specific mathematical context:

```bash
texforge prove --label thm:main --context "graph theory"
```

## Verification and Quality

### Rigor Score Interpretation

- **9-10**: Publishable quality, all steps rigorously justified
- **7-8**: Strong proof, minor gaps or unclear steps
- **5-6**: Generally sound, some steps need more justification
- **3-4**: Proof sketch, significant gaps to address
- **0-2**: Major logical issues or incomplete

### Common Issues Flagged by Checker

1. **Hidden assumptions**: Using facts not explicitly stated
2. **Logical gaps**: Steps that don't follow from previous ones
3. **Domain errors**:
   - Quantum: non-normalized states, non-Hermitian operators
   - Complexity: improper reductions, oracle access violations
   - Information: incorrect use of chain rule, conditioning

### Iterative Refinement

If issues are found, the prover automatically:
1. Identifies specific problems
2. Generates improved proof
3. Re-verifies with checker
4. Repeats up to 3 times

## Best Practices

### 1. Write Clear Theorem Statements

**Good:**
```latex
\begin{theorem}[Main Result]
\label{thm:main}
For any $n$-qubit Hamiltonian $H$ with $\|H\| \leq 1$, the entanglement
entropy $S(\rho(t))$ satisfies $S(\rho(t)) \leq \log(2^n) = n$.
\end{theorem}
```

**Less clear:**
```latex
\begin{theorem}
\label{thm:main}
Entropy is bounded.
\end{theorem}
```

### 2. Use Descriptive Labels

**Good:** `thm:magic_growth`, `lem:lieb_robinson_bound`, `prop:channel_capacity`

**Less clear:** `thm:1`, `lem:a`, `prop:main`

### 3. Provide Context

If your file mixes different topics, help the prover:
```bash
texforge prove --label thm:main --context "quantum information theory"
```

### 4. Review Generated Proofs

Always review the generated proof:
1. Check the standalone proof in `proofs/theorem_name.tex`
2. Read the detailed notes in `proofs/theorem_name_notes.md`
3. Verify the checker's assessment
4. If rigor score < 8, consider running again or manual refinement

### 5. Backup Management

The prover creates `.tex.backup` files. To restore:
```bash
# If you want to revert
cp content/methods.tex.backup content/methods.tex

# Clean up old backups periodically
rm **/*.backup
```

## Troubleshooting

### Theorem Not Found

**Error:** `Label 'thm:main' not found in any .tex files`

**Solutions:**
1. Check the label matches exactly (case-sensitive)
2. Ensure `\label{}` is inside the theorem environment
3. Try specifying the file: `--file content/methods.tex`
4. Verify the file uses supported environments

### Proof Quality Too Low

**Issue:** Rigor score < 6

**Solutions:**
1. Provide more assumptions: `--assumptions "H is Hermitian" "n > 1"`
2. Use more specific context: `--context "quantum many-body physics"`
3. Run again (stochastic AI generation may improve)
4. Manually refine based on checker's feedback in notes

### LaTeX Compilation Errors

**Issue:** Proof uses undefined commands

**Solution:** The proof may reference standard results. Add to your preamble:
```latex
\usepackage{amsthm}
\newtheorem{lemma}{Lemma}
\newtheorem{theorem}{Theorem}
```

## Integration with TexForge Workflow

### Complete Research Workflow

```bash
# 1. Initialize project
texforge init my-quantum-paper --template pra

# 2. Brainstorm and outline
texforge brainstorm

# 3. Write theorem statements in LaTeX files
# (Edit content/methods.tex, add theorems with labels)

# 4. Generate proofs
texforge prove --label thm:main
texforge prove --label lem:technical
texforge prove --label prop:corollary

# 5. Compile paper
texforge compile --notify

# 6. Review
texforge review --journal pra
```

## Command Reference

### Full Syntax

```bash
texforge prove [OPTIONS]

Options:
  --label LABEL           LaTeX label of theorem (e.g., "thm:main")
  --file PATH             Specific .tex file to search
  --theorem TEXT          Theorem statement (alternative to --label)
  --name TEXT             Theorem name
  --assumptions TEXT...   List of assumptions
  --context TEXT          Mathematical context
  -c, --config PATH       Config file

Examples:
  # From LaTeX label
  texforge prove --label thm:main
  texforge prove --label lem:bound --file methods.tex

  # Direct input
  texforge prove --name "Main Theorem" --theorem "Statement..."

  # With assumptions
  texforge prove --label thm:main --assumptions "H is 2-local" "n >= 2"
```

## FAQ

**Q: Can it prove any theorem?**
A: The prover works best on theorems in its specialized domains (quantum info, complexity theory, etc.) with clear statements and well-defined concepts.

**Q: How long does proving take?**
A: Typically 2-5 minutes, depending on theorem complexity and verification rounds needed.

**Q: Will it modify my LaTeX file?**
A: Only if you use `--label` to read from a file. It always creates a backup first.

**Q: Can I use the proof without modification?**
A: Review the rigor score and checker report. Scores 8+ are usually publication-ready with minor edits.

**Q: What if the proof is wrong?**
A: The checker catches most errors, but review is essential. Use the detailed notes to understand each step.

**Q: Can I prove lemmas before the main theorem?**
A: Yes! Prove supporting lemmas first, then the prover can reference them in later proofs.

## Contributing

Found a bug or have suggestions? Please report at:
https://github.com/Jue-Xu/LaTex-paper-automation/issues

## License

GPL-3.0-or-later
