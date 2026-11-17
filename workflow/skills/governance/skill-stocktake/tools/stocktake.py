"""Stocktake: audit the library as an inventory, not as a pile of documents.

Payload::

    {"as_of": "2026-11-05",
     "skills": [{"id": "code-review", "category": "engineering",
                 "phase": "review", "uses": {"code-review": 412},
                 "tools": ["diff-classifier"], "acceptance_tools": 1,
                 "body_lines": 68, "needs": ["review this diff"]},
                {"id": "commit-hygiene", "category": "engineering",
                 "phase": "implement", "uses": {"commit-hygiene": 7},
                 "tools": ["commit-lint"], "acceptance_tools": 0,
                 "body_lines": 120, "needs": ["review this diff"]}]}

`uses` counts router selections observed in the window; a skill with zero selections
in a large window is not necessarily dead, but a skill with zero selections **and**
no tool **and** no citation is. The tool reports duplicate ownership first, because it
is the only finding that produces a wrong answer rather than a wasted one.
"""


def run(payload):
    skills = [s for s in (payload.get("skills") or []) if isinstance(s, dict)]
    problems = []
    if not skills:
        return {"ok": False, "skills": 0, "findings": [],
                "problems": ["no inventory: a stocktake needs the registry, not memory"],
                "advice": "read categories.json and the skill manifests, then rerun"}

    by_id = {str(s.get("id")): s for s in skills if s.get("id")}
    duplicate_pairs = []
    # a duplicate is a pair of skills whose declared needs intersect both ways
    for a_id, a in by_id.items():
        for need in a.get("needs") or []:
            for b_id, b in by_id.items():
                if b_id == a_id:
                    continue
                if need in (b.get("needs") or []) and a.get("phase") == b.get("phase"):
                    pair = tuple(sorted((a_id, b_id)))
                    if pair not in duplicate_pairs:
                        duplicate_pairs.append(pair)

    dead, no_tool, thin, unmeasurable, drifting = [], [], [], [], []
    for skill_id, skill in sorted(by_id.items()):
        uses = sum((skill.get("uses") or {}).values()) if isinstance(
            skill.get("uses"), dict) else int(skill.get("uses") or 0)
        tools = skill.get("tools") or []
        cited = skill.get("cited_in") or []
        if uses == 0 and not tools and not cited:
            dead.append(skill_id)
        if not tools:
            no_tool.append(skill_id)
        lines = int(skill.get("body_lines") or 0)
        if tools and lines > 110 and len(tools) < 2:
            thin.append(f"{skill_id}: {lines} lines of prose for {len(tools)} tool(s)")
        if int(skill.get("acceptance_tools") or 0) < 1:
            unmeasurable.append(skill_id)
        missing_refs = skill.get("missing_artifacts") or []
        if missing_refs:
            drifting.append(f"{skill_id}: names {', '.join(map(str, missing_refs[:2]))}")
        elif int(skill.get("body_lines") or 0) < 60:
            drifting.append(f"{skill_id}: {lines} lines, below the 60-line standard")

    if duplicate_pairs:
        problems.append("duplicate ownership: " + ", ".join(
            f"{a}/{b}" for a, b in duplicate_pairs[:3]))
    if dead:
        problems.append(f"{len(dead)} dead skill(s) nobody routes to: "
                        + ", ".join(dead[:3]))
    if unmeasurable:
        problems.append(f"{len(unmeasurable)} skill(s) with no executable criterion: "
                        + ", ".join(unmeasurable[:3]))
    if thin:
        problems.append("prose outgrew the tooling: " + "; ".join(thin[:2]))
    if drifting:
        problems.append("drift: " + "; ".join(drifting[:3]))

    findings = [{"kind": "duplicate", "pair": list(pair)} for pair in duplicate_pairs]
    findings += [{"kind": "dead", "skill": s} for s in dead]
    findings += [{"kind": "unmeasurable", "skill": s} for s in unmeasurable]
    findings += [{"kind": "thin", "detail": s} for s in thin]
    findings += [{"kind": "drift", "detail": s} for s in drifting]

    return {
        "ok": not problems,
        "as_of": payload.get("as_of"),
        "skills": len(by_id),
        "with_tools": len(by_id) - len(no_tool),
        "without_tools": len(no_tool),
        "duplicates": [list(p) for p in duplicate_pairs],
        "dead": dead,
        "unmeasurable": unmeasurable,
        "findings": findings,
        "problems": problems,
        "advice": ("no duplicate owner, no dead skill, every skill has an executable "
                   "criterion" if not problems else "; ".join(problems[:3])),
    }
