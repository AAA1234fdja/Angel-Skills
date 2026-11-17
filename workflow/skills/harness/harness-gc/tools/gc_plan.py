"""GC plan: what can be removed on evidence, without losing a capability.

Payload::

    {"window_days": 90,
     "candidates": [{"name": "old-lint-hook", "category": "superseded",
                     "evidence": "0 invocations in 90 days; successor lint-v2",
                     "replacement": "lint-v2", "quarantined": true,
                     "last_copy": false,
                     "parts": ["artefact", "registration", "docs", "permission"]},
                    {"name": "legacy-skill", "category": "unused",
                     "evidence": "", "quarantined": false, "last_copy": true,
                     "parts": ["artefact"]}]}

The two refusals that matter: no evidence window (an opinion, not a finding) and
`last_copy` (removal would delete the only route to a capability). A quarantine flag is
required when the evidence is thin, because deletion should be the last step.
"""

CATEGORIES = {"unused", "superseded", "expired", "orphaned", "broken"}
PARTS = {"artefact", "registration", "docs", "permission"}


def run(payload):
    window = payload.get("window_days")
    try:
        window = int(window)
    except (TypeError, ValueError):
        window = 0
    candidates = [c for c in (payload.get("candidates") or []) if isinstance(c, dict)]
    problems, decisions, refused = [], [], []

    if window <= 0:
        problems.append("no evidence window: 'unused' without a window is an opinion")
    if not candidates:
        problems.append("nothing to collect: is this a GC or a ritual?")

    for index, cand in enumerate(candidates):
        name = str(cand.get("name") or f"candidates[{index}]")
        issues = []
        category = str(cand.get("category") or "").strip()
        if category not in CATEGORIES:
            issues.append(f"category '{category or '?'}' is not one of "
                          + "/".join(sorted(CATEGORIES)))
        if not str(cand.get("evidence") or "").strip():
            issues.append("no evidence recorded")
        if cand.get("last_copy") is True:
            issues.append("last copy of the capability: removing it deletes the route")
        elif category == "superseded" and not str(cand.get("replacement") or "").strip():
            issues.append("superseded with no named replacement")
        if str(cand.get("evidence") or "") and cand.get("quarantined") is not True \
                and category == "unused" and window < 60:
            issues.append(f"{window}-day window is thin evidence: quarantine first")
        parts = set(map(str, cand.get("parts") or []))
        missing = PARTS - parts
        if missing:
            issues.append("removal incomplete, would leave: " + ", ".join(sorted(missing)))
        if issues:
            refused.append({"name": name, "issues": issues})
            problems.extend(f"{name}: {issue}" for issue in issues)
        else:
            decisions.append({"name": name, "action": "quarantine"
                              if cand.get("quarantined") else "remove",
                              "category": category})

    return {
        "ok": not problems,
        "window_days": window or None,
        "candidates": len(candidates),
        "removable": decisions,
        "refused": refused,
        "problems": problems,
        "advice": ("every candidate is evidenced, complete and not the last copy"
                   if not problems else "; ".join(problems[:3])),
    }
