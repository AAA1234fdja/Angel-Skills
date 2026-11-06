"""Profile check: distinct modes, one copy of each rule, explicit handovers.

Payload::

    {"shared_rules": ["never force-push", "no secrets in prompts"],
     "profiles": [{"name": "build", "decision": "how to implement",
                   "rules": ["never force-push", "tdd first"],
                   "tools": ["edit", "run-tests"], "context_budget": 8000,
                   "handover": "diff + evidence to review", "switch_rule": "human"},
                  {"name": "review", "decision": "how to implement",
                   "rules": ["never force-push", "tdd first"],
                   "tools": ["read", "diff"], "context_budget": 6000,
                   "handover": "", "switch_rule": ""}]}

Two failures are structural rather than stylistic: a rule duplicated across profiles
(it will diverge) and two profiles owning the same decision (the switch becomes
arbitrary). Both are cheap to see in a set and invisible one file at a time.
"""


def _norm(rule):
    return " ".join(str(rule).lower().split())


def run(payload):
    shared = {_norm(r) for r in (payload.get("shared_rules") or [])}
    profiles = [p for p in (payload.get("profiles") or []) if isinstance(p, dict)]
    problems, duplicated, decisions = [], [], {}

    if not profiles:
        problems.append("no profiles: a single always-on prompt is not a profile set")

    for index, profile in enumerate(profiles):
        name = str(profile.get("name") or f"profiles[{index}]")
        decision = str(profile.get("decision") or "").strip().lower()
        if not decision:
            problems.append(f"{name}: no decision it owns, so it is a persona")
        else:
            if decision in decisions:
                problems.append(f"{name}: same decision as '{decisions[decision]}' — the "
                                "switch between them is arbitrary")
            decisions.setdefault(decision, name)
        own = [_norm(r) for r in (profile.get("rules") or [])]
        for rule in own:
            if rule in shared:
                duplicated.append(f"{name}: '{rule}' is a shared rule and was copied")
        if len(set(own)) != len(own):
            problems.append(f"{name}: lists the same rule twice")
        if not profile.get("tools"):
            problems.append(f"{name}: no tools declared, so its action space is unclear")
        budget = profile.get("context_budget")
        if not isinstance(budget, int) or budget <= 0:
            problems.append(f"{name}: unbounded context — a profile that loads "
                            "everything is an always-on prompt with a new name")
        if not str(profile.get("handover") or "").strip():
            problems.append(f"{name}: no handover to the next mode")
        if not str(profile.get("switch_rule") or "").strip():
            problems.append(f"{name}: no switching rule, and in-flight work is undefined")

    if duplicated:
        problems.append(f"{len(duplicated)} copied shared rule(s): "
                        + "; ".join(duplicated[:3]))

    return {
        "ok": not problems,
        "profiles": len(profiles),
        "shared_rules": len(shared),
        "decisions": sorted(decisions),
        "duplicated_rules": duplicated,
        "problems": problems,
        "advice": ("each mode owns a distinct decision, rules are shared once and "
                   "handovers are explicit" if not problems else "; ".join(problems[:3])),
    }
