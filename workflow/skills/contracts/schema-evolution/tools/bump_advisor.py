"""Classify planned schema changes and state the required version bump.

Payload::

    {"current": "1.4.2",
     "changes": [{"kind": "add_optional", "field": "trace_id"},
                 {"kind": "add_required", "field": "tenant"}]}
"""

BREAKING = {
    "remove_property", "add_required", "change_type", "narrow_enum",
    "forbid_additional", "rename_property", "tighten_constraint",
}
MINOR = {"add_optional", "widen_enum", "relax_constraint"}
PATCH = {"doc_only", "example_only"}


def _bump(version, kind):
    parts = [int(p) for p in str(version or "1.0.0").split(".")]
    while len(parts) < 3:
        parts.append(0)
    if kind == "major":
        return f"{parts[0] + 1}.0.0"
    if kind == "minor":
        return f"{parts[0]}.{parts[1] + 1}.0"
    return f"{parts[0]}.{parts[1]}.{parts[2] + 1}"


def run(payload):
    current = str(payload.get("current") or "1.0.0")
    changes = list(payload.get("changes") or [])
    rows, unknown = [], []

    for change in changes:
        kind = str(change.get("kind") or "")
        field = change.get("field")
        if kind in BREAKING:
            cls = "major"
        elif kind in MINOR:
            cls = "minor"
        elif kind in PATCH:
            cls = "patch"
        else:
            cls = "unknown"
            unknown.append(kind)
        rows.append({"kind": kind, "field": field, "class": cls,
                     "migration": _migration(kind, field)})

    order = {"major": 0, "minor": 1, "patch": 2, "unknown": 3}
    rows.sort(key=lambda r: order[r["class"]])
    classes = [r["class"] for r in rows if r["class"] != "unknown"]
    required = "patch"
    if "major" in classes:
        required = "major"
    elif "minor" in classes:
        required = "minor"

    return {
        "ok": not unknown,
        "current": current,
        "required_bump": required,
        "next_version": _bump(current, required),
        "changes": rows,
        "unknown_kinds": unknown,
        "advice": ("all changes are compatible" if required != "major" else
                   "a new major file is required; keep the old one readable"),
    }


def _migration(kind, field):
    return {
        "remove_property": f"deprecate {field} for one minor, remove in the next major",
        "add_required": f"backfill {field} in existing payloads before requiring it",
        "change_type": f"add a new field and migrate {field} over one major",
        "narrow_enum": f"confirm no consumer sends values removed from {field}",
        "rename_property": f"emit both {field} and the new name for one major",
        "forbid_additional": "audit producers for extra fields before forbidding them",
        "add_optional": f"document {field} as optional and default it in consumers",
        "widen_enum": f"consumers must tolerate new values of {field}",
    }.get(kind, "no automatic migration advice")
