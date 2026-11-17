"""Alert audit: would a tired person be able to act on these alerts?

Payload::

    {"alerts": [{"name": "checkout failure rate", "symptom": "users cannot pay",
                 "signal": "error_rate", "threshold": 0.02, "window": "5m",
                 "reason": "2% of checkouts is 40 lost orders a day",
                 "runbook": "open the payments dashboard, check provider status",
                 "resolves": true, "owner": "payments"}],
     "incidents_last_90d": 12, "pages_last_90d": 96}

The ratio matters as much as the fields: an alerting system that pages eight times
per incident trains people to ignore it, which is worse than no alert because the
silence looks like safety.
"""

REQUIRED_FIELDS = ("name", "symptom", "threshold", "window", "runbook")


def run(payload):
    alerts = payload.get("alerts") or []
    pages = payload.get("pages_last_90d")
    incidents = payload.get("incidents_last_90d")
    problems, rows = [], []

    for index, alert in enumerate(alerts):
        if not isinstance(alert, dict) or not alert.get("name"):
            problems.append(f"alerts[{index}]: no name")
            continue
        name = str(alert["name"])
        issues = []
        for field in REQUIRED_FIELDS:
            if alert.get(field) in (None, "", []):
                issues.append(f"missing {field}")
        if not alert.get("reason"):
            issues.append("threshold with no stated reason: it will drift")
        if not alert.get("symptom") and alert.get("signal"):
            issues.append("signals a cause but no symptom: keep it as a dashboard")
        if alert.get("resolves") is False:
            issues.append("does not auto-resolve: responders learn to ignore stale pages")
        if not alert.get("owner"):
            issues.append("no owner")
        if alert.get("silenced_until") and not alert.get("silence_reason"):
            issues.append("silenced with no reason: a silence without a date is a deletion")
        rows.append({"alert": name, "issues": issues})
        problems.extend(f"{name}: {issue}" for issue in issues)

    ratio = None
    if isinstance(pages, (int, float)) and isinstance(incidents, (int, float)) and incidents:
        ratio = round(float(pages) / float(incidents), 2)
        if ratio > 4:
            problems.append(f"{ratio} pages per incident: the rotation is being trained "
                            "to ignore alerts")

    if not alerts:
        problems.append("no alerts to audit")
    return {
        "ok": not problems,
        "alerts": len(rows),
        "rows": rows,
        "pages_per_incident": ratio,
        "problems": problems,
        "advice": ("each alert names a symptom, a reason and a first action"
                   if not problems else "; ".join(problems[:3])),
    }
