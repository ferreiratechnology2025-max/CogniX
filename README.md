# AEP — Agent Execution Protocol

**Status:** Stable Specification  
**Version:** 1.1.0  
**Classification:** Deterministic Execution Envelope for AI Agents

[![Status: Stable](https://img.shields.io/badge/status-stable-brightgreen)]()
[![Version: 1.1.0](https://img.shields.io/badge/version-1.1.0-blue)]()
[![Behavioral tests: 10/10](https://img.shields.io/badge/pytest-10%2F10-brightgreen)]()
[![Normative: smoke 20/20](https://img.shields.io/badge/normative-smoke%2020%2F20-yellow)]()
[![Implementations: 3](https://img.shields.io/badge/implementations-3-blue)]()

---

> **AEP is a deterministic execution envelope for AI Agents.** It bounds state, cycles, transactions, and error recovery around the agent — using only structured files. The agent still executes the task; AEP makes everything *around* that execution deterministic.

---

## What is AEP?

AEP is a protocol that provides a deterministic execution envelope for AI agents over persistent knowledge resources. Based on:

- **Structured files** — Markdown, JSON, YAML, or any structured format
- **Universal Resource protocol** — all artifacts follow the same pattern
- **7 opcodes** — BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT, YIELD
- **Immutable kernel** — the kernel never changes, only programs and resources
- **Minimal state** — registers maintain only the current session delta

## What AEP is NOT

- Not an agent framework — it does not build agents.
- Not an execution sandbox — task execution belongs to the agent (see the
  Execution Boundary, AEP-0003 §3.4).
- Not a RAG alternative — different category.
- It does not make LLM inference deterministic — it makes everything *around*
  inference deterministic: state, cycles, transactions, error recovery.

---

## Specification

The protocol is formally defined in [AEP/](AEP/) documents:

| Document | Description | Status |
|----------|-------------|--------|
| [AEP-0001](AEP/AEP-0001-core.md) | Core Protocol | Stable |
| [AEP-0002](AEP/AEP-0002-resource.md) | Resource Specification | Stable |
| [AEP-0003](AEP/AEP-0003-isa.md) | Kernel ISA | Stable |
| [AEP-0004](AEP/AEP-0004-conformance.md) | Conformance Tests | Stable |
| [AEP-0005](AEP/AEP-0005-lifecycle.md) | Resource Lifecycle | Stable |
| [AEP-0006](AEP/AEP-0006-simplified.md) | Simplified Execution Mode | Stable |
| [AEP-0007](AEP/AEP-0007-profiles.md) | Compliance Profiles | Stable |
| [AEP-0008](AEP/AEP-0008-fault-tolerance.md) | Fault Tolerance & Execution Guarantees | Active |

For the pure specification without implementation details, see [AEP/README.md](AEP/README.md).

---

## Implementations

| Implementation | Status | Conformance | Notes |
|----------------|--------|-------------|-------|
| Reference (Markdown) | Stable | N/A — executable conformance not applicable (LLM-interpreted) | KOS v6.0 |
| Python | Stable | pytest 10/10 behavioral; normative smoke 10 | Watchdog + validation rollback |
| SQLite | Stable | normative smoke 10 (no behavioral suite yet) | Indexer & complex resource querying |

---

## Fault Tolerance (AEP-0008)

AEP-0008 (Active) bounds the execution envelope around the agent. Its scope is
**logical validation failures**, not process crashes:

- **Watchdog Timer (R1):** Bounds runaway loops. An agent issues a `YIELD`
  instruction to request additional cycles when a task is valid but complex.
- **Validation rollback:** COMMIT buffers changes and validates them. If a
  resource fails schema validation, the runtime discards the change, restores
  the last stable snapshot (`R3`), and writes a structured error into `R4`
  (AEP Stderr) for self-correction.

Scope boundary: this is logical rollback within a single process. Process
crashes, write-ahead logging, and crash recovery are out of scope (see the
Security Considerations in AEP-0001). Durability of history is delegated to the
underlying version control system, not guaranteed by the kernel.

---

## Conformance

Conformance is exercised at three levels, with different strengths. Read the
labels literally:

- **Behavioral suite (pytest) — real conformance evidence.** `implementations/python/tests/`
  exercises distinct kernel behavior, including the Execution Boundary
  (`test_exec_does_not_interpret_r2`, verified to fail against a kernel that
  executes R2). This is the strongest guarantee the repo currently offers.
  ```bash
  cd implementations/python && python -m pytest
  ```
- **Normative suite — pipeline smoke.** `conformance/normative/test_runner.py`
  runs a default program end-to-end against the python and sqlite runtimes
  (10 cases × 2 runtimes). It currently asserts only status + exit code and
  runs the same default program for every case; each case's per-case
  `procedure` is **documented but not yet enforced by the runner**. Treat
  "20/20" as a pipeline smoke test, not 10 distinct scenarios.
  ```bash
  python conformance/normative/test_runner.py
  ```
- **Compliance Kit — structural validation only.** The
  [Compliance Kit](compliance-kit/) validates that third-party *test
  definitions* are well-formed. It does **not** yet execute implementations;
  runtime conformance is verified by the normative runner and the pytest suite.
  ```bash
  python compliance-kit/runner/runner.py --implementation /path/to/runtime
  ```

See [compliance-kit/README.md](compliance-kit/README.md) for details.

---

## Compliance Profiles

| Profile | Opcodes | Use Case |
|---------|---------|----------|
| **Lite** | LOAD, EXEC, COMMIT | Edge agents, prototyping |
| **Extended** | LOAD, VALIDATE, EXEC, COMMIT, EXIT | Enterprise, auditing |

---

## Benchmarks

Protocol overhead benchmarks: planned.

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/ferreiratechnology2025-max/CogniX.git
cd CogniX
```

### 2. Quick start
```bash
# With Claude Code
claude "Read AGENTS.md and execute the task"

# With Cursor
cursor "Read AGENTS.md and execute the task"
```

### 3. Create a Resource
```yaml
---
type: project
id: my-project
version: 1.0.0
status: active
---
# My Project
```

---

## Architecture

### Registers (R0-R7)
| Register | Function | Rule |
|----------|----------|------|
| R0 [SESSION] | Session identifier | Generated at BOOT |
| R1 [WATCHDOG] | Instruction counter | Decremented per operation, extendable via YIELD |
| R2 [NEXT_ACT] | Next planned action | Defined by agent |
| R3 [MODIFIED] | Modified files this session | Delta only |
| R4 [STDERR] | Structured error output | Written on rollback |
| R5 [ACTIVE_SK] | Active skill | Defined by agent |
| R6 [HEALTH] | System health | OK or FAIL |
| R7 [TIMESTAMP] | Session timestamp | Updated at COMMIT |

---

## Governance

- [ROADMAP.md](ROADMAP.md) — Project roadmap
- [CHANGELOG.md](CHANGELOG.md) — Version history

---

## License

MIT

---

## Project Status

| Component | Status |
|-----------|--------|
| Specification (AEP-0001 to AEP-0007) | Stable |
| Specification (AEP-0008 Fault Tolerance) | Active |
| Python Runtime — behavioral tests (pytest) | 10/10 passed |
| Normative suite | 10 cases × 2 runtimes (pipeline smoke; see Conformance) |
| Compliance Kit | Structural validation only (does not execute implementations) |
| Independent Implementations | Seeking contributors |

**Stage: Specification with a validation-rollback execution envelope.** The
kernel provides a Watchdog Timer and logical validation rollback (see
AEP-0008, Active). Behavioral conformance is exercised by the pytest suite;
the normative runner currently performs a pipeline smoke test (see
[Conformance](#conformance)).
