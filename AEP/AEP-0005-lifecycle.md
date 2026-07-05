# AEP-0005: Resource Lifecycle

**Status:** Stable  
**Version:** 1.0.0  
**Date:** 2026-07-05  

---

## 1. Introduction

This document specifies the lifecycle of Resources in the Agent Execution Protocol.

## 2. Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 3. Resource States

A Resource MUST be in one of the following states:

| State | Description |
|-------|-------------|
| draft | Initial state, not yet validated |
| review | Under review, may have issues |
| active | Valid and in use |
| deprecated | No longer recommended, but still functional |
| archived | Read-only, preserved for reference |

## 4. State Transitions

```
draft → review → active → deprecated → archived
  ↓        ↓        ↓          ↓
review   active  deprecated  archived
```

**Rules:**
- A Resource MUST NOT skip states
- A Resource MAY transition backwards (e.g., active → draft)
- Archived Resources MUST NOT be modified

## 5. Version Management

### 5.1 Semantic Versioning
- `0.x.x`: Draft (unstable)
- `1.0.0`: First stable release
- `1.x.x`: Compatible changes (new features)
- `2.0.0`: Breaking change

### 5.2 Version Increments
- **PATCH** (Z): Bug fixes, documentation
- **MINOR** (Y): New features, backward compatible
- **MAJOR** (X): Breaking changes

### 5.3 Version Rules
- version MUST be incremented on change
- version MUST follow SemVer
- version MUST be present in all states

## 6. Dependency Management

### 6.1 Dependency Rules
- depends MUST reference existing Resources
- depends MUST NOT create circular dependencies
- depends MUST be resolved recursively

### 6.2 Dependency Resolution
When LOAD is called:
1. Locate the Resource
2. Check if all dependencies exist
3. Load dependencies first
4. Load the Resource

### 6.3 Error Handling
- Missing dependency: MUST fail with clear error
- Circular dependency: MUST detect and fail
- Broken dependency: MUST fail gracefully

## 7. R3 [MODIFIED] Lifecycle

### 7.1 During EXEC
- R3 MUST be updated with any modified Resources
- R3 MUST contain only the delta of the current session

### 7.2 During COMMIT
- R3 MUST be used to persist changes
- R3 MUST be cleared and set to delta only
- History MUST be in Git, not in R3

### 7.3 After EXIT
- R3 MUST contain only the last session's delta
- R3 MUST NOT accumulate history across sessions

## 8. Best Practices

### 8.1 Creating Resources
1. Start with draft status
2. Use templates for consistency
3. Validate before marking as active

### 8.2 Updating Resources
1. Increment version
2. Update status if needed
3. Validate after changes

### 8.3 Deprecating Resources
1. Mark as deprecated
2. Document reason
3. Provide migration path if possible

### 8.4 Archiving Resources
1. Ensure no active dependencies
2. Mark as archived
3. Preserve for reference

## 9. Implementation Requirements

A conforming implementation:
- MUST enforce state transitions
- MUST validate version format
- MUST detect circular dependencies
- MUST maintain R3 lifecycle
- MUST support all resource states