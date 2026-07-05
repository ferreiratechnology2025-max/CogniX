# AEP for Legal Engineering

## Overview

AEP structures legal knowledge for AI-assisted case management, enabling consistent reasoning and precedent tracking.

## Resource Structure

| Resource Type | Purpose | Example |
|---------------|---------|---------|
| project | Case definition | case-contract-dispute |
| status | Case status | status-case-123 |
| skill | Legal knowledge | skill-contract-law |
| adr | Strategic decisions | adr-001-litigation-approach |
| incident | Risk tracking | incident-001-deadline-risk |

## Benefits

- **Precedent Management**: Skills capture legal reasoning patterns
- **Decision Audit Trail**: ADRs document strategic choices
- **Risk Tracking**: Incidents flag compliance issues
- **Knowledge Continuity**: Context persists across meetings

## Example Use

```yaml
---
type: skill
id: skill-contract-analysis
version: 1.0.0
depends: []
status: active
---
# Contract Analysis Checklist

1. Identify parties and obligations
2. Review termination clauses
3. Assess liability limitations
4. Check compliance requirements
```