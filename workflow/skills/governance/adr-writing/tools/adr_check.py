"""ADR check: is this record a decision or a justification?

Payload::

    {"title": "Use Redis for sessions", "date": "2026-11-05",
     "status": "accepted",
     "context": "sessions live in the app process; two replicas drop logins",
     "decision": "sessions will be stored in Redis",
     "options": [{"name": "sticky sessions", "lost_because": "still loses on deploy"},
                 {"name": "redis", "chosen": true}],
     "consequences": {"positive": ["deploys no longer log people out"],
                      "negative": ["a new dependency with an SLO"]},
     "reversal": "if p99 session read exceeds 5ms or Redis cost exceeds $400/m"}

The single-option ADR is the thing this tool exists to catch: it reads as analysis
and is actually a press release, and it is the reason the same debate comes back.
"""

REQUIRED_SCALARS = ("title", "date", "status", "context", "decision")
STATUSES = ("proposed", "accepted", "rejected", "superseded", "deprecated")


def run(payload):
    problems = []
    for field in REQUIRED_SCALARS:
        if not str(payload.get(field) or "").strip():
            problems.append(f"missing {field}")
    status = str(payload.get("status") or "")
    if status and status not in STATUSES:
        problems.append(f"status {status!r} not one of {', '.join(STATUSES)}")

    context = str(payload.get("context") or "")
    if context and len(context.split()) < 12:
        problems.append("context is too thin to state the forces at play")

    options = payload.get("options") or []
    chosen = [o for o in options if isinstance(o, dict) and o.get("chosen")]
    rejected = [o for o in options if isinstance(o, dict) and not o.get("chosen")]
    if len(options) < 2:
        problems.append("fewer than two options: an ADR with one option is a press release")
    if len(chosen) != 1:
        problems.append(f"{len(chosen)} option(s) marked chosen: exactly one decision per record")
    for option in rejected:
        if not str(option.get("lost_because") or "").strip():
            problems.append(f"option {option.get('name', '?')!r} lost with no stated reason: "
                            "the debate will return")

    consequences = payload.get("consequences") or {}
    if not consequences.get("positive"):
        problems.append("no positive consequences recorded")
    if not consequences.get("negative"):
        problems.append("no negative consequences: an ADR with only benefits will be reopened")
    if not str(payload.get("reversal") or "").strip():
        problems.append("no reversal condition: the decision has no expiry")

    return {
        "ok": not problems,
        "title": payload.get("title"),
        "status": status,
        "options": len(options),
        "rejected": [o.get("name") for o in rejected],
        "problems": problems,
        "advice": ("the record states the forces, the alternatives and what would undo it"
                   if not problems else "; ".join(problems[:3])),
    }
