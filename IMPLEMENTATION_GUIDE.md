# AEP Implementation Guide

**For third-party runtime authors.**  
This guide assumes you have read the AEP specification suite (AEP-0001 through AEP-0008) and the Architecture Decision Records (`ARCHITECTURE_DECISIONS.md`). It does not replace the normative specification — it provides the implementation pathway.

---

## 1. Conformance Kit Overview

To implement a conformant AEP runtime, you need **three artifacts** and nothing else:

| Artifact | Role |
|----------|------|
| **AEP specifications (AEP-0001 to AEP-0008)** | Normative contract. Every MUST/SHALL clause is authoritative. |
| **Conformance test suite** (`conformance/normative/` + `conformance/kmc/`) | Automated pass/fail against the contract. |
| **This guide** | Non-normative implementation pathway and edge-case map. |

The KMC Behavioral Oracle (`conformance/kmc/`) is a **passive checker** — it reads execution traces and validates metamorphic invariants without importing or executing your runtime code. You do not need to modify it. You only need to produce traces it can consume (see §5).

---

## 2. Lifecycle Contract and State Machine

The AEP runtime is a **deterministic finite-state machine** over six core opcodes plus one conditional extension:

```
BOOT → LOAD → VALIDATE → EXEC → COMMIT → EXIT
                          ↑
                     YIELD (conditional)
```

### 2.1 Opcode Contracts

| Opcode | Precondition | Effect | R1 (Watchdog) |
|--------|-------------|--------|---------------|
| `BOOT` | None | Initializes session (R0), loads program, seeds R1 | Set to configured initial value |
| `LOAD` | `BOOT` executed | Loads resource by ID into memory | **Not decremented** (§1.1) |
| `VALIDATE` | Resource loaded | Validates structure (type, id, version, status) | **Not decremented** (§1.1) |
| `EXEC` | `R2` defined | Decrements R1; task is **not** interpreted by kernel | **Decremented by exactly 1** |
| `COMMIT` | None | Persists changes; on validation failure: rollback + R4 | **Not decremented** (§1.1) |
| `EXIT` | None | Records final health state | **Not decremented** (§1.1) |
| `YIELD` | None (always permitted) | Extends R1 by requested cycles (max 10 per call) | Increased by `requested_cycles` |

### 2.2 Register Semantics

| Register | Name | Type | Persistence |
|----------|------|------|-------------|
| R0 | SESSION | session identifier (string) | Generated at BOOT; preserved on exhaustion |
| R1 | WATCHDOG | integer counter | Decremented only on EXEC; modified by YIELD |
| R2 | NEXT_ACT | opaque string | Defined by agent; kernel MUST NOT interpret |
| R3 | MODIFIED | JSON string (delta) | Cleared per COMMIT; captures pre-commit snapshot |
| R4 | STDERR | structured error (JSON) | Written on rollback or exhaustion |
| R5 | ACTIVE_SK | skill identifier (string) | Defined by agent |
| R6 | HEALTH | `OK` or `FAIL` | Set to FAIL on exhaustion or rollback |
| R7 | TIMESTAMP | ISO 8601 with microseconds | Updated at EXEC, COMMIT, EXIT |

### 2.3 Watchdog Exhaustion (AEP-0008 §1.3)

When R1 reaches 0 at the start of any opcode:

1. The operation is **aborted** — no side effects are produced.
2. The runtime writes a structured error to R4 with `error_code: AEP_ERR_WATCHDOG_EXHAUSTION`, a human-readable trace, and the watchdog value at failure.
3. R6 is set to `FAIL`.
4. R7 is set to `EXIT_1_WATCHDOG_TIMEOUT`.
5. R0, R3, and R7 are preserved (rollback scope).
6. The runtime returns `status: FAIL` with `rollback: true`.

YIELD is **preventive only** — it must be called before exhaustion. There is no rescue path once R1 reaches 0.

### 2.4 Validation Rollback (AEP-0008 §2)

On COMMIT, if a resource fails schema validation:

1. The transaction is discarded.
2. State is restored from the pre-commit snapshot captured in R3.
3. A structured error is written to R4 with `error_code: ERR_AEP_0002_VALIDATION`.
4. R7 is set to `ROLLBACK_EXECUTED`.

---

## 3. Sandbox Isolation

The runtime MUST respect the `AEP_STATE_PATH` environment variable for all persistent state operations.

### 3.1 State File Resolution

```
if AEP_STATE_PATH is set:
    state_file = AEP_STATE_PATH
else:
    state_file = <runtime_root>/AEP/runtime_state/state.md
```

- The state file uses Markdown with YAML frontmatter. Register lines follow the format `R1 [WATCHDOG] = 5`.
- The runtime MUST create the parent directory if it does not exist.
- The runtime MUST write state atomically (write to a temporary file in the same directory, then rename) to prevent partial writes.

### 3.2 Resource Directory

Resources are stored under `<runtime_root>/RESOURCES/` as Markdown files with YAML frontmatter:

```markdown
---
type: project
id: my-resource
version: 1.0.0
depends: [base-resource]
status: active
---
# My Resource
```

- Each file is named `<resource-id>.md`.
- Required frontmatter fields: `type`, `id`, `version`, `status`.
- The `depends` field is optional and declares resource dependencies.
- Path traversal in resource IDs (`../`, absolute paths) MUST be rejected with `ERR_AEP_0003_E003`.

### 3.3 CI/CD Injection

For CI pipelines, set `AEP_STATE_PATH` to a temporary path unique per run:

```yaml
env:
  AEP_STATE_PATH: ${{ github.workspace }}/.ci_sandbox/state.md
```

This guarantees that each execution starts from a clean state and leaves no residue between runs. The conformance workflow in this repository uses this exact pattern.

---

## 4. Reference Payloads

### 4.1 Valid Program (Full Cycle)

This program executes a complete AEP lifecycle and MUST return `status: OK` for every opcode.

```json
{
  "program": [
    "BOOT",
    "YIELD 'prepare for load' 2",
    "LOAD project-core",
    "VALIDATE project-core",
    "EXEC",
    "COMMIT",
    "EXIT"
  ],
  "resources": {
    "project-core": {
      "type": "project",
      "id": "project-core",
      "version": "1.0.0",
      "status": "active"
    }
  },
  "expected": {
    "BOOT":    { "status": "OK", "watchdog_initial": "5" },
    "YIELD":  { "status": "OK", "new_watchdog": 7 },
    "LOAD":   { "status": "OK" },
    "VALIDATE": { "status": "OK" },
    "EXEC":   { "status": "OK", "watchdog_remaining": 6 },
    "COMMIT": { "status": "OK" },
    "EXIT":   { "status": "OK" }
  }
}
```

Key assertions for the implementer:
- R1 starts at 5 (default), YIELD adds 2 → 7, EXEC decrements → 6.
- LOAD and VALIDATE do **not** change R1.
- EXEC does **not** interpret R2 — returns it verbatim.
- COMMIT persists state without decrementing R1.

### 4.2 Invalid Program (Watchdog Exhaustion)

This program triggers immediate watchdog exhaustion on the second EXEC.

```json
{
  "program": [
    "BOOT",
    "EXEC",
    "EXEC",
    "EXEC"
  ],
  "r1_initial": 2,
  "resources": {},
  "expected": {
    "BOOT":  { "status": "OK" },
    "EXEC":  { "status": "OK", "watchdog_remaining": 1 },
    "EXEC":  { "status": "FAIL",
               "error_code": "AEP_ERR_WATCHDOG_EXHAUSTION",
               "rollback": true,
               "watchdog_remaining": 0 }
  }
}
```

Key assertions for the implementer:

| Step | R1 before | Operation | R1 after | Status |
|------|-----------|-----------|----------|--------|
| BOOT | — | Initialize | 2 | OK |
| EXEC | 2 | Decrement → 1 | 1 | OK |
| EXEC | 1 | Decrement → 0 | 0 | **FAIL (exhaustion)** |
| EXEC | 0 | Guard blocks | 0 | **Not reached** (program halts) |

The third EXEC is never reached because the program halts on the second EXEC failure. The runtime MUST stop execution immediately on any opcode returning `FAIL`.

### 4.3 Invalid Resource (Validation Rollback)

```json
{
  "program": [
    "BOOT",
    "LOAD bad-resource",
    "COMMIT bad-resource"
  ],
  "resources": {
    "bad-resource": {
      "id": "bad-resource",
      "version": "1.0.0",
      "status": "active"
    }
  },
  "expected": {
    "BOOT":  { "status": "OK" },
    "LOAD":  { "status": "OK" },
    "COMMIT": { "status": "FAIL",
                "rollback": true,
                "error_code": "ERR_AEP_0002_VALIDATION" }
  }
}
```

Key assertions:
- `bad-resource` is missing the required `type` field.
- COMMIT detects the validation failure, discards the change, and writes the error to R4.
- R7 is set to `ROLLBACK_EXECUTED`.

---

## 5. Independent Validation Roadmap

### 5.1 Plug Your Runtime into the Normative Runner

The normative test runner (`conformance/normative/test_runner.py`) drives all 14 test cases against each registered runtime. To add yours:

1. **Create a test method** in `AEPTestRunner` similar to `_test_python_runtime` or `_test_sqlite_runtime`:
   - Accept a `test_data` dictionary.
   - Execute your runtime's CLI or API with the test's program and resources.
   - Return a dict with `status`, `returncode`, and optional `stdout`.

2. **Register the runtime** in the `runtime` argument of `run_all()`.

3. **Handle KMC tracing** — your runtime does not need to integrate the KMC oracle directly. The runner calls the oracle separately on the trace produced by the Python kernel's equivalent program. Your runtime's pass/fail is compared against expected status and exit code.

### 5.2 Conformance Target

| Suite | Tests | Target |
|-------|-------|--------|
| Normative | 14 (11 core + 3 watchdog) | 14/14 |
| KMC Oracle | 14 (6 valid + 4 mutant + 4 integration) | 14/14 |
| Behavioral (Python) | 23 | Reference only — your runtime may use different test infrastructure |

The normative suite is the **minimum bar** for claiming AEP conformance. The KMC oracle provides metamorphic invariant verification that catches semantic regressions.

### 5.3 Implementation Order (Recommended)

1. **State persistence** — implement `AEP_STATE_PATH`-aware state load/save with atomic writes.
2. **Resource loading** — implement `RESOURCES/` directory scanning with path traversal rejection.
3. **Opcode execution** — implement the FSM: `BOOT → LOAD → VALIDATE → EXEC → COMMIT → EXIT`.
4. **Watchdog** — implement R1 decrement **only** on EXEC, YIELD extension, exhaustion guard on every opcode.
5. **Validation rollback** — implement pre-COMMIT snapshot capture and state restoration on failure.
6. **Run normative suite** — plug into `test_runner.py` and iterate until 14/14.
7. **KMC oracle** — validate that your execution traces pass all four metamorphic invariants.

### 5.4 Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| R1 decremented in LOAD/VALIDATE | Normative watchdog tests fail | Guard every opcode except EXEC and YIELD |
| YIELD after R1=0 | Silent cycle extension | YIELD is preventive — check happens before any opcode runs |
| R2 executed/interpreted | Behavioral test detects side effect | R2 is opaque — store and return, never eval |
| Non-atomic state write | Partial state file on crash | Write to temp file, then `rename`/`os.replace` |
| Missing `type` in resource frontmatter | Validation passes for invalid resources | Validate all required fields: `type`, `id`, `version`, `status` |
| State file path hardcoded | CI pipelines leave residue between runs | Always read `AEP_STATE_PATH` environment variable first |
