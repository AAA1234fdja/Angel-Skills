"""Check sample records against declared invariants.

Payload::

    {"invariants": [{"field": "amount_cents", "rule": "min", "value": 0},
                    {"field": "email", "rule": "required"},
                    {"field": "status", "rule": "enum", "value": ["active","cancelled"]}],
     "records": [{"amount_cents": 100, "email": "a@b.c", "status": "active"}]}
"""

import re

RULES = ("min", "max", "required", "enum", "type", "pattern", "unique", "after")
PY_TYPES = {"string": str, "integer": int, "number": (int, float),
            "boolean": bool, "array": list, "object": dict}


def run(payload):
    invariants = list(payload.get("invariants") or [])
    records = list(payload.get("records") or [])
    violations, unknown = [], []

    for invariant in invariants:
        if str(invariant.get("rule")) not in RULES:
            unknown.append(str(invariant.get("rule")))

    seen = {}
    for index, record in enumerate(records):
        for invariant in invariants:
            field = str(invariant.get("field") or "")
            rule = str(invariant.get("rule") or "")
            expected = invariant.get("value")
            value = record.get(field)

            def fail(message, _field=field, _rule=rule):
                violations.append({"record": index, "field": _field, "rule": _rule,
                                   "message": message})

            if rule == "required" and (value is None or value == ""):
                fail("required field is missing or empty")
            elif rule == "min" and isinstance(value, (int, float)) and value < expected:
                fail(f"{value} < {expected}")
            elif rule == "max" and isinstance(value, (int, float)) and value > expected:
                fail(f"{value} > {expected}")
            elif rule == "enum" and value is not None and value not in (expected or []):
                fail(f"{value!r} not in {expected}")
            elif rule == "pattern" and isinstance(value, str) and expected:
                if not re.search(str(expected), value):
                    fail(f"{value!r} does not match {expected}")
            elif rule == "unique":
                bucket = seen.setdefault(field, set())
                if value in bucket:
                    fail(f"duplicate value {value!r}")
                bucket.add(value)
            elif rule == "type" and value is not None:
                wanted = PY_TYPES.get(str(expected))
                if wanted and not isinstance(value, wanted):
                    fail(f"expected {expected}, got {type(value).__name__}")
            elif rule == "after":
                other = record.get(str(expected))
                if value and other and str(value) <= str(other):
                    fail(f"{field} is not after {expected}")

    by_rule = {}
    for violation in violations:
        by_rule[violation["rule"]] = by_rule.get(violation["rule"], 0) + 1
    return {
        "ok": not violations and not unknown,
        "records": len(records),
        "invariants": len(invariants),
        "violations": violations[:50],
        "by_rule": by_rule,
        "unknown_rules": unknown,
        "advice": ("sample data satisfies the invariants" if not violations else
                   f"{len(violations)} violation(s): decide database or application enforcement"),
    }
