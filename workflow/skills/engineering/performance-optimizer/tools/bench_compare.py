"""Compare two sample sets and decide whether the difference is real.

Payload:: ``{"before": [120, 118, 121], "after": [80, 79, 82], "metric": "ms"}``

No statistics library: median, p95 and a dispersion-aware verdict. The point is
to stop "feels faster" from becoming a merge.
"""


def _median(values):
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        return None
    mid = n // 2
    return ordered[mid] if n % 2 else (ordered[mid - 1] + ordered[mid]) / 2


def _p95(values):
    ordered = sorted(values)
    if not ordered:
        return None
    index = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[index]


def _spread(values):
    if len(values) < 2:
        return 0.0
    low, high = min(values), max(values)
    return 0.0 if low == 0 else (high - low) / low


def run(payload):
    before = [float(v) for v in payload.get("before") or []]
    after = [float(v) for v in payload.get("after") or []]
    metric = payload.get("metric", "units")

    if not before or not after:
        return {"ok": False, "verdict": "insufficient data",
                "advice": "at least one sample per side; three is the practical minimum"}

    b_med, a_med = _median(before), _median(after)
    change = (a_med - b_med) / b_med if b_med else 0.0
    noise = max(_spread(before), _spread(after))

    if len(before) < 3 or len(after) < 3:
        verdict = "under-sampled"
        advice = "take at least three runs per side before deciding"
    elif abs(change) <= max(noise, 0.03):
        verdict = "noise"
        advice = "difference is inside the dispersion: do not keep the change on these numbers"
    elif change < 0:
        verdict = "improved"
        advice = f"{abs(change) * 100:.1f}% faster on median"
    else:
        verdict = "worse"
        advice = f"{change * 100:.1f}% slower on median: revert"

    return {
        "ok": verdict == "improved",
        "metric": metric,
        "before": {"n": len(before), "median": b_med, "p95": _p95(before),
                   "spread": round(_spread(before), 3)},
        "after": {"n": len(after), "median": a_med, "p95": _p95(after),
                  "spread": round(_spread(after), 3)},
        "change": round(change, 4),
        "noise_band": round(noise, 4),
        "verdict": verdict,
        "advice": advice,
    }
