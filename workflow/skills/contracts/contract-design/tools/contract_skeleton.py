"""Build a JSON-schema skeleton from a field list.

Payload::

    {"name": "skill-report", "version": "1.0.0",
     "fields": [{"name": "skill", "type": "string", "required": true,
                 "description": "skill id"},
                {"name": "status", "type": "string", "required": true,
                 "enum": ["pass", "fail"]}]}
"""

TYPES = {"string", "number", "integer", "boolean", "object", "array", "null"}


def run(payload):
    name = str(payload.get("name") or "")
    version = str(payload.get("version") or "1.0.0")
    fields = list(payload.get("fields") or [])
    problems = []

    if not name:
        problems.append("name is required")
    if not all(part.isdigit() for part in version.split(".")) or version.count(".") != 2:
        problems.append(f"version {version!r} must be x.y.z")

    properties, required = {}, []
    for field in fields:
        key = str(field.get("name") or "")
        kind = str(field.get("type") or "string")
        if not key:
            problems.append("a field has no name")
            continue
        if kind not in TYPES:
            problems.append(f"{key}: unknown type {kind!r}")
            continue
        spec = {"type": kind}
        if field.get("description"):
            spec["description"] = str(field["description"])
        if field.get("enum"):
            spec["enum"] = list(field["enum"])
        if field.get("items"):
            spec["items"] = {"type": str(field["items"])}
        if field.get("minLength") is not None:
            spec["minLength"] = int(field["minLength"])
        properties[key] = spec
        if field.get("required"):
            required.append(key)

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
    }
    if required:
        schema["required"] = sorted(required)

    return {
        "ok": not problems,
        "contract": name,
        "version": version,
        "schema": schema,
        "file": f"workflow/contracts/{name}/{version}.schema.json" if name else None,
        "problems": problems,
        "advice": ("review the required set: each entry blocks every future producer"
                   if not problems else "fix the field problems first"),
    }
