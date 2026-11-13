"""Scrape policy: may this collector run, and on what terms?

Payload::

    {"source": "example.com/listings", "official_api": false,
     "api_rejected_because": "no bulk endpoint for listings",
     "terms": {"read": true, "quote": "no automated collection without written consent",
               "allows": false},
     "robots": {"read": true, "disallows_path": true},
     "data_class": "personal", "legal_basis": "", "retention_days": 0,
     "rate_per_second": 0, "user_agent": "",
     "evasion": ["rotating proxies"], "provenance_recorded": true,
     "takedown": {"command": "kubectl scale deploy scraper --replicas=0",
                  "owner": "ana"}}

The tool is deliberately blunt about three things: a terms quote that says no is a
refusal regardless of what is technically possible; a disallowed robots path is the
same; and evasion of a block converts a policy question into an incident.
"""


def run(payload):
    terms = payload.get("terms") or {}
    robots = payload.get("robots") or {}
    takedown = payload.get("takedown") or {}
    problems = []

    if not str(payload.get("source") or "").strip():
        problems.append("no source named")
    if terms.get("read") is not True:
        problems.append("terms never read: 'no explicit prohibition' is not permission")
    elif terms.get("allows") is False:
        problems.append(f"terms refuse automated collection: \"{terms.get('quote', '')[:80]}\"")
    if robots.get("read") is not True:
        problems.append("robots.txt never read")
    elif robots.get("disallows_path") is True:
        problems.append("robots.txt disallows this path")

    if payload.get("official_api") is not True and not str(
            payload.get("api_rejected_because") or "").strip():
        problems.append("official interface not considered: say why it was rejected")

    data_class = str(payload.get("data_class") or "").strip().lower()
    if data_class not in ("public", "personal", "special"):
        problems.append(f"data class '{data_class or '?'}' is not public/personal/special")
    if data_class in ("personal", "special"):
        if not str(payload.get("legal_basis") or "").strip():
            problems.append("personal data with no legal basis")
        days = payload.get("retention_days")
        if not isinstance(days, int) or days <= 0:
            problems.append("personal data with no retention period: it cannot be "
                            "retrofitted once collected")

    rate = payload.get("rate_per_second")
    if not isinstance(rate, (int, float)) or rate <= 0:
        problems.append("no rate budget: load on someone else's system is the harm "
                        "that gets noticed first")
    if not str(payload.get("user_agent") or "").strip():
        problems.append("no descriptive user agent with contact: the operator cannot "
                        "reach you")

    evasion = [str(e) for e in (payload.get("evasion") or [])]
    if evasion:
        problems.append("evasion of a control: " + ", ".join(evasion[:3])
                        + " — a block is an answer, not an obstacle")
    if payload.get("provenance_recorded") is not True:
        problems.append("no provenance per record: a later question about one row has "
                        "no answer")
    if not str(takedown.get("command") or "").strip():
        problems.append("no takedown command: stopping it under pressure must be one "
                        "command")
    if not str(takedown.get("owner") or "").strip():
        problems.append("takedown has no owner")

    return {
        "ok": not problems,
        "source": payload.get("source"),
        "data_class": data_class or None,
        "rate_per_second": rate if isinstance(rate, (int, float)) else None,
        "decision": "collect" if not problems else "do not collect",
        "problems": problems,
        "advice": ("collect at a stated rate, with provenance and a one-command "
                   "takedown" if not problems else "; ".join(problems[:3])),
    }
