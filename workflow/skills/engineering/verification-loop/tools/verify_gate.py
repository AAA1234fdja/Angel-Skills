"""Verification gate: decide whether a change may be closed.

Payload::

    {"phases": {"build": {"status": "pass", "command": "npm run build", "output": "ok"},
                "tests": {"status": "fail", "command": "npm test"}},
     "allow_skips": ["security"]}

A phase is evidence-bearing only if it has a command and a status. Silence is
not a pass: a missing phase blocks the gate.
"""

PHASES = ("build", "types", "lint", "tests", "security", "diff")
STATUSES = ("pass", "fail", "skip")


def run(payload):
    phases = dict(payload.get("phases") or {})
    allow_skips = set(payload.get("allow_skips") or [])
    rows, blocking, advised = [], [], []

    for name in PHASES:
        entry = phases.get(name)
        if entry is None:
            rows.append({"phase": name, "status": "missing", "why": "phase did not run"})
            blocking.append(name)
            continue
        status = str(entry.get("status") or "").lower()
        command = entry.get("command")
        output = entry.get("output")
        if status not in STATUSES:
            rows.append({"phase": name, "status": "invalid", "why": "status must be pass|fail|skip"})
            blocking.append(name)
            continue
        evidence = bool(command) or bool(output)
        row = {"phase": name, "status": status, "command": command, "evidence": evidence}
        rows.append(row)
        if status == "fail":
            blocking.append(name)
        elif status == "skip":
            if name in allow_skips:
                advised.append({"phase": name, "why": "skipped but allowed by policy"})
            else:
                blocking.append(name)
        elif not evidence:
            blocking.append(name)
            row["why"] = "no command and no output: nothing to quote"

    extra = [name for name in phases if name not in PHASES]
    return {
        "ok": not blocking,
        "blocking": sorted(set(blocking)),
        "rows": rows,
        "advised": advised,
        "unknown_phases": extra,
        "verdict": "may close" if not blocking else "do not close",
        "next": ("quote the six results in the final message" if not blocking
                 else "fix and re-run: " + ", ".join(sorted(set(blocking)))),
        "advice": ("closing is allowed: every phase reported its own result"
                   if not blocking else
                   "do not close: " + ", ".join(sorted(set(blocking)))),
    }
