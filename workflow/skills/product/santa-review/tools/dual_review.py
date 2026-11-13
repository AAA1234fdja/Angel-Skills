"""Dual review: did two independent reviewers both pass, on different lenses?

Payload::

    {"change": "refund authorisation rewrite",
     "criteria": ["no double refund under retry", "audit trail preserved"],
     "reviewers": [{"name": "ana", "lens": "correctness", "verdict": "pass",
                    "blockers": [], "reviewed_independently": true,
                    "wrote_before_discussion": true},
                   {"name": "luis", "lens": "operability",
                    "verdict": "pass_with_concerns", "blockers": ["no timeout on retry"],
                    "reviewed_independently": false,
                    "wrote_before_discussion": false}],
     "disagreements": [{"topic": "retry timeout", "settled_by": "measured 90s worst case"}]}

"Pass with concerns" is treated as a fail on purpose: the concerns are the reason the
second reviewer exists, and a verdict that approves while listing blockers teaches the
author to read only the first word.
"""

VERDICTS = {"pass", "fail", "pass_with_concerns", "blocked"}


def run(payload):
    reviewers = [r for r in (payload.get("reviewers") or []) if isinstance(r, dict)]
    problems, concerns = [], []

    if not (payload.get("criteria") or []):
        problems.append("no pass criteria: independence without a rubric is two opinions")
    if len(reviewers) < 2:
        problems.append("fewer than two reviewers: this is a normal review")

    lenses = [str(r.get("lens") or "").strip().lower() for r in reviewers]
    if len(reviewers) >= 2 and len(set(lenses)) < len(lenses):
        problems.append("identical lenses: the pair covers one review, twice")

    for index, reviewer in enumerate(reviewers):
        name = str(reviewer.get("name") or f"reviewers[{index}]")
        verdict = str(reviewer.get("verdict") or "").strip().lower()
        if verdict not in VERDICTS:
            problems.append(f"{name}: verdict '{verdict or '?'}' is not one of "
                            + "/".join(sorted(VERDICTS)))
        if verdict == "pass_with_concerns":
            concerns.append(name)
        if verdict in ("fail", "blocked") or reviewer.get("blockers"):
            problems.append(f"{name}: unresolved blockers — "
                            + ", ".join(map(str, (reviewer.get("blockers") or
                                                  ["verdict " + verdict])[:2])))
        if reviewer.get("reviewed_independently") is not True:
            problems.append(f"{name}: review was not independent")
        if reviewer.get("wrote_before_discussion") is not True:
            problems.append(f"{name}: verdict was formed after discussion, so the "
                            "independence was paid for and not used")

    if concerns:
        problems.append("'pass with concerns' is a fail: " + ", ".join(concerns))

    disagreements = [d for d in (payload.get("disagreements") or [])
                     if isinstance(d, dict)]
    for index, item in enumerate(disagreements):
        if not str(item.get("settled_by") or "").strip():
            problems.append(f"disagreements[{index}]: settled by nobody, so it was "
                            "settled by seniority")

    passed = sum(1 for r in reviewers
                 if str(r.get("verdict") or "").lower() == "pass")
    return {
        "ok": not problems,
        "change": payload.get("change"),
        "reviewers": len(reviewers),
        "independent_passes": passed,
        "lenses": sorted(set(l for l in lenses if l)),
        "disagreements": len(disagreements),
        "problems": problems,
        "advice": ("two independent passes on different lenses, no open blocker"
                   if not problems else "; ".join(problems[:3])),
    }
