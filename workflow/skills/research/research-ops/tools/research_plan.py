"""Research plan: is this an operation with a stop condition?

Payload::

    {"question": "is Postgres 17 supported on our host",
     "decision": "which database version the 2027 migration targets",
     "evidence_bar": {"yes": "host docs list 17 GA", "no": "host docs cap at 16",
                      "unknown": "docs silent or older than 6 months"},
     "phases": [{"name": "primary docs", "minutes": 20, "spent": 25,
                 "sources": ["host docs"]},
                {"name": "communities", "minutes": 15, "spent": 10, "sources": []}],
     "findings": [{"claim": "17 is GA", "confidence": "high"},
                  {"claim": "extensions work", "confidence": ""}],
     "gaps": ["did not read the 17.1 release notes"]}

The two controls that matter are the evidence bar (fixed before searching) and the
confidence per finding. Without them, research ends when the researcher is tired,
which is not a stop condition anybody can plan around.
"""

CONFIDENCE = {"high", "medium", "low"}


def run(payload):
    phases = [p for p in (payload.get("phases") or []) if isinstance(p, dict)]
    findings = [f for f in (payload.get("findings") or []) if isinstance(f, dict)]
    bar = payload.get("evidence_bar") or {}
    problems, unlevelled, overruns = [], [], []

    if not str(payload.get("question") or "").strip():
        problems.append("no question")
    if not str(payload.get("decision") or "").strip():
        problems.append("no decision attached: nobody will read the answer")
    for key in ("yes", "no", "unknown"):
        if not str(bar.get(key) or "").strip():
            problems.append(f"evidence_bar.{key} is not defined, so the search has no "
                            "stop condition")
    if not phases:
        problems.append("no search phases planned")

    for index, phase in enumerate(phases):
        name = str(phase.get("name") or f"phases[{index}]")
        budget = phase.get("minutes")
        spent = phase.get("spent")
        if not isinstance(budget, int) or budget <= 0:
            problems.append(f"{name}: no time box, so the phase expands to fill the day")
        elif isinstance(spent, int) and spent > budget:
            overruns.append(f"{name} ({spent} > {budget}m)")

    for index, finding in enumerate(findings):
        claim = str(finding.get("claim") or f"findings[{index}]")
        level = str(finding.get("confidence") or "").strip().lower()
        if level not in CONFIDENCE:
            unlevelled.append(claim[:50])

    if unlevelled:
        problems.append(f"{len(unlevelled)} finding(s) without confidence: "
                        + "; ".join(unlevelled[:3]))
    if not findings:
        problems.append("no findings: the research has no output")
    if not (payload.get("gaps") or []):
        problems.append("no gaps listed: implicit gaps read as coverage")
    if str(payload.get("change_trigger") or "").strip() == "":
        problems.append("no 'what would change this': the answer has no shelf life")

    return {
        "ok": not problems,
        "question": payload.get("question"),
        "phases": len(phases),
        "findings": len(findings),
        "high_confidence": sum(1 for f in findings
                               if str(f.get("confidence") or "").lower() == "high"),
        "overruns": overruns,
        "gaps": len(payload.get("gaps") or []),
        "problems": problems,
        "advice": ("the search had a bar, met it, and says what would change the "
                   "answer" if not problems else "; ".join(problems[:3])),
    }
