"""Threat coverage: which STRIDE categories did the model actually visit?

Payload::

    {"boundaries": [{"name": "browser->api",
                     "threats": [{"category": "spoofing", "threat": "stolen token",
                                  "score": "high", "decision": "mitigate",
                                  "mechanism": "short-lived tokens"},
                                 {"category": "information disclosure",
                                  "threat": "errors leak ids",
                                  "decision": "accept", "owner": "ana"}]}]}

The tool is deliberately unimpressed by long threat lists: it checks that every
category was visited per boundary, that a scored threat has a decision, that a
mitigation names a mechanism and that an acceptance names a human. Unvisited
categories are reported, because "we did not think about denial of service" is the
finding you want from a model, not from an incident.
"""

STRIDE = ("spoofing", "tampering", "repudiation", "information disclosure",
          "denial of service", "elevation of privilege")
DECISIONS = ("mitigate", "accept", "transfer", "eliminate")
SCORES = ("high", "medium", "low")


def _normalise(category):
    text = str(category or "").strip().lower().replace("_", " ")
    aliases = {"info disclosure": "information disclosure",
               "dos": "denial of service",
               "privilege escalation": "elevation of privilege",
               "eop": "elevation of privilege"}
    return aliases.get(text, text)


def run(payload):
    boundaries = payload.get("boundaries") or []
    problems, rows = [], []
    for index, boundary in enumerate(boundaries):
        if not isinstance(boundary, dict) or not boundary.get("name"):
            problems.append(f"boundaries[{index}]: no name")
            continue
        name = str(boundary["name"])
        seen = set()
        issues = []
        threats = boundary.get("threats") or []
        if not threats:
            issues.append("no threats recorded: an empty boundary is unexamined, not safe")
        for threat in threats:
            if not isinstance(threat, dict):
                issues.append("threat entry is not an object")
                continue
            category = _normalise(threat.get("category"))
            if category not in STRIDE:
                issues.append(f"unknown STRIDE category {threat.get('category')!r}")
                continue
            seen.add(category)
            decision = str(threat.get("decision") or "").lower()
            if decision not in DECISIONS:
                issues.append(f"{category}: no decision (mitigate/accept/transfer/eliminate)")
            elif decision == "mitigate" and not threat.get("mechanism"):
                issues.append(f"{category}: mitigated without naming the mechanism")
            elif decision == "accept" and not threat.get("owner"):
                issues.append(f"{category}: accepted without an owner")
            score = str(threat.get("score") or "").lower()
            if score and score not in SCORES:
                issues.append(f"{category}: score {score!r} is not high/medium/low")
        unvisited = [c for c in STRIDE if c not in seen]
        rows.append({"boundary": name, "threats": len(threats),
                     "visited": sorted(seen), "unvisited": unvisited,
                     "issues": issues})
        problems.extend(f"{name}: {issue}" for issue in issues)
        problems.extend(f"{name}: never considered {c}" for c in unvisited)

    if not boundaries:
        problems.append("no boundaries: a threat model needs at least one trust boundary")
    return {
        "ok": not problems,
        "boundaries": len(rows),
        "rows": rows,
        "stride": list(STRIDE),
        "problems": problems,
        "advice": ("every boundary was walked through all six categories"
                   if not problems else
                   "close the gaps or record them: " + "; ".join(problems[:3])),
    }
