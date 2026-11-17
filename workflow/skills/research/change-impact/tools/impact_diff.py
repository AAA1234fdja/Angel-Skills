"""Impact diff: was the blast radius understood, or discovered?

Payload::

    {"surface": "POST /v1/refunds: `amount` becomes integer cents",
     "predicted": ["checkout/refund.py", "docs/api.md", "tests/test_refund.py"],
     "actual": ["checkout/refund.py", "docs/api.md", "tests/test_refund.py",
                "billing/report.sql"],
     "second_order": [{"consumer": "checkout", "effect": "fails to compile"},
                      {"consumer": "report.sql", "effect": ""}],
     "irreversible": ["backfill wrote cents into the amount column"],
     "rehearsed": false}

Missing files are the obvious finding. The subtler one is a consumer whose
second-order effect is "nothing changes", which is almost never true and is where a
silent misread hides. Over-prediction is reported too, because a prediction that
covers everything is a prediction nobody reads.
"""


def run(payload):
    predicted = [str(p) for p in (payload.get("predicted") or [])]
    actual = [str(p) for p in (payload.get("actual") or [])]
    second = [c for c in (payload.get("second_order") or []) if isinstance(c, dict)]
    problems, misses, silent = [], [], []

    if not str(payload.get("surface") or "").strip():
        problems.append("no surface delta stated: 'refactor' is not a delta")
    if not predicted:
        problems.append("no predicted reach: the change was made blind")
    if not actual:
        problems.append("no actual reach recorded: nothing was compared")

    misses = sorted(set(actual) - set(predicted))
    extra = sorted(set(predicted) - set(actual))
    if misses:
        problems.append(f"{len(misses)} unpredicted file(s): " + ", ".join(misses[:3]))

    for index, consumer in enumerate(second):
        effect = str(consumer.get("effect") or "").strip().lower()
        if not effect:
            silent.append(str(consumer.get("consumer") or f"second_order[{index}]"))
        elif effect in ("nothing", "no change", "none"):
            silent.append(str(consumer.get("consumer") or f"second_order[{index}]"))
    if silent:
        problems.append("consumers assumed unaffected: " + ", ".join(silent[:3]))
    if not second:
        problems.append("no second-order effects predicted")

    irreversible = [str(x) for x in (payload.get("irreversible") or [])]
    if irreversible and payload.get("rehearsed") is not True:
        problems.append("irreversible part never rehearsed: "
                        + "; ".join(irreversible[:2]))

    ratio = None
    if predicted:
        ratio = round(len(actual) / max(1, len(predicted)), 2)
    if ratio is not None and ratio < 0.5:
        problems.append(f"over-prediction: {len(extra)} predicted file(s) were not "
                        "touched, which trains readers to ignore the analysis")

    return {
        "ok": not problems,
        "surface": payload.get("surface"),
        "predicted": len(predicted),
        "actual": len(actual),
        "misses": misses,
        "over_predicted": extra,
        "coverage": ratio,
        "silent_consumers": silent,
        "irreversible": len(irreversible),
        "problems": problems,
        "advice": ("the predicted radius held, and the silent consumers were found "
                   "before the change" if not problems else "; ".join(problems[:3])),
    }
