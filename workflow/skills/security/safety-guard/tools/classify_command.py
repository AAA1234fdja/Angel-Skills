"""Classify a shell command by risk and state the required confirmation.

Payload:: ``{"command": "git push --force origin main", "profile": "standard"}``
"""

import re

RULES = (
    ("destructive", re.compile(r"\brm\s+(-[a-z]*[rf][a-z]*\s+)+(/|~|\$HOME|\*)", re.I),
     "deletes a broad path"),
    ("destructive", re.compile(r"git\s+push[^\n]*(--force|-f\b)", re.I), "rewrites remote history"),
    ("destructive", re.compile(r"git\s+(reset\s+--hard|clean\s+-[a-z]*f)", re.I), "discards local work"),
    ("destructive", re.compile(r"(drop\s+(table|database|schema)|truncate\s+table)", re.I), "drops data"),
    ("destructive", re.compile(r"(chmod\s+-R\s+777|chown\s+-R)", re.I), "changes permissions recursively"),
    ("destructive", re.compile(r"(kubectl\s+delete|terraform\s+(destroy|apply))", re.I), "changes infrastructure"),
    ("execute", re.compile(r"(curl|wget)[^\n]*\|\s*(sh|bash)", re.I), "pipes remote content into a shell"),
    ("execute", re.compile(r"(npm\s+publish|docker\s+push|cargo\s+publish)", re.I), "publishes artefacts"),
    ("execute", re.compile(r"\b(sudo|doas)\b", re.I), "escalates privileges"),
    ("write", re.compile(r"(>\s*[^\s|&]+|sed\s+-i|tee\s)", re.I), "writes files"),
    ("read", re.compile(r"\b(ls|cat|grep|rg|git\s+(status|log|diff)|find)\b", re.I), "reads only"),
)

ALLOWED = {"observe": {"read"}, "standard": {"read", "write", "execute"},
           "full": {"read", "write", "execute", "destructive"}}


def run(payload):
    command = str(payload.get("command") or "")
    profile = str(payload.get("profile") or "standard")
    if not command.strip():
        return {"ok": False, "error": "empty command"}

    hits = []
    for level, pattern, why in RULES:
        if pattern.search(command):
            hits.append({"risk": level, "why": why})
    order = {"read": 0, "write": 1, "execute": 2, "destructive": 3}
    risk = max((h["risk"] for h in hits), key=lambda r: order[r], default="read")
    allowed = ALLOWED.get(profile, {"read"})

    return {
        "ok": risk in allowed,
        "command": command[:200],
        "risk": risk,
        "reasons": hits,
        "profile": profile,
        "allowed": risk in allowed,
        "confirmation": ("none" if risk in ("read", "write") else
                         "explicit flag --allow-destructive plus a dry-run" if risk == "destructive"
                         else "inform the operator what will run"),
        "advice": ("allowed under this profile" if risk in allowed else
                   f"refused: needs risk '{risk}'; raise the profile deliberately"),
    }
