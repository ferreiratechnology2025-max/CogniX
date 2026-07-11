# AEP-IR v1.1 — Design Notes (not prescriptions, not spec)

Recorded separately from `experiment-results/REPORT.md` per protocol: the
REPORT carries no prescriptive conclusions about changing the spec; this file
does. `SPEC/AEP-IR-1.0.md` remains frozen and untouched by this experiment.

## 1. `origin: external` — a fourth Origin Rule route (from the pre-calibration audit)

**Observation (pre-calibration, reconfirmed after reading §7.5 directly):** the
class "binding is `scope: execution`, `mutability: readonly`, no `default`" is
structurally unsatisfiable under the current three origins (producer / default
/ external scope) — CR-1 forbids a producer on a readonly binding, so there is
no legal way to express "this execution-scoped value arrives from outside the
plan but must never be treated as session/persistent state."

The current spec routes this case through `scope: session`/`persistent`
instead — which the generability experiment confirms LLMs can reliably do
(29/30 plans correctly used this route where applicable). So this is not a
generability blocker; it is a modeling-fidelity gap: an execution-scoped value
that is genuinely external to the plan (e.g., a one-shot tool result the plan
consumes but never re-derives) currently has to borrow `session`/`persistent`
scope semantics it doesn't otherwise carry.

**Candidate for v1.1:** a fourth Origin Rule, `origin: external`, orthogonal to
`scope`, marking a binding as externally-supplied without implying
session/persistent lifetime. Would need its own validation rule (still no
producer allowed) and a Type-Effect Consistency Table update. Not urgent — no
plan in this experiment needed it — but worth tracking before the class is
rediscovered by a task shape this experiment didn't cover.

## 2. Markdown-fence tolerance at the envelope boundary

**Observation:** 30/30 generated responses in this experiment wrapped the plan
JSON in a ` ```json ` fence despite an explicit "no markdown formatting"
instruction in the prompt. This is not a spec violation — fences are outside
the plan JSON — but it is a 100% miss rate on one output-format instruction,
consistent across every task shape tested.

**Candidate for v1.1 tooling (not the IR spec itself):** rather than fighting
this via ever-more-emphatic prompt language, treat markdown fences as a
legitimate transport wrapper at the compiler boundary — i.e., `runner.py`'s
envelope-creation step (or a v1.1 reference implementation) strips a single
outer fence unconditionally before attempting to parse, the same way it
already handles this defensively. This is a tooling/reference-implementation
recommendation, not an IR-1.0/1.1 semantic change — the IR itself is
unaffected either way.

## 3. §10 IR→ISA Mapping — reconcile "7 opcodes" framing (editorial, not semantic)

`SPEC/AEP-IR-1.0.md` §10 states "ISA permanece com 7 opcodes," predating the
ISA session's reconciliation to "six core opcodes + YIELD (conditional
extension, AEP-0008)." The semantic content of §10 — `sync → no opcode, no
watchdog cost`; `YIELD = agent request for watchdog cycles` — is already
consistent with the reconciled ISA. Only the flat "7 opcodes" framing is
stale.

**Candidate for v1.1:** update §10's opening line to match the six-core +
conditional-extension framing used everywhere else in the reconciled spec set
(AEP-0001/0003/0004/0007/0008). Purely editorial; no validator behavior
depends on this line, confirmed during the generability experiment (no plan's
validity turned on this framing).

## 4. "Fetch vs. write" — how does a tool_call populate an externally-sourced binding? (n=1, but precisely named)

**Observation:** `plan-05-01`'s single failure (CR-1) modeled a `tool_call`
node that fetches an external value (`policy_document`, correctly declared
`scope: session`, `readonly`, per Rule 5) as writing directly into that same
binding. CR-1 correctly rejects this — a readonly binding cannot receive
`access: write`.

This is distinct from the `origin: external` gap in §1: that gap is about
*declaring* a binding's origin; this one is about *populating* a binding whose
origin is already correctly declared. The generator got the origin classification
right (external → session-scoped, readonly) and then had no spec-stated pattern
for "how does the node that retrieves this value get its result into the
plan?" The only legal v1.0 pattern is: the `tool_call` writes into a *separate*,
newly-declared `execution`-scoped, mutable binding that holds the fetched
result — the `session`-scoped input binding itself is never a write target. The
spec is internally consistent on this (CR-1 enforces it correctly), but does
not state the pattern anywhere a generator or a human plan-author would
encounter it before making the mistake.

**Candidate for v1.1 (documentation, not necessarily a rule change):** an
explicit worked example in the spec (or the reference prompt) showing the
correct three-step pattern — declare the external `session`/`persistent`
input, declare a *separate* `execution`-scoped output binding for the fetch
result, and have the `tool_call` write only to the latter. This may fully
resolve the ambiguity without any change to the validation rules themselves,
since CR-1 is already correct — the gap is pedagogical, not semantic.

n=1 is not enough to claim a systematic rate on this task shape; flagging for
future experiment rounds (more samples per task, or a task variant that
isolates "fetch semantics") to confirm whether this recurs before treating the
rate itself as a spec-design signal. The naming of the exact ambiguity,
however, does not require a higher n — it is precise regardless of frequency.
