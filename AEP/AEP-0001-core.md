# AEP-0001: Core Protocol

**Status:** Stable  
**Version:** 1.0.0  
**Date:** 2026-07-05  
**Author:** KOS Contributors  

---

## 1. Introduction

This document specifies the core protocol for Agent Execution Protocol (AEP).

## 2. Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 3. Core Concepts

### 3.1 Resource
A Resource is a unit of knowledge.

**Structure:**
- `type` (REQUIRED): The type of resource
- `id` (REQUIRED): Unique identifier
- `version` (REQUIRED): Semantic version
- `depends` (OPTIONAL): Array of resource IDs
- `status` (REQUIRED): draft | review | active | deprecated | archived

**Rules:**
- `id` MUST be unique
- `id` MUST use kebab-case
- `version` MUST follow SemVer
- `depends` MUST reference existing resources
- `status` MUST be one of the defined values

### 3.2 State Registers
State is maintained as eight registers (R0-R7):

| Register | Name | Purpose | Update Rule |
|----------|------|---------|-------------|
| R0 | SESSION | Session identifier | Set on BOOT |
| R1 | LAST_ACT | Last action performed | Set on COMMIT |
| R2 | NEXT_ACT | Next action planned | Set by agent |
| R3 | MODIFIED | Files modified in current session | **MUST contain ONLY the delta** |
| R4 | BLOCKERS | Current blockers | Updated as needed |
| R5 | ACTIVE_SK | Active skill | Set by agent |
| R6 | HEALTH | System health | Updated on VALIDATE |
| R7 | TIMESTAMP | Session timestamp | Updated on COMMIT |

**Rules:**
- R3 MUST contain ONLY the delta of the current session
- R3 MUST NOT accumulate history
- History MUST be maintained in Git, not in state

### 3.3 Program
A Program is a sequence of opcodes.

**Default Program:**
```
BOOT
LOAD [ACTIVE_PROJECT]
LOAD [ACTIVE_STATUS]
VALIDATE [ACTIVE_PROJECT]
VALIDATE [ACTIVE_STATUS]
EXEC
COMMIT
EXIT
```

## 4. Boot Sequence

1. Read `AGENTS.md`
2. Read `KERNEL/BOOT.md`
3. Load `KERNEL/STATE.md`
4. Load `KERNEL/PROGRAM.md`
5. Execute first opcode

## 5. Resource Types

| Type | Purpose | Required Fields |
|------|---------|-----------------|
| project | Project definition | objective, scope, stack, rules |
| status | Current state | R0-R7 registers |
| skill | Reusable knowledge | objective, procedure, examples |
| adr | Architectural decision | problem, decision, consequences |
| incident | Error log | problem, cause, fix, prevention |
| rule | Project rule | applies to, description |
| template | Template for new Resources | usage instructions |

## 6. Implementation Requirements

A conforming implementation (Full conformance):
- MUST implement all six core opcodes (BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT)
- MUST follow all contracts
- MUST maintain R0-R7 registers
- MUST support Resource protocol
- MUST persist state across sessions
- MUST use Git for history

A seventh opcode, YIELD, is defined as a conditional extension in AEP-0008
(required if and only if the implementation enforces a Watchdog Timer). Reduced
conformance classes are defined in AEP-0007.

## 7. Extensibility

New Resource types MAY be added without changing the protocol.

## 8. Versioning

- 0.x.x: Draft (unstable)
- 1.0.0: Active (stable)
- 1.x.x: Active (compatible)
- 2.0.0: Active (breaking change)

## 9. Security Considerations

AEP is an execution *envelope*: it governs state, cycles, transactions, and
error recovery, but it does not execute task payloads. The kernel's attack
surface is therefore limited to three operations:

1. **Opcode parsing.** The kernel parses a fixed, closed set of opcodes — the
   six core opcodes plus the conditional YIELD extension (AEP-0008). The set
   remains closed: unknown opcodes MUST fail without side effects. Opcode
   arguments are the only agent-controlled input the kernel acts upon.

2. **Resource ID resolution.** `LOAD`/`VALIDATE` resolve a `resource_id` to a
   file path. Implementations MUST reject any `resource_id` that is not a
   plain identifier (kebab-case; no path separators, no `..`) before touching
   the filesystem, so that resolution cannot escape the resource directory.

3. **State writing.** The kernel persists registers R0–R7 to a fixed state
   location. Register *values* are opaque data; they are written and read
   back verbatim and MUST NOT be interpreted as instructions.

Payload execution is explicitly excluded from this surface by the Execution
Boundary (AEP-0003 section 3.4): R2 [NEXT_ACT] is opaque, and an implementation
that interprets, evaluates, or executes R2 contents is NON-CONFORMANT.
Consequently, threats such as arbitrary code execution, shell injection, and
sandbox escape are out of scope for the kernel — they belong to the agent's
own execution environment, not to the protocol. Process crashes and durability
are likewise out of scope; recovery of committed history is delegated to the
underlying version control system.