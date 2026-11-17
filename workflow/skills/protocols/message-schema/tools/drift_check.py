"""Compare code fields with a schema's properties.

Payload:: ``{"code_fields": ["step_id", "skills"], "schema": {"properties": {...}}}``

A field on one side only is drift; a field on both sides with a different type is
drift with a bigger blast radius.
"""


def run(payload):
    code_fields = [str(f) for f in payload.get("code_fields") or []]
    schema = payload.get("schema") or {}
    properties = schema.get("properties") or {}
    required = set(schema.get("required") or [])

    schema_fields = set(properties)
    code_set = set(code_fields)

    only_code = sorted(code_set - schema_fields)
    only_schema = sorted(schema_fields - code_set)
    required_missing = sorted(r for r in required if r not in code_set)

    rows = []
    for field in sorted(code_set & schema_fields):
        spec = properties.get(field) or {}
        rows.append({
            "field": field,
            "schema_type": spec.get("type"),
            "required": field in required,
            "enum": bool(spec.get("enum")),
        })

    ok = not only_code and not only_schema and not required_missing
    return {
        "ok": ok,
        "in_sync": rows,
        "only_in_code": only_code,
        "only_in_schema": only_schema,
        "required_but_absent_in_code": required_missing,
        "advice": ("schema and code agree" if ok else
                   "generate one from the other; do not fix both by hand"),
    }
