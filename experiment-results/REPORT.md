# AEP-IR LLM Generability Experiment — Report

**Question:** Can an LLM reliably generate valid AEP-IR v1.0 Execution Plans from
real-world task descriptions?

**Answer: Yes, for this instrument, this spec revision, and this generator.**
29/30 plans (96.7%) validated against the calibrated instrument on the first
attempt — well above the pre-registered 70% gate.

---

## Provenance

| | |
|---|---|
| Spec baseline (frozen) | `990acf4` — `SPEC/AEP-IR-1.0.md` |
| Instrument head (frozen) | `cc7dd41` — `validator.py` / `runner.py` / `prompt.md` / `canonical.py` |
| Generator | scripted API, fresh isolated context per plan (`generate.py`, zero external dependency — stdlib `urllib`) |
| Model | `claude-opus-4-8` |
| Sampling | n/a — `temperature`/`top_p`/`top_k` removed on this model; independent samples via default sampling |
| Context per call | `input-coder.md` verbatim as the sole user message; no system prompt; no tools; no account memory (raw API call) |
| Canonicalization | `rfc8785` 0.1.4 (RFC 8785 / JCS) |
| Full manifest | `experiment-results/manifest.json` |

30 calls were made across two API keys, both used transiently for this
experiment and neither persisted in any committed file (verified before each
commit — `grep` for the key literal returned zero matches). The first key's
validity window elapsed mid-run after 26/30 calls (a `401 authentication_error`
— a final, structured 4xx outcome, not a transport failure, and therefore
correctly *not* retried per the pre-registered policy). The remaining 4 slots
(`tarefa-09-gen-03`, `tarefa-10-gen-01/02/03`) were generated with a second key
once supplied. Both keys were transient by design; the operator was advised to
revoke them after use.

## Methodology disclosures (declared deviations from the pre-registered protocol)

**1. Generation ran in two batches with an interim validation between them —
not "a single validate pass over the 30."** The actual sequence was: 26 plans
generated → the first API key's validity window elapsed (`401`) → *the 26 were
validated* (25/26, CR-1 identified) → a second key supplied → the remaining 4
plans generated → the full 30 validated. This is a deviation from the
pre-registered "single `validate` pass, over the 30" protocol, and is recorded
here rather than smoothed over. It is inert, and verifiably so, for three
independent reasons:

- **The generator is stateless per call.** Each of the 30 calls saw only that
  plan's `input-coder.md`, frozen before batch 1 began (`spec_sha256` /
  `instrument_head` unchanged across both batches — see below). No call could
  have been influenced by another call's result, interim or otherwise.
- **The instrument did not change between batches.** `git log
  cc7dd41..HEAD -- validator.py runner.py prompt.md canonical.py` returns zero
  commits — `instrument_head` remained `cc7dd41` throughout. The generation
  timestamps in `generation-log.jsonl` show batch 1 ending at `02:36:16Z` and
  batch 2 beginning at `02:40:24Z`, with `skip-exists` records confirming batch
  2 did not regenerate anything from batch 1.
- **The operator seeing interim results has no causal channel to the 4 final
  plans.** The interim validation revealed *a rate and one rejection code*, not
  guidance that could steer generation — the prompt and instrument were
  already frozen, and the 4 remaining calls used the identical, unmodified
  `input-coder.md` files.

The deviation is harmless *because the design made it harmless*, not by
assumption — each of the three claims above is independently checkable in the
commit history and the log timestamps.

**2. Post-run manifest edits are provenance-only.** After generation completed,
`experiment-results/manifest.json` was updated to record `status` and
`generation_note`. Diffed against the last commit before generation began
(`f91a5ad`), these are the **only two fields that changed** — every
pre-registered rule field (`spec_fixable`, `spec_fixable_rationale`,
`prompt_fixable`, `canonicalization`, `generator`, `transport_retry_policy`) is
byte-identical to its pre-generation value. The pre-registration was not
touched after seeing results.

## Results

| Metric | Value |
|---|---|
| N (total plans) | 30 |
| Valid | 29 |
| Invalid | 1 |
| **Primary pass rate** (all 30 count) | **96.7%** |
| **Secondary pass rate** (excluding failures whose *entire* error set is a subset of the pre-registered `SPEC_FIXABLE = {OR-1, DAG-1}`) | **96.7%** (N=30 — zero plans excluded; see below) |
| Pre-registered gate | ≥ 70% |
| **Gate result** | **PASSED** (primary rate exceeds the gate by 26.7 points) |

The primary and secondary rates are identical because the one failure's error
set (`{CR-1}`) is not a subset of `SPEC_FIXABLE` — no plan was excluded from
the secondary calculation. **This equality is itself a result, not an absence
of one:** zero plans failed on `OR-1`/`DAG-1` alone, so the conservative,
deliberately-over-inclusive `SPEC_FIXABLE` pre-registration (kept at GATE 0
after weighing the counter-argument) cost nothing in this run. A pre-registered
set that over-includes and turns out not to distort the measured rate is the
best possible resolution of that eleventh-hour dilemma — the caution was free.

### Rejection modes (by frequency, across all failures)

| Code | Count | Classification |
|---|---|---|
| CR-1 | 1 | **unclassified** (outside `SPEC_FIXABLE ∪ PROMPT_FIXABLE`) |

Per the frozen `classify_verdict`, a code outside both pre-registered sets is
reported as `unclassified`, not silently folded into `prompt-fixable`. This is
the intended behavior of the honest classifier calibrated in GATE 0.

### The one failure (`plan-05-01`, task 05, generation 01)

The plan declares two external inputs (`policy_document`, `regulation_text`)
correctly per the §7.5 Origin Rules — `mutability: readonly`, `scope: session`,
no default — because they are fed from outside the plan, not computed by it.
Two `tool_call` nodes then *fetch* these values and declare `access: write` on
them, tripping CR-1 (`write access requires mutability: mutable`).

This is a genuine semantic tension, not a validator artifact or a prompt gap:
the generator correctly learned the three-origins lesson (external input →
`session`/`persistent`, readonly, per Rule 5) and then tripped on a question
the spec doesn't answer cleanly: **how does a `tool_call` populate a binding
that represents externally-sourced data?** The correct v1.0 pattern is for the
fetching `tool_call` to write into a *separate*, `execution`-scoped, mutable
binding — never into the `session`-scoped input binding itself, which stays
readonly by definition. The generator's error is not noise; it mirrors a real
modeling ambiguity ("is fetched data the environment's input, or the tool's
output?") that the spec resolves correctly but does not state explicitly
anywhere a generator would see it stated. This is the second design
contribution this experiment paid for, alongside `origin: external` — see
`IR-v1.1-notes.md` § "Fetch vs. write" for the write-up. One plan out of 30
exhibiting this is not enough to claim a systematic rate on this task shape,
but it is precise enough to name the exact ambiguity, which is what makes it
worth recording. No spec change is implied by n=1; see `IR-v1.1-notes.md` for a
design observation, not a prescription.

## Instrument findings surfaced by this run (not spec changes — recorded here per protocol)

- **Universal markdown fencing.** 30/30 generated responses wrapped the JSON
  plan in a ```` ```json ```` fence despite the prompt's explicit "no markdown
  formatting" instruction. The harness detected and stripped it in every case
  (`fences_stripped: true` logged per plan in `generation-log.jsonl`), and no
  plan was lost to this. This is a signal about *instruction* generability
  distinct from *format* generability — the model reliably ignores this one
  formatting instruction regardless of task content. See `IR-v1.1-notes.md`.
- **Zero parse errors, zero transport retries.** All 30 raw responses were
  syntactically valid JSON on receipt; no `PARSE-ERROR` rows in
  `results-table.csv`. No transport failure (network error, timeout, 5xx)
  occurred during generation — the two key-expiry failures were final 4xx
  authentication errors, correctly excluded from the retry path per the
  pre-registered transport policy.
- **ENV-5 and the origin-rules alignment held in production.** The checksum
  integrity check (ENV-5, added at GATE 0) and the three-origin Rule 5 (also
  aligned at GATE 0) both operated exactly as calibrated against real,
  independently-generated plans — not just the GATE 0 fixtures. This is the
  strongest evidence yet that the calibration pass measured something real.
- **§10 IR→ISA Mapping divergence (frozen artifact, read but not edited).**
  `SPEC/AEP-IR-1.0.md` §10 still frames the ISA as flat "7 opcodes," predating
  the ISA-session reconciliation ("6 core + conditional YIELD extension,
  AEP-0008"). This divergence does not affect plan generation or validation
  (§10 is descriptive cross-reference, not enforced by the validator) and the
  spec was correctly left untouched per the freeze rule. Recorded in
  `IR-v1.1-notes.md`.

## Limitations (declared, not hidden)

- **Single generator, single model family.** All 30 plans were generated by
  `claude-opus-4-8` via the Claude API. The prompt is contextually clean
  (fresh, isolated calls, no memory), but the generability question has only
  been answered for one model family. Replication with a diverse set of
  generators is future work, not part of this experiment's design.
- **n=3 per task.** Three independent generations per task bound the sample;
  the single CR-1 failure is n=1 out of 30, not enough to distinguish "rare
  generator slip" from "underlying rate on this task shape" with confidence.
- **Temperature could not be pinned.** `claude-opus-4-8` rejects
  `temperature`/`top_p`/`top_k` (removed on this model tier). Independence
  across the 3 generations per task rests on the model's default sampling
  behavior, not an explicit, reproducible temperature setting.
- **The `OR-1 ∧ CR-1` structural finding from the pre-calibration audit is
  reclassified, not retracted.** Three sessions ago, `OR-1` combined with the
  readonly/no-default constraint appeared to make an entire class of external
  input ("readonly + execution-scoped + no default") structurally
  inexpressible. Reading the frozen §7.5 Origin Rules directly showed the spec
  *names* the legal route (`scope: session`/`persistent`) — the class remains
  unsatisfiable, but the spec provides an explicit, legal way to express
  external inputs outside it. The finding survives only as a design
  observation for `origin: external` in a future revision (see
  `IR-v1.1-notes.md`), not as a gap the current experiment measures against.

## Conclusion

Against the AEP-IR v1.0 spec as frozen, an instrument calibrated with a
genuine positive control and a mechanically-verified integrity check (ENV-5),
and a generator that never saw the validator, the spec, or this repository's
tooling: **yes — for this instrument, this spec revision, and this generator.**
29/30 independently-generated plans (96.7%) validated on first attempt, no
retries, no cherry-picking. The remaining 3.3% is not noise: it is the spec
teaching, in one precise instance, exactly where its own semantics are still
ambiguous (`plan-05-01`, CR-1 — see above). The one failure is a substantive,
specific semantic error, correctly caught and correctly left unclassified
rather than force-fit into a bucket that would understate its novelty.

This is the number three sessions of calibration exist to make trustworthy. It
survived the same scrutiny the calibration itself was built under.
