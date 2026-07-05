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
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class AEPTestRunner:
    """Run normative tests against AEP implementations"""
    
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
            
            if result["passed"]:
                passed += 1
                print(f"  PASS {result['id']}: PASSED")
            else:
                failed += 1
                print(f"  FAIL {result['id']}: FAILED - {result.get('error', '')}")
        
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
            "expected": expected
        }
    
    def _execute_runtime_test(self, runtime: str, test_data: Dict) -> Dict[str, Any]:
        """Execute test against a specific runtime"""
        if runtime == "python":
            return self._test_python_runtime(test_data)
        elif runtime == "sqlite":
            return self._test_sqlite_runtime(test_data)
        else:
            return {"error": f"Unknown runtime: {runtime}"}
    
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
        sqlite_path = self.base_path / "implementations" / "sqlite"
        
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

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {results.get('total', 0)} |
| Passed | {results.get('passed', 0)} |
| Failed | {results.get('failed', 0)} |
| Pass Rate | {results.get('passed', 0) / max(results.get('total', 1), 1) * 100:.1f}% |

## Test Results

| Test ID | Name | Status |
|---------|------|--------|
"""
    for test in results.get('results', []):
        status = "PASS" if test.get('passed') else "FAIL"
        report += f"| {test.get('id')} | {test.get('name')} | {status} |\n"
    
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AEP Normative Test Runner")
    parser.add_argument('--runtime', choices=['python', 'sqlite', 'all'],
                       default='all', help='Runtime to test')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--report', action='store_true', help='Generate report')
    
    args = parser.parse_args()
    
    # Find project root
    base_path = Path(__file__).parent.parent.parent
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