"""Classify unused-symbol candidates from supplied evidence.

Payload::

    {"symbols": [{"name": "old_helper", "file": "src/a.py",
                  "references": 0, "exported": false, "in_tests": 0,
                  "dynamic": false}]}

The tool does not search: reference counts are supplied, so the decision is
reproducible and reviewable. Searching happens in the procedure.
"""


def run(payload):
    symbols = list(payload.get("symbols") or [])
    rows, safe, review, keep = [], [], [], []

    for symbol in symbols:
        name = str(symbol.get("name") or "")
        refs = int(symbol.get("references") or 0)
        in_tests = int(symbol.get("in_tests") or 0)
        exported = bool(symbol.get("exported"))
        dynamic = bool(symbol.get("dynamic"))
        generated = bool(symbol.get("generated"))

        if generated:
            decision, why = "keep", "generated code"
        elif dynamic:
            decision, why = "review", "possibly reached dynamically"
        elif exported:
            decision, why = "review", "public API: consumers may be external"
        elif refs == 0 and in_tests == 0:
            decision, why = "safe", "no references anywhere"
        elif refs == 0 and in_tests > 0:
            decision, why = "review", f"{in_tests} test reference(s): stale test or real use"
        else:
            decision, why = "keep", f"{refs} reference(s)"

        rows.append({"symbol": name, "file": symbol.get("file"), "decision": decision,
                     "why": why})
        {"safe": safe, "review": review, "keep": keep}[decision].append(name)

    return {
        "ok": True,
        "rows": rows,
        "safe": safe,
        "review": review,
        "keep": keep,
        "plan": [f"delete {n} in its own commit" for n in safe] or ["nothing is safely removable"],
        "advice": ("start with 'safe', one commit each, suite green after every step"
                   if safe else "review the 'review' bucket before deleting anything"),
    }
