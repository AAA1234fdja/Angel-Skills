"""Validate an error-policy table and render it as documentation.

Payload:: ``{"policy": {"E_X": {"severity": "error", "retryable": false,
                                "owner": "author", "exit": 2, "hint": "…"}}}``
"""

SEVERITIES = ("info", "warn", "error", "fatal")
OWNERS = ("user", "author", "caller", "runtime", "producer", "tool")


def run(payload):
    policy = payload.get("policy") or {}
    problems = []
    seen_exit = {}
    rows = []

    for code in sorted(policy):
        entry = policy[code] or {}
        severity = str(entry.get("severity") or "")
        owner = str(entry.get("owner") or "")
        exit_code = entry.get("exit")
        retryable = entry.get("retryable")

        if not code.startswith("E_"):
            problems.append(f"{code}: code should be prefixed with E_")
        if severity not in SEVERITIES:
            problems.append(f"{code}: invalid severity {severity!r}")
        if owner not in OWNERS:
            problems.append(f"{code}: invalid owner {owner!r}")
        if not isinstance(exit_code, int):
            problems.append(f"{code}: exit code must be an integer")
        if not isinstance(retryable, bool):
            problems.append(f"{code}: retryable must be a boolean")
        if not str(entry.get("hint") or "").strip():
            problems.append(f"{code}: missing remediation hint")
        if severity == "fatal" and retryable is True:
            problems.append(f"{code}: fatal cannot be retryable")
        if isinstance(exit_code, int):
            if exit_code in seen_exit and severity != "info":
                problems.append(
                    f"{code}: exit code {exit_code} already used by {seen_exit[exit_code]}")
            seen_exit.setdefault(exit_code, code)

        rows.append({
            "code": code, "severity": severity, "owner": owner,
            "retryable": retryable, "exit": exit_code,
        })

    counts = {sev: sum(1 for r in rows if r["severity"] == sev) for sev in SEVERITIES}
    table = ["| Code | Severity | Owner | Retry | Exit |", "|---|---|---|---|---|"]
    for row in rows:
        table.append(f"| `{row['code']}` | {row['severity']} | {row['owner']} | "
                     f"{'yes' if row['retryable'] else 'no'} | {row['exit']} |")

    return {
        "ok": not problems,
        "codes": len(policy),
        "by_severity": counts,
        "problems": problems,
        "markdown": "\n".join(table),
        "advice": ("table is consistent" if not problems else
                   f"{len(problems)} problem(s): fix before publishing"),
    }
