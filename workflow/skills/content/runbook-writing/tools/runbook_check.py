"""Runbook check: could a tired person execute this at 3 a.m.?

Payload::

    {"symptom": "checkout returns 500 for card payments",
     "steps": [{"action": "open the payments dashboard", "expect": "error rate > 2%"},
               {"action": "run purge_retry_queue --dry-run", "expect": "0 pending",
                "dangerous": true, "confirm": "ask the payments owner"}],
     "branches": [{"if": "queue empty", "then": "escalate to platform"}],
     "escalation": {"owner": "payments-oncall", "evidence": "dashboard snapshot"},
     "recovery": {"check": "error rate back under 0.5% for 10 minutes", "window": "10m"}}

The four failures this catches are the four that turn an incident into an outage:
no first action, a dangerous step without a confirmation, no escalation path, and no
stated end condition.
"""


def run(payload):
    symptom = str(payload.get("symptom") or "").strip()
    steps = payload.get("steps") or []
    branches = payload.get("branches") or []
    escalation = payload.get("escalation") or {}
    recovery = payload.get("recovery") or {}
    problems, rows = [], []

    if not symptom:
        problems.append("no symptom: the title must be what the responder was paged for")
    if not steps:
        problems.append("no steps: there is no first action")

    for index, step in enumerate(steps):
        if not isinstance(step, dict) or not str(step.get("action") or "").strip():
            problems.append(f"steps[{index}]: no action")
            continue
        label = str(step["action"])[:60]
        issues = []
        if not step.get("expect"):
            issues.append("no expected observation: the reader cannot tell if it worked")
        if step.get("dangerous") and not step.get("confirm"):
            issues.append("dangerous step with no confirmation: it can make things worse")
        rows.append({"action": label, "dangerous": bool(step.get("dangerous")),
                     "issues": issues})
        problems.extend(f"step '{label}': {issue}" for issue in issues)

    for index, branch in enumerate(branches):
        if not isinstance(branch, dict) or not branch.get("if") or not branch.get("then"):
            problems.append(f"branches[{index}]: needs both 'if' and 'then'")
    if not escalation.get("owner"):
        problems.append("no escalation owner: with nobody to call, the reader improvises")
    if not escalation.get("evidence"):
        problems.append("escalation without evidence: say what to bring")
    if not recovery.get("check"):
        problems.append("no recovery criterion: the incident never formally ends")
    elif not recovery.get("window"):
        problems.append("recovery criterion with no observation window")

    actionable = bool(steps) and bool(str((steps[0] or {}).get("action") or "").strip())
    return {
        "ok": not problems,
        "symptom": symptom,
        "steps": len(rows),
        "branches": len(branches),
        "first_action": (steps[0].get("action") if actionable else None),
        "dangerous_steps": [r["action"] for r in rows if r["dangerous"]],
        "problems": problems,
        "advice": ("a tired person can start, branch, escalate and stop" if not problems
                   else "; ".join(problems[:3])),
    }
