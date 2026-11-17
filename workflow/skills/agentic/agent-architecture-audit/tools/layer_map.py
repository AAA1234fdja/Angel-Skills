"""Map symptoms to likely layers, with the check that would confirm it.

Payload:: ``{"symptoms": ["ignores instructions", "repeats the same tool call"]}``
"""

RULES = (
    ("wrapper regression", ("ignores instructions", "different system prompt", "acts like another"),
     "layer 2", "diff the effective system prompt against the intended one"),
    ("memory contamination", ("forgets", "old context", "mentions previous", "contradicts"),
     "layer 5", "dump retrieved context and check relevance and recency"),
    ("tool discipline failure", ("wrong tool", "repeats the same tool", "never calls"),
     "layer 3", "list tools available in that turn and their descriptions"),
    ("transport corruption", ("truncated", "broken json", "invalid markdown", "cut off"),
     "layer 6", "compare the model output bytes with what the consumer received"),
    ("hidden layer", ("works locally", "only fails in production", "sometimes"),
     "6", "trace the network path: proxy, template, cache, gateway"),
    ("input validation", ("empty input", "huge input", "weird characters"),
     "layer 1", "log the raw input and the validation result"),
)


def run(payload):
    symptoms = [str(s).lower() for s in payload.get("symptoms") or []]
    matches = []
    for name, needles, layer, check in RULES:
        hits = [s for s in symptoms if any(n in s for n in needles)]
        if hits:
            matches.append({"pattern": name, "layer": layer, "matched": hits, "check": check})
    matches.sort(key=lambda m: -len(m["matched"]))
    return {
        "ok": bool(matches),
        "matches": matches,
        "first_check": matches[0]["check"] if matches else "collect a full trace before diagnosing",
        "advice": ("start with the top match; eliminate it with the check before moving on"
                   if matches else "symptoms do not map: get the trace"),
    }
