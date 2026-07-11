"""
KMC Tracer — wraps an AEP kernel to produce execution traces.

The tracer calls kernel methods directly but does NOT emulate or
re-implement kernel logic. It simply captures the observable register
state before and after each opcode invocation and packages it into
TraceEvent objects for the oracle.
"""

from typing import Dict, Any, List, Optional
from .models import TraceEvent


class KernelTracer:
    """Wraps an AEP kernel instance to capture execution traces.

    Usage:
        kernel = AEPKernel(...)
        tracer = KernelTracer(kernel)
        trace = tracer.run_program(["BOOT", "LOAD res", "EXEC", ...])
        result = KMCOracle("TC-001").validate(trace)
    """

    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.events: List[TraceEvent] = []

    def _capture_state(self) -> Dict[str, str]:
        """Capture current register state from the kernel's state manager."""
        try:
            state = self.kernel.state_manager.load_state()
            return state.get_all_registers()
        except Exception:
            return {}

    def _capture_state_sqlite(self) -> Dict[str, str]:
        """Capture register state from SQLite kernel."""
        try:
            raw = self.kernel.state_manager.get_state()
            reg_map = {
                'r0_session': 'R0', 'r2_next_act': 'R2',
                'r3_modified': 'R3', 'r4_blockers': 'R4',
                'r5_active_sk': 'R5', 'r6_health': 'R6',
                'r7_timestamp': 'R7',
            }
            result = {}
            for db_key, reg in reg_map.items():
                val = raw.get(db_key)
                if val is not None:
                    result[reg] = str(val)
            return result
        except Exception:
            return {}

    def _record(self, opcode: str, pre: Dict[str, str],
                post: Dict[str, str], result: Dict[str, Any],
                payload: Optional[str] = None):
        """Record a trace event."""
        event = TraceEvent(
            opcode=opcode,
            pre_state=pre,
            post_state=post,
            result=result,
            cycle=len(self.events) + 1,
            payload=payload,
        )
        self.events.append(event)

    def _is_sqlite(self) -> bool:
        return hasattr(self.kernel, 'db') or 'SQLite' in type(self.kernel).__name__

    def _state(self) -> Dict[str, str]:
        if self._is_sqlite():
            return self._capture_state_sqlite()
        return self._capture_state()

    def boot(self, **kwargs) -> Dict[str, Any]:
        pre = self._state()
        result = self.kernel.boot(**kwargs)
        post = self._state()
        self._record("BOOT", pre, post, result)
        return result

    def load(self, resource_id: str, **kwargs) -> Dict[str, Any]:
        pre = self._state()
        result = self.kernel.load(resource_id, **kwargs)
        post = self._state()
        self._record("LOAD", pre, post, result, payload=resource_id)
        return result

    def validate(self, resource_id: str, **kwargs) -> Dict[str, Any]:
        pre = self._state()
        result = self.kernel.validate(resource_id, **kwargs)
        post = self._state()
        self._record("VALIDATE", pre, post, result, payload=resource_id)
        return result

    def exec(self, **kwargs) -> Dict[str, Any]:
        pre = self._state()
        result = self.kernel.exec(**kwargs)
        post = self._state()
        self._record("EXEC", pre, post, result)
        return result

    def yield_cycles(self, reason: str = "", requested_cycles: int = 1,
                     **kwargs) -> Dict[str, Any]:
        pre = self._state()
        result = self.kernel.yield_cycles(reason, requested_cycles, **kwargs)
        post = self._state()
        self._record("YIELD", pre, post, result,
                     payload=f"{reason}:{requested_cycles}")
        return result

    def commit(self, **kwargs) -> Dict[str, Any]:
        pre = self._state()
        result = self.kernel.commit(**kwargs)
        post = self._state()
        self._record("COMMIT", pre, post, result)
        return result

    def exit(self, **kwargs) -> Dict[str, Any]:
        pre = self._state()
        result = self.kernel.exit(**kwargs)
        post = self._state()
        self._record("EXIT", pre, post, result)
        return result

    def run_program(self, program: List[str],
                    verbose: bool = False) -> List[TraceEvent]:
        """Execute a program through the wrapped kernel and return the trace.

        The program is a list of opcode strings as accepted by the kernel's
        own run_program method. This method mirrors the kernel's dispatch
        logic but captures pre/post state for every step.
        """
        self.events = []

        for instruction in program:
            parts = instruction.strip().split()
            command = parts[0].upper()

            result = {"status": "FAIL", "error": "Unhandled opcode"}

            if command == "BOOT":
                result = self.boot(verbose=verbose)
            elif command == "YIELD":
                rest = instruction.strip()[5:].strip()
                if rest.startswith("'") or rest.startswith('"'):
                    quote_char = rest[0]
                    end_quote = rest.find(quote_char, 1)
                    reason = rest[1:end_quote].strip() if end_quote > 0 else ""
                    remaining = rest[end_quote + 1:].strip() if end_quote > 0 else ""
                    cycles = int(remaining) if remaining and remaining.isdigit() else 1
                else:
                    tokens = rest.split()
                    reason = tokens[0] if tokens else ""
                    cycles = int(tokens[1]) if len(tokens) > 1 and tokens[1].isdigit() else 1
                result = self.yield_cycles(reason, cycles, verbose=verbose)
            elif command == "LOAD":
                resource_id = parts[1] if len(parts) > 1 else ""
                result = self.load(resource_id, verbose=verbose)
            elif command == "VALIDATE":
                resource_id = parts[1] if len(parts) > 1 else ""
                result = self.validate(resource_id, verbose=verbose)
            elif command == "EXEC":
                result = self.exec(verbose=verbose)
            elif command == "COMMIT":
                result = self.commit(verbose=verbose)
            elif command == "EXIT":
                result = self.exit(verbose=verbose)

            if result.get("status") == "FAIL" and command not in ("COMMIT",):
                break

        return self.events
