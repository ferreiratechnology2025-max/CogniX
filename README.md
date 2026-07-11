# AEP — Agent Execution Protocol

**Status:** Stable Specification  
**Version:** 1.1.0  
**Classification:** Deterministic Execution Envelope for AI Agents

[![Status: Stable](https://img.shields.io/badge/status-stable-brightgreen)]()
[![Version: 1.1.0](https://img.shields.io/badge/version-1.1.0-blue)]()
[![Behavioral tests: 23/23](https://img.shields.io/badge/pytest-23%2F23-brightgreen)]()
[![Normative: 28/28](https://img.shields.io/badge/normative-28%2F28-brightgreen)]()
[![KMC Oracle: 14/14](https://img.shields.io/badge/kmc-14%2F14-brightgreen)]()
[![Implementations: 2](https://img.shields.io/badge/implementations-2-blue)]()

---

> **AEP is a deterministic execution envelope for AI Agents.** It bounds state, cycles, transactions, and error recovery around the agent — using only structured files. The agent still executes the task; AEP makes everything *around* that execution deterministic.

---

## What is AEP?

AEP is a protocol that provides a deterministic execution envelope for AI agents over persistent knowledge resources. Based on:

- **Structured files** — Markdown, JSON, YAML, or any structured format
- **Universal Resource protocol** — all artifacts follow the same pattern
- **6 core opcodes** — BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT — plus YIELD (conditional extension, AEP-0008)
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
| [GOVERNANCE](AEP/GOVERNANCE.md) | Promotion Criteria (Active → Stable) | Active |

For the pure specification without implementation details, see [AEP/README.md](AEP/README.md).

---

## Implementations

| Implementation | Status | Conformance | Notes |
|----------------|--------|-------------|-------|
| Reference (Markdown) | Stable | N/A — interpreted by LLM, not executable | KOS v6.0 |
| Python | Stable | **23/23** behavioral (pytest); **14/14** normative; **14/14** KMC oracle | Full watchdog, YIELD, validation rollback |
| SQLite | Stable | **14/14** normative (no behavioral suite yet) | Indexer & complex resource querying |

---

## Fault Tolerance (AEP-0008)

AEP-0008 (Active) bounds the execution envelope around the agent. Its scope is
**logical validation failures** and **watchdog exhaustion**, not process crashes:

- **Watchdog Timer (R1):** Decrements only on EXEC (AEP-0008 §1.1). An agent
  issues a `YIELD` instruction *preventively* to request additional cycles.
  Exhaustion at R1=0 triggers immediate halt with `AEP_ERR_WATCHDOG_EXHAUSTION`
  and rollback preserving R0, R3, R7.
- **Validation rollback:** COMMIT buffers changes and validates them. If a
  resource fails schema validation, the runtime discards the change, restores
  the last stable snapshot (`R3`), and writes a structured error into `R4`
  (AEP Stderr) for self-correction.

Scope boundary: this is logical rollback within a single process. Process
crashes, write-ahead logging, and crash recovery are out of scope (see the
Security Considerations in AEP-0001). Durability of history is delegated to the
underlying version control system, not guaranteed by the kernel.

See [AEP/GOVERNANCE.md](AEP/GOVERNANCE.md) for the Active → Stable promotion
criteria (C1–C6) that govern AEP-0008's path to frozen status.

---

## Conformance

Conformance is exercised at four levels, with increasing strength. Read the
labels literally:

### 1. KMC Behavioral Oracle — strongest guarantee

The [Kernel Metamorphic Oracle](conformance/kmc/) (`conformance/kmc/`) is a
**passive invariant checker** that validates execution traces against four
metamorphic invariants (KMC-001 through KMC-004). It imports zero kernel code
and operates solely on `TraceEvent` data.

```bash
python -m pytest conformance/kmc/test_kmc.py
```

**14/14** — 6 valid traces + 4 deliberate mutants (teeth checks) + 4 integration.

### 2. Behavioral suite (pytest) — real conformance evidence

`implementations/python/tests/` exercises distinct kernel behavior, including
the Execution Boundary (`test_exec_does_not_interpret_r2`, verified to fail
against a kernel that executes R2), snapshot rollback with teeth checks,
watchdog exhaustion, and YIELD isolation.

```bash
cd implementations/python && python -m pytest
```

**23/23** — covers watchdog, YIELD, rollback, R2 opacity, snapshot C12, atomic I/O, KOS isolation.

### 3. Normative suite — cross-runtime smoke

`conformance/normative/test_runner.py` runs **14 test cases** (11 core + 3
watchdog) against each runtime, validated by the KMC oracle when available.

```bash
python conformance/normative/test_runner.py
```

**Python:** 14/14 ✅ | **SQLite:** 14/14 ✅

### 4. Compliance Kit — structural validation only

The [Compliance Kit](compliance-kit/) validates that third-party *test
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
| R1 [WATCHDOG] | Instruction counter | Decremented **only on EXEC** (§1.1), extendable via YIELD |
| R2 [NEXT_ACT] | Next planned action | Defined by agent; opaque to kernel (§3.4) |
| R3 [MODIFIED] | Modified files this session | Delta only |
| R4 [STDERR] | Structured error output | Written on rollback or exhaustion |
| R5 [ACTIVE_SK] | Active skill | Defined by agent |
| R6 [HEALTH] | System health | OK or FAIL |
| R7 [TIMESTAMP] | Session timestamp | Microsecond granularity (`%Y-%m-%dT%H:%M:%S.%fZ`) |

---

## Governance

- [AEP/GOVERNANCE.md](AEP/GOVERNANCE.md) — Promotion criteria (C1–C6) for Active → Stable
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
| Governance (AEP/GOVERNANCE.md) | Active |
| Python Runtime — behavioral tests (pytest) | 23/23 passed |
| KMC Behavioral Oracle | 14/14 passed |
| Normative suite | 14 cases × 2 runtimes (28/28) |
| Compliance Kit | Structural validation only (does not execute implementations) |
| Independent Implementations | Seeking contributors |

**Stage: Specification with watchdog and validation-rollback execution envelope.**
The kernel provides an abstract Watchdog Timer (R1 decrements only on EXEC),
preventive YIELD extension, immediate exhaustion with `AEP_ERR_WATCHDOG_EXHAUSTION`,
and logical validation rollback (see AEP-0008, Active). Behavioral conformance
is exercised by the KMC oracle and the pytest suite; the normative runner
validates both Python and SQLite at parity.
