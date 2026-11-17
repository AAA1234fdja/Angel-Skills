"""Event compatibility: additive or breaking, decided by comparing two shapes.

Payload::

    {"name": "order.created", "old": {"version": "1", "fields": {
         "id": {"type": "string", "required": true},
         "amount": {"type": "integer", "required": true}}},
     "new": {"version": "2", "fields": {
         "id": {"type": "string", "required": true},
         "amount": {"type": "number", "required": true},
         "currency": {"type": "string", "required": false}}}}

The classification is mechanical: an added optional field and a widened enum are
additive; a removed field, a renamed one, a narrowed type, a unit change or a new
required field is breaking and needs a dual-write window. The tool never decides
whether the window is acceptable — that is a human decision with a date.
"""

BREAKING_KINDS = ("removed", "renamed", "retyped", "made_required", "unit_changed",
                  "enum_narrowed")


def _fields(shape):
    fields = (shape or {}).get("fields") or {}
    return {str(k): dict(v or {}) for k, v in fields.items() if isinstance(v, dict)}


def run(payload):
    name = str(payload.get("name") or "").strip()
    old = _fields(payload.get("old"))
    new = _fields(payload.get("new"))
    problems, changes = [], []

    for field in sorted(set(old) - set(new)):
        old_spec = old[field]
        moved = [f for f in new if new[f].get("renamed_from") == field
                 or new[f].get("was") == field]
        kind = "renamed" if moved else "removed"
        changes.append({"field": field, "kind": kind, "breaking": True,
                        "detail": f"now {moved[0]}" if moved else "no longer emitted"})
    for field in sorted(set(new) - set(old)):
        spec = new[field]
        renamed = bool(spec.get("renamed_from") or spec.get("was"))
        required = bool(spec.get("required"))
        breaking = required and not renamed
        changes.append({"field": field, "kind": "added",
                        "breaking": breaking,
                        "detail": ("required on a new field" if breaking
                                   else "optional: consumers may ignore it")})
    for field in sorted(set(old) & set(new)):
        before, after = old[field], new[field]
        if before.get("type") != after.get("type"):
            changes.append({"field": field, "kind": "retyped", "breaking": True,
                            "detail": f"{before.get('type')} -> {after.get('type')}"})
        elif before.get("unit") != after.get("unit"):
            changes.append({"field": field, "kind": "unit_changed", "breaking": True,
                            "detail": f"{before.get('unit')} -> {after.get('unit')}"})
        elif before.get("required") is False and after.get("required") is True:
            changes.append({"field": field, "kind": "made_required", "breaking": True,
                            "detail": "consumers that omit it will fail"})

    breaking = [c for c in changes if c["breaking"]]
    additive = [c for c in changes if not c["breaking"]]
    if not name:
        problems.append("no event name")
    if not old or not new:
        problems.append("both shapes are required to classify a change")
    if breaking:
        problems.append(f"{len(breaking)} breaking change(s): they need a dual-write "
                        "window with a retirement date")
    if len(additive) > 3:
        problems.append(f"{len(additive)} additive changes in one release: ship one field "
                        "per release")
    if payload.get("window_ends") is None and breaking:
        problems.append("breaking change with no window end: dual-write forever")

    version = (payload.get("new") or {}).get("version")
    return {
        "ok": not problems,
        "event": name,
        "new_version": version,
        "compatible": not breaking,
        "breaking": [f"{c['field']}: {c['kind']}" for c in breaking],
        "additive": [f"{c['field']}: {c['kind']}" for c in additive],
        "changes": changes,
        "problems": problems,
        "advice": ("additive only: consumers on the old shape keep working"
                   if not breaking else
                   "dual-write both shapes and retire the old one on the stated date"),
    }
