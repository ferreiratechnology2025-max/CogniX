#!/usr/bin/env python3
"""
AEP-IR LLM Generability experiment — clean-room plan generator (zero-dependency).

Each plan is produced by a FRESH HTTPS POST to the Anthropic Messages API whose
SOLE user message is the verbatim contents of pipeline/<task>/input-coder.md —
no system prompt, no prior turns, no tools, and no account memory (a raw API
call has none). One call per plan; the three generations per task are
INDEPENDENT samples (separate calls), never turns of a single conversation.

Uses only the Python standard library (urllib) — no `anthropic` SDK, no pip
install — so it runs in restricted environments where the PyPI wheel download
is blocked but the API host is reachable.

This file is NOT part of the frozen instrument (validator.py / runner.py /
prompt.md / canonical.py); it generates the data the instrument measures, so it
does not affect instrument_head.

Provenance note: temperature/top_p/top_k are REMOVED on claude-opus-4-8 (400 if
sent). No temperature knob to pin; the 3 generations are independent via the
model's default sampling. Recorded in the manifest rather than a numeric value.

Transport-failure retry policy (pre-registered before any Phase 2 call): a
plan the model actually GENERATED is data and is never retried, whether or not
it validates. A transport failure that produced no content (network error,
timeout, or 5xx/529 overloaded) is not a sample — it is a call that never
happened, and is retried up to TRANSPORT_RETRY_MAX times, with each attempt's
reason logged. Any HTTP error carrying a structured API error body (4xx: bad
request, auth, credit, content policy, refusal) is a final outcome of a real
request and is never retried.

Usage:
    ANTHROPIC_API_KEY=...  python generate.py --task 01           # pilot: tarefa-01 x3
    ANTHROPIC_API_KEY=...  python generate.py                     # all 30
    python generate.py --task 01 --force                          # overwrite existing
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.resolve()
PIPELINE = BASE / "pipeline"
SPEC = (BASE / ".." / ".." / "SPEC" / "AEP-IR-1.0.md").resolve()
RESULTS = (BASE / ".." / ".." / "experiment-results").resolve()
LOG = RESULTS / "generation-log.jsonl"

# ── Frozen generator config (recorded in manifest.json) ──────────────────────
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
MODEL = "claude-opus-4-8"
THINKING = {"type": "adaptive"}   # explicit: on opus-4-8, omitting thinking runs WITHOUT it
MAX_TOKENS = 16000
TIMEOUT = 180                     # seconds; adaptive thinking can take a while

_FENCE = re.compile(r"^\s*```(?:json)?\s*\n(.*?)\n\s*```\s*$", re.DOTALL)


def _sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _strip_fences(text: str):
    m = _FENCE.match(text.strip())
    if m:
        return m.group(1), True
    return text, False


def _call_api(api_key: str, prompt_text: str) -> dict:
    """One fresh, isolated call: input-coder.md is the ONLY user message; no
    system prompt; no tools. Returns the parsed response JSON. Raises on non-2xx
    (the caller records it — a 4xx is an instrument/mechanics finding, not plan
    data)."""
    body = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "thinking": THINKING,
        "messages": [{"role": "user", "content": prompt_text}],
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "x-api-key": api_key,
        "anthropic-version": API_VERSION,
        "content-type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


# Transport-failure retry policy (pre-registered BEFORE any Phase 2 call, per
# the protocol: a plan that was actually GENERATED is data and is never
# retried; a call that produced no content because of a transport failure
# (network error, timeout, 5xx/529 overloaded) is not a sample — it is a call
# that never happened, and a bounded retry is legitimate. Any HTTP error that
# carries a structured API error body (4xx: bad request, auth, credit, content
# policy, refusal) is a FINAL outcome of a real request and is never retried.
TRANSPORT_RETRY_MAX = 3
TRANSPORT_RETRY_STATUS = {500, 502, 503, 504, 529}


def _generate_one(api_key: str, folder: Path, force: bool) -> dict:
    plan_id = folder.name  # tarefa-XX-gen-YY
    input_path = folder / "input-coder.md"
    out_path = folder / "output-plan.json"

    if not input_path.exists():
        return {"plan": plan_id, "status": "no-input"}
    if out_path.exists() and not force:
        return {"plan": plan_id, "status": "skip-exists"}

    prompt = input_path.read_text(encoding="utf-8")
    retries = []
    attempt = 0
    while True:
        attempt += 1
        try:
            data = _call_api(api_key, prompt)
            break
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            if e.code in TRANSPORT_RETRY_STATUS and attempt <= TRANSPORT_RETRY_MAX:
                retries.append({"attempt": attempt, "reason": f"http-{e.code}", "detail": detail})
                continue
            return {"plan": plan_id, "status": f"api-error-{e.code}", "detail": detail,
                    "prompt_sha256": _sha256_text(prompt), "transport_retries": retries}
        except Exception as e:  # network error / timeout — pure transport failure
            if attempt <= TRANSPORT_RETRY_MAX:
                retries.append({"attempt": attempt, "reason": "transport-exception", "detail": str(e)})
                continue
            return {"plan": plan_id, "status": "call-failed", "detail": str(e),
                    "prompt_sha256": _sha256_text(prompt), "transport_retries": retries}

    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    body, fences_stripped = _strip_fences(text)
    # A malformed plan IS data — including non-parseable JSON. Save verbatim,
    # unconditionally, whether or not `body` is valid JSON. No re-generation
    # "because it was clearly an accident" — the runner's validate step is
    # what classifies this (as PARSE-ERROR), not this script.
    out_path.write_text(body, encoding="utf-8")

    usage = data.get("usage", {})
    return {
        "plan": plan_id,
        "status": "generated",
        "transport_retries": retries,
        "model": data.get("model"),
        "response_id": data.get("id"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stop_reason": data.get("stop_reason"),
        "fences_stripped": fences_stripped,
        "response_chars": len(body),
        "prompt_sha256": _sha256_text(prompt),
        "usage": {"input_tokens": usage.get("input_tokens"),
                  "output_tokens": usage.get("output_tokens")},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="AEP-IR clean-room plan generator (zero-dep)")
    ap.add_argument("--task", help="limit to tarefa-<NN> (e.g. 01 for the pilot)")
    ap.add_argument("--force", action="store_true", help="overwrite existing output-plan.json")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY is not set.")

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
        rec = _generate_one(api_key, folder, args.force)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        extra = ""
        if rec["status"] == "generated":
            extra = (f"  stop={rec['stop_reason']}  fences_stripped={rec['fences_stripped']}"
                     f"  out_chars={rec['response_chars']}")
        elif "detail" in rec:
            extra = f"  {rec['detail'][:120]}"
        print(f"  {rec['status']:14} {rec['plan']}{extra}")


if __name__ == "__main__":
    main()
