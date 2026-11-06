"""Install gate: may this artefact enter the harness, and on what terms?

Payload::

    {"name": "ecc-rules", "source": {"repo": "affaan-m/ECC", "ref": "b38be6a"},
     "integrity": "sha256:…", "executable_surface": ["hooks/pre-tool.sh"],
     "reviewed_files": ["hooks/pre-tool.sh", "install.sh"],
     "capability_delta": {"hooks": ["execute"], "skills": ["read"]},
     "removal_path": "ecc uninstall --keep-config", "removal_tested": true,
     "update_policy": {"reviewer": "platform", "evidence": ["diff", "changelog"]}}

A branch name, `latest`, or a tag that can move is refused: the question is which
exact bytes are trusted, and only a commit or an integrity hash answers it. An
unreviewed file that executes is refused too — a README review is not a review.
"""

MOVING = {"main", "master", "head", "latest", "trunk", "develop", "nightly"}
EXECUTABLE = {"hooks", "install", "servers", "permissions", "autoload"}


def run(payload):
    source = payload.get("source") or {}
    ref = str(source.get("ref") or "").strip().lower()
    repo = str(source.get("repo") or "").strip()
    integrity = str(payload.get("integrity") or "").strip()
    surface = [str(x) for x in (payload.get("executable_surface") or [])]
    reviewed = set(map(str, payload.get("reviewed_files") or []))
    delta = payload.get("capability_delta") or {}
    problems = []

    if not repo:
        problems.append("no source named: a package with no origin cannot be trusted "
                        "or removed")
    if not ref:
        problems.append("no ref: pin a commit or provide an integrity hash")
    elif ref in MOVING or len(ref) < 7:
        problems.append(f"moving ref '{ref}': a branch or short tag is not a version")
    if not integrity and not (ref and len(ref) >= 7 and ref not in MOVING):
        problems.append("no integrity: neither a commit nor a hash identifies the bytes")
    for item in surface:
        if item not in reviewed:
            problems.append(f"{item} executes and was not reviewed")
    if not delta:
        problems.append("no capability delta: 'it only adds docs' is a claim, not a "
                        "measurement")
    for layer, caps in (delta or {}).items():
        if layer in EXECUTABLE and not caps:
            problems.append(f"layer '{layer}' declared with no capability listed")
    if not str(payload.get("removal_path") or "").strip():
        problems.append("no removal path: installing without one is a one-way door")
    if str(payload.get("removal_path") or "").strip() and payload.get("removal_tested") is not True:
        problems.append("removal path never executed: test it before you need it")
    policy = payload.get("update_policy") or {}
    if not str(policy.get("reviewer") or "").strip():
        problems.append("no reviewer for bumps: a pin nobody updates becomes a freeze")
    if not (policy.get("evidence") or []):
        problems.append("no evidence required for a bump: say what a bump must show")

    return {
        "ok": not problems,
        "name": payload.get("name"),
        "pinned_to": ref or None,
        "capability_delta": {k: list(v or []) for k, v in (delta or {}).items()},
        "widest_layer": max((delta or {}).items(), key=lambda kv: len(kv[1] or []),
                            default=("none", []))[0],
        "decision": "install" if not problems else "refuse",
        "problems": problems,
        "advice": ("install, pinned and reviewable, with a tested removal path"
                   if not problems else "; ".join(problems[:3])),
    }
