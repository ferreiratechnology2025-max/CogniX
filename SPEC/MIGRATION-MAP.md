# AEP Documentation Migration Map

**Status:** Living Document  
**Last Updated:** 2026-07-07  
**Maintainer:** AEP Governance

This document tracks the migration of AEP documentation from the legacy flat structure (`AEP/AEP-000X.md`) to the new hierarchical normative structure (`SPEC/`, `RFC/`, `COMPLIANCE/`).

## Migration Principles

1. **Compatible and incremental**: No existing files are moved or deleted until a complete replacement exists
2. **Concept-based**: Migration is driven by conceptual coverage, not filename matching
3. **No broken links**: All existing references remain valid during transition
4. **Controlled deprecation**: Old documents are marked deprecated only when superseded

---

## Current Mapping

| Legacy Document | Core Concept | Future Destination | Action | Status |
|---|---|---|---|---|
| `AEP/AEP-0001-core.md` | Core Protocol, opcodes, registers | `SPEC/AEP-ISA-1.0.md` | Evolve (absorb IR mapping) | Current |
| `AEP/AEP-0002-resource.md` | Universal Resource format | `SPEC/AEP-RESOURCE-1.0.md` | Maintain | Current |
| `AEP/AEP-0003-isa.md` | Kernel ISA (7 opcodes: BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT, YIELD) | `SPEC/AEP-ISA-1.0.md` | Consolidate with AEP-0001 | Current |
| `AEP/AEP-0004-conformance.md` | Conformance test suite | `COMPLIANCE/Conformance-Suite.md` | Move | Current |
| `AEP/AEP-0005-lifecycle.md` | Resource lifecycle | `SPEC/AEP-LIFECYCLE-1.0.md` | Maintain | Current |
| `AEP/AEP-0006-simplified.md` | Simplified execution mode | `RFC/RFC-0001-Simplified-Mode.md` | Move to RFC | Current |
| `AEP/AEP-0007-profiles.md` | Compliance profiles | `SPEC/AEP-PROFILES-1.0.md` | Maintain | Current |
| `AEP/AEP-0008-fault-tolerance.md` | Fault tolerance (Watchdog, ACID, ROLLBACK→R4) | `SPEC/AEP-FAULT-TOLERANCE-1.0.md` | Maintain | Current |
| `SPEC/AEP-IR-1.0.md` | Intermediate Representation (DAG, Bindings, Effects) | — | First normative document of new structure | **Draft** |

---

## Status Definitions

| Status | Meaning |
|---|---|
| **Current** | Document is active and has no replacement yet |
| **Draft** | New document in the target structure, under review |
| **Deprecated** | Document has a replacement; old links should migrate |
| **Superseded** | Document is fully replaced; redirects to new location |
| **Split** | Document content was divided into multiple new documents |
| **Merged** | Document content was consolidated into another document |

---

## Action Definitions

| Action | Meaning |
|---|---|
| **Maintain** | Document remains as-is; future SPEC will reference it |
| **Evolve** | Document will be updated to incorporate new concepts |
| **Consolidate** | Document content will be merged with another document |
| **Move** | Document will be relocated to new structure |
| **Move to RFC** | Document becomes a Request for Comments (non-normative) |

---

## Migration Progress

### Completed
- ✅ CHANGELOG.md updated to 1.1.0 (2026-07-06)
- ✅ `SPEC/AEP-IR-1.0.md` created as first normative document of new structure

### In Progress
- 🔄 AEP-0003 (ISA) → needs consolidation with AEP-0001 into `SPEC/AEP-ISA-1.0.md`

### Pending
- ⏳ AEP-0002 → `SPEC/AEP-RESOURCE-1.0.md`
- ⏳ AEP-0004 → `COMPLIANCE/Conformance-Suite.md`
- ⏳ AEP-0005 → `SPEC/AEP-LIFECYCLE-1.0.md`
- ⏳ AEP-0006 → `RFC/RFC-0001-Simplified-Mode.md`
- ⏳ AEP-0007 → `SPEC/AEP-PROFILES-1.0.md`
- ⏳ AEP-0008 → `SPEC/AEP-FAULT-TOLERANCE-1.0.md`

---

## Next Steps

1. **Stabilize `SPEC/AEP-IR-1.0.md`**: Wait for implementation feedback before creating conformance suite
2. **Consolidate ISA**: Merge AEP-0001 and AEP-0003 into `SPEC/AEP-ISA-1.0.md` when IR mapping is validated
3. **Create RFC structure**: Establish `RFC/` directory and migrate AEP-0006 as first RFC
4. **Build conformance suite**: Create `COMPLIANCE/Conformance-Suite.md` based on AEP-0004 + IR validation rules

**Note**: No migration action will be taken until the replacement document is complete and reviewed. This prevents broken links and documentation gaps.
