"""Tour check: is this a route, or a reading list?

Payload::

    {"reader": "backend dev who needs to know where a refund is authorised",
     "question": "where is a refund approved, and what can stop it",
     "steps": [{"title": "request enters", "file": "api/refunds.py",
                "symbol": "create_refund", "notice": "the idempotency guard"},
               {"title": "service layer", "file": "", "notice": ""}],
     "untoured_branches": [{"branch": "async retry path", "leads_to": "workers/refund.py"}],
     "verified_after_edit": true,
     "existing_files": ["api/refunds.py", "workers/refund.py"]}

An anchor whose file does not exist is worse than no anchor: it teaches the reader
that the tour is stale, so they stop trusting the steps that are still right.
"""

MAX_STEPS = 8


def run(payload):
    steps = [s for s in (payload.get("steps") or []) if isinstance(s, dict)]
    existing = set(str(f) for f in (payload.get("existing_files") or []))
    problems, unanchored, broken, mute = [], [], [], []

    if not str(payload.get("reader") or "").strip():
        problems.append("no reader named: the tour will be a table of contents")
    if not str(payload.get("question") or "").strip():
        problems.append("no question stated: the route has no purpose")
    if not steps:
        problems.append("no steps")
    if len(steps) > MAX_STEPS:
        problems.append(f"{len(steps)} steps: past eight this is a book, split it")

    for index, step in enumerate(steps):
        label = str(step.get("title") or f"steps[{index}]")
        anchor = str(step.get("file") or "").strip()
        if not anchor:
            unanchored.append(label)
        elif existing and anchor not in existing:
            broken.append(f"{label} -> {anchor}")
        if not str(step.get("notice") or "").strip():
            mute.append(label)

    if unanchored:
        problems.append(f"{len(unanchored)} step(s) with no anchor: "
                        + ", ".join(unanchored[:3]))
    if broken:
        problems.append(f"{len(broken)} anchor(s) point at no file: "
                        + ", ".join(broken[:3]))
    if mute:
        problems.append(f"{len(mute)} step(s) with nothing to notice: "
                        + ", ".join(mute[:3]))
    if payload.get("verified_after_edit") is not True:
        problems.append("anchors were never re-verified after the last edit")

    return {
        "ok": not problems,
        "reader": payload.get("reader"),
        "steps": len(steps),
        "anchored": len(steps) - len(unanchored),
        "broken_anchors": broken,
        "untoured_branches": len(payload.get("untoured_branches") or []),
        "problems": problems,
        "advice": (f"{len(steps)} anchored steps take the reader to the answer"
                   if not problems else "; ".join(problems[:3])),
    }
