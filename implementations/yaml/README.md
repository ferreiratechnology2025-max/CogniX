# AEP YAML Implementation

**Status:** Not Started  
**Priority:** Low  

---

## Goal

Implement AEP using YAML as the storage format (similar to Markdown but more structured).

## Structure

```
yaml/
├── state.yaml
├── program.yaml
├── resources/
│   ├── project-cognix.yaml
│   ├── status-cognix.yaml
│   └── ...
└── lib/
    ├── boot.js
    ├── load.js
    ├── validate.js
    ├── exec.js
    ├── commit.js
    └── exit.js
```

## Resource Format (YAML)

```yaml
type: project
id: project-cognix
version: "0.2.0"
depends:
  - skill-markdown
  - skill-kos
  - skill-git
status: active
content:
  objective: "..."
  scope: "..."
  stack:
    - "..."
  rules:
    - "..."
```

## Status

- [ ] Directory structure
- [ ] State management
- [ ] Resource loading
- [ ] Validation
- [ ] Execution
- [ ] Commit
- [ ] Conformance tests