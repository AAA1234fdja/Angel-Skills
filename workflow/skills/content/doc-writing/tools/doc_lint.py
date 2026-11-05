"""Lint a document for the things that make docs useless.

Payload::

    {"doc": {"path": "README.md", "audience": "developers",
             "source_of_truth": "workflow/angel/cli.py",
             "examples_run": 2, "failure_section": true,
             "last_verified": "2026-11-05", "has_duplicated_truth": false,
             "words": 900}}
"""


def run(payload):
    doc = payload.get("doc") or {}
    problems, warnings = [], []

    if not str(doc.get("audience") or "").strip():
        problems.append("audience is not stated")
    if not str(doc.get("source_of_truth") or "").strip():
        warnings.append("source of truth not named: readers cannot check staleness")
    if int(doc.get("examples_run") or 0) == 0:
        problems.append("no example was executed as written")
    if not doc.get("failure_section"):
        problems.append("no failure-modes section")
    if not str(doc.get("last_verified") or "").strip():
        warnings.append("no last-verified date")
    if doc.get("has_duplicated_truth"):
        problems.append("duplicated truth: link to the source instead")
    words = int(doc.get("words") or 0)
    if words > 4000:
        warnings.append(f"{words} words: split it or link to detail")

    return {
        "ok": not problems,
        "problems": problems,
        "warnings": warnings,
        "advice": ("documentation is checkable" if not problems else
                   "fix: " + problems[0]),
    }
