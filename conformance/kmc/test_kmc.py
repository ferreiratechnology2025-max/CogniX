"""
KMC Teeth Check Tests — verifies the behavioral oracle catches invariants.

Valid traces must pass; deliberately broken traces (mutants) must be
flagged with the exact KMC-XXX failure code.
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "implementations" / "python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from conformance.kmc.oracle import KMCOracle
from conformance.kmc.models import TraceEvent
from conformance.kmc.tracer import KernelTracer


def _make_event(opcode: str, pre: dict, post: dict,
                result: dict = None, cycle: int = 1) -> TraceEvent:
    return TraceEvent(
        opcode=opcode,
        pre_state=pre,
        post_state=post,
        result=result or {"status": "OK"},
        cycle=cycle,
    )


class TestKMCOracleUnit(unittest.TestCase):
    """Unit tests for the KMC oracle with synthetic traces."""

    # ---- Valid traces ----

    def test_valid_boot_to_exit(self):
        """A complete valid trace passes all invariants."""
        events = [
            _make_event("BOOT", {}, {"R1": "5", "R7": "2026-07-11T00:00:00Z",
                                     "R2": "task"}),
            _make_event("LOAD", {"R1": "5"}, {"R1": "4", "R7": "2026-07-11T00:00:01Z",
                                              "R2": "task"}, cycle=2),
            _make_event("EXEC", {"R1": "4", "R2": "task"},
                        {"R1": "3", "R7": "2026-07-11T00:00:02Z",
                         "R2": "task"}, cycle=3),
            _make_event("COMMIT", {"R1": "3", "R7": "2026-07-11T00:00:02Z"},
                        {"R1": "2", "R7": "2026-07-11T00:00:03Z",
                         "R2": "task"},
                        result={"status": "OK"}, cycle=4),
            _make_event("EXIT", {"R1": "2", "R7": "2026-07-11T00:00:03Z"},
                        {"R1": "2", "R7": "2026-07-11T00:00:04Z",
                         "R2": "task"}, cycle=5),
        ]
        oracle = KMCOracle("TC-valid")
        result = oracle.validate(events)
        self.assertTrue(result.behavioral_valid, f"Expected valid, got {result.failure_mode}")
        self.assertIsNone(result.failure_mode)
        self.assertEqual(result.assertions_failed, 0)

    def test_valid_yield_extends_watchdog(self):
        """A trace with valid YIELD passes KMC-001."""
        events = [
            _make_event("BOOT", {}, {"R1": "3", "R7": "T1", "R2": ""}),
            _make_event("EXEC", {"R1": "3"}, {"R1": "2", "R7": "T2", "R2": ""}, cycle=2),
            _make_event("EXEC", {"R1": "2"}, {"R1": "1", "R7": "T3", "R2": ""}, cycle=3),
            _make_event("YIELD", {"R1": "1"}, {"R1": "4", "R7": "T3", "R2": ""},
                        result={"status": "OK", "approved": 3}, cycle=4),
            _make_event("EXEC", {"R1": "4"}, {"R1": "3", "R7": "T4", "R2": ""}, cycle=5),
            _make_event("COMMIT", {"R1": "3", "R7": "T4"},
                        {"R1": "2", "R7": "T5", "R2": ""},
                        result={"status": "OK"}, cycle=6),
        ]
        oracle = KMCOracle("TC-yield-ok")
        result = oracle.validate(events)
        self.assertTrue(result.behavioral_valid, f"Expected valid, got {result.failure_mode}")

    def test_valid_rollback_restores_state(self):
        """A rollback with proper R4 injection passes KMC-003."""
        pre_transaction = {"R0": "s1", "R5": "sk", "R6": "OK",
                           "R7": "2026-07-11T00:01:00Z", "R2": "task"}
        post_rollback = {"R0": "s1", "R5": "sk", "R6": "OK",
                         "R7": "ROLLBACK_EXECUTED", "R2": "task",
                         "R4": json.dumps({
                             "error_code": "ERR_AEP_0002_VALIDATION",
                             "trace": "validation failed",
                             "watchdog_at_failure": 0,
                         })}
        events = [
            _make_event("BOOT", {}, {"R1": "5", "R7": "2026-07-11T00:00:00Z", "R2": ""}),
            _make_event("COMMIT", {"R1": "4"},
                        {"R1": "3", "R7": "2026-07-11T00:01:00Z", "R2": "",
                         "R0": "s1", "R5": "sk", "R6": "OK"},
                        result={"status": "OK"}, cycle=2),
            _make_event("EXEC", {"R1": "3"}, {"R1": "2", "R7": "2026-07-11T00:02:00Z",
                                              "R2": "task"}, cycle=3),
            _make_event("COMMIT", pre_transaction, post_rollback,
                        result={"status": "FAIL", "rollback": True},
                        cycle=4),
        ]
        oracle = KMCOracle("TC-rollback-ok")
        result = oracle.validate(events)
        self.assertTrue(result.behavioral_valid,
                        f"Expected rollback valid, got {result.failure_mode}: {result.failure_detail}")

    # ---- Mutant traces (must fail) ----

    def test_kmc001_watchdog_exhaustion(self):
        """KMC-001: Watchdog exhausts without YIELD."""
        events = [
            _make_event("BOOT", {}, {"R1": "2", "R7": "T1", "R2": ""}),
            _make_event("EXEC", {"R1": "2"}, {"R1": "1", "R7": "T2", "R2": ""}, cycle=2),
            _make_event("EXEC", {"R1": "1"}, {"R1": "0", "R7": "T3", "R2": ""}, cycle=3),
            # No YIELD — counter exhausted
            _make_event("EXEC", {"R1": "0"}, {"R1": "0", "R7": "T4", "R2": ""}, cycle=4),
        ]
        oracle = KMCOracle("TC-mutant-001")
        result = oracle.validate(events)
        self.assertFalse(result.behavioral_valid)
        self.assertEqual(result.failure_mode, "KMC-001")

    def test_kmc002_timestamp_regression(self):
        """KMC-002: R7 regresses between steps."""
        events = [
            _make_event("BOOT", {}, {"R1": "5", "R7": "2026-07-11T00:00:05Z", "R2": ""}),
            _make_event("EXEC", {"R1": "5"}, {"R1": "4", "R7": "2026-07-11T00:00:03Z",
                                              "R2": ""}, cycle=2),
        ]
        oracle = KMCOracle("TC-mutant-002")
        result = oracle.validate(events)
        self.assertFalse(result.behavioral_valid)
        self.assertEqual(result.failure_mode, "KMC-002")

    def test_kmc002_timestamp_not_strict_on_commit(self):
        """KMC-002: R7 not strictly increasing on COMMIT.

        Uses ISO-format timestamps so _is_timestamp recognises them.
        The COMMIT post-state has the same R7 as pre-state — KMC-002
        MUST catch this as a failure.
        """
        events = [
            _make_event("BOOT", {}, {"R1": "5", "R7": "2026-07-11T00:00:00Z", "R2": ""}),
            _make_event("COMMIT", {"R1": "4", "R7": "2026-07-11T00:00:00Z"},
                        {"R1": "3", "R7": "2026-07-11T00:00:00Z", "R2": ""},
                        result={"status": "OK"}, cycle=2),
        ]
        oracle = KMCOracle("TC-mutant-002b")
        result = oracle.validate(events)
        self.assertFalse(result.behavioral_valid)
        self.assertEqual(result.failure_mode, "KMC-002")

    def test_kmc003_rollback_no_r4(self):
        """KMC-003: Rollback without R4 structured error."""
        pre = {"R0": "s1", "R5": "sk", "R6": "OK", "R7": "T1", "R2": ""}
        post = {"R0": "s1", "R5": "sk", "R6": "OK", "R7": "ROLLBACK_EXECUTED", "R2": "",
                "R4": "None"}
        events = [
            _make_event("BOOT", {}, {"R1": "5", "R7": "T0", "R2": ""}),
            _make_event("COMMIT", {"R1": "4"}, {"R1": "3", "R7": "T1", "R2": "",
                                                "R0": "s1", "R5": "sk", "R6": "OK"},
                        result={"status": "OK"}, cycle=2),
            _make_event("COMMIT", pre, post,
                        result={"status": "FAIL", "rollback": True},
                        cycle=3),
        ]
        oracle = KMCOracle("TC-mutant-003")
        result = oracle.validate(events)
        self.assertFalse(result.behavioral_valid)
        self.assertEqual(result.failure_mode, "KMC-003")

    def test_kmc003_rollback_state_not_restored(self):
        """KMC-003: R6 not restored to pre-transaction value."""
        pre = {"R0": "s1", "R5": "sk", "R6": "OK", "R7": "T1", "R2": ""}
        post = {"R0": "s1", "R5": "sk", "R6": "FAIL", "R7": "ROLLBACK_EXECUTED", "R2": "",
                "R4": json.dumps({"error_code": "ERR_TEST"})}
        events = [
            _make_event("BOOT", {}, {"R1": "5", "R7": "T0", "R2": ""}),
            _make_event("COMMIT", {"R1": "4"}, {"R1": "3", "R7": "T1", "R2": "",
                                                "R0": "s1", "R5": "sk", "R6": "OK"},
                        result={"status": "OK"}, cycle=2),
            _make_event("COMMIT", pre, post,
                        result={"status": "FAIL", "rollback": True},
                        cycle=3),
        ]
        oracle = KMCOracle("TC-mutant-003b")
        result = oracle.validate(events)
        self.assertFalse(result.behavioral_valid)
        self.assertEqual(result.failure_mode, "KMC-003")

    def test_kmc004_r2_cleared_by_commit(self):
        """KMC-004: R2 cleared by non-agent opcode."""
        events = [
            _make_event("BOOT", {}, {"R1": "5", "R7": "T1", "R2": "task"}),
            _make_event("COMMIT", {"R1": "4", "R2": "task"},
                        {"R1": "3", "R7": "T2", "R2": None},
                        result={"status": "OK"}, cycle=2),
        ]
        oracle = KMCOracle("TC-mutant-004")
        result = oracle.validate(events)
        self.assertFalse(result.behavioral_valid)
        self.assertEqual(result.failure_mode, "KMC-004")

    # ---- Output format verification ----

    def test_kmc_output_format(self):
        """KMC output JSON must contain all required fields."""
        events = [
            _make_event("BOOT", {}, {"R1": "5", "R7": "T1", "R2": ""}),
        ]
        oracle = KMCOracle("TC-format")
        result = oracle.validate(events)
        d = result.to_dict()

        self.assertIn("task_id", d)
        self.assertIn("behavioral_valid", d)
        self.assertIn("failure_mode", d)
        self.assertIn("metrics", d)
        self.assertIn("registers_final_snapshot", d)
        self.assertIn("assertions_passed", d)
        self.assertIn("assertions_failed", d)
        self.assertEqual(d["task_id"], "TC-format")
        self.assertEqual(d["metrics"]["cycles_expected"], 1)
        self.assertEqual(d["metrics"]["cycles_observed"], 1)


class TestKMCOracleIntegration(unittest.TestCase):
    """Integration tests: KMC w/ real Python kernel traces via tracer."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.state_path = os.path.join(self.test_dir, "KERNEL", "STATE.md")
        self.resources_path = os.path.join(self.test_dir, "RESOURCES")
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        os.makedirs(self.resources_path, exist_ok=True)
        self._create_initial_state()

    def _create_initial_state(self):
        from aep.core.state import State, StateManager
        state = State()
        state.set_register("R0", "test-session")
        state.set_register("R1", "5")
        state.set_register("R2", "test-task")
        state.set_register("R3", "{}")
        state.set_register("R4", None)
        state.set_register("R5", "skill-test")
        state.set_register("R6", "OK")
        state.set_register("R7", "2026-07-11T00:00:00Z")
        state.type = "state"
        state.id = "kernel-state"
        state.version = "1.0.0"
        state.status = "active"
        manager = StateManager(self.test_dir)
        manager.save_state(state)

    def _make_resource(self, resource_id: str, content: str = None):
        if content is None:
            content = ("---\ntype: project\n"
                       f"id: {resource_id}\n"
                       "version: 1.0.0\nstatus: active\n---\n# Test\n")
        path = os.path.join(self.resources_path, f"{resource_id}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def test_valid_program_passes_oracle(self):
        """A real BOOT→LOAD→EXEC→COMMIT→EXIT passes the Oracle."""
        from aep.core.kernel import AEPKernel
        self._make_resource("test-resource")

        kernel = AEPKernel(self.test_dir)
        tracer = KernelTracer(kernel)
        program = ["BOOT", "LOAD test-resource", "EXEC", "COMMIT", "EXIT"]
        trace = tracer.run_program(program, verbose=False)

        oracle = KMCOracle("TC-int-valid")
        result = oracle.validate(trace)
        self.assertTrue(result.behavioral_valid,
                        f"Expected valid, got {result.failure_mode}: {result.failure_detail}")
        self.assertEqual(result.assertions_failed, 0)

    def test_valid_program_with_yield_passes(self):
        """BOOT→YIELD→EXEC→COMMIT→EXIT with valid YIELD passes."""
        from aep.core.kernel import AEPKernel
        self._make_resource("yield-res")

        kernel = AEPKernel(self.test_dir)
        tracer = KernelTracer(kernel)
        program = ["BOOT", "YIELD 'need cycles' 3", "EXEC", "COMMIT", "EXIT"]
        trace = tracer.run_program(program, verbose=False)

        oracle = KMCOracle("TC-int-yield")
        result = oracle.validate(trace)
        self.assertTrue(result.behavioral_valid,
                        f"Expected valid, got {result.failure_mode}: {result.failure_detail}")

    def test_rollback_trace_passes(self):
        """A failed COMMIT with rollback passes KMC-003."""
        from aep.core.kernel import AEPKernel
        # Invalid resource — no 'type' field
        self._make_resource("bad-res", "---\nid: bad-res\nversion: 1.0.0\nstatus: active\n---\nBad\n")

        kernel = AEPKernel(self.test_dir)
        tracer = KernelTracer(kernel)
        program = ["BOOT", "LOAD bad-res", "EXEC", "COMMIT", "EXIT"]
        trace = tracer.run_program(program, verbose=False)

        oracle = KMCOracle("TC-int-rollback")
        result = oracle.validate(trace)
        self.assertTrue(result.behavioral_valid,
                        f"Expected valid, got {result.failure_mode}: {result.failure_detail}")

    def test_output_json_serializable(self):
        """KMC result can be serialised to JSON."""
        from aep.core.kernel import AEPKernel
        self._make_resource("json-res")

        kernel = AEPKernel(self.test_dir)
        tracer = KernelTracer(kernel)
        program = ["BOOT", "LOAD json-res", "EXEC", "COMMIT", "EXIT"]
        trace = tracer.run_program(program, verbose=False)

        oracle = KMCOracle("TC-int-json")
        result = oracle.validate(trace)
        serialised = json.dumps(result.to_dict(), indent=2)
        self.assertIn("behavioral_valid", serialised)
        self.assertIn("TC-int-json", serialised)


if __name__ == "__main__":
    unittest.main()
