"""Benchmark compare: is the difference bigger than the noise?

Payload::

    {"metric": "p99 latency ms", "iterations": 12,
     "environment": {"cpu": "4 vCPU", "limits": "cgroup 2GB", "cache": "cold",
                     "dataset": "1M rows"},
     "baseline": {"samples": [41, 43, 40, 44, 42, 45, 41, 43, 42, 40, 44, 43]},
     "candidate": {"samples": [30, 31, 29, 33, 30, 32, 30, 31, 29, 30, 34, 31]}}

The comparison is deliberately conservative: a delta smaller than the combined spread
is reported as no difference, because the alternative is publishing noise as a win.
Medians and tails are both reported — a better median with a worse tail is a
regression for the users who notice.
"""

import statistics


def _stats(samples):
    values = sorted(float(v) for v in samples if isinstance(v, (int, float)))
    if len(values) < 3:
        return None
    median = statistics.median(values)
    tail = values[max(0, int(len(values) * 0.95) - 1):][-1]
    spread = statistics.pstdev(values) if len(values) > 1 else 0.0
    return {"n": len(values), "median": round(median, 3),
            "tail": round(tail, 3), "spread": round(spread, 3),
            "min": round(values[0], 3), "max": round(values[-1], 3)}


def run(payload):
    problems = []
    env = payload.get("environment") or {}
    for field in ("cpu", "limits", "cache", "dataset"):
        if not str(env.get(field) or "").strip():
            problems.append(f"environment.{field} is not stated: the number is not "
                            "reproducible")
    if not str(payload.get("metric") or "").strip():
        problems.append("no metric: faster than what?")

    base = _stats((payload.get("baseline") or {}).get("samples") or [])
    cand = _stats((payload.get("candidate") or {}).get("samples") or [])
    if base is None:
        problems.append("baseline needs at least three samples")
    if cand is None:
        problems.append("candidate needs at least three samples")
    if base and cand and (base["n"] < 10 or cand["n"] < 10):
        problems.append(f"only {min(base['n'], cand['n'])} iterations: ten is the "
                        "minimum to see the noise")

    verdict, delta = "inconclusive", None
    if base and cand:
        delta = round(cand["median"] - base["median"], 3)
        noise = round(base["spread"] + cand["spread"], 3)
        if abs(delta) <= noise:
            verdict = "no difference (delta inside the noise)"
        else:
            verdict = "improved" if delta < 0 else "regressed"
            if (cand["tail"] > base["tail"]) and delta < 0:
                verdict = "regressed on the tail despite a better median"
        if abs(delta) > noise and not str(payload.get("command") or "").strip():
            problems.append("difference claimed but no command recorded: the result "
                            "cannot be reproduced")

    return {
        "ok": not problems and verdict not in ("inconclusive",)
        and not verdict.startswith("regressed"),
        "metric": payload.get("metric"),
        "baseline": base,
        "candidate": cand,
        "delta_median": delta,
        "verdict": verdict,
        "problems": problems,
        "advice": (verdict if isinstance(verdict, str) and verdict != "inconclusive"
                   else "; ".join(problems[:3]) or "record a baseline and a candidate"),
    }
