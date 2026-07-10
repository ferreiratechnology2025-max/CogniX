#!/usr/bin/env python3
"""
AEP-IR LLM Generability experiment — clean-room plan generator (scripted API).

Each plan is produced by a FRESH Anthropic API call whose SOLE user message is
the verbatim contents of pipeline/<task>/input-coder.md. No system prompt is
added, and the API carries no account memory — so the generator is contaminated
by neither this repository's tooling nor any prior session (the two channels a
"clean" chat session would leak through). One call per plan; the three
generations per task are INDEPENDENT samples (separate calls), never turns of a
single conversation.

This file is NOT part of the frozen instrument (validator.py / runner.py /
prompt.md / canonical.py). It generates the data the instrument measures, so it
does not affect instrument_head.

Provenance note: temperature/top_p/top_k are REMOVED on claude-opus-4-8 (the API
returns 400 if they are sent). There is no temperature knob to pin on this
model; the 3 generations are independent via the model's default sampling. That
fact is recorded in the manifest rather than a numeric temperature.

Usage:
    ANTHROPIC_API_KEY=...  python generate.py --task 01           # pilot: tarefa-01 x3
    ANTHROPIC_API_KEY=...  python generate.py                     # all 30
    python generate.py --task 01 --force                          # overwrite existing outputs
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import anthropic
except ImportError:
    sys.exit("The 'anthropic' SDK is required: pip install anthropic")

BASE = Path(__file__).parent.resolve()
PIPELINE = BASE / "pipeline"
SPEC = (BASE / ".." / ".." / "SPEC" / "AEP-IR-1.0.md").resolve()
PROMPT = BASE / "prompt.md"
RESULTS = (BASE / ".." / ".." / "experiment-results").resolve()
LOG = RESULTS / "generation-log.jsonl"

# ── Frozen generator config (recorded in manifest.json) ──────────────────────
MODEL = "claude-opus-4-8"
# temperature/top_p/top_k are not sent — removed on claude-opus-4-8 (400 if sent).
THINKING = {"type": "adaptive"}   # explicit: on opus-4-8, omitting thinking runs WITHOUT it
MAX_TOKENS = 16000                # plans are small JSON; well under the non-streaming ceiling

# Strip a single leading/trailing markdown code fence if the model wrapped the JSON.
_FENCE = re.compile(r"^\s*```(?:json)?\s*\n(.*?)\n\s*```\s*$", re.DOTALL)


def _sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _strip_fences(text: str):
    """Return (body, stripped_bool). Markdown fences are removed and LOGGED —
    the protocol requires recording whenever the saved output was not verbatim."""
    m = _FENCE.match(text.strip())
    if m:
        return m.group(1), True
    return text, False


def _generate_one(client, folder: Path, force: bool) -> dict:
    plan_id = folder.name  # e.g. tarefa-01-gen-01
    input_path = folder / "input-coder.md"
    out_path = folder / "output-plan.json"

    if not input_path.exists():
        return {"plan": plan_id, "status": "no-input"}
    if out_path.exists() and not force:
        return {"plan": plan_id, "status": "skip-exists"}

    prompt = input_path.read_text(encoding="utf-8")

    # FRESH, isolated call: the input-coder.md content is the ONLY user message.
    # No system prompt; no prior turns; no tools.
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking=THINKING,
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(b.text for b in resp.content if b.type == "text")
    body, fences_stripped = _strip_fences(text)
    out_path.write_text(body, encoding="utf-8")

    return {
        "plan": plan_id,
        "status": "generated",
        "model": resp.model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": getattr(resp, "_request_id", None),
        "stop_reason": resp.stop_reason,
        "fences_stripped": fences_stripped,
        "response_chars": len(body),
        "prompt_sha256": _sha256_text(prompt),
        "usage": {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="AEP-IR clean-room plan generator")
    ap.add_argument("--task", help="limit to tarefa-<NN> (e.g. 01 for the pilot)")
    ap.add_argument("--force", action="store_true", help="overwrite existing output-plan.json")
    args = ap.parse_args()

    client = anthropic.Anthropic()  # resolves ANTHROPIC_API_KEY / auth profile
    RESULTS.mkdir(parents=True, exist_ok=True)

    folders = sorted(f for f in PIPELINE.iterdir() if f.is_dir())
    if args.task:
        folders = [f for f in folders if f.name.startswith(f"tarefa-{args.task}-")]
    if not folders:
        sys.exit("No matching pipeline folders.")

    print(f"model={MODEL}  thinking={THINKING['type']}  temperature=n/a(removed on {MODEL})")
    print(f"spec_sha256={_sha256_file(SPEC)[:16]}  script_sha256={_sha256_file(__file__)[:16]}")
    print(f"plans={len(folders)}  (one fresh, isolated API call each)\n")

    for folder in folders:
        rec = _generate_one(client, folder, args.force)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        extra = ""
        if rec["status"] == "generated":
            extra = f"  fences_stripped={rec['fences_stripped']}  out_chars={rec['response_chars']}"
        print(f"  {rec['status']:12} {rec['plan']}{extra}")


if __name__ == "__main__":
    main()
