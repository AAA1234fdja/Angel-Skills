"""Order journal entries and flag the first anomaly.

Payload:: ``{"entries": [{"seq": 0, "kind": "run.start", "data": {...}}, …]}``

The first anomaly — not the last error — is what explains a run. Sequence gaps,
results without dispatch, dispatches without result, and verdicts before results
are all detectable from the record alone.
"""

EXPECTED_AFTER = {
    "dispatch": ("tool.call", "result", "error"),
    "tool.call": ("tool.result", "error"),
    "tool.result": ("result", "tool.call", "error"),
    "result": ("verdict", "dispatch", "gate", "error"),
    "verdict": ("dispatch", "gate", "run.end"),
    "plan": ("dispatch", "error", "run.end"),
}


def run(payload):
    entries = sorted(payload.get("entries") or [], key=lambda e: e.get("seq", 0))
    problems, timeline = [], []

    previous = None
    for index, entry in enumerate(entries):
        seq = entry.get("seq")
        kind = str(entry.get("kind") or "?")
        if seq != index:
            problems.append(f"seq {seq} at position {index}: gap or reordering")
        if previous and previous in EXPECTED_AFTER and kind not in EXPECTED_AFTER[previous]:
            problems.append(f"{previous} -> {kind} at seq {seq}: unexpected order")
        timeline.append({"seq": seq, "kind": kind,
                         "summary": _summary(entry.get("data") or {})})
        previous = kind

    kinds = [t["kind"] for t in timeline]
    counts = {kind: kinds.count(kind) for kind in sorted(set(kinds))}
    errors = [t for t in timeline if t["kind"] == "error"]

    return {
        "ok": not problems,
        "entries": len(timeline),
        "counts": counts,
        "first_anomaly": problems[0] if problems else None,
        "problems": problems[:20],
        "timeline": timeline[:200],
        "errors": errors[:10],
        "advice": (problems[0] if problems
                   else "no ordering problem: inspect the data of the last successful step"),
    }


def _summary(data):
    keys = ("objective", "step_id", "skill", "tool", "status", "verdict", "code", "message")
    parts = [f"{k}={data[k]}" for k in keys if data.get(k) is not None]
    return " ".join(parts)[:160] or "{}"
