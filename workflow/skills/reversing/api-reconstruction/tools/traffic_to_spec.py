"""Group captured requests into an endpoint spec.

Payload::

    {"requests": [{"method": "GET", "path": "/users/123",
                   "status": 200, "body": {"id": 123, "name": "a"}}],
     "min_samples": 2}
"""

import re

ID_SEGMENT = re.compile(r"/(\d+|[0-9a-f]{8}-[0-9a-f-]{27,}|[0-9a-f]{16,})(?=/|$)")


def _normalise(path):
    return ID_SEGMENT.sub("/{id}", str(path or "").split("?")[0])


def _infer(values):
    kinds = set()
    for value in values:
        if value is None:
            kinds.add("null")
        elif isinstance(value, bool):
            kinds.add("boolean")
        elif isinstance(value, int):
            kinds.add("integer")
        elif isinstance(value, float):
            kinds.add("number")
        elif isinstance(value, str):
            kinds.add("string")
        elif isinstance(value, list):
            kinds.add("array")
        elif isinstance(value, dict):
            kinds.add("object")
    kinds.discard("null")
    if len(kinds) == 1:
        return kinds.pop()
    return "mixed:" + ",".join(sorted(kinds)) if kinds else "unknown"


def run(payload):
    requests = list(payload.get("requests") or [])
    min_samples = int(payload.get("min_samples", 2))
    endpoints = {}

    for request in requests:
        key = f"{str(request.get('method') or 'GET').upper()} {_normalise(request.get('path'))}"
        bucket = endpoints.setdefault(key, {"samples": 0, "statuses": set(),
                                            "fields": {}, "empty": 0})
        bucket["samples"] += 1
        bucket["statuses"].add(int(request.get("status") or 0))
        body = request.get("body")
        if isinstance(body, dict):
            if not body:
                bucket["empty"] += 1
            for field, value in body.items():
                bucket["fields"].setdefault(field, []).append(value)

    spec, weak = {}, []
    for key in sorted(endpoints):
        bucket = endpoints[key]
        if bucket["samples"] < min_samples:
            weak.append(key)
        properties = {}
        for field in sorted(bucket["fields"]):
            values = bucket["fields"][field]
            kind = _infer(values)
            entry = {"type": kind}
            non_null = [v for v in values if v is not None]
            if non_null and len(non_null) < bucket["samples"]:
                entry["nullable"] = True
            if kind == "string" and 1 < len(set(non_null)) <= 6:
                entry["enum"] = sorted({str(v) for v in non_null})
            properties[field] = entry
        spec[key] = {
            "samples": bucket["samples"],
            "statuses": sorted(bucket["statuses"]),
            "empty_responses": bucket["empty"],
            "response": {"type": "object", "properties": properties},
        }

    return {
        "ok": not weak,
        "endpoints": len(spec),
        "spec": spec,
        "under_sampled": weak,
        "advice": ("spec has enough samples per endpoint" if not weak else
                   "collect more samples for: " + ", ".join(weak[:5])),
        "unknowns": ["auth refresh", "rate limits", "rare error envelopes"],
    }
