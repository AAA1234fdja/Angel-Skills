"""Mechanical review of a unified diff: the findings a human should not spend time on.

Payload: ``{"diff": "…", "max_added_lines": 400}``
Returns findings with severity so the reviewer can start from the real ones.
"""

import re

SECRETS = (
    re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}", re.I),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
)
DEBUG = re.compile(r"^\+.*\b(console\.log|print\(|debugger|pdb\.set_trace|binding\.pry|fmt\.Println)\b")
SWALLOW = re.compile(r"^\+.*(except\s*:|except Exception:\s*$|catch\s*\([^)]*\)\s*\{\s*\}|catch\s*\(\s*\))")
TEST_HINT = re.compile(r"^\+\+\+ b/(.*(test|spec)[^/]*)$", re.I)


def run(payload):
    diff = str(payload.get("diff") or "")
    limit = int(payload.get("max_added_lines", 400))
    findings = []
    added = removed = 0
    files = []
    tests_touched = False
    current = None

    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            current = raw[4:].strip()
            files.append(current)
            if TEST_HINT.match(raw):
                tests_touched = True
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            added += 1
            for pattern in SECRETS:
                if pattern.search(raw):
                    findings.append({"severity": "blocking", "kind": "possible_secret",
                                     "file": current, "line": raw[:120]})
                    break
            if DEBUG.search(raw):
                findings.append({"severity": "important", "kind": "debug_leftover",
                                 "file": current, "line": raw[:120]})
            if SWALLOW.search(raw):
                findings.append({"severity": "blocking", "kind": "swallowed_error",
                                 "file": current, "line": raw[:120]})
            if re.search(r"\bTODO\b(?!\(|:.*#\d+)", raw):
                findings.append({"severity": "minor", "kind": "todo_without_owner",
                                 "file": current, "line": raw[:120]})
        elif raw.startswith("-") and not raw.startswith("---"):
            removed += 1

    source_files = [f for f in files if f and not re.search(r"(test|spec|md$)", f, re.I)]
    if source_files and not tests_touched:
        findings.append({"severity": "important", "kind": "no_test_change",
                         "file": None, "line": "source files changed, no test file in the diff"})
    if added > limit:
        findings.append({"severity": "important", "kind": "diff_too_large",
                         "file": None, "line": f"{added} added lines (limit {limit})"})

    order = {"blocking": 0, "important": 1, "minor": 2}
    findings.sort(key=lambda f: order.get(f["severity"], 3))
    blocking = [f for f in findings if f["severity"] == "blocking"]
    return {
        "ok": not blocking,
        "verdict": "request changes" if blocking else ("approve with minors" if findings else "approve"),
        "files": len(files),
        "added": added,
        "removed": removed,
        "tests_touched": tests_touched,
        "counts": {sev: sum(1 for f in findings if f["severity"] == sev)
                   for sev in ("blocking", "important", "minor")},
        "findings": findings[:80],
        "advice": ("address the blocking findings before requesting review"
                   if blocking else "no blocking finding: request the review"),
    }
