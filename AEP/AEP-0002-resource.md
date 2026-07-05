# AEP-0002: Resource Specification

**Status:** Stable  
**Version:** 1.0.0  
**Date:** 2026-07-05  

---

## 1. Introduction

This document specifies the Resource format used by the Agent Execution Protocol.

## 2. Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 3. Resource Structure

### 3.1 Header (Metadata)
```
---
type: <string>
id: <string>
version: <semver>
depends: [<id>, ...]
status: <string>
---
```

### 3.2 Content
Any structured content (Markdown, JSON, YAML, etc.)

### 3.3 Fields

#### type
- **Type:** string
- **REQUIRED**
- **Valid values:** project, status, skill, adr, incident, rule, template

#### id
- **Type:** string
- **REQUIRED**
- **Format:** kebab-case
- **Uniqueness:** MUST be unique across all Resources

#### version
- **Type:** string
- **REQUIRED**
- **Format:** semantic version (X.Y.Z)

#### depends
- **Type:** array of strings
- **OPTIONAL**
- **Validation:** All dependencies MUST exist

#### status
- **Type:** string
- **REQUIRED**
- **Valid values:** draft, review, active, deprecated, archived

### 3.4 Validation Rules

A Resource MUST pass all validation checks:
1. `type` is valid
2. `id` is unique
3. `version` is SemVer
4. `depends` all exist
5. `status` is valid
6. Content is present

### 3.5 Example

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

## 4. Resource Types

### 4.1 project
- **Purpose:** Project definition
- **REQUIRED:** objective, scope, stack, rules

### 4.2 status
- **Purpose:** Current state
- **REQUIRED:** R0-R7 registers

### 4.3 skill
- **Purpose:** Reusable knowledge
- **REQUIRED:** objective, procedure, examples

### 4.4 adr
- **Purpose:** Architectural decision
- **REQUIRED:** problem, decision, consequences

### 4.5 incident
- **Purpose:** Error log
- **REQUIRED:** problem, cause, fix, prevention

### 4.6 rule
- **Purpose:** Project rule
- **REQUIRED:** applies_to, description

### 4.7 template
- **Purpose:** Template for new Resources
- **REQUIRED:** usage_instructions, template

## 5. Implementation

A conforming implementation:
- MUST validate all required fields
- MUST check all dependencies exist
- MUST ensure uniqueness of IDs
- MUST support all defined types