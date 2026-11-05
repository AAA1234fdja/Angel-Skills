"""pass@k, pass^k and cost per success.

Payload::

    {"evals": {"auth_flow": {"attempts": ["pass","pass","fail"], "cost": 0.12},
               "pdf_parse": {"attempts": ["fail","fail","pass"], "cost": 0.30}},
     "k": 3}
"""


def run(payload):
    evals = payload.get("evals") or {}
    k = int(payload.get("k", 3))
    rows, capability, reliability = [], [], []
    total_cost = 0.0
    successes = 0

    for name in sorted(evals):
        entry = evals[name] or {}
        attempts = [str(a).lower() in ("pass", "ok", "true", "1")
                    for a in (entry.get("attempts") or [])][:k]
        if not attempts:
            rows.append({"eval": name, "state": "never ran"})
            continue
        cost = float(entry.get("cost") or 0.0)
        total_cost += cost
        passed = sum(1 for a in attempts if a)
        at_k = passed > 0
        hat_k = all(attempts)
        per_success = (cost / passed) if passed else None
        rows.append({
            "eval": name,
            "attempts": len(attempts),
            "passed": passed,
            "pass@k": at_k,
            "pass^k": hat_k,
            "cost": round(cost, 4),
            "cost_per_success": round(per_success, 4) if per_success is not None else None,
        })
        if at_k:
            capability.append(name)
        if hat_k:
            reliability.append(name)
        successes += passed

    total = len([r for r in rows if "attempts" in r])
    return {
        "ok": bool(total) and len(reliability) == total,
        "k": k,
        "evals": rows,
        f"pass@{k}": round(len(capability) / total, 3) if total else 0.0,
        f"pass^{k}": round(len(reliability) / total, 3) if total else 0.0,
        "unreliable": [r["eval"] for r in rows if "attempts" in r and not r["pass^k"]],
        "cost": round(total_cost, 4),
        "cost_per_success": round(total_cost / successes, 4) if successes else None,
        "advice": ("reliable across attempts" if total and len(reliability) == total else
                   "unreliable evals: " + ", ".join(r["eval"] for r in rows
                                                    if "attempts" in r and not r["pass^k"])[:120]),
    }
