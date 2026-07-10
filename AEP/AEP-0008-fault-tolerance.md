# AEP-0008: Execution Guarantees, Fault Tolerance and Recovery

**Status:** Active
**Version:** 1.0.0
**Date:** 2026-07-05

---

## 0. Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

## 0.1 Scope

This specification covers **logical validation failures**: the detection of an
invalid state mutation at COMMIT and the deterministic rollback that follows.
Process crashes, write-ahead logging, and durability are **out of scope**; see
the Security Considerations in AEP-0001 and the version-control delegation
model. The kernel does not guarantee recovery from a process that is killed
mid-transaction — it guarantees that a *validated* transaction is applied and an
*invalid* one is rolled back within a running process.

---

## 1. The Abstract Watchdog Timer (Register R1)

Register R1 acts as the strict instruction counter (Instruction Counter /
Quantum). Each `EXEC` cycle consumes exactly one unit of R1.

### 1.1 The YIELD Instruction

If the agent determines that the computational complexity of a task requires
more cycles than the current R1 ceiling, it MUST emit the `YIELD` opcode before
`R1 == 0`.

```yaml
# Syntax
instruction: YIELD
payload:
  reason: "Descriptive string explaining the extension"
  requested_cycles: Integer (Max: 10)
```

### 1.2 Usage Example

```python
# Request a 3-cycle extension for complex processing
result = kernel.yield_cycles(
    reason="Validating complex dependency graph",
    requested_cycles=3
)
```

### 1.3 Limits

- Maximum cycles per YIELD: **10**. A YIELD requesting more than 10 MUST be
  refused.
- Global cycle limit: **20** (configurable via `max_watchdog_cycles`). A YIELD
  that would exceed the global limit MUST be refused.
- YIELD history MUST be retained for auditing.

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

### 2.2 R4 Stderr Example

```json
{
  "timestamp": "2026-07-05T01:18:03Z",
  "error_code": "ERR_AEP_0002_DANGLING_DEP",
  "trace": "Resource 'incident-04' has dangling dependency: 'nonexistent-resource'",
  "watchdog_at_failure": 2
}
```

### 2.3 Stable Snapshot (R3)

Before each COMMIT, the Runtime MUST capture the current state as a stable
snapshot in R3. On failure, the state MUST be restored to this snapshot.

---

## 3. Error Codes

| Code | Description |
|------|-------------|
| ERR_AEP_0002_VALIDATION | Resource validation failed |
| ERR_AEP_0003_E001 | Resource not found |
| ERR_AEP_0003_E002 | Dependency not found |
| ERR_AEP_0008_TIMEOUT | Watchdog expired |
| ERR_SYSTEM_UNEXPECTED | Unexpected system failure |

---

## 4. Lifecycle with Fault Tolerance

```
BOOT → YIELD? → LOAD → VALIDATE → EXEC → COMMIT → EXIT
                  ↑                   ↓
                  └── Watchdog > 0 ───┘
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

See `implementations/python/aep/core/kernel.py` for the complete implementation.

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
