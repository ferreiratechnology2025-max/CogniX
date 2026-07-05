# AEP-0004: Conformance Tests

**Status:** Stable  
**Version:** 1.0.0  
**Date:** 2026-07-05  

---

## 1. Introduction

This document specifies conformance tests for Agent Execution Protocol implementations.

## 2. Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 3. Conformance Requirements

A conforming implementation MUST:
1. Implement all six opcodes
2. Follow all contracts
3. Maintain R0-R7 registers
4. Support Resource protocol
5. Persist state across sessions
6. Use Git for history

## 4. Test Suite

### TC-001: Boot
**Purpose:** Validate BOOT opcode

**Setup:**
- Valid KOS installation
- STATE.md and PROGRAM.md exist

**Procedure:**
1. Read AGENTS.md
2. Execute BOOT

**Expected:**
- STATE.md loaded
- PROGRAM.md loaded
- R0 [SESSION] set

### TC-002: Load
**Purpose:** Validate LOAD opcode

**Setup:**
- Project Resource exists
- Dependencies exist

**Procedure:**
1. LOAD project-cognix

**Expected:**
- Resource loaded
- Dependencies loaded

### TC-003: Validate
**Purpose:** Validate VALIDATE opcode

**Setup:**
- Resource exists

**Procedure:**
1. VALIDATE project-cognix

**Expected:**
- OK if valid
- FAIL with details if invalid

### TC-004: Execute
**Purpose:** Validate EXEC opcode

**Setup:**
- R2 [NEXT_ACT] defined

**Procedure:**
1. EXEC

**Expected:**
- Task executed
- R1 [LAST_ACT] updated

### TC-005: Commit
**Purpose:** Validate COMMIT opcode

**Setup:**
- Resource modified

**Procedure:**
1. COMMIT

**Expected:**
- Resources persisted
- R3 cleared to delta only

### TC-006: Exit
**Purpose:** Validate EXIT opcode

**Procedure:**
1. EXIT

**Expected:**
- STATE saved
- Session ended

### TC-007: Complete Flow
**Purpose:** Validate full program

**Procedure:**
1. Execute full PROGRAM flow

**Expected:**
- All opcodes executed
- Final state persisted

## 5. Compliance Levels

| Level | Requirements |
|-------|-------------|
| Basic | BOOT, LOAD, VALIDATE |
| Standard | All 6 opcodes |
| Advanced | + Dependency resolution |
| Complete | + Custom Resources |

## 6. Test Report Template

```markdown
# Conformance Test Report

**Agent:** [Name]
**Version:** [X.Y.Z]
**Date:** [YYYY-MM-DD]

## Results

| Test | Result | Notes |
|------|--------|-------|
| TC-001 | PASS/FAIL | |
| TC-002 | PASS/FAIL | |
| TC-003 | PASS/FAIL | |
| TC-004 | PASS/FAIL | |
| TC-005 | PASS/FAIL | |
| TC-006 | PASS/FAIL | |
| TC-007 | PASS/FAIL | |

**Compliance Level:** [Basic|Standard|Advanced|Complete]
```