# KOS — Conformance Specification

**Version:** 1.0.0  
**Status:** Active Specification  

---

## 1. What is a Conforming Agent?

A conforming agent is an AI system that correctly interprets and executes the KOS protocol.

---

## 2. Requirements

### 2.1 Bootloader Interpretation
- [ ] Must read `AGENTS.md` as the entry point
- [ ] Must load `KERNEL/BOOT.md` as the boot sequence
- [ ] Must load `KERNEL/STATE.md` and `KERNEL/PROGRAM.md`

### 2.2 ISA Execution
- [ ] Must execute all 6 opcodes: BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT
- [ ] Must follow the contracts defined in ISA.md
- [ ] Must not skip or reorder opcodes

### 2.3 Resource Protocol
- [ ] Must validate all Resources have: type, id, version, depends, status
- [ ] Must resolve dependencies recursively
- [ ] Must not modify Resources outside the protocol

### 2.4 State Management
- [ ] Must maintain registers R0-R7
- [ ] R3 [MODIFIED] must contain ONLY the delta of the current session
- [ ] Must persist state on COMMIT

### 2.5 Error Handling
- [ ] Must report validation failures
- [ ] Must not proceed on invalid Resources
- [ ] Must handle missing dependencies gracefully

---

## 3. Conformance Tests

### Test 1: Basic Boot
```
Input: AGENTS.md with valid KOS
Expected: BOOT successful, STATE and PROGRAM loaded
Status: ___________________
```

### Test 2: Load Resource
```
Input: LOAD project-cognix
Expected: Resource loaded with all dependencies
Status: ___________________
```

### Test 3: Validate Resource
```
Input: VALIDATE project-cognix
Expected: OK if valid, FAIL with error if invalid
Status: ___________________
```

### Test 4: Execute Task
```
Input: EXEC with R2 defined
Expected: Task executed, registers updated
Status: ___________________
```

### Test 5: Commit Changes
```
Input: COMMIT with modified Resources
Expected: Resources persisted, R3 cleared to delta only
Status: ___________________
```

### Test 6: Complete Flow
```
Input: Full PROGRAM flow
Expected: All opcodes executed, final state persisted
Status: ___________________
```

### Test 7: Error Recovery
```
Input: LOAD invalid-resource
Expected: FAIL with clear error message
Status: ___________________
```

### Test 8: Dependency Resolution
```
Input: LOAD resource with nested dependencies
Expected: All dependencies loaded
Status: ___________________
```

---

## 4. Compliance Levels

### Level 1: Basic
- BOOT implemented
- LOAD implemented
- VALIDATE implemented

### Level 2: Standard
- All 6 opcodes implemented
- Basic state management

### Level 3: Advanced
- Full protocol with dependency resolution
- Custom Resource types

### Level 4: Complete
- Full protocol
- Custom Resources
- Custom Programs
- All error handling

---

## 5. Reporting Compliance

Conforming agents should report:

```
AGENT: [Agent Name]
VERSION: [Agent Version]
KOS COMPLIANCE: [Level]

TESTS PASSED: [Count]/[Total]
TESTS FAILED: [Count]/[Total]
```

---

## 6. Known Conforming Agents

| Agent | Version | Compliance Level | Test Date | Status |
|-------|---------|-----------------|-----------|--------|
| Claude Code (MiMoCode) | v1.0 | Advanced | 2026-07-04 | ✅ |
| Cursor | — | Pending | — | ⏳ |
| Aider | — | Pending | — | ⏳ |
| Gemini CLI | — | Pending | — | ⏳ |

---

## 7. How to Test

### Manual Test
1. Initialize a KOS repository
2. Run the agent with: `agent "Leia AGENTS.md e execute a tarefa"`
3. Verify all opcodes execute correctly
4. Check if state persists
5. Document results

### Automated Test (Future)
1. Test suite with all compliance checks
2. Run against any agent
3. Report results