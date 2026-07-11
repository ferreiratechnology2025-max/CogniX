# AEP Specification Governance — Promotion Criteria

**Parent:** [`../GOVERNANCE.md`](../GOVERNANCE.md) (Organizational Change Process)

---

## 0. Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

This document defines the criteria that every AEP specification MUST
satisfy before it MAY transition from **Active** to **Stable** status.
These criteria serve as the binding gate between experimental adoption
and ecosystem-wide contract.

---

## 2. Status Lifecycle

```
Draft → Review → Active → Stable → Deprecated
                ↑          │
                └──────────┘
```

- **Draft:** Exploratory; no conformance required.
- **Review:** Proposed for adoption; under adversarial scrutiny.
- **Active:** Implemented and exercised; eligible for promotion.
- **Stable:** Frozen normative contract; ecosystem-wide trust.
- **Deprecated:** Superseded; retained for compatibility.

---

## 3. Promotion Criteria (Active → Stable)

A specification SHALL NOT transition from **Active** to **Stable**
unless it satisfies ALL of the following criteria.

### C1 — Normative Language

- The specification MUST use RFC 2119 key words (MUST, SHOULD, MAY,
  MUST NOT, SHOULD NOT) for every normative clause.
- Descriptive or explanatory text MUST be clearly separable from
  normative text.
- Every MUST/SHALL clause MUST be individually identifiable (e.g.,
  numbered, labelled, or anchorable).

### C2 — Test Coverage with Teeth

- Every MUST/SHALL clause MUST be exercised by at least one automated
  test that is executable by the project's test runner.
- At least one test per clause MUST include a **Teeth Check**: proof
  that the test fails when the corresponding implementation behavior is
  removed or violated.
- A clause MAY be granted a **Waiver** from test coverage, but only
  when accompanied by a written justification of one paragraph or less
  explaining why automated coverage is infeasible or disproportionate.
- Waivers MUST be registered in the conformance matrix. More than 50 %
  of clauses covered by Waiver (rather than automated test) SHALL block
  promotion automatically.

### C3 — Honest Scope and Declared Limits

- The specification MUST declare what is **in scope** and what is
  **out of scope** explicitly.
- Any claim about non-functional characteristics (performance,
  durability, security) MUST be qualified with measurable bounds or
  explicitly labelled as aspirational.
- The specification MUST NOT claim conformance from a reference
  implementation that does not fully implement every MUST clause.

### C4 — Zero Unresolved Code–Spec Drift

- Every normative clause MUST have a demonstrable correspondence in at
  least one implementation.
- Every named register, opcode, error code, or state referenced in the
  specification MUST exist with matching semantics in every
  implementation that claims conformance.
- Drifts discovered during a promotion audit MUST be either:
  (a) corrected in the code, (b) corrected in the specification, or
  (c) registered as a Pending Drift with a triage date.
- A Pending Drift SHALL block promotion.

### C5 — External Consistency

- The specification MUST NOT contradict any other AEP specification
  that has **Stable** status. Contradictions with **Active** or
  **Draft** specifications MUST be documented in the conformance
  matrix.
- Register semantics, opcode contracts, and error code namespaces MUST
  be consistent across all AEPs at the same or higher status level.

### C6 — Survival of Adversarial Scrutiny

- The specification MUST have undergone at least one formal review
  session that attempted to find contradictions, ambiguities, or
  unstated assumptions.
- Issues found during adversarial review MUST be resolved or
  explicitly deferred with a rationale before promotion.
- The review record MUST be referenced in the promotion request.

---

## 4. Retroactive Applicability

These criteria take effect immediately upon approval of this document.

Specifications that have already attained **Stable** status before this
document's adoption SHALL NOT be demoted solely for non-conformance
with these criteria. However, a conformance audit of every
pre-existing Stable specification is hereby registered as **mandatory
technical debt** and MUST appear in the repository's active work queue.

---

## 5. Promotion Procedure

1. **Audit phase:** The promotion agent compiles the conformance matrix
   mapping every clause to evidence, test, or waiver.
2. **Drift resolution:** Any code–spec drifts are corrected or
   registered as Pending.
3. **Verdict:** The agent issues a [PROMOVE] or [NÃO PROMOVE] verdict
   with per-criterion evidence links.
4. **Human ratification:** No status metadata SHALL be changed in any
   file without explicit human authorisation after the verdict.
5. **Status flip:** On authorisation, the specification's status
   metadata is updated and propagated across the repository.
6. **Registration:** The promotion is recorded in `CHANGELOG.md` with a
   reference to the conformance matrix.

---

## 6. Pending Drifts

Pre-existing Stable specifications are listed below for retroactive
audit. Each entry is a debt item — it does not demote the spec, but it
MUST be triaged before the next promotion of any AEP.

| AEP | Status | Known Drift | Triage Date |
|-----|--------|-------------|-------------|
| *(to be populated by first promotion audit)* | | | |

---

## 7. Scope

This document governs only the **status promotion** of AEP
specifications. It does not supersede or replace the organizational
change process defined in [`../GOVERNANCE.md`](../GOVERNANCE.md).
