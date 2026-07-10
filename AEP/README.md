# AEP Specification

**Version:** 1.1.0  
**Status:** Stable  

---

This directory contains the formal specification of the Agent Execution Protocol.

## Documents

| Document | Description | Status |
|----------|-------------|--------|
| [AEP-0001](AEP-0001-core.md) | Core Protocol | Stable |
| [AEP-0002](AEP-0002-resource.md) | Resource Specification | Stable |
| [AEP-0003](AEP-0003-isa.md) | Kernel ISA | Stable |
| [AEP-0004](AEP-0004-conformance.md) | Conformance Tests | Stable |
| [AEP-0005](AEP-0005-lifecycle.md) | Resource Lifecycle | Stable |
| [AEP-0006](AEP-0006-simplified.md) | Simplified Execution Mode | Stable |
| [AEP-0007](AEP-0007-profiles.md) | Compliance Profiles | Stable |
| [AEP-0008](AEP-0008-fault-tolerance.md) | Fault Tolerance & Execution Guarantees | Active |

## Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in these documents are to be interpreted as described in RFC 2119.

## Compliance

Implementations claiming AEP compliance MUST pass the normative conformance
suite (`conformance/normative/test_runner.py`) and SHOULD provide a behavioral
test suite exercising the opcodes (see `implementations/python/tests/`). The
[Compliance Kit](../compliance-kit/) currently performs structural validation of
test definitions only and does not yet execute implementations.

## Quick Reference

### Registers

| Register | Name | Purpose |
|----------|------|---------|
| R0 | SESSION | Session identifier |
| R1 | WATCHDOG | Instruction counter / fault tolerance timer |
| R2 | NEXT_ACT | Next planned action |
| R3 | MODIFIED | Modified files (delta) |
| R4 | STDERR | Structured error output |
| R5 | ACTIVE_SK | Active skill |
| R6 | HEALTH | System health |
| R7 | TIMESTAMP | Last timestamp |

### Opcodes

| Opcode | Description |
|--------|-------------|
| BOOT | Initialize system, load state |
| LOAD | Load a Resource by ID |
| VALIDATE | Validate Resource structure |
| EXEC | Execute current task |
| COMMIT | Persist changes (ACID transaction) |
| EXIT | End session |
| YIELD | Request watchdog extension (conditional — see AEP-0008) |

### Error Codes

| Code | Description |
|------|-------------|
| ERR_AEP_0002_VALIDATION | Resource validation failed |
| ERR_AEP_0003_E001 | Resource not found |
| ERR_AEP_0003_E002 | Dependency not found |
| ERR_AEP_0003_E003 | Invalid resource id (not a plain identifier; rejected before path resolution) |
| ERR_AEP_0008_TIMEOUT | Watchdog timer expired |
| ERR_SYSTEM_UNEXPECTED | Unexpected system error |
