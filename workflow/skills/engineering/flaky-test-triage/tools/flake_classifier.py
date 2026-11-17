"""Flake classifier: name the source of nondeterminism from what was observed.

Payload::

    {"runs": ["pass", "fail", "pass", "pass", "fail", "pass", "pass", "pass",
              "fail", "pass"],
     "signals": ["timing", "shared_state"]}

It answers two different questions. The **runs** say whether this is flakiness at
all (all-pass or all-fail is not flaky, and the ticket should be wrong about
that). The **signals** say where the nondeterminism lives, ordered by how often
each one is the real cause. Naming the category is the step people skip, and the
skip is why the same flake returns with a bigger timeout.
"""

SIGNALS = {
    "timing": ("sleeps, timeouts or wall-clock comparisons: fix the synchronisation "
               "or inject a clock"),
    "ordering": ("iteration over a set or dict, or test-order dependence: sort or "
                 "isolate the state"),
    "shared_state": ("a module-level cache, a row left behind, a singleton: reset "
                     "between tests and prove it with a failing second run"),
    "network": ("a real socket in a unit test, or a DNS lookup: stub at the boundary"),
    "randomness": ("unseeded random, uuid or hash order: seed it and log the seed"),
    "concurrency": ("unsynchronised threads or a race on an await: force the "
                    "interleaving, then fix the access"),
    "resource": ("file handles, ports or memory not released: close in a fixture and "
                 "leak-check"),
    "environment": ("locale, timezone, CPU count or a missing env var: pin them in "
                    "the test runner"),
}


def run(payload):
    runs = [str(r).lower() for r in payload.get("runs") or []]
    signals = [str(s).lower().replace("-", "_") for s in payload.get("signals") or []]
    problems, hints = [], []

    passes = runs.count("pass")
    fails = runs.count("fail")
    flaky = 0 < passes and 0 < fails
    if not runs:
        problems.append("no runs recorded: run it ten times before diagnosing")
    elif not flaky:
        problems.append("not flaky by this evidence: "
                        f"{passes} pass / {fails} fail means a deterministic failure "
                        "or a green test, not nondeterminism")
    elif len(runs) < 10:
        problems.append(f"only {len(runs)} run(s): ten is the minimum to call it flaky")

    unknown = [s for s in signals if s not in SIGNALS]
    if unknown:
        problems.append("unknown signal(s): " + ", ".join(unknown))
    for signal in signals:
        if signal in SIGNALS:
            hints.append({"signal": signal, "fix": SIGNALS[signal]})
    if flaky and not signals:
        problems.append("no signal named: classify the source before fixing")

    rate = round(fails / len(runs), 2) if runs else None
    dominant = signals[0] if signals else None
    return {
        "ok": not problems,
        "runs": len(runs),
        "fail_rate": rate,
        "flaky": flaky,
        "signals": hints,
        "dominant": dominant,
        "problems": problems,
        "advice": (f"reproduce the {dominant} path deterministically, fix the cause, "
                   "then re-run ten times" if dominant and flaky else
                   (problems[0] if problems else "record the runs and the signal")),
    }
