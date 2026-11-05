"""Lint changelog entries for actionability.

Payload::

    {"entries": [{"version": "0.3.0", "type": "breaking",
                  "text": "skills moved to folders", "action": "re-run workflow validate"}]}
"""

VAGUE = ("various", "misc", "improvements", "cleanup", "minor fixes", "stuff",
         "update things", "refactor")
TYPES = ("breaking", "deprecated", "added", "changed", "fixed", "security", "removed")


def run(payload):
    entries = list(payload.get("entries") or [])
    problems, rows = [], []

    for entry in entries:
        version = str(entry.get("version") or "")
        kind = str(entry.get("type") or "").lower()
        text = str(entry.get("text") or "").strip()
        action = str(entry.get("action") or "").strip()
        issues = []

        if not version:
            issues.append("no version")
        if kind not in TYPES:
            issues.append(f"type {kind!r} not in {', '.join(TYPES)}")
        if not text:
            issues.append("empty entry")
        if any(word in text.lower() for word in VAGUE):
            issues.append("vague wording: state the observable change")
        if kind == "breaking" and not action:
            issues.append("breaking change without a required action")
        if kind == "security" and not action:
            issues.append("security fix without guidance")

        rows.append({"version": version, "type": kind, "issues": issues})
        problems.extend(f"{version or '?'}: {issue}" for issue in issues)

    return {
        "ok": not problems,
        "entries": len(entries),
        "rows": rows,
        "problems": problems,
        "advice": ("entries are actionable" if not problems else
                   "rewrite for the consumer: what changes for them"),
    }
