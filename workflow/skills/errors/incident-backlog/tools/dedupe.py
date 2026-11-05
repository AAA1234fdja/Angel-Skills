"""Cluster failure reports by signature and rank them.

Payload::

    {"reports": [{"code": "E_TOOL_TIMEOUT", "operation": "fetch", "component": "zev",
                  "seen": 12, "severity": "high"}],
     "similarity": 0.8}
"""

SEVERITY_WEIGHT = {"low": 1, "medium": 3, "high": 8, "critical": 20}


def _signature(report):
    code = str(report.get("code") or "E_UNKNOWN")
    operation = str(report.get("operation") or "?").strip().lower()
    component = str(report.get("component") or "?").strip().lower()
    return f"{code}|{operation}|{component}"


def run(payload):
    reports = list(payload.get("reports") or [])
    clusters = {}

    for report in reports:
        sig = _signature(report)
        bucket = clusters.setdefault(sig, {
            "signature": sig,
            "code": report.get("code"),
            "operation": report.get("operation"),
            "component": report.get("component"),
            "seen": 0,
            "severity": "low",
            "owners": set(),
        })
        bucket["seen"] += int(report.get("seen") or 1)
        sev = str(report.get("severity") or "low")
        if SEVERITY_WEIGHT.get(sev, 0) > SEVERITY_WEIGHT.get(bucket["severity"], 0):
            bucket["severity"] = sev
        if report.get("owner"):
            bucket["owners"].add(str(report["owner"]))

    rows = []
    for bucket in clusters.values():
        score = bucket["seen"] * SEVERITY_WEIGHT.get(bucket["severity"], 1)
        rows.append({
            "signature": bucket["signature"],
            "severity": bucket["severity"],
            "seen": bucket["seen"],
            "score": score,
            "owners": sorted(bucket["owners"]),
            "needs_owner": not bucket["owners"],
        })
    rows.sort(key=lambda r: -r["score"])

    return {
        "ok": True,
        "reports": len(reports),
        "clusters": len(rows),
        "duplicate_ratio": round(1 - (len(rows) / len(reports)), 3) if reports else 0.0,
        "ranked": rows,
        "unowned": [r["signature"] for r in rows if r["needs_owner"]],
        "advice": ("one owner per cluster before planning" if any(r["needs_owner"] for r in rows)
                   else "backlog is owned and ranked"),
    }
