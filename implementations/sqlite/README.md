# AEP SQLite Implementation

**Status:** Not Started  
**Priority:** Medium  

---

## Goal

Implement AEP using SQLite as the storage backend.

## Structure

```
sqlite/
├── schema.sql
├── kos.db
├── lib/
│   ├── boot.js
│   ├── load.js
│   ├── validate.js
│   ├── exec.js
│   ├── commit.js
│   └── exit.js
└── README.md
```

## Schema

```sql
CREATE TABLE state (
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE TABLE resources (
  id TEXT PRIMARY KEY,
  type TEXT,
  version TEXT,
  depends TEXT,
  status TEXT,
  content TEXT
);

CREATE TABLE registers (
  name TEXT PRIMARY KEY,
  value TEXT
);
```

## Status

- [ ] Schema design
- [ ] Database initialization
- [ ] State management
- [ ] Resource loading
- [ ] Validation
- [ ] Execution
- [ ] Commit
- [ ] Conformance tests