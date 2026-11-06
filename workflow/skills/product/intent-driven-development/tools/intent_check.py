"""Intent check: could two people implement this and build the same thing?

Payload::

    {"intent": "users can resume an abandoned checkout",
     "criteria": [{"id": "resume", "statement": "a cart idle for 24h can be resumed "
                                                "within 2 clicks",
                   "check": "e2e: resume.spec.ts"},
                  {"id": "fast", "statement": "the resume page is fast", "check": ""}],
     "non_goals": ["changing the payment flow"],
     "ambiguities": [{"question": "24h or 48h?", "resolved_by": "ana"}]}

The tool refuses adjectives that cannot be observed, criteria without a check and
ambiguities resolved by nobody. It does not judge whether the criteria are the *right*
ones — that is the conversation with the requester.
"""

VAGUE = {"fast", "clean", "robust", "simple", "better", "improved", "nice",
         "user-friendly", "seamless", "modern", "scalable", "efficient", "proper",
         "correct"}


def run(payload):
    criteria = [c for c in (payload.get("criteria") or []) if isinstance(c, dict)]
    problems, vague = [], []

    if not str(payload.get("intent") or "").strip():
        problems.append("no intent sentence")
    if not criteria:
        problems.append("no criteria: an intent with no criteria is a mood")

    for index, crit in enumerate(criteria):
        cid = str(crit.get("id") or f"criteria[{index}]")
        statement = str(crit.get("statement") or "").strip().lower()
        words = set(statement.replace(",", " ").replace(".", " ").split())
        hits = sorted(words & VAGUE)
        if hits:
            vague.append(f"{cid}: {', '.join(hits)}")
        if not str(crit.get("check") or "").strip():
            problems.append(f"{cid}: no check attached (test, query, tool or owned step)")

    if vague:
        problems.append("unobservable wording: " + "; ".join(vague[:3]))
    if not (payload.get("non_goals") or []):
        problems.append("no non-goals: scope will be negotiated during review")
    for index, amb in enumerate(payload.get("ambiguities") or []):
        if not isinstance(amb, dict):
            continue
        if not str(amb.get("resolved_by") or "").strip():
            problems.append(f"ambiguities[{index}]: resolved by nobody, so it will "
                            "resurface at review")

    return {
        "ok": not problems,
        "intent": payload.get("intent"),
        "criteria": len(criteria),
        "checkable": sum(1 for c in criteria if str(c.get("check") or "").strip()),
        "vague": vague,
        "non_goals": len(payload.get("non_goals") or []),
        "ambiguities": len(payload.get("ambiguities") or []),
        "problems": problems,
        "advice": ("two people implementing this build the same thing"
                   if not problems else "; ".join(problems[:3])),
    }
