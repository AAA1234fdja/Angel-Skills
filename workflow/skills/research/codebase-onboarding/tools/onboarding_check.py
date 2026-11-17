"""Onboarding check: has this codebase actually been learned, or only read?

Payload::

    {"repo": "billing-service",
     "commands": {"start": "make dev", "test": "pytest", "single": "pytest -k"},
     "traced_paths": [{"kind": "read", "from": "GET /invoices", "to": "db"},
                      {"kind": "write", "from": "POST /refunds", "to": "queue"}],
     "boundaries": ["stripe client", "validation at the router"],
     "conventions": [{"rule": "errors are returned, not raised", "confirmed_file": "refunds.py"},
                     {"rule": "snake_case everywhere", "confirmed_file": ""}],
     "first_change": {"predicted_files": ["refunds.py", "test_refunds.py"],
                      "actual_files": ["refunds.py", "test_refunds.py", "models.py"]}}

The evidence that onboarding worked is the last field: a predicted change compared
with the actual one. Everything before it is preparation, and preparation that is
never tested by a change is reading with extra steps.
"""

KINDS = {"read", "write", "failure"}
CONVENTIONS_TO_CONFIRM = 3


def run(payload):
    commands = payload.get("commands") or {}
    paths = [p for p in (payload.get("traced_paths") or []) if isinstance(p, dict)]
    conventions = [c for c in (payload.get("conventions") or []) if isinstance(c, dict)]
    change = payload.get("first_change") or {}
    problems = []

    for name in ("start", "test", "single"):
        if not str(commands.get(name) or "").strip():
            problems.append(f"no {name} command: {name} was never executed")

    kinds = {str(p.get("kind") or "").lower() for p in paths}
    missing = KINDS - kinds
    if missing:
        problems.append("paths never traced: " + ", ".join(sorted(missing)))
    for index, path in enumerate(paths):
        if not str(path.get("from") or "").strip() or not str(path.get("to") or "").strip():
            problems.append(f"traced_paths[{index}]: needs both a start and a destination")

    if not (payload.get("boundaries") or []):
        problems.append("no boundaries named: every change touches one")

    unconfirmed = [str(c.get("rule") or "?") for c in conventions
                   if not str(c.get("confirmed_file") or "").strip()]
    if len(conventions) < CONVENTIONS_TO_CONFIRM:
        problems.append(f"only {len(conventions)} convention(s) recorded; three is the "
                        "minimum to notice a pattern")
    if unconfirmed:
        problems.append("unconfirmed conventions: " + "; ".join(unconfirmed[:3]))

    predicted = [str(f) for f in (change.get("predicted_files") or [])]
    actual = [str(f) for f in (change.get("actual_files") or [])]
    surprise = []
    if not predicted:
        problems.append("no change predicted, so the understanding was never tested")
    if predicted and not actual:
        problems.append("the change was predicted but never made")
    if predicted and actual:
        surprise = sorted(set(actual) - set(predicted))
        if surprise:
            problems.append(f"prediction missed {len(surprise)} file(s): "
                            + ", ".join(surprise[:3]))
    if not (payload.get("open_questions") or []):
        problems.append("no open questions: a newcomer with no questions did not look")

    return {
        "ok": not problems,
        "repo": payload.get("repo"),
        "paths": len(paths),
        "conventions": len(conventions),
        "unconfirmed": unconfirmed,
        "predicted": len(predicted),
        "surprise_files": surprise,
        "open_questions": len(payload.get("open_questions") or []),
        "problems": problems,
        "advice": ("the first change matched the prediction, so the codebase is known "
                   "well enough to change" if not problems else "; ".join(problems[:3])),
    }
