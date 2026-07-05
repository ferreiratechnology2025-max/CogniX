# AEP — Agent Execution Protocol

**Status:** Stable Specification  
**Version:** 1.1.0  
**Classification:** Execution Protocol for AI Agents

[![Status: Stable](https://img.shields.io/badge/status-stable-brightgreen)]()
[![Version: 1.1.0](https://img.shields.io/badge/version-1.1.0-blue)]()
[![Conformity: 18/18](https://img.shields.io/badge/conformity-18%2F18-brightgreen)]()
[![Implementations: 3](https://img.shields.io/badge/implementations-3-blue)]()

---

> **AEP is an Execution Protocol for AI Agents.** It defines how agents can persist state, share knowledge, and execute tasks deterministically — using only structured files.

---

## What is AEP?

AEP is a protocol for deterministic execution of AI agents over persistent knowledge resources. Based on:

- **Structured files** — Markdown, JSON, YAML, or any structured format
- **Universal Resource protocol** — all artifacts follow the same pattern
- **7 opcodes** — BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT, YIELD
- **Immutable kernel** — the kernel never changes, only programs and resources
- **Minimal state** — registers maintain only the current session delta

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
| [AEP-0008](AEP/AEP-0008-fault-tolerance.md) | Fault Tolerance & Execution Guarantees | Stable |

For the pure specification without implementation details, see [AEP/README.md](AEP/README.md).

---

## Implementations

| Implementation | Status | Conformance | Notes |
|----------------|--------|-------------|-------|
| Reference (Markdown) | Stable | 18/18 | KOS v6.0 |
| Python | Stable | 18/18 | RTOS-like capabilities (Watchdog, ACID) |
| SQLite | Stable | 18/18 | Indexer & complex resource querying |

---

## Fault Tolerance (AEP-0008)

Differing from standard LLM frameworks, the AEP core doesn't just prompt the agent — it bounds it within a deterministic sandbox:

- **Watchdog Timer (R1):** Prevents token-draining infinite loops. Agents must issue a `YIELD` instruction to request more CPU cycles if a task is valid but complex.
- **ACID Transactions:** Buffers all changes. If the LLM generates an invalid resource schema, the runtime triggers a `ROLLBACK` to the last stable state (`R3`) and dumps a structured stack trace into `R4` (AEP Stderr) for self-correction.

---

## Compliance Kit

An independent [Compliance Kit](compliance-kit/) is available for third-party implementations to validate conformance.

```bash
# Run compliance tests against your implementation
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

## Benchmark (Preliminary)

| Metric | AEP | RAG Baseline | Improvement |
|--------|-----|--------------|-------------|
| Tokens | 390 | 1950 | -80% |
| Accuracy | 95% | 78% | +22% |
| Latency | ~50ms | ~200ms | -75% |

*Preliminary benchmark under controlled conditions. See [METHODOLOGY](tools/aep-benchmark/METHODOLOGY.md).*

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
| Specification (AEP-0001 to AEP-0008) | Stable |
| Python Runtime | 18/18 tests passed |
| Compliance Kit | Available |
| Independent Implementations | Seeking contributors |

**Stage: Stable Specification with Fault Tolerance Guarantees**

> AEP v1.1.0 is a stable specification with OS-level guarantees (ACID), Watchdog Timer, and protection against infinite loops. Ready for production adoption.
