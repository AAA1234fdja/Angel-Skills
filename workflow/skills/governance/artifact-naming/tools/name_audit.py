"""Name audit: will a stranger find and trust this artefact?

Payload::

    {"artifacts": [{"name": "report-quarterly-1.2.0-2026-11-05.pdf",
                    "version": "1.2.0", "date": "2026-11-05",
                    "provenance": {"commit": "abc123", "job": "42",
                                   "checksum": "sha256:...", "produced": "2026-11-05"}}]}

Four checks: a status word in the name (`final`, `latest`, `copy` — the four words
that make a name a question), a date that is not ISO-8601, characters that shells and
filesystems disagree about, and two artefacts claiming the same version.
"""

STATUS_WORDS = ("final", "latest", "new", "old", "copy", "real", "v2-real",
                "backup", "temp", "tmp", "draft", "test", "fixed", "def")
BAD_CHARS = (" ", "_", "(", ")", "[", "]", "#", "%", "&", "+", "'", '"', ",",
             "á", "é", "í", "ó", "ú", "ñ", "ü")
VERSION_CHARS = ("0123456789.")


def _bad_date(date):
    text = str(date or "")
    if len(text) != 10 or text[4] != "-" or text[7] != "-":
        return True
    return not (text[:4].isdigit() and text[5:7].isdigit() and text[8:].isdigit())


def run(payload):
    artifacts = payload.get("artifacts") or []
    problems, rows = [], []
    versions = {}

    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict) or not artifact.get("name"):
            problems.append(f"artifacts[{index}]: no name")
            continue
        name = str(artifact["name"])
        stem = name.rsplit(".", 1)[0]
        issues = []
        lowered = stem.lower()
        for word in STATUS_WORDS:
            if word in lowered.split("-") or f"-{word}" == lowered[-len(word) - 1:] \
                    or word in lowered.split("_"):
                issues.append(f"status word {word!r} in the name: status is metadata")
                break
        for char in BAD_CHARS:
            if char in name:
                issues.append(f"character {char!r} breaks shells or filesystems")
                break
        if name != name.lower():
            issues.append("mixed case: case-insensitive filesystems will merge names")
        version = str(artifact.get("version") or "")
        if not version:
            issues.append("no version")
        elif not all(c in VERSION_CHARS for c in version) or version.count(".") != 2:
            issues.append(f"version {version!r} is not x.y.z")
        else:
            versions.setdefault(version, []).append(name)
        if _bad_date(artifact.get("date")):
            issues.append(f"date {artifact.get('date')!r} is not ISO-8601")
        provenance = artifact.get("provenance") or {}
        for field in ("commit", "job", "checksum"):
            if not str(provenance.get(field) or "").strip():
                issues.append(f"no provenance.{field}: the artefact cannot be traced")
        rows.append({"name": name, "version": version, "issues": issues})
        problems.extend(f"{name}: {issue}" for issue in issues)

    for version, names in versions.items():
        if len(names) > 1:
            problems.append(f"version {version} claimed by {len(names)} artefacts: "
                            + ", ".join(names[:3]))
    if not artifacts:
        problems.append("no artefacts audited")
    return {
        "ok": not problems,
        "artifacts": len(rows),
        "rows": rows,
        "problems": problems,
        "advice": ("every name is traceable, versioned and safe for tools" if not problems
                   else "; ".join(problems[:3])),
    }
