"""Pairwise overlap between skills.

Payload::

    {"skills": [{"id": "a", "triggers": ["fix build"], "keywords": ["build"],
                 "verbs": ["fix"], "phase": "verify"}],
     "threshold": 0.5}
"""


def _jaccard(left, right):
    a = {str(x).lower() for x in left if x}
    b = {str(x).lower() for x in right if x}
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def run(payload):
    skills = list(payload.get("skills") or [])
    threshold = float(payload.get("threshold", 0.5))
    pairs, overlapping = [], []

    for i, left in enumerate(skills):
        for right in skills[i + 1:]:
            trigger = _jaccard(left.get("triggers") or [], right.get("triggers") or [])
            keyword = _jaccard(left.get("keywords") or [], right.get("keywords") or [])
            verb = _jaccard(left.get("verbs") or [], right.get("verbs") or [])
            score = round(0.5 * trigger + 0.4 * keyword + 0.1 * verb, 3)
            same_phase = left.get("phase") == right.get("phase")
            row = {
                "a": left.get("id"), "b": right.get("id"),
                "score": score, "same_phase": same_phase,
                "trigger_overlap": round(trigger, 3),
                "keyword_overlap": round(keyword, 3),
            }
            pairs.append(row)
            if score >= threshold:
                overlapping.append(row)

    pairs.sort(key=lambda p: -p["score"])
    decisions = []
    for pair in overlapping:
        if pair["trigger_overlap"] >= 0.6:
            decisions.append(f"merge {pair['a']} into {pair['b']}: same trigger")
        elif pair["same_phase"]:
            decisions.append(f"differentiate {pair['a']} and {pair['b']}: same phase, shared keywords")
        else:
            decisions.append(f"keep {pair['a']} and {pair['b']}: different phases, review wording")

    return {
        "ok": not overlapping,
        "pairs": pairs[:40],
        "overlapping": overlapping,
        "decisions": decisions,
        "advice": ("no pair above threshold" if not overlapping else
                   "decide on each pair before the next release"),
    }
