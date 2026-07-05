# KOS — Agent Execution Protocol (AEP)

**Version:** 1.0.0  
**Status:** Active Specification

---

## 1. Scope

This specification defines a protocol for deterministic execution of AI agents over persistent knowledge resources.

The protocol is:
- **Format-agnostic** — can be implemented in Markdown, JSON, YAML, or any structured format
- **Runtime-agnostic** — works with Claude Code, Cursor, Aider, Gemini CLI, or any AI agent
- **Stateful** — maintains state between sessions via registers (R0-R7)

---

## 2. Core Concepts

### 2.1 Resource
A Resource is a unit of knowledge. All artifacts are Resources, differentiated only by metadata.

**Structure:**
```yaml
---
type: <string>          # project, status, skill, adr, incident, rule, template
id: <string>            # unique identifier (kebab-case)
version: <semver>       # semantic version (X.Y.Z)
depends: [<id>, ...]    # resource dependencies
status: <string>        # draft | review | active | deprecated | archived
---
# Content
...
```

**Example:**
```yaml
---
type: project
id: project-cognix
version: 0.2.0
depends: [skill-markdown, skill-kos, skill-git]
status: active
---
# PROJETO: CogniX
...
```

---

### 2.2 State Registers (R0-R7)
State is maintained as eight registers:

| Register | Name | Purpose | Update Rule |
|----------|------|---------|-------------|
| R0 | SESSION | Session identifier | Set on BOOT |
| R1 | LAST_ACT | Last action performed | Set on COMMIT |
| R2 | NEXT_ACT | Next action planned | Set by agent |
| R3 | MODIFIED | Files modified in current session | **Delta only, cleared on COMMIT** |
| R4 | BLOCKERS | Current blockers | Updated as needed |
| R5 | ACTIVE_SK | Active skill | Set by agent |
| R6 | HEALTH | System health (OK/FAIL) | Updated on VALIDATE |
| R7 | TIMESTAMP | Session timestamp | Updated on COMMIT |

---

### 2.3 Program
A Program is a sequence of opcodes that defines the execution flow.

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

---

## 3. Instruction Set Architecture (ISA)

The protocol defines exactly six opcodes:

### 3.1 BOOT
**Purpose:** Initialize the system.

**Behavior:**
1. Load STATE (global system state)
2. Load PROGRAM (execution flow)
3. Set R0 [SESSION] to current timestamp

**Contracts:**
- Input: STATE.md, PROGRAM.md
- Output: System initialized, R0 set
- Side effects: None

### 3.2 LOAD
**Purpose:** Load a Resource by ID.

**Behavior:**
1. Locate Resource by ID
2. Load Resource content
3. Recursively load all dependencies (depends field)

**Contracts:**
- Input: Resource ID
- Output: Resource loaded, dependencies loaded
- Side effects: None

**Errors:**
- Resource not found → FAIL
- Missing dependency → FAIL
- Circular dependency → FAIL

### 3.3 VALIDATE
**Purpose:** Validate Resource structure.

**Behavior:**
1. Verify Resource exists
2. Validate metadata fields:
   - type: valid string
   - id: unique, kebab-case
   - version: semver format
   - depends: all resources exist
   - status: valid status

**Contracts:**
- Input: Resource ID
- Output: OK or FAIL with error details
- Side effects: None

**Validation Rules:**
- type must be a valid type
- id must be unique
- version must be semver
- depends must exist
- status must be valid

### 3.4 EXEC
**Purpose:** Execute the current task.

**Behavior:**
1. Read R2 [NEXT_ACT] from STATUS
2. Execute the task
3. Update R1 [LAST_ACT] with result

**Contracts:**
- Input: R2 [NEXT_ACT]
- Output: Task executed, R1 updated
- Side effects: May modify files

**Rules:**
- Task must be defined in R2
- Agent may modify only allowed Resources
- R3 [MODIFIED] must be updated

### 3.5 COMMIT
**Purpose:** Persist changes and classify new knowledge.

**Behavior:**
1. Persist all modified Resources
2. **Clear R3 [MODIFIED] and set to delta only**
3. Classify new knowledge:
   - Decision → ADR
   - Procedure → Skill
   - Error → Incident
   - Rule → Rule
4. Update R1 [LAST_ACT]
5. Update R7 [TIMESTAMP]

**Contracts:**
- Input: Modified Resources
- Output: Resources persisted, R1/R7 updated
- Side effects: Writes files

**Rules:**
- R3 must contain ONLY delta of current session
- History belongs to Git, not state
- New knowledge classified automatically

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

---

## 4. Boot Sequence

1. Read `AGENTS.md`
2. Read `KERNEL/BOOT.md`
3. Load `KERNEL/STATE.md`
4. Load `KERNEL/PROGRAM.md`
5. Execute first opcode

---

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

---

## 6. Conformance

A conforming implementation must:
1. Implement all six opcodes
2. Follow all contracts
3. Maintain R0-R7 registers
4. Support Resource protocol
5. Persist state across sessions
6. Use Git for history, not state

---

## 7. Versioning

- **0.x.x**: Draft (instable)
- **1.0.0**: Active (stable)
- **1.x.x**: Active (compatible)
- **2.0.0**: Active (breaking change)

### Deprecation
- Deprecated Resources remain active
- New Resources should use latest version
- Archived Resources are read-only

---

## 8. Extensibility

New Resource types can be added without changing the protocol:
1. Define new type in metadata
2. Add template for new type
3. Update validation if needed

---

## Appendix A: Example Session

```
[Agent] claude "Leia AGENTS.md e execute a tarefa"

[BOOT] → STATE.md loaded, PROGRAM.md loaded
[LOAD] → project-cognix loaded
[LOAD] → status-cognix loaded
[VALIDATE] → project-cognix OK
[VALIDATE] → status-cognix OK
[EXEC] → Task executed (R2 [NEXT_ACT])
[COMMIT] → Changes persisted, R3 cleared
[EXIT] → Session closed
```

---

## Appendix B: Compliance Checklist

- [ ] All 6 opcodes implemented
- [ ] R0-R7 maintained correctly
- [ ] R3 contains only delta
- [ ] VALIDATE checks all fields
- [ ] COMMIT persists changes
- [ ] Resources follow protocol
- [ ] Dependencies resolved
- [ ] Errors handled gracefully