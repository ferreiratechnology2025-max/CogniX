# AEP-0003: Kernel ISA

**Status:** Stable  
**Version:** 1.0.0  
**Date:** 2026-07-05  

---

## 1. Introduction

This document specifies the Instruction Set Architecture (ISA) for the Agent Execution Protocol.

## 2. Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 3. Opcodes

### 3.1 BOOT
**Purpose:** Initialize the system.

**Behavior:**
1. Load STATE
2. Load PROGRAM
3. Set R0 to current timestamp

**Contracts:**
- Input: STATE.md, PROGRAM.md
- Output: System initialized
- Side effects: None

### 3.2 LOAD
**Purpose:** Load a Resource by ID.

**Behavior:**
1. Locate Resource
2. Load content
3. Recursively load dependencies

**Contracts:**
- Input: Resource ID
- Output: Resource loaded
- Side effects: None

**Errors:**
- Resource not found → FAIL
- Missing dependency → FAIL
- Circular dependency → FAIL

### 3.3 VALIDATE
**Purpose:** Validate Resource structure.

**Behavior:**
1. Verify Resource exists
2. Validate all required fields
3. Check dependencies

**Contracts:**
- Input: Resource ID
- Output: OK or FAIL

**Validation Rules:**
- type MUST be valid
- id MUST be unique
- version MUST be SemVer
- depends MUST exist
- status MUST be valid

### 3.4 EXEC — Execution Boundary
**Purpose:** Mark the point where task execution occurs.

The EXEC opcode marks the point where task execution occurs. The semantics of
the task itself are OUT OF SCOPE for this protocol.

**Normative clauses:**
- The kernel MUST NOT interpret, evaluate, or execute the contents of
  R2 [NEXT_ACT]. R2 is opaque to the kernel.
- The kernel MUST decrement R1 [WATCHDOG] exactly once per EXEC cycle and
  MUST refuse the cycle if R1 == 0.
- The executing agent is the sole execution environment. Task consequences
  re-enter the protocol ONLY through R3 [MODIFIED] and are subject to
  VALIDATE/COMMIT.
- Implementations MUST NOT add execution semantics to EXEC (e.g., eval, shell
  dispatch, subprocess). An implementation that executes R2 contents is
  NON-CONFORMANT.

**Behavior:**
1. Read R2 [NEXT_ACT] as an opaque value
2. Decrement R1 [WATCHDOG]; refuse the cycle if R1 == 0
3. Update R1 [LAST_ACT] and R7 [TIMESTAMP]

**Contracts:**
- Input: R2 [NEXT_ACT] (opaque)
- Output: EXEC cycle acknowledged; R2 returned unchanged
- Side effects: Register update only; the kernel writes no files as a result
  of R2's contents

### 3.5 COMMIT
**Purpose:** Persist changes.

**Behavior:**
1. Persist modified Resources
2. Clear R3 (set to delta only)
3. Classify new knowledge
4. Update R1, R7

**Contracts:**
- Input: Modified Resources
- Output: Resources persisted
- Side effects: Writes files

**Rules:**
- R3 MUST contain ONLY delta
- History MUST be in Git, not state

### 3.6 EXIT
**Purpose:** End session.

**Behavior:**
1. Save final STATE
2. Log timestamp
3. Close session

**Contracts:**
- Input: None
- Output: Session ended
- Side effects: Saves STATE

## 4. Execution Flow

The core flow consists of the six core opcodes:

```
BOOT → LOAD → VALIDATE → EXEC → COMMIT → EXIT
```

A conforming agent MUST execute the core opcodes in this order.

### 4.1 Conditional Branch — YIELD

YIELD is a conditional extension (AEP-0008), not part of the core flow. It is
**agent-initiated**: when the Watchdog Timer (R1) approaches 0, the agent emits
YIELD to request additional cycles before returning to the EXEC cycle:

```
… EXEC → YIELD? → (back to the cycle while R1 > 0)
```

The full contract has two sides — the agent's obligation to emit YIELD before
`R1 == 0` and the runtime's obligation to implement YIELD when it enforces a
Watchdog Timer. Both are defined normatively in AEP-0008 (§1.1 and §1.4).

## 5. Error Handling

- Validation failures: MUST report details
- Missing dependencies: MUST fail with clear error
- Circular dependencies: MUST detect and fail
- I/O errors: MUST fail gracefully