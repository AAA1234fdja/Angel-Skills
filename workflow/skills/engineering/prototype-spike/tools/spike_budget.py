"""Spike budget: is this spike still a spike?

Payload::

    {"question": "does the vendor API paginate under 200ms?",
     "box_hours": 4, "spent_hours": 5.5,
     "delete_date": "2026-11-12", "today": "2026-11-05",
     "cloned_files": 0, "promoted": false}

The tool does not judge the answer; it judges whether the box is holding. A spike
that overruns, a spike that grew into a product (`cloned_files` > 0 means the code
is being copied into the real tree) and a spike past its delete date are reported
as failures, because those are the three ways a spike stops being disposable.
"""


def _days_between(start, end):
    """Calendar days between two ISO dates, or None when one does not parse."""
    try:
        from datetime import date

        a = date.fromisoformat(str(start))
        b = date.fromisoformat(str(end))
    except (TypeError, ValueError):
        return None
    return (b - a).days


def run(payload):
    question = str(payload.get("question") or "").strip()
    box = float(payload.get("box_hours") or 0)
    spent = float(payload.get("spent_hours") or 0)
    cloned = int(payload.get("cloned_files") or 0)
    promoted = bool(payload.get("promoted"))
    delete_date = payload.get("delete_date")
    days_left = _days_between(payload.get("today"), delete_date)

    problems = []
    if not question or question.count("?") != 1:
        problems.append("a spike needs exactly one question, written as one sentence")
    if box <= 0:
        problems.append("no timebox: an unbounded spike is a rewrite")
    if box and spent > box:
        problems.append(f"over the box: {spent:g}h spent of {box:g}h")
    if promoted:
        problems.append("promoted into production: write the real version from the finding")
    if cloned > 0:
        problems.append(f"{cloned} file(s) copied out: the code was supposed to be deleted")
    if days_left is None:
        problems.append("no usable delete date (expected ISO dates)")
    elif days_left < 0:
        problems.append(f"delete date passed {-days_left} day(s) ago: delete the code")

    remaining = round(box - spent, 2) if box else None
    return {
        "ok": not problems,
        "question": question,
        "box_hours": box,
        "spent_hours": spent,
        "remaining_hours": remaining,
        "days_until_delete": days_left,
        "problems": problems,
        "advice": ("the box is holding: keep going, then write the five-line finding"
                   if not problems else problems[0]),
    }
