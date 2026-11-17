"""Cross-check declared dependencies against imports.

Payload::

    {"declared": [{"name": "requests", "version": ">=2", "pinned": false,
                   "licence": "Apache-2.0", "last_release_days": 30,
                   "transitive": 6, "install_scripts": false}],
     "imports": ["requests", "json"]}
"""

IMPORT_ALIASES = {"pyyaml": "yaml", "pillow": "PIL", "beautifulsoup4": "bs4"}


def _normalise(name):
    return str(name or "").strip().lower().replace("-", "_")


def run(payload):
    declared = list(payload.get("declared") or [])
    imports = {_normalise(i) for i in payload.get("imports") or []}
    rows, unused, loose, risky = [], [], [], []

    for dep in declared:
        name = str(dep.get("name") or "")
        key = _normalise(name)
        alias = IMPORT_ALIASES.get(key, key)
        used = key in imports or _normalise(alias) in imports
        pinned = bool(dep.get("pinned"))
        scripts = bool(dep.get("install_scripts"))
        age = dep.get("last_release_days")
        licence = dep.get("licence")
        transitive = int(dep.get("transitive") or 0)

        problems = []
        if not used:
            problems.append("not imported")
            unused.append(name)
        if not pinned:
            problems.append("not pinned")
            loose.append(name)
        if scripts:
            problems.append("install script")
            risky.append(name)
        if age is not None and int(age) > 730:
            problems.append(f"last release {age} days ago")
        if not licence:
            problems.append("licence unknown")
        if transitive > 50:
            problems.append(f"{transitive} transitive packages")

        rows.append({"dependency": name, "used": used, "pinned": pinned,
                     "licence": licence, "transitive": transitive,
                     "problems": problems})

    return {
        "ok": not unused and not risky,
        "dependencies": rows,
        "unused": unused,
        "unpinned": loose,
        "with_install_scripts": risky,
        "advice": ("no removable or risky dependency" if not unused and not risky else
                   "remove unused first: " + ", ".join(unused[:5])),
    }
