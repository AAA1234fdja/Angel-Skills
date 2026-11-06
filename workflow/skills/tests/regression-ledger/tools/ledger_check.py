"""Ledger check: is the downstream surface legible and provable?

Payload::

    {"as_of": "2026-11-05", "stale_days": 180,
     "modules": [{"name": "billing", "surface": ["charge", "refund"],
                  "updated_on": "2026-09-01", "changed_on": "2026-10-20",
                  "consumers": [{"name": "checkout", "coupling": "runtime",
                                 "check": "e2e: checkout.mjs"}]},
                 {"name": "legacy-export", "surface": ["dump"],
                  "updated_on": "2025-01-10", "changed_on": "2026-10-30",
                  "consumers": []}]}

Two findings dominate: a consumer with no executable check (a comment pretending to be
a control) and a module that changed after the ledger was last updated (the ledger is
describing a system that no longer exists).
"""

COUPLINGS = {"compile", "runtime", "data", "contract"}


def _days(a, b):
    try:
        from datetime import date

        return (date.fromisoformat(str(b)) - date.fromisoformat(str(a))).days
    except (TypeError, ValueError):
        return None


def run(payload):
    modules = [m for m in (payload.get("modules") or []) if isinstance(m, dict)]
    problems, unchecked, stale = [], [], []

    if not modules:
        problems.append("no modules recorded: there is nothing to reason about")

    for index, module in enumerate(modules):
        name = str(module.get("name") or f"modules[{index}]")
        consumers = module.get("consumers") or []
        if not module.get("surface"):
            problems.append(f"{name}: no published surface, so nobody can know what "
                            "they depend on")
        if not consumers:
            problems.append(f"{name}: no consumers recorded — write 'unknown' rather "
                            "than nothing")
        for cindex, consumer in enumerate(consumers):
            if not isinstance(consumer, dict):
                continue
            cname = str(consumer.get("name") or f"{name}.consumers[{cindex}]")
            if not str(consumer.get("check") or "").strip():
                unchecked.append(f"{name}->{cname}")
            coupling = str(consumer.get("coupling") or "").strip()
            if coupling not in COUPLINGS:
                problems.append(f"{name}->{cname}: coupling '{coupling or '?'}' is not "
                                "one of " + "/".join(sorted(COUPLINGS)))
        drift = _days(module.get("updated_on"), module.get("changed_on"))
        if drift is not None and drift > 0:
            stale.append(f"{name} (changed {drift}d after the ledger)")
        age = _days(module.get("updated_on"), payload.get("as_of"))
        if age is not None and age > int(payload.get("stale_days") or 180):
            stale.append(f"{name} (ledger {age}d old)")

    if unchecked:
        problems.append(f"{len(unchecked)} consumer(s) with no executable check: "
                        + ", ".join(unchecked[:3]))
    if stale:
        problems.append("stale entries: " + "; ".join(stale[:3]))

    return {
        "ok": not problems,
        "as_of": payload.get("as_of"),
        "modules": len(modules),
        "consumers": sum(len(m.get("consumers") or []) for m in modules),
        "unchecked": unchecked,
        "stale": stale,
        "unknown_consumers": [str(m.get("name")) for m in modules
                              if str((m.get("consumers_note") or "")).lower() == "unknown"],
        "problems": problems,
        "advice": ("every published surface has named consumers and a check for each"
                   if not problems else "; ".join(problems[:3])),
    }
