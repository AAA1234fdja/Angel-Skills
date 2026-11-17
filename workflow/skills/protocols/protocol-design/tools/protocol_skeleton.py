"""Generate an envelope + payload schema for a new protocol.

Payload::

    {"name": "yev-dispatch", "origin": "yev", "targets": ["xev"],
     "fields": [{"name": "step_id", "type": "string", "required": true}]}
"""

ENVELOPE = {
    "protocol": {"type": "string", "const": None},
    "version": {"type": "string", "pattern": "^\d+\.\d+$"},
    "task_id": {"type": "string", "minLength": 1},
    "origin": {"type": "string", "enum": None},
    "target": {"type": "string", "enum": None},
    "msg_id": {"type": "string", "minLength": 4},
    "ts": {"type": "number"},
}


def run(payload):
    name = str(payload.get("name") or "")
    origin = str(payload.get("origin") or "")
    targets = [str(t) for t in payload.get("targets") or []]
    fields = list(payload.get("fields") or [])
    problems = []

    if not name:
        problems.append("name is required")
    if not origin:
        problems.append("origin role is required")
    if not targets:
        problems.append("at least one consumer is required")

    envelope = {}
    for key, spec in ENVELOPE.items():
        spec = dict(spec)
        if key == "protocol":
            spec["const"] = name
        if key == "origin":
            spec["enum"] = [origin] if origin else []
        if key == "target":
            spec["enum"] = targets
        envelope[key] = spec

    payload_props = {}
    required = []
    for field in fields:
        key = str(field.get("name") or "")
        if not key:
            problems.append("a payload field has no name")
            continue
        spec = {"type": str(field.get("type") or "string")}
        if field.get("enum"):
            spec["enum"] = list(field["enum"])
        if field.get("minItems") is not None:
            spec["minItems"] = int(field["minItems"])
        payload_props[key] = spec
        if field.get("required"):
            required.append(key)

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {**envelope, **payload_props},
    }
    if required:
        schema["required"] = ["protocol", "version", "task_id", "origin", "target"] + sorted(required)

    return {
        "ok": not problems,
        "protocol": name,
        "consumers": targets,
        "schema": schema,
        "rejection_rules": {
            "unknown_field": "reject",
            "unknown_version": "reject",
            "unknown_role": "reject",
            "missing_required": "reject",
        },
        "problems": problems,
        "advice": "declare the consumers in the receiver; a message nobody validates drifts",
    }
