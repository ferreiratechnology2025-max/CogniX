# AEP JSON Implementation

**Status:** Not Started  
**Priority:** High  

---

## Goal

Implement AEP using JSON as the storage format.

## Structure

```
json/
├── state.json          # Global state (R0-R7)
├── program.json        # Execution flow
├── resources/
│   ├── project-cognix.json
│   ├── status-cognix.json
│   └── ...
└── lib/
    ├── boot.js
    ├── load.js
    ├── validate.js
    ├── exec.js
    ├── commit.js
    └── exit.js
```

## Resource Format (JSON)

```json
{
  "type": "project",
  "id": "project-cognix",
  "version": "0.2.0",
  "depends": ["skill-markdown", "skill-kos", "skill-git"],
  "status": "active",
  "content": {
    "objective": "...",
    "scope": "...",
    "stack": ["..."],
    "rules": ["..."]
  }
}
```

## Status

- [ ] Directory structure
- [ ] State management
- [ ] Resource loading
- [ ] Validation
- [ ] Execution
- [ ] Commit
- [ ] Conformance tests