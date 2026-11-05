"""Validate a loop definition before it is allowed to run.

Payload::

    {"loop": {"success_test": "npm test", "max_iterations": 10,
              "max_seconds": 3600, "max_cost": 5.0,
              "no_progress_after": 3, "checkpoint": "git commit",
              "gates": ["deploy"], "failure_policy": "revert"}}
"""

REQUIRED = ("success_test", "max_iterations", "failure_policy")
RECOMMENDED = ("max_seconds", "max_cost", "no_progress_after", "checkpoint")
GATED = ("deploy", "delete", "force", "push", "migrate", "drop", "rotate")


def run(payload):
    loop = payload.get("loop") or {}
    missing, warnings = [], []

    for key in REQUIRED:
        if not loop.get(key):
            missing.append(key)
    for key in RECOMMENDED:
        if not loop.get(key):
            warnings.append(f"missing {key}")

    stops = sum(1 for key in ("max_iterations", "max_seconds", "max_cost", "no_progress_after")
                if loop.get(key))
    if stops < 3:
        warnings.append(f"only {stops} stop condition(s): three is the practical minimum")

    gates = [str(g).lower() for g in loop.get("gates") or []]
    policy = str(loop.get("failure_policy") or "").lower()
    risky = [word for word in GATED if word in policy]
    if risky and not gates:
        missing.append("gates (failure policy mentions " + ", ".join(risky) + ")")

    if loop.get("max_iterations") and int(loop["max_iterations"]) > 100:
        warnings.append("max_iterations above 100: is this really a loop?")

    return {
        "ok": not missing,
        "missing": missing,
        "warnings": warnings,
        "stop_conditions": stops,
        "gates": gates,
        "advice": ("loop is safe to run unattended" if not missing and stops >= 3 else
                   "add the missing guards before starting"),
    }
