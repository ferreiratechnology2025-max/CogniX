# AEP Conformance Report

**Runtimes:** python (AEP Kernel v1.0.0), sqlite
**Regenerated:** post-UTF-8 hotfix (commit that forces UTF-8 stdout/stderr)

> **Canonical evidence.** The per-run JSON snapshots under
> `conformance/normative/snapshots/actual/` are gitignored because they embed
> non-deterministic session-ids/timestamps. This report is the versioned,
> human-reviewed summary of the last run.

## What the numbers mean (read literally)

The normative runner (`conformance/normative/test_runner.py`) runs a single
default program end-to-end against each runtime and asserts only `status` and
`exit_code`. It does **not** yet execute each case's per-case `procedure` — that
enforcement is pending (see backlog: discriminating runner). Treat the result
below as a **pipeline smoke test**, not as 10 independent scenarios.

Distinct kernel behavior — including the Execution Boundary (R2 opacity) — is
enforced by the **behavioral pytest suite** (`implementations/python/tests/`),
which is the strongest conformance evidence in the repo.

## Normative suite (pipeline smoke)

| Metric | Value |
|--------|-------|
| Test cases | 10 |
| Runtimes | 2 (python, sqlite) |
| Executions | 20 |
| Passed | 20 |
| Failed | 0 |

Prior to the UTF-8 hotfix this suite reported 0/20 on legacy code pages
(cp1252) because the CLI crashed while printing opcode logs; the snapshots
previously committed under `snapshots/actual/` captured that failing state.

## Behavioral suite (pytest — real conformance)

| Metric | Value |
|--------|-------|
| Tests | 10 |
| Passed | 10 |
| Failed | 0 |

Includes `test_exec_does_not_interpret_r2`, verified to fail against a mutated
kernel that executes R2 (mutation-tested invariant).
