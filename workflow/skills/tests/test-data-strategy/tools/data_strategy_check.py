"""Data strategy check: is the suite's data owned, deterministic and safe?

Payload::

    {"fixtures": [{"name": "users_shared", "mutable": true, "shared": true,
                   "provenance": "production dump 2023", "anonymised": false},
                  {"name": "currencies", "mutable": false, "shared": true,
                   "provenance": "synthetic", "anonymised": true}],
     "tests": [{"id": "test_refund", "owns_data": true, "seeded": true},
               {"id": "test_invoice", "owns_data": false, "seeded": false}],
     "determinism": {"clock_pinned": true, "random_seeded": false, "ids_fixed": true}}

Shared mutable fixtures and production-derived data are the two findings that turn
into incidents rather than flakes: the first makes the suite order-dependent, the
second makes it a personal-data problem with a git history.
"""


def run(payload):
    fixtures = [f for f in (payload.get("fixtures") or []) if isinstance(f, dict)]
    tests = [t for t in (payload.get("tests") or []) if isinstance(t, dict)]
    determinism = payload.get("determinism") or {}
    problems, shared_mutable, unowned, unsafe = [], [], [], []

    for index, fixture in enumerate(fixtures):
        name = str(fixture.get("name") or f"fixtures[{index}]")
        if fixture.get("mutable") and fixture.get("shared"):
            shared_mutable.append(name)
        provenance = str(fixture.get("provenance") or "").strip().lower()
        derives_from_prod = any(word in provenance for word in
                                ("production", "prod", "dump", "backup", "real"))
        if derives_from_prod and fixture.get("anonymised") is not True:
            unsafe.append(name)
        if not str(fixture.get("provenance") or "").strip():
            problems.append(f"{name}: no provenance, so nobody knows if it is safe")

    for index, test in enumerate(tests):
        tid = str(test.get("id") or f"tests[{index}]")
        if test.get("owns_data") is not True:
            unowned.append(tid)
        if test.get("seeded") is not True:
            problems.append(f"{tid}: no seeded data, so the run depends on leftovers")

    if not fixtures and not tests:
        problems.append("no inventory: nothing to reason about")
    if shared_mutable:
        problems.append(f"{len(shared_mutable)} shared mutable fixture(s): "
                        + ", ".join(shared_mutable[:3]))
    if unowned:
        problems.append(f"{len(unowned)} test(s) that do not own their data: "
                        + ", ".join(unowned[:3]))
    if unsafe:
        problems.append(f"production-derived data without anonymisation: "
                        + ", ".join(unsafe[:3]))
    for field in ("clock_pinned", "random_seeded", "ids_fixed"):
        if determinism.get(field) is not True:
            problems.append(f"determinism.{field} is not ensured")

    return {
        "ok": not problems,
        "fixtures": len(fixtures),
        "tests": len(tests),
        "shared_mutable": shared_mutable,
        "tests_without_own_data": unowned,
        "unanonymised": unsafe,
        "determinism": {k: bool(v) for k, v in determinism.items()},
        "problems": problems,
        "advice": ("every test owns deterministic data, and nothing real leaked in"
                   if not problems else "; ".join(problems[:3])),
    }
