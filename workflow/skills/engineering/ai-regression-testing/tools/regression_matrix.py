"""Guard matrix: which fixed defects have a permanent test.

Payload::

    {"defects": [{"id": "BUG-12", "area": "auth", "fixed": true}],
     "tests":   [{"name": "auth_blocks_expired_token", "issue": "BUG-12", "sandboxed": true}]}
"""


def run(payload):
    defects = list(payload.get("defects") or [])
    tests = list(payload.get("tests") or [])

    by_issue = {}
    for test in tests:
        issue = str(test.get("issue") or "").strip()
        if issue:
            by_issue.setdefault(issue, []).append(test)

    rows, unguarded, unsandboxed = [], [], []
    for defect in defects:
        issue = str(defect.get("id") or "")
        guards = by_issue.get(issue, [])
        sandboxed = [t for t in guards if t.get("sandboxed", True)]
        state = ("guarded" if sandboxed else
                 "guarded-but-leaky" if guards else
                 "unguarded" if defect.get("fixed", True) else "open")
        rows.append({"defect": issue, "area": defect.get("area"), "state": state,
                     "tests": [t.get("name") for t in guards]})
        if state == "unguarded":
            unguarded.append(issue)
        elif state == "guarded-but-leaky":
            unsandboxed.append(issue)

    areas = {}
    for row in rows:
        area = row["area"] or "<none>"
        areas.setdefault(area, {"guarded": 0, "unguarded": 0})
        areas[area]["guarded" if row["state"].startswith("guarded") else "unguarded"] += 1

    return {
        "ok": not unguarded and not unsandboxed,
        "defects": rows,
        "unguarded": unguarded,
        "leaky": unsandboxed,
        "by_area": areas,
        "advice": ("every fixed defect has a sandboxed guard" if not unguarded and not unsandboxed
                   else "write tests for: " + ", ".join((unguarded + unsandboxed)[:6])),
    }
