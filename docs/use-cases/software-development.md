# AEP for Software Development

## Overview

AEP provides structured knowledge management for software projects, enabling AI agents to maintain context across sessions and collaborate effectively.

## Resource Structure

| Resource Type | Purpose | Example |
|---------------|---------|---------|
| project | Project definition | project-api-core |
| status | Current state | status-api-core |
| skill | Technical knowledge | skill-python, skill-docker |
| adr | Architecture decisions | adr-001-database-choice |
| incident | Error tracking | incident-001-timeout |

## Benefits

- **Persistent Context**: Agents remember project state between sessions
- **Decision Tracking**: ADRs capture why choices were made
- **Knowledge Reuse**: Skills accumulate technical expertise
- **Error Learning**: Incidents prevent repeated mistakes

## Example Workflow

1. **Boot**: Initialize project context
2. **Load**: Read project definition and current status
3. **Validate**: Ensure all resources are well-formed
4. **Execute**: Perform the planned task
5. **Commit**: Update state and persist changes
6. **Exit**: Save session for next agent