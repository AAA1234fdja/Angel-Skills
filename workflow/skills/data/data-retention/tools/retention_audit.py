"""Retention audit: does every dataset have a purpose, a window and a copy list?

Payload::

    {"datasets": [{"name": "support_tickets", "purpose": "answer customer questions",
                   "classification": "personal", "window_days": 365,
                   "trigger": "ticket closed", "owner": "support",
                   "copies": ["primary", "backup", "warehouse"],
                   "deletion_job": "jobs/purge_tickets", "verified": true}]}

Two things are checked beyond presence: a window without a trigger (nobody knows
when it starts) and a copy list that omits the obvious locations (backup, cache,
warehouse, vendor) — that omission is what turns a deletion request into a
compliance incident.
"""

CLASSIFICATIONS = ("personal", "sensitive", "financial", "health", "operational")
USUAL_COPIES = ("primary", "backup", "warehouse", "cache", "vendor", "analytics")
MAX_WINDOW = 3650


def run(payload):
    datasets = payload.get("datasets") or []
    problems, rows = [], []

    for index, data in enumerate(datasets):
        if not isinstance(data, dict) or not data.get("name"):
            problems.append(f"datasets[{index}]: no name")
            continue
        name = str(data["name"])
        issues = []
        if not str(data.get("purpose") or "").strip():
            issues.append("no purpose: data without a purpose has a habit, not a policy")
        classification = str(data.get("classification") or "").lower()
        if classification not in CLASSIFICATIONS:
            issues.append(f"classification {classification!r} not one of "
                          f"{', '.join(CLASSIFICATIONS)}")
        window = data.get("window_days")
        if not isinstance(window, int) or window <= 0:
            issues.append("no positive window_days")
        elif window > MAX_WINDOW:
            issues.append(f"window of {window} days exceeds {MAX_WINDOW}: "
                          "justify or shorten")
        if not str(data.get("trigger") or "").strip():
            issues.append("no trigger: nobody knows when the window starts")
        if not str(data.get("owner") or "").strip():
            issues.append("no owner")
        copies = [str(c).lower() for c in (data.get("copies") or [])]
        if not copies:
            issues.append("no copy inventory: a deletion that misses a copy is not one")
        else:
            missing = [c for c in ("primary",) if c not in copies]
            if missing:
                issues.append("copy inventory omits the primary store")
            if classification in ("personal", "sensitive", "health") and "backup" not in copies:
                issues.append("sensitive data with no backup in the inventory: "
                              "the policy does not reach the copy that leaks")
        if not str(data.get("deletion_job") or "").strip():
            issues.append("no deletion job: the policy has no execution")
        elif data.get("verified") is False:
            issues.append("deletion job never verified end to end")
        if data.get("legal_hold") and not data.get("hold_expires"):
            issues.append("legal hold without an expiry: retention by inertia")
        rows.append({"dataset": name, "classification": classification,
                     "window_days": window, "issues": issues})
        problems.extend(f"{name}: {issue}" for issue in issues)

    if not datasets:
        problems.append("no datasets audited")
    return {
        "ok": not problems,
        "datasets": len(rows),
        "rows": rows,
        "usual_copies": list(USUAL_COPIES),
        "problems": problems,
        "advice": ("every dataset has a purpose, a window, an owner and a copy list"
                   if not problems else "; ".join(problems[:3])),
    }
