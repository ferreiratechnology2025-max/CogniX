"""
KMC data models — trace events and oracle results.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class TraceEvent:
    """A single step in an execution trace.

    Captures the opcode executed, the register state before and after,
    the result dict returned by the kernel, and the oracle's internal
    cycle counter at this step.
    """
    opcode: str
    pre_state: Dict[str, str]
    post_state: Dict[str, str]
    result: Dict[str, Any]
    cycle: int
    payload: Optional[str] = None


@dataclass
class KMCResult:
    """Result of a KMC oracle validation run."""
    task_id: str
    behavioral_valid: bool
    failure_mode: Optional[str] = None
    failure_detail: Optional[str] = None
    metrics: Dict[str, int] = field(default_factory=dict)
    registers_final_snapshot: Dict[str, str] = field(default_factory=dict)
    assertions_passed: int = 0
    assertions_failed: int = 0
    trace_exit_code: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "behavioral_valid": self.behavioral_valid,
            "failure_mode": self.failure_mode,
            "failure_detail": self.failure_detail,
            "metrics": self.metrics,
            "registers_final_snapshot": self.registers_final_snapshot,
            "assertions_passed": self.assertions_passed,
            "assertions_failed": self.assertions_failed,
            "trace_exit_code": self.trace_exit_code,
        }
