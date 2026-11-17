"""Flow audit: how expensive is this path, and where does it break?

Payload::

    {"job": "renew an expired card",
     "steps": [{"id": "open", "kind": "decision", "cost": 1},
               {"id": "confirm", "kind": "input", "cost": 2},
               {"id": "save", "kind": "wait", "cost": 3, "recoverable": true},
               {"id": "declined", "kind": "error", "cost": 5, "dead_end": true}]}

Steps are weighted because they are not equal: a wait the user cannot influence
costs more than a click, a decision costs more than a field, and an error path the
user did not ask for costs the most. The tool returns the weighted total, the share
that is the user's work, and every dead end — the part a screenshot review misses.
"""

KINDS = ("input", "decision", "wait", "error", "confirm")
DEFAULT_COST = {"input": 2, "decision": 3, "wait": 3, "error": 5, "confirm": 1}
USER_WORK = ("input", "decision")


def run(payload):
    job = str(payload.get("job") or "").strip()
    steps = payload.get("steps") or []
    problems, rows = [], []
    total = user_cost = 0
    dead_ends, unrecoverable = [], []

    for index, step in enumerate(steps):
        if not isinstance(step, dict) or not step.get("id"):
            problems.append(f"steps[{index}]: no id")
            continue
        kind = str(step.get("kind") or "")
        cost = step.get("cost")
        cost = DEFAULT_COST.get(kind, 3) if cost is None else int(cost)
        if kind not in KINDS:
            problems.append(f"{step['id']}: kind {kind!r} not one of {', '.join(KINDS)}")
        total += cost
        if kind in USER_WORK:
            user_cost += cost
        if step.get("dead_end"):
            dead_ends.append(str(step["id"]))
        if step.get("recoverable") is False and not step.get("recovery"):
            unrecoverable.append(str(step["id"]))
        rows.append({"step": str(step["id"]), "kind": kind, "cost": cost,
                     "dead_end": bool(step.get("dead_end"))})

    if not job:
        problems.append("no job statement: a flow without a job cannot be judged")
    if not steps:
        problems.append("no steps recorded")
    if dead_ends:
        problems.append(f"{len(dead_ends)} dead end(s): " + ", ".join(dead_ends))
    if unrecoverable:
        problems.append("unrecoverable step(s) with no recovery path: "
                        + ", ".join(unrecoverable))

    share = round(user_cost / total, 2) if total else None
    heaviest = sorted(rows, key=lambda r: (-r["cost"], r["step"]))[:3]
    return {
        "ok": not problems,
        "job": job,
        "steps": len(rows),
        "weighted_cost": total,
        "user_share": share,
        "dead_ends": dead_ends,
        "unrecoverable": unrecoverable,
        "heaviest": heaviest,
        "problems": problems,
        "advice": ("the flow is short, recoverable and has no dead ends" if not problems
                   else "; ".join(problems[:3])),
    }
