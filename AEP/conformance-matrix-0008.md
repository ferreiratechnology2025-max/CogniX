# Conformance Matrix — AEP-0008 (Fault Tolerance & Execution Guarantees)

**Spec:** `AEP/AEP-0008-fault-tolerance.md`  
**Status:** Active  
**Audit date:** 2026-07-11  
**Criteria per:** `AEP/GOVERNANCE.md` (C1–C6)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Covered by automated test + Teeth |
| ◐ | Covered by automated test (no Teeth) |
| ⚠️ | Waiver (justified gap) |
| ❌ | Gap (no coverage, no waiver) |
| 🚫 | Not applicable (MAY clause) |

---

## Normative Clause → Evidence Matrix

| # | Clause | Verbatim (location) | Python Runtime | SQLite Runtime | Test(s) |
|---|--------|---------------------|----------------|----------------|---------|
| C1 | MUST emit YIELD before R1==0 | `:34-36` | ✅ | ⚠️ Waiver | `test_yield_extension`, `test_complete_program_with_yield` |
| C2 | MUST refuse YIELD > 10 | `:58-59` | ✅ | 🚫 N/A | `test_yield_global_limit` |
| C3 | MUST refuse YIELD exceeding global limit | `:60-61` | ✅ | 🚫 N/A | `test_yield_global_limit` |
| C4 | MUST retain YIELD history | `:62` | ✅ | 🚫 N/A | `test_yield_history_tracking`, `test_yield_metadata_in_exit` |
| C5 | Watchdog-enforcing impl MUST implement YIELD | `:69-71` | ✅ | ⚠️ Waiver | `test_complete_program_with_yield` (smoke) + normative TC-011 |
| C6 | Non-watchdog impl MAY omit YIELD | `:72` | 🚫 N/A | ✅ 🚫 | (permissive — no test needed) |
| C7 | YIELD MUST extend R1, MUST NOT modify other registers | `:73-74` | ✅ Teeth | ⚠️ Waiver | `test_yield_modifies_only_r1`, normative TC-011 |
| C8 | State mutation MUST NOT persist without validation | `:81-82` | ✅ | ⚠️ Waiver | `test_rollback_on_invalid_commit` |
| C9 | On failure, Runtime MUST perform rollback steps in order | `:86` | ✅ | ⚠️ Waiver | `test_rollback_on_invalid_commit` |
| C10 | MUST discard changes and restore R3 snapshot | `:88-89` | ✅ Teeth | ⚠️ Waiver | `test_snapshot_captured_before_commit` + `test_snapshot_teeth_without_r3` |
| C11 | MUST write structured error to R4 | `:90` | ✅ | ⚠️ Waiver | `test_rollback_on_invalid_commit` (R4 stderr assertion) |
| C12 | MUST capture snapshot before COMMIT; MUST restore on failure | `:106-107` | ✅ Teeth | ⚠️ Waiver | `test_snapshot_captured_before_commit` + `test_snapshot_teeth_without_r3` |

---

## Waiver Registry

| Clause | Runtime | Justification |
|--------|---------|---------------|
| C1, C5, C7, C8, C9, C10, C11, C12 | SQLite | SQLite runtime does not implement AEP-0008 fault tolerance (no watchdog counter, no YIELD, no rollback). R1 is used as `LAST_ACT` string field, not as `WATCHDOG` counter. Full AEP-0008 conformance is out of scope for the SQLite backend in its current version. |
| C2, C3, C4 | SQLite | 🚫 Not applicable — SQLite does not implement YIELD. |
| C6 | Python | 🚫 Not applicable — Python runtime enforces watchdog, so this MAY clause is irrelevant. |

**Waiver count:** 8 clauses waived for SQLite; 0 waived for Python.  
**Ratio:** 8/12 ≈ 67 % waived — **exceeds 50 % threshold per C2 → promotion blocked automatically** (see GATE 4).

---

## Summary by Runtime

| Runtime | Covered | Waived | N/A | Coverage % (of applicable) |
|---------|---------|--------|-----|---------------------------|
| **Python** | 10 | 0 | 2 (C6 irrelevant) | 100 % |
| **SQLite** | 0 | 8 | 4 (C2–C4 N/A, C6 N/A) | 0 % |

---

## Key Gaps for Promotion

| Criteria | Verdict | Evidence |
|----------|---------|----------|
| **C1** (Normative Language) | ✅ Pass | AEP-0008 uses RFC 2119 throughout |
| **C2** (Test Coverage with Teeth) | ❌ Fail | 67 % waivers exceed 50 % threshold; SQLite has zero coverage |
| **C3** (Honest Scope) | ✅ Pass | §0.1 declares scope and out-of-scope explicitly |
| **C4** (Zero Unresolved Drift) | ❌ Fail | SQLite R1 semântica LAST_ACT ≠ WATCHDOG; drift não resolvido |
| **C5** (External Consistency) | ⚠️ Partial | R7 update rule inconsistente entre AEP-0001 (COMMIT only) e AEP-0003 (EXEC+COMMIT) |
| **C6** (Adversarial Scrutiny) | ⚠️ Pending | Esta sessão é o primeiro escrutínio adversarial formal |

---

## Appendix: Clause-to-Test Detail (Python Runtime)

| Test method | Clauses | Teeth proof |
|------------|---------|-------------|
| `test_yield_extension` | C1 | Asserts R1 increases by exact YIELD amount |
| `test_yield_global_limit` | C2, C3 | Over-limit YIELD returns FAIL |
| `test_yield_history_tracking` | C4 | Asserts history list length and content |
| `test_yield_metadata_in_exit` | C4 | Asserts yield_history in EXIT output |
| `test_yield_modifies_only_r1` | C7 ✅ Teeth | Strict equality on all 7 non-R1 registers; docstring states "Verified to fail against a kernel where YIELD also writes R3/R5" |
| `test_rollback_on_invalid_commit` | C8, C9, C11 | Asserts FAIL + rollback=True + R4 structured error |
| `test_snapshot_captured_before_commit` | C10, C12 ✅ Teeth | Mutates R0 after snapshot → asserts restoration; companion `test_snapshot_teeth_without_r3` proves empty R3 → no restoration |
| `test_complete_program_with_yield` | C1, C5 | Smoke: full BOOT→YIELD→LOAD→VALIDATE→EXEC→COMMIT→EXIT |
| `TC-011 (normative)` | C7 | YAML test case (smoke; mechanical enforcement in pytest) |

**Total tests:** 15 (13 existing + 2 new C12)  
**Normative TC:** 1 (011-yield-r1-only)
