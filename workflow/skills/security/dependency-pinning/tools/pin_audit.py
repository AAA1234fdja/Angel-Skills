"""Pin audit: is what ships reproducible, and is the surface known?

Payload::

    {"lockfile": "poetry.lock",
     "packages": [{"name": "requests", "version": "2.31.0", "direct": true,
                   "hash": "sha256:9f...", "requires": ["urllib3", "certifi"]},
                  {"name": "urllib3", "version": "2.0.7", "direct": false,
                   "hash": "sha256:aa...", "requires": []}],
     "declared_ranges": ["requests>=2.0,<3"]}

A range in the manifest is acceptable when a lockfile exists; a range in the
lockfile is not. The tool reports the transitive surface (the number that surprises
people), duplicate versions, missing hashes and floating entries, and it separates
"pinned and updated" from "pinned and frozen" by asking for the update path.
"""

import re

EXACT = re.compile(r"^\d+\.\d+(\.\d+)?([-+.\w]+)?$")


def run(payload):
    packages = payload.get("packages") or []
    lockfile = payload.get("lockfile")
    floating, unhashed, duplicates = [], [], {}
    direct = transitive = 0
    known = set()

    for index, package in enumerate(packages):
        if not isinstance(package, dict) or not package.get("name"):
            floating.append(f"packages[{index}] has no name")
            continue
        name = str(package["name"])
        version = str(package.get("version") or "")
        if package.get("direct"):
            direct += 1
        else:
            transitive += 1
        if not EXACT.match(version):
            floating.append(f"{name}@{version or '?'}: not an exact version")
        if not str(package.get("hash") or "").strip():
            unhashed.append(name)
        duplicates.setdefault(name, set()).add(version)
        known.add(name)

    for name in list(duplicates):
        if len(duplicates[name]) > 1:
            duplicates[name] = sorted(duplicates[name])
        else:
            del duplicates[name]

    problems = []
    if not lockfile:
        problems.append("no lockfile recorded: a range without a lockfile is a guess")
    if floating:
        problems.extend(f"floating dependency: {f}" for f in floating[:5])
    if unhashed:
        problems.append(f"{len(unhashed)} package(s) without an integrity hash: "
                        + ", ".join(unhashed[:3]))
    if duplicates:
        problems.append("same package resolved to several versions: "
                        + ", ".join(sorted(duplicates)[:3]))
    if not packages:
        problems.append("no packages listed")
    if packages and not payload.get("update_path"):
        problems.append("no update path: a pin nobody updates is a vulnerability "
                        "with a date on it")
    ratio = round(transitive / direct, 2) if direct else None
    if ratio is not None and ratio > 20:
        problems.append(f"{transitive} transitive packages for {direct} direct: the "
                        "surface shipped is much larger than the one chosen")

    return {
        "ok": not problems,
        "lockfile": lockfile,
        "direct": direct,
        "transitive": transitive,
        "surface": direct + transitive,
        "transitive_ratio": ratio,
        "floating": floating,
        "unhashed": unhashed,
        "duplicates": {k: v for k, v in duplicates.items()},
        "unknown_requires": sorted({r for p in packages if isinstance(p, dict)
                                    for r in (p.get("requires") or [])
                                    if r not in known})[:5],
        "problems": problems,
        "advice": ("every shipped package is exact, hashed and single-version"
                   if not problems else "; ".join(problems[:3])),
    }
