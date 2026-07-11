# AEP-0008: Execution Guarantees, Fault Tolerance and Recovery

**Status:** Active
**Version:** 1.1.0
**Date:** 2026-07-11

---

## 0. Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

## 0.1 Scope

This specification covers **logical validation failures**: the detection of an
invalid state mutation at COMMIT and the deterministic rollback that follows,
as well as **watchdog exhaustion**: the detection of instruction-cycle
depletion and the structured recovery that follows.

Process crashes, write-ahead logging, and durability are **out of scope**; see
the Security Considerations in AEP-0001 and the version-control delegation
model. The kernel does not guarantee recovery from a process that is killed
mid-transaction — it guarantees that a *validated* transaction is applied, an
*invalid* one is rolled back, and an *exhausted* instruction budget is
reported, all within a running process.

---

## 1. The Abstract Watchdog Timer (Register R1)

Register R1 [WATCHDOG] acts as the strict instruction counter. Each EXEC
cycle consumes exactly one unit of R1.

### 1.1 Decrement Rule

R1 [WATCHDOG] MUST decrement by exactly one unit at the immediate start of
the EXEC phase of any opcode, before any semantic side-effects of that opcode
are evaluated. No other phase (BOOT, LOAD, VALIDATE, COMMIT, ROLLBACK, EXIT)
SHALL decrement R1.

### 1.2 The YIELD Instruction

If the agent determines that the computational complexity of a task requires
more cycles than the current R1 ceiling, it MUST emit the `YIELD` opcode
before `R1 == 0`.

```yaml
instruction: YIELD
payload:
  reason: "Descriptive string explaining the extension"
  requested_cycles: Integer
```

### 1.3 The R1 == 0 Edge Case (Rescue Path)

When `R1 == 1` and the next opcode is a valid `YIELD`, R1 MUST decrement to
`0` during the preceding EXEC. The Runtime MUST evaluate the `YIELD` opcode at
`R1 == 0` before triggering an exhaustion fault. If approved, the extension
MUST be applied immediately within the same execution step, rescuing the
Runtime from interruption.

If the next opcode at `R1 == 0` is NOT `YIELD`, an immediate exhaustion fault
MUST be triggered: the Runtime SHALL invoke a mandatory rollback, write
`AEP_ERR_WATCHDOG_EXHAUSTION` into R4, and terminate with `exit 1`.

### 1.4 Extension Capacity — Policy, Not Protocol

The specification does NOT dictate hardcoded cycle limits for YIELD. The
Runtime MUST enforce an implementation-defined maximum extension capacity and
expose its watchdog scaling policies independently. YIELD history MUST be
retained for auditing.

### 1.5 YIELD — Conditional Requirement

YIELD is a conditional extension opcode defined by this specification. It is
NOT part of the six-opcode core ISA (AEP-0001 §6).

- Implementations that enforce a Watchdog Timer (R1) MUST implement YIELD. A
  watchdog without YIELD provides no recovery path for valid long-running tasks
  and is NON-CONFORMANT with this specification.
- Implementations that do not enforce a Watchdog Timer MAY omit YIELD.
- A YIELD instruction MUST extend R1 [WATCHDOG] and MUST NOT modify any other
  register or resource.

---

## 2. Atomic Transactions and the Validation "Stderr" (R4)

The `COMMIT` opcode operates atomically within a process. A proposed state
mutation MUST NOT become persistent until it has passed the Runtime's syntactic
and semantic validation.

### 2.1 Failure and Structured Rollback Flow

If validation fails, the Runtime MUST perform the following steps, in order:

1. **Rollback:** The Runtime MUST discard the changes and restore the stable
   snapshot held in R3.
2. **Stderr injection:** The Runtime MUST write a structured error into R4.
3. **Self-correction loop:** The agent reads R4 on the next cycle and corrects.

### 2.2 Watchdog Exhaustion Rollback

Watchdog exhaustion is a critical transaction failure. The Runtime MUST
intercept the fault, invoke a mandatory rollback using its internal memory
snapshot, preserve `R0`, `R3` (delta-only), and `R7` intact for post-mortem
audits, populate `R4` with the error structure containing
`AEP_ERR_WATCHDOG_EXHAUSTION`, and terminate with `exit 1`.

### 2.3 R4 Stderr Example

```json
{
  "timestamp": "2026-07-05T01:18:03Z",
  "error_code": "AEP_ERR_WATCHDOG_EXHAUSTION",
  "trace": "Watchdog exhausted at cycle 3",
  "watchdog_at_failure": 0
}
```

### 2.4 Stable Snapshot (R3)

Before each COMMIT, the Runtime MUST capture the current state as a stable
snapshot in R3. On failure, the state MUST be restored to this snapshot.

---

## 3. Error Codes

Error codes are namespaced by the specification that defines the violated rule;
all codes are registered in this table regardless of origin.

| Code | Description |
|------|-------------|
| ERR_AEP_0002_VALIDATION | Resource validation failed |
| ERR_AEP_0003_E001 | Resource not found |
| ERR_AEP_0003_E002 | Dependency not found |
| ERR_AEP_0003_E003 | Invalid resource id: not a plain identifier |
| **AEP_ERR_WATCHDOG_EXHAUSTION** | Watchdog exhausted — instruction budget depleted |
| ERR_SYSTEM_UNEXPECTED | Unexpected system failure |

The runtime MUST write the protocol-level string `AEP_ERR_WATCHDOG_EXHAUSTION`
into R4 upon exhaustion. The runtime MUST NOT reference testing-framework
error codes (e.g., `KMC-001`) in its output.

---

## 4. Lifecycle with Fault Tolerance

```
BOOT → YIELD? → LOAD → VALIDATE → EXEC → COMMIT → EXIT
                  ↑                   │
                  └── R1 > 0 ─────────┘
                        ↓ (if == 0)
                    YIELD or HALT
```

### 4.1 Exit States

| State | Meaning |
|-------|---------|
| EXIT_0_SUCCESS | Session ended successfully |
| EXIT_1_WATCHDOG_TIMEOUT | Session ended by Watchdog timeout |
| ROLLBACK_EXECUTED | Rollback executed due to validation failure |
| ROLLBACK_FORCED | Rollback forced by an unexpected error |

---

## 5. Reference Implementation

See `implementations/python/aep/core/kernel.py` for the reference
implementation.

### 5.1 Main Methods

| Method | Opcode | Description |
|--------|--------|-------------|
| `boot()` | BOOT | Initialize the system with the Watchdog |
| `yield_cycles()` | YIELD | Request a cycle extension |
| `load()` | LOAD | Load a Resource with validation |
| `validate()` | VALIDATE | Validate Resource structure |
| `exec()` | EXEC | Run one EXEC cycle (R2 is opaque; see AEP-0003 §3.4) |
| `execute_commit()` | COMMIT | Transaction with logical validation rollback |
| `exit()` | EXIT | End the session |
