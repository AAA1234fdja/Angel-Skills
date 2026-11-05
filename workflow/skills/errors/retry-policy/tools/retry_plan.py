"""Build and validate a bounded retry schedule.

Payload::

    {"codes": {"E_TOOL_TIMEOUT": {"retryable": true},
               "E_TOOL_INPUT": {"retryable": false}},
     "max_attempts": 3, "base_ms": 200}
"""


def run(payload):
    codes = payload.get("codes") or {}
    max_attempts = int(payload.get("max_attempts", 3))
    base_ms = float(payload.get("base_ms", 200))
    problems, schedules = [], {}

    if max_attempts < 1:
        problems.append("max_attempts must be >= 1")
    if max_attempts > 10:
        problems.append("max_attempts above 10 is almost always a design smell")
    if base_ms <= 0:
        problems.append("base_ms must be positive")

    for code in sorted(codes):
        entry = codes[code] or {}
        retryable = entry.get("retryable")
        idempotent = entry.get("idempotent", True)
        if not isinstance(retryable, bool):
            problems.append(f"{code}: retryable must be a boolean")
            continue
        if retryable and not idempotent:
            problems.append(f"{code}: retryable but not idempotent")
        if not retryable:
            schedules[code] = {"attempts": 1, "delays_ms": [], "note": "fail fast"}
            continue
        delays = []
        for attempt in range(1, max_attempts):
            wait = base_ms * (2 ** (attempt - 1))
            jitter = wait * 0.25
            delays.append({"attempt": attempt + 1,
                           "wait_ms": round(wait, 1),
                           "jitter_up_to_ms": round(jitter, 1)})
        total = sum(d["wait_ms"] + d["jitter_up_to_ms"] for d in delays)
        schedules[code] = {
            "attempts": max_attempts,
            "delays_ms": delays,
            "max_total_wait_ms": round(total, 1),
            "stop_condition": f"after {max_attempts} attempts or {round(total)}ms, surface the last cause",
        }

    return {
        "ok": not problems,
        "max_attempts": max_attempts,
        "schedules": schedules,
        "problems": problems,
        "advice": ("bounded and idempotency-aware" if not problems else
                   "fix the problems before shipping the retry"),
    }
