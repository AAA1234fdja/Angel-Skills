"""Premortem scan: are these failure modes specific, detectable and worth fixing?

Payload::

    {"modes": [{"mode": "the vendor rate limit forces a queue nobody built",
                "signal": "429s appear in the integration logs",
                "likelihood": "high", "impact": "high",
                "prevention": "add a bounded queue before launch",
                "cost": "medium", "owner": "platform"}]}

Three checks, each aimed at the way premortems fail: a mode written as a category
("scalability") cannot be monitored, a mode without a signal is discovered too late,
and a prevention that costs more than the risk is the one that gets postponed.
"""

CATEGORY_WORDS = ("scalability", "performance", "security", "quality", "risk",
                  "complexity", "communication", "resources", "timing")
LEVELS = ("high", "medium", "low")
COSTS = ("low", "medium", "high")


def run(payload):
    modes = payload.get("modes") or []
    problems, rows = [], []
    for index, mode in enumerate(modes):
        if not isinstance(mode, dict) or not str(mode.get("mode") or "").strip():
            problems.append(f"modes[{index}]: no failure mode")
            continue
        text = str(mode["mode"]).strip()
        issues = []
        if len(text.split()) < 6:
            issues.append("too short to name a mechanism")
        if any(word in text.lower() for word in CATEGORY_WORDS) and len(text.split()) < 9:
            issues.append("reads as a category: say how it fails")
        if not str(mode.get("signal") or "").strip():
            issues.append("no earliest observable signal: it will be found too late")
        for field in ("likelihood", "impact"):
            if str(mode.get(field) or "").lower() not in LEVELS:
                issues.append(f"{field} must be high, medium or low")
        prevention = str(mode.get("prevention") or "").strip()
        cost = str(mode.get("cost") or "").lower()
        if not prevention:
            issues.append("no prevention")
        elif cost and cost not in COSTS:
            issues.append(f"cost {cost!r} not one of {', '.join(COSTS)}")
        elif cost == "high" and str(mode.get("impact") or "").lower() != "high":
            issues.append("expensive prevention for a non-critical mode: it will be postponed")
        if prevention and not str(mode.get("owner") or "").strip():
            issues.append("prevention with no owner")
        rows.append({"mode": text[:70], "issues": issues})
        problems.extend(f"{text[:40]}: {issue}" for issue in issues)

    if not modes:
        problems.append("no failure modes: a premortem needs at least one")
    elif len(modes) < 3:
        problems.append(f"only {len(modes)} mode(s): three is the floor for the exercise")
    elif len(modes) > 7:
        problems.append(f"{len(modes)} modes: more than seven produces no action")
    return {
        "ok": not problems,
        "modes": len(rows),
        "rows": rows,
        "problems": problems,
        "advice": ("each failure mode is specific, detectable and cheaply preventable"
                   if not problems else "; ".join(problems[:3])),
    }
