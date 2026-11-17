"""Replay check: does the failure happen on demand, and is the fix proven?

Payload::

    {"failure": "refund created twice for one order",
     "record": {"version": "1.9.4", "input": "POST /refunds x2 (parallel)",
                "at": "2026-11-04T21:12Z", "order": ["pay", "refund", "retry"]},
     "unpinned_variables": [{"name": "concurrency", "plausibility": "high",
                             "replayed": true},
                            {"name": "data volume", "plausibility": "low",
                             "replayed": false}],
     "parallel_changes": ["concurrency", "locale"],
     "reproduction": {"same_path": true, "same_message": true, "same_state": true},
     "minimal_input": "two parallel refund calls",
     "test": {"name": "test_double_refund", "failed_before": true,
              "reason": "assert 2 == 1"}}

Two findings are fatal and both are common: a reproduction claimed without comparing
the signature (you fixed something else) and a fix with no test that failed first
(you will never know whether it did anything).
"""


def run(payload):
    record = payload.get("record") or {}
    variables = [v for v in (payload.get("unpinned_variables") or [])
                 if isinstance(v, dict)]
    repro = payload.get("reproduction") or {}
    test = payload.get("test") or {}
    problems = []

    for field in ("version", "input", "at", "order"):
        if not record.get(field):
            problems.append(f"record.{field} is not frozen: it is a variable you will "
                            "change by accident")
    if not variables:
        problems.append("no unpinned variables listed: the search space is unknown")
    plausibility = [str(v.get("plausibility") or "").lower() for v in variables]
    for value in plausibility:
        if value not in ("high", "medium", "low"):
            problems.append(f"variable plausibility '{value or '?'}' is not "
                            "high/medium/low, so nothing is ranked")
            break

    parallel = [str(c) for c in (payload.get("parallel_changes") or [])]
    if len(parallel) > 1:
        problems.append(f"{len(parallel)} variables changed at once: "
                        + ", ".join(parallel[:3]) + " — a success teaches nothing")

    signature = all(repro.get(f) is True for f in ("same_path", "same_message",
                                                   "same_state"))
    if not signature:
        missing = [f for f in ("same_path", "same_message", "same_state")
                   if repro.get(f) is not True]
        problems.append("reproduction not proven to be the same failure (unchecked: "
                        + ", ".join(missing) + ")")
    if not str(payload.get("minimal_input") or "").strip():
        problems.append("no minimal failing input: the test will be as wide as the "
                        "original incident")

    if not str(test.get("name") or "").strip():
        problems.append("no test: the fix has nothing to be verified against")
    elif test.get("failed_before") is not True:
        problems.append("the test never failed before the fix, so it proves nothing")
    if not str(test.get("reason") or "").strip():
        problems.append("no recorded failure reason: a test that fails for the wrong "
                        "reason passes for the wrong reason later")

    unreplayed = [str(v.get("name")) for v in variables
                  if v.get("replayed") is not True
                  and str(v.get("plausibility") or "").lower() == "high"]
    if unreplayed:
        problems.append("high-plausibility variables never replayed: "
                        + ", ".join(unreplayed[:3]))

    return {
        "ok": not problems,
        "failure": payload.get("failure"),
        "variables": len(variables),
        "replayed": sum(1 for v in variables if v.get("replayed") is True),
        "same_signature": signature,
        "minimal_input": payload.get("minimal_input"),
        "test": test.get("name"),
        "problems": problems,
        "advice": ("the failure is reproducible on demand and the fix is proven by a "
                   "test that failed first" if not problems else "; ".join(problems[:3])),
    }
