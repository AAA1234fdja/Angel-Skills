"""Score a harness description on four axes.

Payload::

    {"tools": [{"id": "read", "input_schema": true, "returns": ["status","summary"]}],
     "system_prompt_chars": 8000, "max_prompt_chars": 6000,
     "has_recovery_contract": true}
"""


def run(payload):
    tools = list(payload.get("tools") or [])
    prompt_chars = int(payload.get("system_prompt_chars", 0))
    max_prompt = int(payload.get("max_prompt_chars", 6000))
    has_recovery = bool(payload.get("has_recovery_contract"))

    findings, scores = [], {}

    # action space
    ids = [str(t.get("id") or "") for t in tools]
    duplicates = len(ids) - len(set(ids))
    schema_ok = sum(1 for t in tools if t.get("input_schema"))
    action = 1.0
    if not tools:
        action = 0.0
        findings.append({"axis": "action", "issue": "no tools declared"})
    else:
        action = schema_ok / len(tools)
        if duplicates:
            action = max(0.0, action - 0.2)
            findings.append({"axis": "action", "issue": f"{duplicates} duplicate tool id(s)"})
        if any(str(t.get("id", "")).endswith("all") or "everything" in str(t.get("id", ""))
               for t in tools):
            action = max(0.0, action - 0.2)
            findings.append({"axis": "action", "issue": "catch-all tool present"})

    # observation
    required = {"status", "summary", "next_actions", "artifacts"}
    observation = 1.0
    if tools:
        covered = sum(1 for t in tools if required.issubset(set(t.get("returns") or [])))
        observation = covered / len(tools)
        if covered < len(tools):
            findings.append({"axis": "observation",
                             "issue": f"{len(tools) - covered} tool(s) without the four fields"})

    # recovery
    recovery = 1.0 if has_recovery else 0.0
    if not has_recovery:
        findings.append({"axis": "recovery", "issue": "no recovery contract declared"})

    # context
    if max_prompt <= 0:
        context = 0.0
    else:
        context = 1.0 if prompt_chars <= max_prompt else max(0.0, 1 - (prompt_chars - max_prompt) / max_prompt)
    if prompt_chars > max_prompt:
        findings.append({"axis": "context",
                         "issue": f"system prompt {prompt_chars} chars > budget {max_prompt}"})

    scores = {"action": round(action, 2), "observation": round(observation, 2),
              "recovery": round(recovery, 2), "context": round(context, 2)}
    overall = round(sum(scores.values()) / 4, 2)
    return {
        "ok": overall >= 0.75,
        "scores": scores,
        "overall": overall,
        "findings": findings,
        "advice": ("harness is in good shape" if overall >= 0.75 else
                   "fix the lowest axis first: " + min(scores, key=scores.get)),
    }
