"""Suite baseline: which tests can fail, and what we agreed to trust.

Payload::

    {"suite": "backend", "duration_s": 640,
     "tests": [{"id": "test_resume", "assertions": 3, "skipped": false,
                "noticed_mutation": true},
               {"id": "test_health", "assertions": 0, "skipped": false},
               {"id": "test_legacy_export", "assertions": 2, "skipped": true,
                "skip_reason": "", "skip_owner": ""}],
     "known_failures": [{"name": "test_legacy_export", "owner": "ana"}]}

A test with zero assertions is not a test that passes, it is a test that cannot fail.
The duration check exists for a mundane reason: past ten minutes, someone disables the
suite and the next audit finds the same problem, worse.
"""


def run(payload):
    tests = [t for t in (payload.get("tests") or []) if isinstance(t, dict)]
    problems, silent, unattributed = [], [], []
    for index, test in enumerate(tests):
        tid = str(test.get("id") or f"tests[{index}]")
        assertions = test.get("assertions")
        if not isinstance(assertions, int) or assertions <= 0:
            silent.append(tid)
        if test.get("skipped"):
            if not str(test.get("skip_reason") or "").strip():
                unattributed.append(f"{tid} (no reason)")
            elif not str(test.get("skip_owner") or "").strip():
                unattributed.append(f"{tid} (no owner)")

    if not tests:
        problems.append("no tests listed: there is no baseline to adopt")
    if silent:
        problems.append(f"{len(silent)} test(s) that cannot fail: " + ", ".join(silent[:3]))
    if unattributed:
        problems.append(f"{len(unattributed)} unattributed skip(s): "
                        + ", ".join(unattributed[:3]))

    checked = [t for t in tests if isinstance(t.get("noticed_mutation"), bool)]
    caught = [t for t in checked if t["noticed_mutation"]]
    if checked and len(caught) < max(1, int(len(checked) * 0.5)):
        problems.append(f"only {len(caught)}/{len(checked)} sampled tests noticed a real "
                        "behaviour change")

    duration = payload.get("duration_s")
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        duration = None
        problems.append("no suite duration: the baseline is not reproducible")
    if duration and duration > 600:
        problems.append(f"suite takes {int(duration)}s: past ten minutes someone "
                        "disables it and the problem comes back worse")

    known = payload.get("known_failures") or []
    for index, failure in enumerate(known):
        if not isinstance(failure, dict) or not str(failure.get("owner") or "").strip():
            problems.append(f"known_failures[{index}]: no owner, so it is not known, "
                            "it is tolerated")

    skipped = sum(1 for t in tests if t.get("skipped"))
    return {
        "ok": not problems,
        "suite": payload.get("suite"),
        "tests": len(tests),
        "trusted": len(tests) - len(silent) - skipped,
        "silent": silent,
        "skipped": skipped,
        "unattributed_skips": unattributed,
        "mutation_sample": {"checked": len(checked), "caught": len(caught)},
        "duration_s": duration,
        "known_failures": len(known),
        "problems": problems,
        "advice": (f"{len(tests) - len(silent) - skipped} trusted test(s), and the "
                   "skips are decisions" if not problems else "; ".join(problems[:3])),
    }
