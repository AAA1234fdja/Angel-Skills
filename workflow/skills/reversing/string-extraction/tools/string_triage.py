"""String triage: group extracted strings by what they would prove.

Payload::

    {"artefact": {"path": "bin/agent", "sha256": "9f2c...", "arch": "x86_64"},
     "strings": ["https://api.example.com/v2/upload", "/etc/agent/config.yaml",
                 "AKIAIOSFODNN7EXAMPLE", "BEGIN RSA PRIVATE KEY",
                 "context deadline exceeded"]}

Grouping is the whole job: an ungrouped list is output, not evidence. Credential-
shaped strings are separated from the rest because they are the only group where a
false negative is expensive and a false positive is embarrassing, so each one is
classified rather than reported as a leak.
"""

import re

GROUPS = {
    "endpoint": re.compile(r"^(https?|ftp|wss?|grpc)://\S+$", re.I),
    "path": re.compile(r"^(/|[A-Za-z]:\\|\\\\|~/)", re.I),
    "registry": re.compile(r"^(HKEY_|HKLM|HKCU|SOFTWARE\\)", re.I),
    "email": re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$"),
    "version": re.compile(r"^v?\d+\.\d+(\.\d+)?([-+]\w+)?$"),
    "error": re.compile(r"(error|failed|denied|timeout|refused|invalid|exception)", re.I),
    "sql": re.compile(r"^\s*(select|insert|update|delete|create)\s", re.I),
}
SECRET_MARKERS = ("begin rsa", "begin openssl", "begin ec", "private key",
                  "secret", "password=", "token=", "api_key=", "aws_secret")
AKIA = re.compile(r"^AKIA[0-9A-Z]{12,}$")
NOISE = re.compile(r"^[\W_]+$|^[a-z]{1,3}$|^[\x00-\x1f]+$")


def _classify(text):
    low = text.lower()
    if "private key" in low or any(m in low for m in SECRET_MARKERS):
        return "credential", "high"
    if AKIA.match(text):
        return "credential", "high"
    if len(text) >= 24 and re.fullmatch(r"[A-Za-z0-9+/=_-]{24,}", text):
        return "credential", "medium"
    for name, pattern in GROUPS.items():
        if pattern.search(text):
            return name, "low"
    return "other", "low"


def run(payload):
    artefact = payload.get("artefact") or {}
    raw = payload.get("strings") or []
    problems, buckets = [], {}
    noise = 0
    unclassified = []

    for item in raw:
        text = str(item or "").strip()
        if not text or NOISE.match(text):
            noise += 1
            continue
        group, risk = _classify(text)
        buckets.setdefault(group, []).append({"value": text[:120], "risk": risk})
        if group == "credential" and not payload.get("credential_reviewed"):
            unclassified.append(text[:60])

    for field in ("path", "sha256"):
        if not str(artefact.get(field) or "").strip():
            problems.append(f"artefact.{field} is missing: the finding is not reproducible")
    if not raw:
        problems.append("no strings supplied")
    if unclassified:
        problems.append(f"{len(unclassified)} credential-shaped string(s) not yet "
                        "classified as public id, fixture or secret")

    priority = sorted(buckets, key=lambda g: (g != "credential", -len(buckets[g])))
    return {
        "ok": not problems,
        "artefact": artefact.get("path"),
        "extracted": len(raw),
        "kept": sum(len(v) for v in buckets.values()),
        "noise": noise,
        "groups": {g: len(buckets[g]) for g in priority},
        "priority": priority,
        "samples": {g: [row["value"] for row in buckets[g][:3]] for g in priority},
        "unclassified_credentials": unclassified,
        "problems": problems,
        "advice": ("grouped evidence: classify the credential-shaped hits before "
                   "reporting any of them as a leak" if not problems else
                   "; ".join(problems[:3])),
    }
