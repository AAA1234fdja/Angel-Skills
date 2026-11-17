"""Audit error definitions for the three recovery fields.

Payload:: ``{"errors": [{"code": "E_X", "message": "…", "hint": "…",
                         "retryable": false, "stop_condition": "…"}]}``
"""


def run(payload):
    errors = list(payload.get("errors") or [])
    rows, incomplete, over_retry = [], [], []

    for error in errors:
        code = str(error.get("code") or "<no code>")
        hint = str(error.get("hint") or "").strip()
        retryable = error.get("retryable")
        stop = str(error.get("stop_condition") or "").strip()
        missing = []
        if not hint:
            missing.append("hint")
        if not isinstance(retryable, bool):
            missing.append("retryable")
        if retryable is True and not stop:
            missing.append("stop_condition")
        vague = hint.lower() in ("error", "failed", "something went wrong", "unknown")
        if vague:
            missing.append("hint_is_vague")
        rows.append({"code": code, "missing": missing, "hint": hint[:80],
                     "retryable": retryable})
        if missing:
            incomplete.append(code)
        if retryable is True and not stop:
            over_retry.append(code)

    return {
        "ok": not incomplete,
        "errors": rows,
        "incomplete": incomplete,
        "retry_without_stop": over_retry,
        "advice": ("every error answers hint, retry and stop" if not incomplete else
                   "complete: " + ", ".join(incomplete[:6])),
    }
