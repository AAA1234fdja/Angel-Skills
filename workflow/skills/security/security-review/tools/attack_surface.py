"""High-signal vulnerability patterns in a diff, with reachability hints.

Payload:: ``{"diff": "<unified diff>"}``

Every finding is a *lead*, not a verdict: severity is capped until the path is
verified by a human (see the skill's step 4).
"""

import re

RULES = (
    ("sql_injection", re.compile(r"(execute|query|raw)\s*\(.*(\+|\$\{|%s|f\")", re.I),
     "critical", "string-built SQL: use parameters"),
    ("shell_injection", re.compile(r"(os\.system|subprocess\.[a-z]+\(.*shell\s*=\s*True|exec\(|eval\()", re.I),
     "critical", "command built from data: use an argv list"),
    ("path_traversal", re.compile(r"(open|readFile|read_text)\(\s*[^)]*(request|input|param|query)", re.I),
     "high", "path from input: normalise and confine to a root"),
    ("missing_authz", re.compile(r"@(app|router)\.(route|get|post|put|delete)", re.I),
     "medium", "new endpoint: confirm the authorisation check"),
    ("secret_in_code", re.compile(r"(api[_-]?key|secret|token)\s*=\s*['\"][^'\"]{12,}", re.I),
     "critical", "literal credential: rotate and move to env"),
    ("unsafe_yaml", re.compile(r"yaml\.load\((?![^)]*Loader\s*=\s*yaml\.SafeLoader)", re.I),
     "high", "unsafe deserialisation: SafeLoader"),
    ("debug_on", re.compile(r"(DEBUG\s*=\s*True|debug=True)", re.I),
     "medium", "debug mode in a diff: verify the environment"),
    ("tls_off", re.compile(r"(verify\s*=\s*False|rejectUnauthorized:\s*false|insecure\s*=\s*True)", re.I),
     "high", "TLS verification disabled"),
)


def run(payload):
    diff = str(payload.get("diff") or "")
    findings = []
    added = 0
    current = None
    touches_input = False

    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[4:].strip()
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added += 1
        low = line.lower()
        if any(word in low for word in ("request", "req.", "params", "query", "body", "input")):
            touches_input = True
        for name, pattern, severity, fix in RULES:
            if pattern.search(line):
                findings.append({"pattern": name, "severity": severity,
                                 "file": current, "line": line[1:150].strip(), "fix": fix})

    if not touches_input:
        for finding in findings:
            if finding["severity"] in ("critical", "high"):
                finding["reachable"] = "unverified: no input handling in this diff"

    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: order.get(f["severity"], 9))
    blocking = [f for f in findings if f["severity"] in ("critical", "high")]
    return {
        "ok": not blocking,
        "added_lines": added,
        "findings": findings[:60],
        "counts": {sev: sum(1 for f in findings if f["severity"] == sev)
                   for sev in ("critical", "high", "medium", "low")},
        "input_in_diff": touches_input,
        "advice": ("no high-severity pattern found" if not blocking else
                   "verify reachability, then patch: " + ", ".join(sorted({f["pattern"] for f in blocking}))),
    }
