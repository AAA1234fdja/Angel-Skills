"""Handoff check: does the next responder start informed or start guessing?

Payload::

    {"window": "2026-11-05 -> 2026-11-12",
     "incidents": [{"state": "watching", "owner": "ana", "next": "check error rate"}],
     "changes": [{"what": "deploy 1.4.2", "rollback": "redeploy 1.4.1"}],
     "noise": ["disk-warning closes itself", "cache-hit-rate flap"],
     "fragile": "the export worker, surviving on retries",
     "scheduled": [{"what": "TLS renewal", "when": "2026-11-09"}],
     "contacts": [{"area": "payments", "who": "ana"}]}

The noise list is required on purpose: tolerated alerts are the top source of wasted
pages for a new responder, and they are the one thing a dashboard cannot explain.
"""


def run(payload):
    problems = []
    incidents = payload.get("incidents") or []
    changes = payload.get("changes") or []
    noise = payload.get("noise") or []
    scheduled = payload.get("scheduled") or []
    contacts = payload.get("contacts") or []

    if not str(payload.get("window") or "").strip():
        problems.append("no handoff window: the next responder does not know the scope")
    for index, incident in enumerate(incidents):
        if not isinstance(incident, dict):
            problems.append(f"incidents[{index}] is not an object")
            continue
        for field in ("state", "owner", "next"):
            if not str(incident.get(field) or "").strip():
                problems.append(f"incidents[{index}]: no {field}")
    for index, change in enumerate(changes):
        if isinstance(change, dict) and not str(change.get("rollback") or "").strip():
            problems.append(f"changes[{index}]: {change.get('what', '?')} has no rollback")
    if not noise:
        problems.append("no known-noise list: tolerated alerts are the top source of "
                        "wasted pages")
    if not str(payload.get("fragile") or "").strip():
        problems.append("nothing named as one step from breaking")
    for index, item in enumerate(scheduled):
        if isinstance(item, dict) and not str(item.get("when") or "").strip():
            problems.append(f"scheduled[{index}]: no date")
    if not contacts:
        problems.append("no contacts: the responder has nobody to call by area")
    if not incidents and not changes:
        problems.append("no incidents and no changes: was anything actually handed over?")

    return {
        "ok": not problems,
        "window": payload.get("window"),
        "incidents": len(incidents),
        "changes": len(changes),
        "noise_items": len(noise),
        "scheduled": len(scheduled),
        "contacts": len(contacts),
        "problems": problems,
        "advice": ("the next responder starts informed, including what is noise"
                   if not problems else "; ".join(problems[:3])),
    }
