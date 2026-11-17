"""Coverage gate: turn a coverage report into a pass/fail with reasons.

Payload::

    {"report": {"files": {"a.py": {"covered": 12, "total": 15, "missing": [3, 7]}}},
     "threshold": 0.8, "new_files": ["a.py"], "minimum_new": 0.9}

The tool never reads files: the report is passed in, so the tool stays pure and
the sandbox needs no filesystem access.
"""


def _ratio(entry):
    total = int(entry.get("total") or 0)
    covered = int(entry.get("covered") or 0)
    if total <= 0:
        return None
    return covered / total


def run(payload):
    report = payload.get("report") or {}
    files = report.get("files") or report
    threshold = float(payload.get("threshold", 0.8))
    new_files = list(payload.get("new_files") or [])
    minimum_new = float(payload.get("minimum_new", threshold))

    rows, failures, unknown = [], [], []
    for name in sorted(files):
        entry = files[name]
        if not isinstance(entry, dict):
            unknown.append(name)
            continue
        ratio = _ratio(entry)
        if ratio is None:
            unknown.append(name)
            continue
        is_new = name in new_files
        bar = minimum_new if is_new else threshold
        ok = ratio >= bar
        rows.append({
            "file": name,
            "ratio": round(ratio, 4),
            "threshold": bar,
            "new": is_new,
            "ok": ok,
            "missing_lines": len(entry.get("missing") or []),
        })
        if not ok:
            failures.append(name)

    total = sum(int((files[n].get("total") or 0)) for n in files if isinstance(files[n], dict))
    covered = sum(int((files[n].get("covered") or 0)) for n in files if isinstance(files[n], dict))
    overall = (covered / total) if total else None

    return {
        "ok": not failures,
        "overall": round(overall, 4) if overall is not None else None,
        "threshold": threshold,
        "minimum_new": minimum_new,
        "files": rows,
        "failing": failures,
        "skipped": unknown,
        "advice": ("every file meets its bar" if not failures else
                   "raise coverage for: " + ", ".join(failures[:5])),
    }
