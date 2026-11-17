"""Digest raw build/lint output into an actionable first error.

Payload: ``{"output": "…", "command": "tsc --noEmit"}``

Recognises the common formats (gcc/tsc/mypy/cargo/eslint/go) well enough to sort
by file and code, without pretending to be a parser for all of them.
"""

import re

PATTERNS = (
    re.compile(r"^(?P<file>[^:\s][^:]*):(?P<line>\d+):(?P<col>\d+)?[:\s]+(?P<severity>error|warning)[:\s]+(?P<msg>.+)$"),
    re.compile(r"^(?P<file>[^:\s][^:]*)\((?P<line>\d+),(?P<col>\d+)\)[:\s]+(?P<severity>error|warning)\s*[A-Z]*\d*[:\s]*(?P<msg>.+)$"),
    re.compile(r"^(?P<severity>error|warning)\[(?P<code>[A-Z0-9]+)\][:\s]+(?P<msg>.+)$"),
    re.compile(r"^(?P<file>[^:\s][^:]*):(?P<line>\d+):\s+(?P<severity>error|warning):\s+(?P<msg>.+)$"),
)


def run(payload):
    output = str(payload.get("output") or "")
    command = str(payload.get("command") or "")
    entries = []

    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        for index, pattern in enumerate(PATTERNS):
            match = pattern.match(line)
            if not match:
                continue
            data = match.groupdict()
            entries.append({
                "file": data.get("file"),
                "line": int(data["line"]) if data.get("line") else None,
                "severity": data.get("severity", "error"),
                "code": data.get("code"),
                "message": (data.get("msg") or "").strip(),
                "format": index,
            })
            break

    errors = [e for e in entries if e["severity"] == "error"]
    by_file = {}
    for entry in errors:
        key = entry["file"] or "<no file>"
        by_file[key] = by_file.get(key, 0) + 1
    by_code = {}
    for entry in errors:
        if entry["code"]:
            by_code[entry["code"]] = by_code.get(entry["code"], 0) + 1

    hot = sorted(by_file.items(), key=lambda kv: -kv[1])[:5]
    return {
        "command": command,
        "total_lines": len(output.splitlines()),
        "parsed": len(entries),
        "errors": len(errors),
        "first_error": errors[0] if errors else None,
        "by_file": dict(hot),
        "by_code": by_code,
        "diagnosis": ("no errors parsed: check the output format" if not errors
                      else f"start with {errors[0]['file']}:{errors[0]['line']} — {errors[0]['message'][:90]}"),
        "advice": "fix the first error, re-run the same command, repeat",
    }
