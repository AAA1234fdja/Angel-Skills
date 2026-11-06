"""Doc completeness: does each operation's page answer the caller's question?

Payload::

    {"operations": [{"name": "POST /invoices", "method": "POST",
                     "path": "/invoices", "auth": "bearer", "idempotent": true,
                     "parameters": [{"name": "total", "type": "integer",
                                     "required": true, "wrong": "422"}],
                     "request_example": "{...}", "response_example": "{...}",
                     "errors": [{"code": "422", "retry": false}]}]}

Scoring per operation, not per document: an average hides the one page a caller is
stuck on. Two of the checks are strict on purpose — a placeholder example and a
parameter with no wrong-value behaviour are the two things that make a reference
look complete while answering nothing.
"""

PLACEHOLDERS = ("<", "your_", "example.com", "xxx", "todo", "tbd")


def _missing_parameters(parameters):
    issues = []
    for index, param in enumerate(parameters or []):
        if not isinstance(param, dict) or not param.get("name"):
            issues.append(f"parameters[{index}]: no name")
            continue
        for field in ("type",):
            if not param.get(field):
                issues.append(f"{param['name']}: no {field}")
        if param.get("required") is None:
            issues.append(f"{param['name']}: does not say whether it is required")
        if not param.get("wrong"):
            issues.append(f"{param['name']}: does not say what happens when it is wrong")
    return issues


def _placeholder(text):
    low = str(text or "").lower()
    return any(marker in low for marker in PLACEHOLDERS)


def run(payload):
    operations = payload.get("operations") or []
    problems, rows = [], []

    for index, op in enumerate(operations):
        if not isinstance(op, dict) or not op.get("name"):
            problems.append(f"operations[{index}]: no name")
            continue
        name = str(op["name"])
        issues = []
        for field in ("method", "path", "auth"):
            if not op.get(field):
                issues.append(f"missing {field}")
        if op.get("idempotent") is None:
            issues.append("does not state idempotency")
        issues.extend(_missing_parameters(op.get("parameters")))
        for field in ("request_example", "response_example"):
            if not op.get(field):
                issues.append(f"missing {field}")
            elif _placeholder(op[field]):
                issues.append(f"{field} uses a placeholder: it cannot be run")
        errors = op.get("errors") or []
        if not errors:
            issues.append("no error table")
        else:
            for error in errors:
                if isinstance(error, dict) and error.get("retry") is None:
                    issues.append(f"error {error.get('code', '?')}: does not say whether "
                                  "retrying helps")

        total = 11
        score = round(max(0, total - len(issues)) / total, 2)
        rows.append({"operation": name, "score": score, "issues": issues})
        problems.extend(f"{name}: {issue}" for issue in issues)

    if not operations:
        problems.append("no operations documented")
    worst = min(rows, key=lambda r: r["score"]) if rows else None
    return {
        "ok": not problems,
        "operations": len(rows),
        "worst": worst,
        "rows": rows,
        "problems": problems,
        "advice": ("every page answers the call that arrives with a failed request"
                   if not problems else
                   (f"start with {worst['operation']}: {worst['issues'][0]}" if worst
                    else "nothing to document")),
    }
