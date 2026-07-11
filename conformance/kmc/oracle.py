"""
KMC Behavioral Oracle — invariant validation on execution traces.

This module implements four invariant checkers that operate exclusively
on observed TraceEvent data. It does NOT import, call, or emulate any
kernel code. All counters and snapshots are the oracle's own — they are
derived from the trace, not from the runtime.
"""

from typing import List, Dict, Any, Optional
from .models import TraceEvent, KMCResult


def _get_int(state: Dict[str, str], key: str) -> Optional[int]:
    """Safely extract an integer from a register dict."""
    raw = state.get(key)
    if raw is None:
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        return None


def _parse_cycles(result: Dict[str, Any]) -> Optional[int]:
    """Extract cycle/requested count from an opcode result dict."""
    for key in ("watchdog_remaining", "requested", "requested_cycles", "approved"):
        val = result.get(key)
        if val is not None:
            try:
                return int(val)
            except (ValueError, TypeError):
                pass
    return None


class KMCOracle:
    """Passive behavioral oracle for AEP execution traces.

    Processes a trace event-by-event, maintaining the oracle's own
    internal state (watchdog counter, register snapshots, R7 timeline).
    Never calls into kernel code.
    """

    def __init__(self, task_id: str = "unknown"):
        self.task_id = task_id
        self.assertions_passed = 0
        self.assertions_failed = 0
        self.failure_mode: Optional[str] = None
        self.failure_detail: Optional[str] = None

        # Oracle-internal state
        self._watchdog_counter: Optional[int] = None
        self._last_r7: Optional[str] = None
        self._pre_transaction_snapshot: Optional[Dict[str, str]] = None
        self._in_transaction: bool = False
        self._last_r2: Optional[str] = None

    def validate(self, events: List[TraceEvent]) -> KMCResult:
        """Run all invariant checks on a trace. Returns the first failure
        found, or a passing result if all invariants hold."""
        self.failure_mode = None
        self.failure_detail = None
        self._watchdog_counter = None
        self._last_r7 = None
        self._pre_transaction_snapshot = None
        self._in_transaction = False
        self._last_r2 = None

        # Compute trace exit code: 1 if any step returned exhaustion
        trace_exit_code = 0
        for event in events:
            if event.result.get("error_code") == "AEP_ERR_WATCHDOG_EXHAUSTION":
                trace_exit_code = 1
                break

        for event in events:
            if self.failure_mode is not None:
                break

            opcode = event.opcode.upper()

            if opcode == "BOOT":
                self._check_boot(event)
            elif opcode in ("LOAD", "VALIDATE"):
                self._check_generic_step(event)
            elif opcode == "EXEC":
                self._check_exec(event)
            elif opcode == "YIELD":
                self._check_yield(event)
            elif opcode in ("COMMIT", "EXECUTE_COMMIT"):
                self._check_commit(event)
            elif opcode == "EXIT":
                self._check_exit(event)

        return KMCResult(
            task_id=self.task_id,
            behavioral_valid=self.failure_mode is None,
            failure_mode=self.failure_mode,
            failure_detail=self.failure_detail,
            metrics={
                "cycles_expected": len(events),
                "cycles_observed": len(events),
                "assertions_passed": self.assertions_passed,
                "assertions_failed": self.assertions_failed,
            },
            registers_final_snapshot=(
                events[-1].post_state if events else {}
            ),
            assertions_passed=self.assertions_passed,
            assertions_failed=self.assertions_failed,
            trace_exit_code=trace_exit_code,
        )

    # ---- internal helpers ----

    def _fail(self, code: str, detail: str):
        if self.failure_mode is not None:
            return
        self.failure_mode = code
        self.failure_detail = detail
        self.assertions_failed += 1

    def _pass(self):
        self.assertions_passed += 1

    def _r1_from(self, state: Dict[str, str]) -> Optional[int]:
        return _get_int(state, "R1")

    def _r7_from(self, state: Dict[str, str]) -> Optional[str]:
        return state.get("R7")

    def _r4_from(self, state: Dict[str, str]) -> Optional[str]:
        return state.get("R4")

    def _r2_from(self, state: Dict[str, str]) -> Optional[str]:
        return state.get("R2")

    # ---- invariant checkers ----

    def _check_boot(self, event: TraceEvent):
        """BOOT initialises the watchdog counter from the observed R1 value."""
        r1 = self._r1_from(event.post_state)
        if r1 is not None:
            self._watchdog_counter = r1
        else:
            self._watchdog_counter = None
        self._last_r7 = self._r7_from(event.post_state)
        self._last_r2 = self._r2_from(event.post_state)
        self._pass()

    def _check_generic_step(self, event: TraceEvent):
        """LOAD and VALIDATE do NOT consume watchdog cycles.
        AEP-0008 §1.1: only EXEC decrements R1."""
        self._check_kmc002(event)
        self._check_kmc004(event)
        self._last_r7 = self._r7_from(event.post_state)

    def _check_exec(self, event: TraceEvent):
        """EXEC consumes one watchdog cycle and updates R7."""
        self._check_kmc001(event)
        self._check_kmc002(event)
        self._check_kmc004(event)

        # Track R2 for KMC-004: opaqueness check
        pre_r2 = self._r2_from(event.pre_state)
        post_r2 = self._r2_from(event.post_state)
        if pre_r2 is not None:
            self._last_r2 = pre_r2
        if post_r2 is not None:
            self._last_r2 = post_r2

        self._last_r7 = self._r7_from(event.post_state)

    def _check_yield(self, event: TraceEvent):
        """YIELD extends the oracle's internal watchdog counter.

        KMC-001: YIELD MUST increase R1 and MUST NOT decrease it.
        """
        pre_r1 = self._r1_from(event.pre_state)
        post_r1 = self._r1_from(event.post_state)

        if pre_r1 is not None and post_r1 is not None:
            if post_r1 <= pre_r1:
                self._fail(
                    "KMC-001",
                    f"YIELD did not extend R1: pre={pre_r1}, post={post_r1}",
                )
                return
            # Update oracle counter to match observed post-YIELD value
            self._watchdog_counter = post_r1

        self._check_kmc002(event)
        self._last_r7 = self._r7_from(event.post_state)
        self._pass()

    def _check_commit(self, event: TraceEvent):
        """COMMIT finalises a transactional block.

        KMC-002: R7 MUST be strictly increasing on COMMIT.
        KMC-003: If result indicates FAIL, verify rollback state.
        """
        status = event.result.get("status", "").upper()
        rollback = event.result.get("rollback", False)

        if status == "OK":
            self._check_kmc002(event)
            # Capture pre-transaction snapshot for KMC-003 next cycle
            self._pre_transaction_snapshot = dict(event.post_state)
            self._in_transaction = True
        elif status == "FAIL" and rollback:
            # KMC-002: R7 is expected to be "ROLLBACK_EXECUTED" on rollback
            self._check_kmc002(event)
            self._check_kmc003(event)
            # Reset transaction tracking
            self._in_transaction = False
            self._pre_transaction_snapshot = None
        else:
            self._check_kmc002(event)

        self._watchdog_counter = self._r1_from(event.post_state)
        self._last_r7 = self._r7_from(event.post_state)
        self._check_kmc004(event)

    def _check_exit(self, event: TraceEvent):
        """EXIT ends the session."""
        self._check_kmc002(event)
        self._last_r7 = self._r7_from(event.post_state)
        self._pass()

    # ---- individual invariant checks ----

    def _check_kmc001(self, event: TraceEvent):
        """KMC-001 (WATCHDOG_EXHAUSTION): oracle-internal watchdog counter
        MUST NOT reach zero without a corresponding runtime exhaustion signal.

        The oracle maintains its own counter independent of the runtime's R1.
        AEP-0008 §1.1: only EXEC decrements R1. If the oracle counter reaches
        zero and the runtime did NOT report AEP_ERR_WATCHDOG_EXHAUSTION, the
        invariant is violated (the runtime executed past exhaustion).

        When the runtime properly triggers exhaustion, the counter is NOT
        decremented because the opcode was blocked.
        """
        if self._watchdog_counter is None:
            self._pass()
            return

        # If the runtime already reported exhaustion, the opcode was blocked.
        # Do NOT decrement — the runtime correctly prevented execution.
        result = event.result
        if result.get("error_code") == "AEP_ERR_WATCHDOG_EXHAUSTION":
            self._pass()
            return

        # Decrement oracle counter for this step (opcode consumed a cycle)
        self._watchdog_counter -= 1

        if self._watchdog_counter < 0:
            self._fail(
                "KMC-001",
                f"Watchdog exhausted: oracle counter reached "
                f"{self._watchdog_counter} before YIELD or opcode completion",
            )

    @staticmethod
    def _is_timestamp(val: str) -> bool:
        """Rough check: a timestamp starts with a digit (ISO 8601)."""
        return bool(val) and val[0].isdigit()

    def _check_kmc002(self, event: TraceEvent):
        """KMC-002 (TIMESTAMP_REGRESSION): R7 MUST be non-decreasing across
        all steps and strictly increasing within the COMMIT opcode itself.

        - Across all steps: monotonicidade não-decrescente (post_r7 >= last_r7).
        - On COMMIT: R7 post-COMMIT MUST be strictly greater than R7
          pre-COMMIT (within the single operation), because COMMIT is
          the timestamp-anchoring event per AEP-0001 §3.2.

        Non-timestamp R7 values (e.g. "ROLLBACK_EXECUTED", "ROLLBACK_FORCED",
        "EXIT_1_WATCHDOG_TIMEOUT") bypass the strict-increase check since
        they represent lifecycle states rather than wall-clock time.
        """
        post_r7 = self._r7_from(event.post_state)
        if post_r7 is None:
            self._pass()
            return

        # Non-timestamp values (state strings) bypass strict increase
        if not self._is_timestamp(post_r7):
            self._pass()
            return

        opcode = event.opcode.upper()

        if opcode in ("COMMIT", "EXECUTE_COMMIT"):
            # Strictly increasing within the COMMIT operation itself
            pre_r7 = self._r7_from(event.pre_state)
            if pre_r7 is not None and self._is_timestamp(pre_r7) and post_r7 <= pre_r7:
                self._fail(
                    "KMC-002",
                    f"R7 did not increase during COMMIT: "
                    f"pre='{pre_r7}' -> post='{post_r7}'",
                )
                return
        else:
            # Non-decreasing across the trace for all other steps
            if self._last_r7 is not None and post_r7 < self._last_r7:
                self._fail(
                    "KMC-002",
                    f"R7 timestamp regression at {opcode}: "
                    f"'{self._last_r7}' -> '{post_r7}'",
                )
                return

        self._pass()

    def _check_kmc003(self, event: TraceEvent):
        """KMC-003 (ROLLBACK_MISMATCH): on rollback, mutable registers
        MUST be restored to the pre-transaction snapshot and R4 MUST
        contain a structured error.
        """
        snapshot = self._pre_transaction_snapshot
        post = event.post_state

        if snapshot is None:
            self._fail(
                "KMC-003",
                "Rollback observed but no pre-transaction snapshot available",
            )
            return

        # Check that R0, R5, R6 are restored (registers mutated by COMMIT).
        # R7 is deliberately excluded because AEP-0008 §4.1 sets it to a
        # state string ("ROLLBACK_EXECUTED") on rollback, not the snapshot.
        for reg in ("R0", "R5", "R6"):
            expected = snapshot.get(reg)
            actual = post.get(reg)
            if expected is not None and actual is not None and actual != expected:
                self._fail(
                    "KMC-003",
                    f"Register {reg} not restored on rollback: "
                    f"expected '{expected}', got '{actual}'",
                )
                return

        # R4 MUST contain a structured error
        r4_raw = self._r4_from(post)
        if not r4_raw or r4_raw in ("None", ""):
            self._fail(
                "KMC-003",
                "R4 is empty after rollback — structured error missing",
            )
            return

        import json as _json
        try:
            r4 = _json.loads(r4_raw) if isinstance(r4_raw, str) else r4_raw
            if not isinstance(r4, dict) or "error_code" not in r4:
                self._fail(
                    "KMC-003",
                    "R4 does not contain a structured error with error_code",
                )
                return
        except (_json.JSONDecodeError, TypeError):
            self._fail(
                "KMC-003",
                f"R4 is not valid JSON: '{r4_raw}'",
            )
            return

        self._pass()

    def _check_kmc004(self, event: TraceEvent):
        """KMC-004 (R2_ISOLATION): R2 MUST remain opaque — the oracle
        verifies that R2 appears only as a data buffer. If the result
        indicates execution of R2 contents (e.g. non-standard fields),
        the invariant is violated.

        This is a passive check: the oracle flags any evidence that R2
        contents were executed, interpreted, or caused control-flow
        side effects.
        """
        pre_r2 = self._r2_from(event.pre_state)
        post_r2 = self._r2_from(event.post_state)

        # R2 should not disappear or be cleared by non-agent opcodes
        opcode = event.opcode.upper()
        if opcode in ("LOAD", "VALIDATE", "COMMIT", "EXECUTE_COMMIT", "EXIT"):
            if pre_r2 is not None and pre_r2 != "None" and post_r2 is None:
                self._fail(
                    "KMC-004",
                    f"R2 was cleared by {opcode}: "
                    f"pre='{pre_r2}' -> post=None",
                )
                return

        # Check for side effects that look like R2 was executed
        result = event.result
        if result.get("executed_r2") or result.get("r2_executed"):
            self._fail(
                "KMC-004",
                f"Result indicates R2 was executed at {opcode}",
            )
            return

        self._pass()
