"""Commit lint: would a reviewer and a future bisect thank you for this?

Payload::

    {"commits": [{"subject": "reject expired tokens", "body": "the issuer started...",
                  "files": ["auth/tokens.py"], "insertions": 20, "deletions": 8,
                  "concerns": ["auth"]}]}

Checks are cheap and mechanical: vague subjects, a commit carrying several
concerns, oversized diffs, secret-shaped strings in the message or the paths, and a
body that only repeats the subject. The judgement calls — whether the change is one
revertible unit — are left to the reader; this tool refuses to fake them.
"""

VAGUE = ("wip", "fix", "fixes", "update", "updates", "changes", "stuff", "misc",
         "tidy", "cleanup", "temp", "tmp", "asdf", "test", "tests")
SECRET_SHAPED = ("api_key=", "secret=", "password=", "token=", "begin rsa",
                 "begin openssl", "aws_secret", "ghp_", "sk-")
MAX_SUBJECT = 72
MAX_LINES = 800


def run(payload):
    commits = payload.get("commits") or []
    problems, rows = [], []

    for index, commit in enumerate(commits):
        if not isinstance(commit, dict):
            problems.append(f"commits[{index}] is not an object")
            continue
        subject = str(commit.get("subject") or "").strip()
        body = str(commit.get("body") or "").strip()
        files = [str(f) for f in (commit.get("files") or [])]
        concerns = [str(c) for c in (commit.get("concerns") or [])]
        lines = int(commit.get("insertions") or 0) + int(commit.get("deletions") or 0)
        issues = []

        if not subject:
            issues.append("no subject")
        else:
            if len(subject) > MAX_SUBJECT:
                issues.append(f"subject is {len(subject)} chars (max {MAX_SUBJECT})")
            words = [w for w in subject.lower().replace(":", " ").split() if w]
            if words and all(w in VAGUE or len(w) <= 2 for w in words):
                issues.append("vague subject: say what becomes true after this commit")
            if subject.endswith("."):
                issues.append("subject ends with a period")
        if body and subject and body.lower().startswith(subject.lower()[:30]):
            issues.append("body restates the subject and adds nothing")
        if len(concerns) > 1:
            issues.append(f"carries several concerns ({', '.join(concerns)}): split it")
        if lines > MAX_LINES:
            issues.append(f"{lines} changed lines: revertible is the unit, not reviewable")
        haystack = " ".join([subject, body] + files).lower()
        for marker in SECRET_SHAPED:
            if marker in haystack:
                issues.append(f"secret-shaped content ({marker!r}): rewrite the commit, "
                              "deleting later leaves it in history")
        if files and any(f.endswith((".pyc", ".min.js", ".lock")) for f in files):
            issues.append("looks like a generated artefact")

        rows.append({"subject": subject[:60], "lines": lines, "issues": issues})
        problems.extend(f"{subject[:40] or index}: {issue}" for issue in issues)

    if not commits:
        problems.append("no commits to lint")
    return {
        "ok": not problems,
        "commits": len(rows),
        "rows": rows,
        "problems": problems,
        "advice": ("each commit is one revertible change with a subject that says why"
                   if not problems else "; ".join(problems[:3])),
    }
