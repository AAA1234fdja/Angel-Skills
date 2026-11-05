"""Credential and high-entropy scan over supplied text.

Payload:: ``{"files": {"config.py": "…"}, "min_entropy": 3.6}``

Entropy is Shannon over the token; the threshold is deliberately conservative so the
output stays reviewable.
"""

import math
import re

KNOWN = (
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}"), "critical"),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "critical"),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{20,}"), "critical"),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "critical"),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "critical"),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "high"),
    ("generic_assign", re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]([^'\"]{8,})['\"]", re.I), "high"),
    ("conn_string", re.compile(r"[a-z]+://[^:/\s]+:[^@\s]+@", re.I), "high"),
)
PLACEHOLDER = re.compile(r"(example|placeholder|dummy|changeme|your[_-]?|xxx+|test|sample|<[^>]+>)", re.I)


def _entropy(text):
    if not text:
        return 0.0
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    total = len(text)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def run(payload):
    files = payload.get("files") or {}
    min_entropy = float(payload.get("min_entropy", 3.6))
    findings, skipped = [], []

    for path in sorted(files):
        text = files[path]
        if not isinstance(text, str):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if PLACEHOLDER.search(line):
                skipped.append({"file": path, "line": number, "why": "placeholder"})
                continue
            matched = False
            for name, pattern, severity in KNOWN:
                match = pattern.search(line)
                if not match:
                    continue
                value = match.group(match.lastindex or 0)
                findings.append({
                    "file": path, "line": number, "kind": name, "severity": severity,
                    "fingerprint": _fingerprint(value),
                    "rotate": severity == "critical",
                })
                matched = True
                break
            if matched:
                continue
            for token in re.findall(r"[A-Za-z0-9+/=_-]{20,}", line):
                if _entropy(token) >= min_entropy:
                    findings.append({
                        "file": path, "line": number, "kind": "high_entropy",
                        "severity": "medium", "fingerprint": _fingerprint(token),
                        "rotate": False,
                    })
                    break

    critical = [f for f in findings if f["severity"] == "critical"]
    return {
        "ok": not critical,
        "findings": findings[:100],
        "skipped_placeholders": len(skipped),
        "counts": {sev: sum(1 for f in findings if f["severity"] == sev)
                   for sev in ("critical", "high", "medium")},
        "advice": ("no confirmed credential found" if not critical else
                   "rotate now, then clean: " + ", ".join(sorted({f["kind"] for f in critical}))),
    }


def _fingerprint(value):
    if len(value) <= 8:
        return "***"
    return value[:4] + "…" + value[-2:]
