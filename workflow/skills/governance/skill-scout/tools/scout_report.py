"""Scout report: reuse, adapt, or author — and never twice under two names.

Payload::

    {"need": "retire a message schema without breaking consumers",
     "local_hits": [{"id": "schema-evolution", "overlap": 0.85,
                     "covers": ["compat window"], "missing": ["retirement date"]}],
     "external_hits": [{"name": "ecc/schema-retire", "license": "MIT",
                        "ref": "b38be6a", "overlap": 0.7}],
     "decision": "adapt", "target": "schema-evolution"}

Overlap is the caller's estimate, and the tool's job is to hold the decision to it:
a `new` decision with a 0.6+ local hit is a duplicate waiting to happen, and reuse of
an external hit without a licence or a pinned commit is a trust decision made by
accident.
"""


def run(payload):
    local = [h for h in (payload.get("local_hits") or []) if isinstance(h, dict)]
    external = [h for h in (payload.get("external_hits") or []) if isinstance(h, dict)]
    decision = str(payload.get("decision") or "").strip().lower()
    problems = []

    if not str(payload.get("need") or "").strip():
        problems.append("no need stated: searching before naming the decision finds "
                        "everything and nothing")
    if decision not in ("reuse", "adapt", "author"):
        problems.append(f"decision '{decision or '?'}' is not one of reuse/adapt/author")

    best_local = max((float(h.get("overlap") or 0) for h in local), default=0.0)
    if decision == "author" and best_local >= 0.6:
        problems.append(f"authoring with a {best_local:.2f}-overlap local hit: reuse or "
                        "adapt, or state what the hit cannot do")
    if decision in ("reuse", "adapt") and not (local or external):
        problems.append(f"{decision} with no hit: from what?")

    for hit in external:
        name = str(hit.get("name") or "?")
        if not str(hit.get("license") or "").strip():
            problems.append(f"{name}: no licence recorded")
        ref = str(hit.get("ref") or "").strip()
        if not ref or len(ref) < 7:
            problems.append(f"{name}: no pinned commit, so the thing being reused can "
                            "change under you")
        if decision == "reuse" and not hit.get("audited"):
            problems.append(f"{name}: reuse of unaudited external code")

    for hit in local:
        if hit.get("covers") or hit.get("missing"):
            continue
        problems.append(f"{hit.get('id', '?')}: a hit without 'covers' and 'missing' "
                        "is a name, not an assessment")

    return {
        "ok": not problems,
        "need": payload.get("need"),
        "decision": decision or None,
        "local_hits": len(local),
        "external_hits": len(external),
        "best_local_overlap": round(best_local, 2),
        "target": payload.get("target"),
        "problems": problems,
        "advice": (f"{decision}: {payload.get('target')}" if not problems
                   else "; ".join(problems[:3])),
    }
