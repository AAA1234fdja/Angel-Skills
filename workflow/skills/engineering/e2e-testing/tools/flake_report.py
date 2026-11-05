"""Flake analysis over repeated runs.

Payload::

    {"runs": {"checkout.spec.ts": ["pass","fail","pass", …]},
     "max_flake_rate": 0.0}

A test that fails intermittently is a broken test: it trains everyone to ignore
red. This tool quantifies it so quarantine is a decision, not a feeling.
"""


def run(payload):
    runs = payload.get("runs") or {}
    limit = float(payload.get("max_flake_rate", 0.0))
    rows, quarantine, stable = [], [], []

    for name in sorted(runs):
        results = [str(r).lower() for r in (runs[name] or [])]
        total = len(results)
        if total == 0:
            rows.append({"test": name, "total": 0, "state": "never ran"})
            continue
        passes = sum(1 for r in results if r in ("pass", "ok", "true", "1"))
        fails = sum(1 for r in results if r in ("fail", "error", "false", "0"))
        flake_rate = (min(passes, fails) / total) if passes and fails else 0.0
        state = ("always red" if passes == 0 else
                 "stable" if fails == 0 else
                 "flaky" if flake_rate > limit else "rare")
        rows.append({"test": name, "total": total, "passes": passes, "fails": fails,
                     "flake_rate": round(flake_rate, 3), "state": state})
        if state in ("flaky", "always red"):
            quarantine.append(name)
        elif state == "stable":
            stable.append(name)

    return {
        "ok": not quarantine,
        "tests": rows,
        "quarantine": quarantine,
        "stable": stable,
        "advice": ("all tests stable across runs" if not quarantine else
                   "mark as fixme with an issue: " + ", ".join(quarantine[:5])),
    }
