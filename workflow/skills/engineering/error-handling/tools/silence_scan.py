"""Find swallowed failures in supplied source text.

Payload: ``{"files": {"a.py": "…"}, "max_findings": 100}``
Language-agnostic heuristics over a few common languages; the output is a list of
places to look, not a verdict.
"""

import re

EMPTY_HANDLERS = (
    re.compile(r"except[^:]*:\s*(\n\s*(pass|continue|\.\.\.)\s*)?$"),
    re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}"),
    re.compile(r"catch\s*([A-Za-z_$][\w$]*)\s*\{\s*\}"),
)
LOG_ONLY = re.compile(r"catch|except")
FALLBACK = re.compile(r"(return\s+(None|null|\[\]|\{\}|false|0)\s*;?\s*$|\?:\s*(null|undefined))")


def run(payload):
    files = payload.get("files") or {}
    limit = int(payload.get("max_findings", 100))
    findings = []

    for path in sorted(files):
        text = files[path]
        if not isinstance(text, str):
            continue
        lines = text.splitlines()
        for index, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            for pattern in EMPTY_HANDLERS:
                window = chr(10).join(lines[index - 1:index + 1])
                if pattern.search(stripped) or pattern.search(window):
                    findings.append({"file": path, "line": index, "kind": "empty_handler",
                                     "detail": stripped[:110]})
                    break
            if LOG_ONLY.search(stripped) and re.search(r"(log|print|warn|console)", stripped):
                findings.append({"file": path, "line": index, "kind": "log_then_continue",
                                 "detail": stripped[:110]})
            if FALLBACK.search(stripped) and index > 1 and LOG_ONLY.search(lines[index - 2]):
                findings.append({"file": path, "line": index, "kind": "silent_fallback",
                                 "detail": stripped[:110]})

    counts = {}
    for finding in findings:
        counts[finding["kind"]] = counts.get(finding["kind"], 0) + 1
    return {
        "ok": not any(k in counts for k in ("empty_handler", "silent_fallback")),
        "findings": findings[:limit],
        "counts": counts,
        "advice": ("no swallowed failures found" if not findings else
                   "fix empty_handler first: those hide outages"),
    }
