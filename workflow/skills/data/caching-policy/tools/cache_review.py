"""Score a cache design on the decisions that matter.

Payload::

    {"caches": [{"name": "product_page", "key": ["product_id", "locale"],
                 "ttl_seconds": 300, "tolerance_seconds": 600,
                 "invalidation": "on product update", "bounded": true,
                 "on_outage": "serve stale", "measured": true}]}
"""


def run(payload):
    caches = list(payload.get("caches") or [])
    rows, problems = [], []

    for cache in caches:
        name = str(cache.get("name") or "?")
        key = list(cache.get("key") or [])
        ttl = cache.get("ttl_seconds")
        tolerance = cache.get("tolerance_seconds")
        invalidation = str(cache.get("invalidation") or "").strip()
        bounded = bool(cache.get("bounded"))
        on_outage = str(cache.get("on_outage") or "").strip()
        measured = bool(cache.get("measured"))

        issues = []
        if not key:
            issues.append("no key")
        if ttl is None:
            issues.append("no ttl")
        elif tolerance is not None and float(ttl) > float(tolerance):
            issues.append("ttl longer than staleness tolerance")
        if not invalidation:
            issues.append("no invalidation path")
        if not bounded:
            issues.append("unbounded")
        if not on_outage:
            issues.append("no outage behaviour")
        if not measured:
            issues.append("not measured")

        rows.append({"name": name, "issues": issues,
                     "score": round(1 - len(issues) / 7, 2)})
        problems.extend(f"{name}: {issue}" for issue in issues)

    return {
        "ok": not problems,
        "caches": rows,
        "problems": problems,
        "advice": ("cache design is complete" if not problems else
                   "decide before shipping: " + problems[0]),
    }
