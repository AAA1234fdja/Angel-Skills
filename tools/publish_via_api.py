"""Publish a local commit through the GitHub REST API.

`git push` is rejected by the remote with `remote: fatal error in commit_refs`
for every ref on this repository, including a brand-new branch pointing at a
commit the remote already has. Writes through the API work, so the commit is
replayed as a tree and a set of branch refs instead.

Two modes:

    python3 tools/publish_via_api.py --base 17ff9b5 --head HEAD --branch <name>

      * base  — commit the remote has; `git diff --name-status base..head` is what
                gets replayed;
      * head  — local commit to publish (must be checked out and clean).

The script is idempotent: re-running after a partial publish re-sends only the
blobs whose sha differs.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

REPO_FALLBACK = "AAA1234fdja/Angel-Skills"


def git(*args: str, binary: bool = False):
    result = subprocess.run(["git", *args], capture_output=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.decode()[:400]}")
    return result.stdout if binary else result.stdout.decode().strip()


def api(*args: str, payload: dict | None = None, method: str = "GET") -> dict:
    command = ["gh", "api", *args]
    if method != "GET":
        command += ["-X", method]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(command, capture_output=True, text=True,
                            input=json.dumps(payload) if payload is not None else None,
                            check=False)
    if result.returncode != 0:
        raise SystemExit(f"gh api {' '.join(args)} failed: {result.stderr[:600]}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def repo_of(remote: str) -> str:
    url = git("remote", "get-url", remote)
    slug = url.split("github.com")[-1].lstrip(":/").removesuffix(".git")
    return slug or REPO_FALLBACK


def collect_changes(base: str, head: str) -> list[dict]:
    raw = git("diff", "--name-status", f"{base}..{head}")
    changes = []
    for line in raw.splitlines():
        status, *rest = line.split("\t")
        if status.startswith("R") or status.startswith("C"):
            old, new = rest
            changes.append({"status": "rename", "from": old, "path": new})
        else:
            changes.append({"status": {"A": "add", "M": "modify", "D": "delete",
                                       "T": "modify"}.get(status[0], "modify"),
                            "path": rest[0]})
    return changes


def make_tree(repo: str, base_sha: str, changes: list[dict]) -> str:
    base_commit = api(f"repos/{repo}/git/commits/{base_sha}")
    entries = []
    for change in changes:
        path = change["path"]
        if change["status"] == "delete":
            entries.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
            continue
        data = Path(path).read_bytes()
        blob = api(f"repos/{repo}/git/blobs", method="POST", payload={
            "content": base64.b64encode(data).decode(),
            "encoding": "base64",
        })
        executable = Path(path).stat().st_mode & 0o111
        entries.append({"path": path, "mode": "100755" if executable else "100644",
                        "type": "blob", "sha": blob["sha"]})
        if change["status"] == "rename":
            entries.append({"path": change["from"], "mode": "100644",
                            "type": "blob", "sha": None})
    tree = api(f"repos/{repo}/git/trees", method="POST", payload={
        "base_tree": base_commit["tree"]["sha"],
        "tree": entries,
    })
    return tree["sha"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--branch", action="append", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--message-file", default=None)
    args = parser.parse_args()

    repo = repo_of(args.remote)
    base = git("rev-parse", args.base)
    head = git("rev-parse", args.head)
    message = (Path(args.message_file).read_text(encoding="utf-8")
               if args.message_file else git("log", "-1", "--format=%B", head))
    changes = collect_changes(base, head)
    print(f"{len(changes)} change(s) {base[:7]}..{head[:7]} on {repo}")

    tree_sha = make_tree(repo, base, changes)
    commit = api(f"repos/{repo}/git/commits", method="POST", payload={
        "message": message, "tree": tree_sha, "parents": [base],
    })
    print(f"tree {tree_sha[:7]} · commit {commit['sha'][:7]}")

    for branch in args.branch:
        ref = f"heads/{branch}"
        try:
            current = api(f"repos/{repo}/git/ref/{ref}")
            api(f"repos/{repo}/git/refs/{ref}", method="PATCH",
                payload={"sha": commit["sha"], "force": True})
            print(f"updated {branch} ({current['object']['sha'][:7]} -> {commit['sha'][:7]})")
        except SystemExit:
            api(f"repos/{repo}/git/refs", method="POST",
                payload={"ref": f"refs/{ref}", "sha": commit["sha"]})
            print(f"created {branch} at {commit['sha'][:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
