"""Estimate a load plan against a context window.

Payload::

    {"window": 200000,
     "components": [{"name": "system", "chars": 6000, "cap": 0.2},
                    {"name": "skills", "chars": 40000, "cap": 0.3}]}

Characters are converted with a rough 4 chars/token ratio, which is close enough
for budgeting and honest about being an estimate.
"""

CHARS_PER_TOKEN = 4.0


def run(payload):
    window = int(payload.get("window", 200000))
    components = list(payload.get("components") or [])
    if window <= 0:
        return {"ok": False, "error": "window must be positive"}

    rows, over = [], []
    used_tokens = 0
    for component in components:
        name = str(component.get("name") or "?")
        chars = int(component.get("chars") or 0)
        tokens = int(chars / CHARS_PER_TOKEN)
        used_tokens += tokens
        cap = component.get("cap")
        share = tokens / window
        row = {"name": name, "tokens": tokens, "share": round(share, 3)}
        if cap is not None:
            row["cap"] = cap
            row["within_cap"] = share <= float(cap)
            if not row["within_cap"]:
                over.append(name)
        rows.append(row)

    total_share = used_tokens / window
    return {
        "ok": not over and total_share <= 1.0,
        "window": window,
        "components": rows,
        "used_tokens": used_tokens,
        "used_share": round(total_share, 3),
        "over_cap": over,
        "advice": ("plan fits the window" if not over and total_share <= 1.0 else
                   ("over cap: " + ", ".join(over) if over else "plan exceeds the window: load by phase")),
    }
