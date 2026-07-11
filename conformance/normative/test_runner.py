#!/usr/bin/env python3
"""
AEP Normative Test Runner
Validates equivalence between AEP implementations
"""

import os
import sys
import json
import yaml
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class AEPTestRunner:
    """Run normative tests against AEP implementations"""

    KMC_ENABLED = True  # Set False by --no-kmc flag

    # Maps test case IDs to executable programs for KMC tracing.
    # Tests without an entry use the default 6-opcode program.
    TEST_PROGRAMS = {
        "TC-001-boot": ["BOOT"],
        "TC-004-exec": ["BOOT", "EXEC"],
        "TC-005-commit": ["BOOT", "EXEC", "COMMIT"],
        "TC-006-exit": ["BOOT", "EXIT"],
        "TC-007-complete-flow": ["BOOT", "EXEC", "COMMIT", "EXIT"],
        "TC-011-yield-r1-only": ["BOOT", "YIELD 'test' 1"],
        # Watchdog normative tests (AEP-0008 §1)
        "TC-WD-001": ["BOOT", "EXEC", "EXEC", "EXEC"],
        "TC-WD-002": ["BOOT", "YIELD 'rescue' 3", "EXEC"],
        "TC-WD-003": ["BOOT", "EXEC", "EXEC"],
    }
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.test_cases_path = self.base_path / "conformance" / "normative" / "test_cases"
        self.snapshots_path = self.base_path / "conformance" / "normative" / "snapshots"
        self.results = []
        
    def run_all(self, runtime: str, verbose: bool = False) -> Dict[str, Any]:
        """Run all test cases against a runtime"""
        print(f"\nRunning AEP Normative Tests against {runtime} runtime")
        print("=" * 60)
        
        test_files = sorted(self.test_cases_path.glob("*.yaml"))
        passed = 0
        failed = 0
        
        for test_file in test_files:
            result = self.run_test(test_file, runtime, verbose)
            self.results.append(result)
            
            kmc = result.get("kmc", {}) or {}
            if result["passed"]:
                passed += 1
                label = "PASS"
                if kmc.get("behavioral_valid", True) is False:
                    label += " ⚠️ KMC"
                print(f"  PASS {result['id']}: {label}")
            else:
                failed += 1
                err_msg = result.get("error") or result.get("kmc_error") or ""
                errors = result.get("errors", [])
                if errors:
                    err_msg = errors[0]
                print(f"  FAIL {result['id']}: FAILED - {err_msg}")
        
        print("\n" + "=" * 60)
        print(f"Results: {passed} passed, {failed} failed")
        print("=" * 60)
        
        return {
            "runtime": runtime,
            "total": passed + failed,
            "passed": passed,
            "failed": failed,
            "results": self.results
        }
    
    def run_test(self, test_file: Path, runtime: str, verbose: bool) -> Dict[str, Any]:
        """Run a single test case"""
        with open(test_file, 'r') as f:
            test_data = yaml.safe_load(f)
        
        test_id = test_data.get('id', test_file.stem)
        test_name = test_data.get('name', 'Unknown test')
        
        if verbose:
            print(f"\n  Test: {test_id} - {test_name}")
        
        # Execute test against runtime
        actual = self._execute_runtime_test(runtime, test_data)
        expected = test_data.get('expected', {})
        
        # Compare actual vs expected
        passed, errors = self._compare_results(actual, expected)
        
        # Check KMC result if present
        kmc = actual.get("kmc")
        if kmc and not kmc.get("behavioral_valid", True):
            passed = False
            errors.append(
                f"KMC behavioral validation FAILED: "
                f"{kmc.get('failure_mode')} — {kmc.get('failure_detail', '')}"
            )
        
        # Save snapshot
        snapshot_path = self.snapshots_path / "actual" / f"{test_id}.json"
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with open(snapshot_path, 'w') as f:
            json.dump(actual, f, indent=2, default=str)
        
        return {
            "id": test_id,
            "name": test_name,
            "passed": passed,
            "errors": errors,
            "actual": actual,
            "expected": expected,
            "kmc": kmc
        }
    
    def _execute_runtime_test(self, runtime: str, test_data: Dict) -> Dict[str, Any]:
        """Execute test against a specific runtime"""
        if runtime == "python":
            result = self._test_python_runtime(test_data)
            # Add KMC behavioral validation
            if self.KMC_ENABLED:
                kmc_result = self._run_kmc(test_data)
                result["kmc"] = kmc_result.to_dict()
                if not kmc_result.behavioral_valid:
                    result["status"] = "FAIL"
                    result["kmc_error"] = kmc_result.failure_mode
                else:
                    # For tests with custom programs, use KMC trace exit status
                    test_id = test_data.get("id", "")
                    if test_id in self.TEST_PROGRAMS:
                        if kmc_result.trace_exit_code == 1:
                            result["status"] = "FAIL"
                            result["exit_code"] = 1
                            result["returncode"] = 1
                        else:
                            result["status"] = "OK"
                            result["exit_code"] = 0
                            result["returncode"] = 0
            return result
        elif runtime == "sqlite":
            return self._test_sqlite_runtime(test_data)
        else:
            return {"error": f"Unknown runtime: {runtime}"}

    def _run_kmc(self, test_data: Dict) -> "KMCResult":
        """Run the KMC Behavioral Oracle on a test case by tracing the
        Python kernel in-process.  Creates a temporary kernel environment
        so the trace is isolated from the working tree.

        Returns a KMCResult with an additional trace_exit_code field used
        by the comparison logic in _execute_runtime_test."""
        # Ensure KMC can be imported from repo root
        _kmc_root = str(self.base_path)
        if _kmc_root not in sys.path:
            sys.path.insert(0, _kmc_root)
        import importlib
        kmc_oracle = importlib.import_module("conformance.kmc.oracle")
        kmc_tracer = importlib.import_module("conformance.kmc.tracer")
        KMCOracle = kmc_oracle.KMCOracle
        KernelTracer = kmc_tracer.KernelTracer
        from aep.core.kernel import AEPKernel

        test_id = test_data.get("id", "unknown")
        program = self.TEST_PROGRAMS.get(test_id)

        # If no specific program is registered, build one from the YAML
        # procedure field (extract recognised opcode keywords).
        if program is None:
            procedure = test_data.get("procedure", [])
            program = []
            for step in procedure:
                step_upper = step.upper().strip()
                if step_upper.startswith("YIELD") or step_upper in (
                    "BOOT", "LOAD", "VALIDATE", "EXEC", "COMMIT", "EXIT",
                ):
                    program.append(step if step_upper.startswith("YIELD") else step_upper)

        if not program:
            program = ["BOOT", "EXEC", "COMMIT", "EXIT"]

        # Temporary sandbox so the kernel does not touch the real repo.
        sandbox = Path(tempfile.mkdtemp(prefix="kmc_"))
        try:
            kernel = AEPKernel(str(sandbox))
            # Seed minimal initial state (use per-test R1 if specified)
            kmc_config = test_data.get("kmc", {}) or {}
            r1_initial = kmc_config.get("r1_initial", 10)
            from aep.core.state import State, StateManager
            state = State()
            state.set_register("R0", "kmc-session")
            state.set_register("R1", str(r1_initial))
            state.set_register("R2", "kmc-task")
            state.set_register("R3", "{}")
            state.set_register("R4", None)
            state.set_register("R5", "skill-kmc")
            state.set_register("R6", "OK")
            state.set_register("R7", "2026-07-11T00:00:00.000000Z")
            mgr = StateManager(str(sandbox))
            mgr.save_state(state)

            # Create dummy resources if the program needs them
            for step in program:
                if step.upper().startswith("LOAD "):
                    rid = step.split(" ", 1)[1].strip().strip("'\"")
                    res_dir = sandbox / "RESOURCES"
                    res_dir.mkdir(parents=True, exist_ok=True)
                    content = (
                        "---\ntype: project\nid: "
                        + rid
                        + "\nversion: 1.0.0\nstatus: active\n---\n# "
                        + rid
                    )
                    (res_dir / f"{rid}.md").write_text(content, encoding="utf-8")

            tracer = KernelTracer(kernel)
            trace = tracer.run_program(program, verbose=False)
            oracle = KMCOracle(test_id)
            return oracle.validate(trace)
        finally:
            import shutil
            shutil.rmtree(sandbox, ignore_errors=True)
    
    def _test_python_runtime(self, test_data: Dict) -> Dict[str, Any]:
        """Test against Python implementation"""
        python_path = self.base_path / "implementations" / "python"
        
        result = subprocess.run([
            sys.executable, "-m", "aep.cli.main",
            "--program",
            "--base", str(self.base_path),
            "--verbose"
        ], capture_output=True, cwd=str(python_path), encoding='utf-8', errors='replace')
        
        try:
            stdout_json = json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            stdout_json = {"raw": result.stdout}
        
        return {
            "status": "OK" if result.returncode == 0 else "FAIL",
            "returncode": result.returncode,
            "stdout": stdout_json,
            "runtime": "python"
        }
    
    def _test_sqlite_runtime(self, test_data: Dict) -> Dict[str, Any]:
        """Test against SQLite implementation"""
        import tempfile
        import shutil
        
        sqlite_path = self.base_path / "implementations" / "sqlite"
        
        test_id = test_data.get("id", "")
        if test_id in self.TEST_PROGRAMS:
            # Ensure aep_sqlite is importable for DB seeding
            sqlite_path_str = str(sqlite_path)
            if sqlite_path_str not in sys.path:
                sys.path.insert(0, sqlite_path_str)
            tmp_dir = Path(tempfile.mkdtemp(prefix="aep_sqlite_"))
            db_path = tmp_dir / "test.db"
            try:
                from aep_sqlite.database import Database
                from aep_sqlite.state import StateManager
                db = Database(str(db_path))
                db.initialize()
                kmc_config = test_data.get("kmc", {}) or {}
                r1_initial = kmc_config.get("r1_initial", 10)
                sm = StateManager(db)
                state = sm.get_state()
                state['internal_last_action'] = str(r1_initial)
                state['r2_next_act'] = 'test-task'
                state['r0_session'] = 'test-session'
                sm.save_state(state)
                db.close()
                program_json = json.dumps(self.TEST_PROGRAMS[test_id])
                result = subprocess.run([
                    sys.executable, "-m", "aep_sqlite.cli",
                    "--db", str(db_path),
                    "--program", program_json,
                    "--verbose"
                ], capture_output=True, cwd=str(sqlite_path), encoding='utf-8', errors='replace')
            finally:
                shutil.rmtree(tmp_dir, ignore_errors=True)
        else:
            result = subprocess.run([
                sys.executable, "-m", "aep_sqlite.cli",
                "--program",
                "--verbose"
            ], capture_output=True, cwd=str(sqlite_path), encoding='utf-8', errors='replace')
        
        try:
            stdout_json = json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            stdout_json = {"raw": result.stdout}
        
        return {
            "status": "OK" if result.returncode == 0 else "FAIL",
            "returncode": result.returncode,
            "stdout": stdout_json,
            "runtime": "sqlite"
        }
    
    def _compare_results(self, actual: Dict, expected: Dict) -> tuple:
        """Compare actual vs expected results"""
        errors = []
        
        # Check status
        if expected.get('status'):
            actual_status = actual.get('status')
            if actual_status != expected['status']:
                errors.append(f"Status: expected {expected['status']}, got {actual_status}")
        
        # Check exit code
        if expected.get('exit_code') is not None:
            actual_code = actual.get('returncode', actual.get('exit_code', 0))
            if actual_code != expected['exit_code']:
                errors.append(f"Exit code: expected {expected['exit_code']}, got {actual_code}")
        
        return len(errors) == 0, errors


def generate_report(results: Dict[str, Any]) -> str:
    """Generate a conformance report"""
    report = f"""# AEP Conformance Report

**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Runtime:** {results.get('runtime', 'unknown')}
**KMC Oracle:** {'Enabled' if AEPTestRunner.KMC_ENABLED else 'Disabled'}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {results.get('total', 0)} |
| Passed | {results.get('passed', 0)} |
| Failed | {results.get('failed', 0)} |
| Pass Rate | {results.get('passed', 0) / max(results.get('total', 1), 1) * 100:.1f}% |

## Test Results

| Test ID | Name | Status | KMC |
|---------|------|--------|-----|
"""
    for test in results.get('results', []):
        status = "PASS" if test.get('passed') else "FAIL"
        kmc_raw = test.get("kmc", {}) or {}
        kmc_status = "✅" if kmc_raw.get("behavioral_valid", True) else "❌"
        report += f"| {test.get('id')} | {test.get('name')} | {status} | {kmc_status} |\n"
    
    # KMC detail section
    kmc_tests = [t for t in results.get('results', []) if t.get("kmc")]
    if kmc_tests:
        report += "\n## KMC Behavioral Oracle Details\n\n"
        report += "| Test ID | Valid | Failure | Assertions Passed | Assertions Failed |\n"
        report += "|---------|-------|---------|-------------------|-------------------|\n"
        for t in kmc_tests:
            kmc = t.get("kmc", {})
            valid = "[PASS]" if kmc.get("behavioral_valid", True) else "[FAIL]"
            failure = kmc.get("failure_mode") or "-"
            apass = kmc.get("assertions_passed", 0)
            afail = kmc.get("assertions_failed", 0)
            report += f"| {t.get('id')} | {valid} | {failure} | {apass} | {afail} |\n"
    
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AEP Normative Test Runner")
    parser.add_argument('--runtime', choices=['python', 'sqlite', 'all'],
                       default='all', help='Runtime to test')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--no-kmc', action='store_true',
                       help='Disable KMC Behavioral Oracle validation')
    
    args = parser.parse_args()
    AEPTestRunner.KMC_ENABLED = not args.no_kmc
    
    # Find project root and ensure it's on sys.path for KMC imports
    base_path = Path(__file__).parent.parent.parent
    repo_root = str(base_path)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    
    runner = AEPTestRunner(base_path)
    
    if args.runtime == 'all':
        runtimes = ['python', 'sqlite']
    else:
        runtimes = [args.runtime]
    
    all_results = []
    for runtime in runtimes:
        results = runner.run_all(runtime, args.verbose)
        all_results.append(results)
        
        if args.report:
            report = generate_report(results)
            report_path = base_path / "conformance" / "conformance-report.md"
            with open(report_path, 'w') as f:
                f.write(report)
            print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()