"""Surface audit: what is installed, where it came from, and what it can reach.

Payload::

    {"layers": ["skills", "hooks", "commands", "servers", "permissions",
                "env", "autoload"],
     "entries": [{"name": "docs-site", "layer": "skills", "provenance": "ecc@2.2.3",
                  "trigger": "when writing docs", "can": ["read", "network"]},
                 {"name": "post-tool", "layer": "hooks", "provenance": "unknown",
                  "trigger": "", "can": ["write", "execute"]}],
     "previous": [{"name": "docs-site", "provenance": "ecc@2.2.1", "can": ["read"]}],
     "owned": ["docs-site"]}

Provenance is required per entry: "unknown" is a finding, because an entry nobody
claims is an entry nobody removes. The blast-radius ranking is capability-first — an
entry named `helper` with `execute` outranks `deploy` with `read`.
"""

LEVELS = ["network", "execute", "write", "read"]
REQUIRED_LAYERS = ("skills", "hooks", "commands", "servers", "permissions", "env",
                   "autoload")


def run(payload):
    layers = [str(x) for x in (payload.get("layers") or [])]
    entries = [e for e in (payload.get("entries") or []) if isinstance(e, dict)]
    owned = set(map(str, payload.get("owned") or []))
    problems = []

    missing_layers = [layer for layer in REQUIRED_LAYERS if layer not in layers]
    if missing_layers:
        problems.append("layers never enumerated: " + ", ".join(missing_layers))

    unknown, untriggerable, orphans, wide = [], [], [], []
    for entry in entries:
        name = str(entry.get("name") or "?")
        provenance = str(entry.get("provenance") or "unknown").strip().lower()
        if provenance in ("", "unknown", "none", "?"):
            unknown.append(name)
        if not str(entry.get("trigger") or "").strip():
            untriggerable.append(name)
        if name not in owned:
            orphans.append(name)
        can = [str(c) for c in (entry.get("can") or [])]
        if ("execute" in can or "network" in can) and not entry.get("justification"):
            wide.append(f"{name} ({'/'.join(c for c in can if c in LEVELS)})")

    if unknown:
        problems.append(f"{len(unknown)} entry(ies) with unknown provenance: "
                        + ", ".join(unknown[:3]))
    if untriggerable:
        problems.append(f"{len(untriggerable)} entry(ies) with no stated trigger: "
                        + ", ".join(untriggerable[:3]))
    if orphans:
        problems.append(f"{len(orphans)} orphan(s) with no owner: " + ", ".join(orphans[:3]))
    if wide:
        problems.append("broad capability without justification: " + "; ".join(wide[:3]))

    previous = {str(e.get("name")): e for e in (payload.get("previous") or [])
                if isinstance(e, dict)}
    widened = []
    for entry in entries:
        name = str(entry.get("name") or "?")
        before = set((previous.get(name) or {}).get("can") or [])
        added = set(str(c) for c in (entry.get("can") or [])) - before
        if added:
            widened.append({"entry": name, "added": sorted(added)})

    ranking = sorted(
        ({"entry": str(e.get("name") or "?"),
          "capabilities": [c for c in LEVELS if c in (e.get("can") or [])]}
         for e in entries),
        key=lambda row: len(row["capabilities"]), reverse=True)

    return {
        "ok": not problems,
        "layers": len(layers),
        "missing_layers": missing_layers,
        "entries": len(entries),
        "unknown_provenance": unknown,
        "untriggerable": untriggerable,
        "orphans": orphans,
        "wide_grants": wide,
        "widened_since_last": widened,
        "highest_blast_radius": [r for r in ranking if r["capabilities"]][:5],
        "problems": problems,
        "advice": ("every entry has an owner, a provenance and a stated trigger"
                   if not problems else "; ".join(problems[:3])),
    }
