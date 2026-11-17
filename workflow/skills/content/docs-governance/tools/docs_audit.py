"""Docs audit: does every document have a job, an owner and a shelf life?

Payload::

    {"documents": [{"path": "docs/SETUP.md", "role": "status", "owner": "ana",
                    "review_by": "2027-01-01", "facts": ["db port 5432"]},
                   {"path": "docs/OLD-SETUP.md", "role": "", "owner": "team",
                    "facts": ["db port 5432", "db host db1"]},
                   {"path": "docs/adr/0007-db.md", "role": "history", "owner": "ana",
                    "facts": ["chose postgres"]}],
     "decisions_outside_record": [{"decision": "we use redis for cache",
                                   "document": "docs/MAP.md"}]}

A fact appearing in two documents is not duplication for its own sake: it guarantees
that one of them is wrong eventually, and nobody can tell which. The role check is
the same argument one level up.
"""

ROLES = {"constitution", "map", "status", "history"}


def run(payload):
    documents = [d for d in (payload.get("documents") or []) if isinstance(d, dict)]
    owners_of_fact = {}
    problems, unroled, unowned, stale, duplicated = [], [], [], [], []

    if not documents:
        problems.append("no documents listed: nothing to govern")

    for index, doc in enumerate(documents):
        path = str(doc.get("path") or f"documents[{index}]")
        role = str(doc.get("role") or "").strip().lower()
        if role not in ROLES:
            unroled.append(path)
        owner = str(doc.get("owner") or "").strip()
        if not owner or owner.lower() in ("team", "everyone", "tbd", "all"):
            unowned.append(path)
        if role == "status" and not str(doc.get("review_by") or "").strip():
            stale.append(path)
        for fact in doc.get("facts") or []:
            owners_of_fact.setdefault(str(fact), []).append(path)

    for fact, paths in owners_of_fact.items():
        if len(paths) > 1:
            duplicated.append(f"{fact} in {', '.join(paths[:2])}")

    if unroled:
        problems.append(f"{len(unroled)} document(s) with no role: "
                        + ", ".join(unroled[:3]))
    if unowned:
        problems.append(f"{len(unowned)} document(s) with no real owner: "
                        + ", ".join(unowned[:3]))
    if stale:
        problems.append(f"{len(stale)} status document(s) with no review date: "
                        + ", ".join(stale[:3]))
    if duplicated:
        problems.append(f"{len(duplicated)} duplicated fact(s): "
                        + "; ".join(duplicated[:3]))

    outside = [d for d in (payload.get("decisions_outside_record") or [])
               if isinstance(d, dict)]
    if outside:
        problems.append("decisions living outside the record: " + ", ".join(
            f"{d.get('decision', '?')} in {d.get('document', '?')}"
            for d in outside[:2]))

    return {
        "ok": not problems,
        "documents": len(documents),
        "by_role": {role: sum(1 for d in documents
                              if str(d.get("role") or "").lower() == role)
                    for role in sorted(ROLES)},
        "unroled": unroled,
        "unowned": unowned,
        "needs_review_date": stale,
        "duplicated_facts": duplicated,
        "decisions_outside_record": len(outside),
        "problems": problems,
        "advice": ("every document has one role, one owner and one source per fact"
                   if not problems else "; ".join(problems[:3])),
    }
