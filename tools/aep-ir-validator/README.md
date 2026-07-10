# AEP IR LLM Generability Experiment

Test whether LLMs can generate valid AEP-IR v1.0 Execution Plans from real-world task descriptions.

## The Hypothesis

> If an LLM cannot consistently produce valid AEP IR Execution Plans, the problem is the spec, not the model.

This experiment tests the **central premise of the IR**: that it is a format LLMs can reliably generate. If the rejection rate is high, the spec needs revision before investing in conformance tests.

## Tasks

10 real-world **Vigia Legal** tasks covering the legal engineering domain:

| # | Task | Domain | Complexity |
|---|------|--------|------------|
| 01 | Monitor New Data Privacy Legislation | Regulatory Monitoring | Medium |
| 02 | Analyze Contract for Liability Clauses | Contract Analysis | Medium |
| 03 | Track Regulatory Compliance Deadlines | Compliance Calendar | High |
| 04 | Review Court Ruling for Precedent Relevance | Precedent Analysis | Medium |
| 05 | Audit Internal Policy vs New Regulation | Compliance Audit | Medium-High |
| 06 | Generate Legal Memo on Tax Law Change | Legal Research | High |
| 07 | Cross-Reference Contracts with Regulation | Contract Portfolio Review | High |
| 08 | Monitor ANPD Enforcement Decisions | Regulatory Intelligence | Medium |
| 09 | Assess Patent Litigation Risk | IP Litigation Risk | High |
| 10 | Verify Software License Compliance | License Audit | Very High |

Each task includes:
- Task description
- Expected tools (mapped to `tool_call` nodes)
- Expected bindings (mapped to `mutation`/`transformation` nodes)
- Complexity rating

## How to Run

### Requirements
- Python 3.8+
- `canonicaljson>=2.0.0` (install via `pip install canonicaljson`)
- An LLM API key (optional — interactive mode works without one)

### Interactive Mode (recommended for first run)

```bash
cd tools/aep-ir-validator
python runner.py
```

This will:
1. Load all 10 tasks
2. Build the LLM prompt for each task
3. Save the prompt to `plans/prompt-<task>.txt`
4. Wait for you to paste the LLM's JSON response
5. Validate the plan
6. Report results

### Validate Existing Plans

Once each `pipeline/<task>/output-plan.json` has been generated, validate them
all with the `validate` subcommand:

```bash
python runner.py validate
```

## Validation Rules

The validator checks all rules from **AEP-IR-1.0**:

| Rule | Category | What It Checks |
|------|----------|----------------|
| ENV-1–4 | Envelope | Plan envelope structure, checksum placement |
| PH-1–12 | PlanHeader | ir_version, plan_id, capabilities, bindings |
| B-1–11 | Bindings | Name, type, mutability, scope, capability |
| N-1–21 | Nodes | ID uniqueness, type, effects, capabilities, inputs/outputs |
| BR-1–5 | BindingRefs | Binding reference structure, access mode |
| E-1–6 | Edges | Source/target validity |
| DAG-1 | DAG | Graph must be acyclic (Kahn's algorithm) |
| BU-1 | Binding Usage | All referenced bindings must be declared |
| CC-1–2 | Capabilities | All used capabilities must be declared |
| TEC-1–2 | Type-Effect Consistency | Node type ↔ effect rules (§7.3) |
| CR-1–3 | Cross-References | Write access → mutable binding + WRITE effect + capability |

## Output

### Per-Plan Validation

```
✅ VALID — No errors
❌ INVALID — 3 errors:

  [Rule N-13] node 'node-002': invalid effect 'CALL_FUNCTION'.
              Valid effects: CALL_TOOL, EMIT_EVENT, READ, WRITE, YIELD
  [Rule TEC-1] node 'node-002' of type 'tool_call' is missing required effect: CALL_TOOL
  [Rule CC-1] Capabilities used but not declared: {'tool_execution'}
```

### Experiment Report

> **Status: designed, pending execution.** The 30-plan experiment (10 tasks ×
> 3 generations) has NOT been run. As of this writing, 1 of 30 plans has an
> `output-plan.json`; the other 29 have only their input prompts. The block
> below is an **ILLUSTRATIVE EXAMPLE of the report format — not actual
> results.**

After all tasks are processed, the runner produces (illustrative shape only):

```
════════════════════════════════════════════════════════
  EXPERIMENT RESULTS  (ILLUSTRATIVE EXAMPLE — not actual results)
════════════════════════════════════════════════════════
  Total tasks      : 10
  Validated        : 10
  Valid plans      : 3
  Invalid plans    : 7
  Parse errors     : 0
  Skipped          : 0
  Pass rate        : 30.0%   <-- example value, not measured

  Rejection Modes (by frequency):
    N-13        : 4 (LLM-invented effects)
    BU-1        : 3 (binding not declared in PlanHeader)
    TEC-1       : 3 (tool_call without CALL_TOOL)
    CR-1        : 2 (write access to a readonly binding)
    DAG-1       : 1 (cycle in the graph)

════════════════════════════════════════════════════════
```

The `validate` subcommand writes per-plan envelopes and a `results-table.csv`
to the `experiment-results/` directory. The validator's own self-test report
(over `test_plans/`) is saved as `validator-selftest-report.json`.

## Interpreting Results

| Pass Rate | Interpretation | Action |
|-----------|---------------|--------|
| > 80% | Spec is LLM-generable | Proceed with conformance suite |
| 50–80% | Spec is mostly generable, minor friction | Tweak spec, iterate |
| 20–50% | Spec has significant generability issues | Revise spec before conformance |
| < 20% | Spec is not LLM-generable | Major redesign needed |

### Rejection Mode Analysis

The most valuable output is **how** plans fail, not just how many:

- **N-13 (invalid effects)**: LLM invents effects not in the spec → spec may need more effect types
- **BU-1 (undeclared bindings)**: LLM forgets to declare bindings → PlanHeader verbosity may be too high
- **TEC-1 (missing CALL_TOOL)**: Type-effect mapping is intuitive but LLM doesn't follow it → may need simplification
- **DAG-1 (cycles)**: LLM creates cyclic dependencies → edge syntax may need simplification

## Plan vs Envelope

The LLM generates only the **plan** (plan_header + nodes + edges). The **envelope** (plan + checksum) is constructed by the runner before validation.

This separation exists because:
- Checksum computation is the compiler's responsibility (SPEC/AEP-IR-1.0.md §6.2)
- LLMs are not reliable at computing SHA256 hashes
- The experiment measures plan gerability, not hash computation

The runner automatically:
1. Canonicalizes the plan per RFC 8785
2. Computes SHA256 checksum
3. Wraps in envelope
4. Passes to validator

## Files

```
tools/aep-ir-validator/
├── README.md                  # This file
├── prompt.md                  # LLM prompt template
├── validator.py               # IR Validator (all rules)
├── runner.py                  # Experiment orchestrator
├── tasks/                     # 10 Vigia Legal task descriptions
│   ├── 01-monitor-data-privacy-legislation.md
│   ├── 02-analyze-contract-liability.md
│   ├── 03-track-regulatory-deadlines.md
│   ├── 04-review-court-ruling-precedent.md
│   ├── 05-audit-internal-policy.md
│   ├── 06-generate-tax-law-memo.md
│   ├── 07-cross-ref-contracts-regulation.md
│   ├── 08-monitor-anpd-decisions.md
│   ├── 09-assess-patent-litigation-risk.md
│   └── 10-verify-software-license-compliance.md
├── pipeline/                  # Per-task/gen input prompts + generated plans
└── validator-selftest-report.json  # Validator self-test over test_plans/
```

## Extending

### Add a Task
Create a new `.md` file in `tasks/` following the existing format:
- `# Title`
- `## Domain`
- `## Description`
- `## Expected Tools`
- `## Expected Bindings`
- `## Complexity`

### Add Validation Rules
Edit `validator.py` and add a new `_validate_*` method. Call it from the `validate()` method.

### Add an LLM Backend
Edit `runner.py` to add API-based plan generation. Look for the `--api` flag handler.
