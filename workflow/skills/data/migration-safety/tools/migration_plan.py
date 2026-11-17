"""Assess a migration plan before it runs.

Payload::

    {"steps": [{"op": "add_column", "table": "orders", "column": "tenant",
                "nullable": true, "rollback": "drop_column"},
               {"op": "backfill", "table": "orders", "batched": true, "idempotent": true}],
     "stop_conditions": {"error_rate": 0.01, "lock_seconds": 5, "replication_lag": 2}}
"""

EXPENSIVE = {"rewrite_table", "add_not_null_without_default", "change_type",
             "drop_column", "drop_table", "rename_column"}
REVERSIBLE = {"add_column", "add_index_concurrently", "backfill", "create_table"}


def run(payload):
    steps = list(payload.get("steps") or [])
    problems, warnings, rows = [], [], []

    for step in steps:
        op = str(step.get("op") or "")
        table = step.get("table")
        rollback = step.get("rollback")
        if op in ("add_not_null_without_default", "change_type", "rewrite_table"):
            lock = "exclusive, rewrites table"
        elif op in ("add_column", "create_table"):
            lock = "brief metadata lock"
        elif op == "add_index_concurrently":
            lock = "none (concurrent)"
        elif op == "backfill":
            lock = "row locks per batch"
        else:
            lock = "unknown"

        rows.append({"op": op, "table": table, "lock": lock})
        if op in EXPENSIVE and not rollback:
            problems.append(f"{op} on {table}: no rollback")
        elif op not in REVERSIBLE and not rollback:
            warnings.append(f"{op} on {table}: rollback unclear")
        if op == "backfill":
            if not step.get("batched"):
                problems.append(f"backfill of {table} is not batched")
            if not step.get("idempotent"):
                problems.append(f"backfill of {table} is not idempotent")
            if not step.get("resumable", True):
                warnings.append(f"backfill of {table} cannot resume")
        if op == "drop_column" and not step.get("code_stopped_using"):
            problems.append(f"drop_column on {table} while code may still read it")

    stop = payload.get("stop_conditions") or {}
    for key in ("error_rate", "lock_seconds", "replication_lag"):
        if key not in stop:
            warnings.append(f"no stop condition for {key}")

    return {
        "ok": not problems,
        "steps": rows,
        "problems": problems,
        "warnings": warnings,
        "advice": ("plan is reversible and bounded" if not problems else
                   "do not run: " + "; ".join(problems[:3])),
    }
