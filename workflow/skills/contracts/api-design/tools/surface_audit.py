"""Surface audit: does this API surface make promises a consumer can rely on?

Payload::

    {"operations": [{"name": "get_invoice", "kind": "read", "idempotent": true,
                     "errors": ["NOT_FOUND", "FORBIDDEN"],
                     "returns": ["id", "total"]}]}

The four things checked are the four that consumers cannot recover from on their
own: an unknown retry semantic, an undocumented error, an operation that both
reads and writes, and a required field added without a version note.
"""

KINDS = ("read", "write", "delete", "stream", "batch")


def run(payload):
    operations = payload.get("operations") or []
    problems, rows = [], []
    names = set()

    for index, op in enumerate(operations):
        if not isinstance(op, dict) or not op.get("name"):
            problems.append(f"operations[{index}]: no name")
            continue
        name = str(op["name"])
        kind = str(op.get("kind") or "")
        issues = []
        if name in names:
            issues.append("duplicate operation name")
        names.add(name)
        if kind not in KINDS:
            issues.append(f"kind {kind!r} not one of {', '.join(KINDS)}")
        idempotent = op.get("idempotent")
        if kind in ("write", "delete") and idempotent is None:
            issues.append("no idempotency declared: the consumer cannot know if a retry is safe")
        if kind in ("write", "delete") and idempotent is False and not op.get("retry_key"):
            issues.append("not idempotent and no retry key: a timeout becomes a duplicate")
        errors = [str(e) for e in (op.get("errors") or [])]
        if not errors:
            issues.append("no documented errors")
        if not op.get("returns"):
            issues.append("no declared return fields")
        if op.get("reads") and op.get("writes"):
            issues.append("reads and writes in one operation: split it")
        required = [str(f) for f in (op.get("new_required_fields") or [])]
        if required and not op.get("version_note"):
            issues.append("adds required field(s) without a version note: that breaks consumers")
        rows.append({"operation": name, "kind": kind, "issues": issues})
        problems.extend(f"{name}: {issue}" for issue in issues)

    if not operations:
        problems.append("no operations to audit")
    return {
        "ok": not problems,
        "operations": len(rows),
        "rows": rows,
        "problems": problems,
        "advice": ("the surface is specified enough to be relied on" if not problems else
                   "resolve before implementing: " + "; ".join(problems[:3])),
    }
