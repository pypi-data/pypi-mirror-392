#!/usr/bin/env python3
"""
Dual-Implementation Numerical Simulation Agent
Verifies results by implementing same simulation in two ways:
1. Qiskit (primary) - High-level quantum framework
2. NumPy (verification) - Low-level matrix operations
"""
import subprocess
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

from .config import PaperMaintenanceConfig


@dataclass
class SimulationResult:
    """Result from a simulation"""
    implementation: str  # "qiskit" or "numpy"
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    runtime: float = 0.0


@dataclass
class VerificationResult:
    """Result of comparing two implementations"""
    match: bool
    tolerance: float
    max_difference: float
    details: str


class DualSimulationAgent:
    """Run and verify simulations with dual implementation"""
    
    MAX_RETRIES = 3
    DEFAULT_TOLERANCE = 1e-10
    
    def __init__(self, config: PaperMaintenanceConfig):
        self.config = config
        self.project_dir = config.paper_directory
        self.simulations_dir = self.project_dir / "simulations"
        self.simulations_dir.mkdir(exist_ok=True)
        
        self.results_file = self.simulations_dir / "results.json"
        self.verification_log = self.simulations_dir / "verification.log"
    
    def generate_simulation_code(self, task_description: str) -> Tuple[bool, str, str]:
        """
        Generate both Qiskit and NumPy implementations from description
        
        Returns: (success, qiskit_code, numpy_code)
        """
        
        print("🔬 Generating simulation code...")
        print(f"Task: {task_description[:100]}...")
        
        # Generate Qiskit implementation
        print("\n  Generating Qiskit implementation...")
        qiskit_prompt = f"""Write a Qiskit simulation for the following task:

{task_description}

Requirements:
1. Use Qiskit for quantum simulation
2. Return results as a Python dictionary
3. Include proper error handling
4. Add docstring explaining what it does
5. Make it self-contained (can run standalone)

Write a complete Python function:
```python
def run_qiskit_simulation(params):
    '''
    Docstring here
    '''
    # Your implementation
    return results_dict
```

Include all necessary imports.
Focus on correctness and clarity."""
        
        success_q, qiskit_code = self._call_claude(qiskit_prompt)
        
        if not success_q:
            return False, "", ""
        
        # Generate NumPy verification
        print("\n  Generating NumPy verification implementation...")
        numpy_prompt = f"""Write a NumPy-based verification for this quantum simulation:

{task_description}

QISKIT IMPLEMENTATION (for reference):
{qiskit_code}

Requirements:
1. Use NumPy for direct matrix operations
2. Implement the SAME physics from scratch
3. Return results in SAME dictionary format as Qiskit
4. This is for VERIFICATION - must be independent implementation
5. Use explicit matrix multiplication, no high-level abstractions

Write a complete Python function:
```python
def run_numpy_verification(params):
    '''
    NumPy verification of Qiskit simulation
    '''
    # Your implementation
    return results_dict
```

CRITICAL: Do NOT just wrap Qiskit. Implement physics directly with matrices."""
        
        success_n, numpy_code = self._call_claude(numpy_prompt)
        
        if not success_n:
            return False, qiskit_code, ""
        
        return True, qiskit_code, numpy_code
    
    def _call_claude(self, prompt: str) -> Tuple[bool, str]:
        """Call Claude Code with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                result = subprocess.run(
                    ["claude", "--dangerously-skip-permissions", "-p", prompt],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    return True, result.stdout.strip()
                    
            except Exception as e:
                print(f"    Attempt {attempt + 1} failed: {e}")
        
        return False, f"Failed after {self.MAX_RETRIES} attempts"
    
    def run_dual_simulation(self, task_description: str, params: Dict) -> VerificationResult:
        """
        Run simulation with both implementations and verify
        
        Args:
            task_description: What to simulate
            params: Simulation parameters
        
        Returns:
            VerificationResult showing if implementations match
        """
        
        print("\n" + "="*60)
        print("DUAL SIMULATION VERIFICATION")
        print("="*60)
        
        # Generate code
        success, qiskit_code, numpy_code = self.generate_simulation_code(task_description)
        
        if not success:
            return VerificationResult(
                match=False,
                tolerance=0,
                max_difference=float('inf'),
                details="Failed to generate code"
            )
        
        # Save generated code
        qiskit_file = self.simulations_dir / "sim_qiskit.py"
        numpy_file = self.simulations_dir / "sim_numpy.py"
        
        qiskit_file.write_text(qiskit_code)
        numpy_file.write_text(numpy_code)
        
        print(f"\n✓ Generated code:")
        print(f"  - {qiskit_file}")
        print(f"  - {numpy_file}")
        
        # Run Qiskit implementation
        print("\n  Running Qiskit simulation...")
        qiskit_result = self._run_simulation(qiskit_file, params, "qiskit")
        
        if not qiskit_result.success:
            return VerificationResult(
                match=False,
                tolerance=0,
                max_difference=float('inf'),
                details=f"Qiskit failed: {qiskit_result.error}"
            )
        
        print(f"    ✓ Completed in {qiskit_result.runtime:.2f}s")
        
        # Run NumPy verification
        print("\n  Running NumPy verification...")
        numpy_result = self._run_simulation(numpy_file, params, "numpy")
        
        if not numpy_result.success:
            return VerificationResult(
                match=False,
                tolerance=0,
                max_difference=float('inf'),
                details=f"NumPy failed: {numpy_result.error}"
            )
        
        print(f"    ✓ Completed in {numpy_result.runtime:.2f}s")
        
        # Compare results
        print("\n  Comparing results...")
        verification = self._compare_results(qiskit_result.data, numpy_result.data)
        
        if verification.match:
            print(f"    ✅ MATCH (max diff: {verification.max_difference:.2e})")
        else:
            print(f"    ❌ MISMATCH (max diff: {verification.max_difference:.2e})")
        
        # Save results
        self._save_results(qiskit_result, numpy_result, verification)
        
        return verification
    
    def _run_simulation(self, script_file: Path, params: Dict, 
                       impl_type: str) -> SimulationResult:
        """Run a simulation script"""
        import time
        
        # Create runner script
        runner = f"""
import json
import sys
from pathlib import Path

# Add simulations dir to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the simulation
from {script_file.stem} import *

# Run with parameters
params = {json.dumps(params)}

try:
    results = run_{impl_type}_simulation(params)
    print(json.dumps(results))
except Exception as e:
    print(json.dumps({{"error": str(e)}}), file=sys.stderr)
    sys.exit(1)
"""
        
        runner_file = self.simulations_dir / f"runner_{impl_type}.py"
        runner_file.write_text(runner)
        
        # Run it
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ["python3", str(runner_file)],
                cwd=self.simulations_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            runtime = time.time() - start_time
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return SimulationResult(
                    implementation=impl_type,
                    success=True,
                    data=data,
                    runtime=runtime
                )
            else:
                return SimulationResult(
                    implementation=impl_type,
                    success=False,
                    error=result.stderr,
                    runtime=runtime
                )
                
        except Exception as e:
            return SimulationResult(
                implementation=impl_type,
                success=False,
                error=str(e),
                runtime=time.time() - start_time
            )
    
    def _compare_results(self, data1: Dict, data2: Dict, 
                        tolerance: float = None) -> VerificationResult:
        """Compare two result dictionaries"""
        
        if tolerance is None:
            tolerance = self.DEFAULT_TOLERANCE
        
        if not data1 or not data2:
            return VerificationResult(
                match=False,
                tolerance=tolerance,
                max_difference=float('inf'),
                details="One or both results empty"
            )
        
        # Check keys match
        if set(data1.keys()) != set(data2.keys()):
            return VerificationResult(
                match=False,
                tolerance=tolerance,
                max_difference=float('inf'),
                details=f"Keys don't match: {set(data1.keys())} vs {set(data2.keys())}"
            )
        
        # Compare values
        max_diff = 0.0
        mismatches = []
        
        for key in data1.keys():
            val1 = data1[key]
            val2 = data2[key]
            
            # Convert to numpy arrays if possible
            try:
                arr1 = np.array(val1)
                arr2 = np.array(val2)
                
                if arr1.shape != arr2.shape:
                    mismatches.append(f"{key}: shape mismatch {arr1.shape} vs {arr2.shape}")
                    max_diff = float('inf')
                    continue
                
                diff = np.max(np.abs(arr1 - arr2))
                max_diff = max(max_diff, diff)
                
                if diff > tolerance:
                    mismatches.append(f"{key}: diff={diff:.2e} > tol={tolerance:.2e}")
                    
            except:
                # Non-numeric comparison
                if val1 != val2:
                    mismatches.append(f"{key}: {val1} != {val2}")
                    max_diff = float('inf')
        
        match = (max_diff <= tolerance) and len(mismatches) == 0
        
        details = "Perfect match" if match else f"Mismatches: {'; '.join(mismatches)}"
        
        return VerificationResult(
            match=match,
            tolerance=tolerance,
            max_difference=max_diff,
            details=details
        )
    
    def _save_results(self, qiskit_result: SimulationResult,
                     numpy_result: SimulationResult,
                     verification: VerificationResult) -> None:
        """Save results to file"""
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'qiskit': {
                'success': qiskit_result.success,
                'runtime': qiskit_result.runtime,
                'data': qiskit_result.data
            },
            'numpy': {
                'success': numpy_result.success,
                'runtime': numpy_result.runtime,
                'data': numpy_result.data
            },
            'verification': {
                'match': verification.match,
                'tolerance': verification.tolerance,
                'max_difference': str(verification.max_difference),
                'details': verification.details
            }
        }
        
        with open(self.results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Append to log
        log_entry = f"""
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
Qiskit: {qiskit_result.runtime:.2f}s
NumPy:  {numpy_result.runtime:.2f}s
Match:  {verification.match}
Max diff: {verification.max_difference:.2e}
{'✅ VERIFIED' if verification.match else '❌ MISMATCH'}
---
"""
        
        with open(self.verification_log, 'a') as f:
            f.write(log_entry)


def main():
    """Simulation agent CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dual Simulation Agent")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path.home() / ".paper-automation-config.yaml"
    )
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="Simulation task description"
    )
    parser.add_argument(
        "--params",
        type=str,
        default="{}",
        help="Simulation parameters as JSON"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Config not found: {args.config}")
        return 1
    
    config = PaperMaintenanceConfig.load(args.config)
    agent = DualSimulationAgent(config)
    
    params = json.loads(args.params)
    
    result = agent.run_dual_simulation(args.task, params)
    
    return 0 if result.match else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
