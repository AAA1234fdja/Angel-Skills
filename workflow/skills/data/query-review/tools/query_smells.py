"""Query-level smells from supplied SQL and plan facts.

Payload::

    {"queries": [{"sql": "select * from orders where lower(email) = $1",
                  "rows_scanned": 120000, "rows_returned": 3,
                  "plan_node": "seq_scan", "index_used": false,
                  "executions": 120}]}
"""

import re

FUNCTIONS_ON_COLUMNS = re.compile(r"(lower|upper|date|cast|coalesce)\s*\(\s*[a-z_.]+\s*\)", re.I)


def run(payload):
    queries = list(payload.get("queries") or [])
    findings = []

    for index, query in enumerate(queries):
        sql = str(query.get("sql") or "")
        low = sql.lower()
        scanned = int(query.get("rows_scanned") or 0)
        returned = int(query.get("rows_returned") or 0)
        executions = int(query.get("executions") or 1)
        node = str(query.get("plan_node") or "")
        used_index = bool(query.get("index_used"))

        def add(kind, severity, message, _index=index):
            findings.append({"query": _index, "kind": kind, "severity": severity,
                             "message": message})

        if "select *" in low:
            add("select_star", "minor", "project only the columns used")
        if node in ("seq_scan", "table_scan") and scanned > 10000 and not used_index:
            add("sequential_scan", "high", f"scans {scanned} rows without an index")
        if scanned and returned and scanned / max(returned, 1) > 1000:
            add("poor_selectivity", "high", f"{scanned} scanned for {returned} returned")
        if executions > 50 and "where" in low and " in (" not in low:
            add("likely_n_plus_one", "high", f"executed {executions} times: batch it")
        if FUNCTIONS_ON_COLUMNS.search(sql):
            add("function_on_column", "medium", "prevents index use: compare the raw column")
        if "offset" in low and "limit" in low:
            add("offset_pagination", "minor", "deep offsets degrade: keyset pagination")
        if not re.search(r"\blimit\b|\bfetch first\b", low) and "count(" not in low:
            add("unbounded", "medium", "no limit: an endpoint can return everything")
        if "like '%" in low:
            add("leading_wildcard", "medium", "leading wildcard cannot use a btree index")

    order = {"high": 0, "medium": 1, "minor": 2}
    findings.sort(key=lambda f: order.get(f["severity"], 3))
    blocking = [f for f in findings if f["severity"] == "high"]
    return {
        "ok": not blocking,
        "queries": len(queries),
        "findings": findings[:60],
        "counts": {sev: sum(1 for f in findings if f["severity"] == sev)
                   for sev in ("high", "medium", "minor")},
        "advice": ("no high-severity smell" if not blocking else
                   "fix first: " + ", ".join(sorted({f["kind"] for f in blocking}))),
    }
