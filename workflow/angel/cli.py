"""The single entry point: ``workflow``.

Every command prints machine-readable JSON with ``--json`` and a compact human
view otherwise. Exit codes come from the error policy, never from ad-hoc
``sys.exit(1)`` sprinkled around.

    workflow list / show / plan / validate / pack / install / where   (package)
    workflow route / run / journal                                    (execution)
    workflow protocol / contract / tool / new                         (contracts)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import __version__
from . import contracts as contracts_mod
from . import journal as journal_mod
from . import protocols, registry as registry_mod, router, runner, tools
from .errors import AngelError

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------
# output helpers
# --------------------------------------------------------------------------
def emit(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    if isinstance(data, str):
        print(data)
        return
    print(json.dumps(data, ensure_ascii=False, indent=2))


class Console:
    def __init__(self) -> None:
        self.tty = sys.stdout.isatty()

    def _paint(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.tty else text

    def bold(self, text: str) -> str:
        return self._paint("1", text)

    def dim(self, text: str) -> str:
        return self._paint("2", text)

    def green(self, text: str) -> str:
        return self._paint("32", text)

    def red(self, text: str) -> str:
        return self._paint("31", text)

    def yellow(self, text: str) -> str:
        return self._paint("33", text)


C = Console()


def fail(err: AngelError, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"error": err.to_dict()}, ensure_ascii=False, indent=2))
    else:
        print(f"{C.red('✖')} {err.code}: {err.message}")
        hint = err.recovery()["root_cause_hint"]
        if hint:
            print(f"  {C.dim(hint)}")
        if err.context:
            print(f"  {C.dim(json.dumps(err.context, ensure_ascii=False)[:300])}")
    return err.exit_code


def load(root: Path) -> registry_mod.Registry:
    return registry_mod.load(root)


# --------------------------------------------------------------------------
# package commands
# --------------------------------------------------------------------------
def cmd_list(args: argparse.Namespace) -> int:
    reg = load(args.root)
    rows = [s for s in reg.skills.values()
            if (not args.phase or s.phase == args.phase)
            and (not args.category or s.category == args.category)]
    rows.sort(key=lambda s: (reg.category(s.category).order, s.phase, s.id))
    if args.json:
        emit([s.to_dict() for s in rows], True)
        return 0
    if not rows:
        print(C.dim("(no skills match the filter)"))
        return 0
    width = max(len(s.id) for s in rows)
    current = None
    for skill in rows:
        if skill.category != current:
            current = skill.category
            print(f"\n{C.bold(reg.category(skill.category).name)} {C.dim('· ' + current)}")
        tool_mark = f" [{len(skill.tools)} tool{'s' if len(skill.tools) != 1 else ''}]" if skill.tools else ""
        print(f"  {C.green('●')} {skill.id.ljust(width)}  {C.dim(skill.phase.ljust(9))} "
              f"{skill.description[:78]}{C.dim(tool_mark)}")
    print(f"\n{C.dim(f'{len(rows)} skill(s)')}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    reg = load(args.root)
    skill = reg.skill(args.skill)
    if args.json:
        emit(skill.to_dict(with_body=True), True)
        return 0
    print(skill.path.joinpath("SKILL.md").read_text(encoding="utf-8"))
    if skill.tools:
        print("\n--- tools ---")
        for tool in skill.tools:
            print(f"  {tool.id} ({tool.risk}) — {tool.description}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    reg = load(args.root)
    rows = []
    for category in reg.categories:
        have = [s.id for s in reg.skills.values() if s.category == category.id]
        rows.append({
            "category": category.id,
            "name": category.name,
            "status": category.status,
            "gate": category.gate,
            "installed": sorted(have),
            "pending": [p for p in category.pending if p not in have],
        })
    if args.json:
        emit(rows, True)
        return 0
    for row in rows:
        tag = C.green("active") if row["status"] == "activa" else C.yellow(row["status"])
        print(f"\n{C.bold(row['name'])} {C.dim('· ' + row['category'])} · {tag} · "
              f"{len(row['installed'])} installed")
        if row["gate"]:
            print(f"  {C.dim('gate:')} {row['gate']}")
        for skill_id in row["installed"]:
            print(f"  {C.green('✔')} {skill_id}")
        for pending in row["pending"]:
            print(f"  {C.dim('· ' + pending + ' (pending)')}")
    print()
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    reg = load(args.root)
    report = reg.validate()
    contract_report = contracts_mod.validate_all(args.root)
    for row in contract_report:
        if not row["ok"]:
            report["errors"].append(f"contract {row['contract']}: {row['reason']}")

    if args.json:
        emit(report, True)
    else:
        for warning in report["warnings"]:
            print(f"{C.yellow('⚠')} {warning}")
        for error in report["errors"]:
            print(f"{C.red('✖')} {error}")
        ok = not report["errors"] and not (args.strict and report["warnings"])
        mark = C.green("✔ valid") if ok else C.red("✖ invalid")
        print(f"\n{mark} · {report['skills']} skill(s) · {len(report['errors'])} error(s) · "
              f"{len(report['warnings'])} warning(s) · {len(contract_report)} contract(s)")
    if report["errors"]:
        return 1
    if args.strict and report["warnings"]:
        return 2
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    out = Path(args.out).resolve() if args.out else root / "dist" / "workflow.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    include = ["EXTENSION-STANDARD.md", "WORKFLOW.md", "categories.json", "CHANGELOG.md",
               "README.md", "skills", "contracts", "angel", "tests", "ely-extension"]
    targets = [name for name in include if (root / name).exists()]
    if shutil.which("zip") is None:
        fail(AngelError("zip is not available on this system",
                        hint="install zip, or use `workflow pack --tar`"), args.json)
        return 1
    result = subprocess.run(["zip", "-r", "-q", str(out), *targets], cwd=root, check=False)
    if result.returncode != 0:
        return fail(AngelError(f"zip exited with {result.returncode}"), args.json)
    emit({"out": str(out), "entries": len(targets)}, args.json)
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not args.ely:
        return fail(AngelError("install needs --ely <path to the Ely repo>"), args.json)
    dest = Path(args.ely).resolve() / "IDE" / "ely-extensions" / "angel.workflow"
    source = root / "ely-extension"
    if not source.is_dir():
        return fail(AngelError("workflow/ely-extension is missing"), args.json)
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, dirs_exist_ok=True)
    for name in ("categories.json", "EXTENSION-STANDARD.md", "WORKFLOW.md", "README.md"):
        if (root / name).exists():
            shutil.copy2(root / name, dest / name)
    for name in ("skills", "contracts"):
        if (root / name).is_dir():
            shutil.copytree(root / name, dest / name, dirs_exist_ok=True)
    emit({"installed": str(dest)}, args.json)
    print(C.dim("Reload the IDE or the Extensions view."), file=sys.stderr)
    return 0


def cmd_where(args: argparse.Namespace) -> int:
    reg = load(args.root)
    data = {
        "root": str(Path(args.root).resolve()),
        "registry": str(Path(args.root) / registry_mod.REGISTRY),
        "standard": str(Path(args.root) / registry_mod.STANDARD),
        "skills": str(Path(args.root) / "skills"),
        "contracts": str(Path(args.root) / "contracts"),
        "journal": str(Path(args.root) / ".workflow" / "journal"),
        "version": __version__,
        "categories": len(reg.categories),
        "skills": len(reg.skills),
    }
    emit(data, args.json)
    return 0


# --------------------------------------------------------------------------
# execution commands
# --------------------------------------------------------------------------
def cmd_route(args: argparse.Namespace) -> int:
    reg = load(args.root)
    if args.explain:
        emit(router.explain(reg, args.explain, args.need), args.json)
        return 0
    result = router.route(reg, args.need, limit=args.limit, phase=args.phase,
                          category=args.category, min_score=args.min_score)
    if args.json:
        emit(result.to_dict(), True)
        return 0
    if not result.matches:
        print(C.yellow("no skill scored above the threshold") + C.dim(" (try --min-score 0)"))
        return 0
    print(f"\n{C.bold('route')} · {result.need}\n")
    for step in result.steps:
        tools_txt = C.dim(" tools: " + ", ".join(step["tools"])) if step["tools"] else ""
        print(f"  {step['id']}  {C.green(step['skill'])}  {C.dim(step['phase'])}{tools_txt}")
        for reason in step["why"]:
            print(f"      {C.dim('· ' + reason)}")
    if result.unmatched_verbs:
        print(f"\n  {C.yellow('no skill covers:')} {', '.join(result.unmatched_verbs)}")
    print(f"\n{C.dim(json.dumps(result.budget))}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    reg = load(args.root)
    budget = runner.Budget(steps=args.budget_steps, tool_calls=args.budget_tools,
                           seconds=args.budget_seconds)
    machine = runner.Runner(reg, root=args.root, profile=args.profile,
                            allow_destructive=args.allow_destructive, budget=budget)
    try:
        report = machine.run(args.need, tools=not args.no_tools, limit=args.limit,
                             phase=args.phase, category=args.category,
                             dry_run=args.dry_run, continue_on_error=args.keep_going)
    except AngelError as err:
        return fail(err, args.json)
    if args.json:
        emit(report.to_dict(), True)
    else:
        mark = C.green("pass") if report.verdict == "pass" else C.red(report.verdict)
        print(f"\n{C.bold('run')} {report.run_id} · {mark} · score {report.score:.2f}")
        print(f"{C.dim('objective:')} {report.objective}")
        for step in report.steps:
            tool_summary = ", ".join(
                f"{t['tool']}={'ok' if t.get('ok') else ('dry' if t.get('dry_run') else 'fail')}"
                for t in step.tools) or "procedure only"
            print(f"  {step.step_id}  {step.skill:<28} {step.status:<6} {C.dim(tool_summary)}")
        for error in report.errors:
            print(f"  {C.red('✖')} {error.get('code')}: {error.get('message', '')[:90]}")
        print(f"\n{C.dim('journal: ' + report.journal)}")
        print(C.dim(json.dumps(report.budget)))
    return 0 if report.verdict == "pass" else 10


def cmd_journal(args: argparse.Namespace) -> int:
    if args.verify_all:
        rows = journal_mod.list_journals(args.root)
        if args.json:
            emit(rows, True)
            return 0
        for row in rows:
            mark = C.green("✔") if row["ok"] else C.red("✖")
            print(f"{mark} {row['run']}  {row['entries']} entries  {C.dim(row['last'])}")
        return 0
    if not args.run:
        return fail(AngelError("journal needs --run <id> or --all"), args.json)
    journal = journal_mod.open_journal(args.root, args.run)
    report = journal.verify()
    if args.json:
        emit({"verify": report, "tail": journal.tail(args.tail)}, True)
    else:
        mark = C.green("✔ chain ok") if report["ok"] else C.red("✖ chain broken")
        print(f"{mark} · {report['entries']} entries · last {report['last_hash']}")
        for problem in report["problems"]:
            print(f"  {C.red('✖')} {problem}")
        for entry in journal.tail(args.tail):
            print(f"  {entry['seq']:>3} {entry['kind']:<12} {json.dumps(entry['data'], ensure_ascii=False)[:110]}")
    return 0 if report["ok"] else 11


# --------------------------------------------------------------------------
# contract / protocol / tool commands
# --------------------------------------------------------------------------
def cmd_protocol(args: argparse.Namespace) -> int:
    if args.list or not args.kind:
        emit(protocols.describe(), args.json)
        return 0
    try:
        if args.sample:
            emit({"digest": protocols.digest(protocols.parse(protocols.sample(args.kind))),
                  "message": protocols.sample(args.kind)}, args.json)
            return 0
        elif args.file:
            message = protocols.parse(Path(args.file).read_text(encoding="utf-8"))
        elif args.stdin:
            message = protocols.parse(sys.stdin.read())
        else:
            emit(protocols.describe(), args.json)
            return 0
    except AngelError as err:
        return fail(err, args.json)
    emit({"digest": protocols.digest(message), "label": protocols.label(message),
          "message": message.to_dict()}, args.json)
    return 0


def cmd_contract(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if args.list:
        found = contracts_mod.discover(root)
        rows = [{"contract": name, "versions": [c.version for c in versions],
                 "latest": versions[-1].version, "consumers": versions[-1].consumers}
                for name, versions in found.items()]
        if args.json:
            emit(rows, True)
            return 0
        if not rows:
            print(C.dim("(no contracts yet)"))
        for row in rows:
            print(f"  {row['contract']:<26} {row['versions'][-1]:<8} "
                  f"{C.dim('versions: ' + ', '.join(row['versions']))}")
        return 0
    if args.check:
        report = contracts_mod.validate_all(root)
        bad = [row for row in report if not row["ok"]]
        if args.json:
            emit(report, True)
            return 1 if bad else 0
        for row in bad:
            print(f"{C.red('✖')} {row['contract']}: {row['reason']}")
        print(f"\n{len(report)} contract(s), {len(bad)} problem(s)")
        return 1 if bad else 0
    if args.diff:
        name, old, new = args.diff
        try:
            result = contracts_mod.diff_versions(root, name, old, new)
        except AngelError as err:
            return fail(err, args.json)
        if args.json:
            emit(result, True)
            return 0
        print(f"{name}: {old} -> {new} · required bump: {C.bold(result['required_bump'])} · "
              f"declared: {result['declared_bump']} · {'ok' if result['ok'] else C.red('BREAKING')}")
        for change in result["changes"]:
            print(f"  {change['kind']:<32} {change['path']}")
        return 0 if result["ok"] else 6
    if args.validate:
        name, version = args.validate
        try:
            contract = contracts_mod.resolve(root, name, version)
            payload = json.loads(Path(args.file).read_text(encoding="utf-8")) if args.file else json.load(sys.stdin)
            contract.validate(payload)
        except AngelError as err:
            return fail(err, args.json)
        except json.JSONDecodeError as exc:
            return fail(AngelError(f"payload is not JSON: {exc}"), args.json)
        emit({"ok": True, "contract": name, "version": version}, args.json)
        return 0
    emit(protocols.describe(), args.json)
    return 0


def cmd_tool(args: argparse.Namespace) -> int:
    reg = load(args.root)
    box = tools.ToolBox(reg, profile=args.profile, allow_destructive=args.allow_destructive)
    if args.list:
        rows = box.catalog()
        if args.json:
            emit(rows, True)
            return 0
        current = None
        for row in rows:
            if row["skill"] != current:
                current = row["skill"]
                print(f"\n{C.bold(current)} {C.dim('· ' + row['category'])}")
            ok = C.green("✔") if row["authorised"] else C.dim("·")
            print(f"  {ok} {row['id']:<24} {row['risk']:<12} {row['description'][:70]}")
        print(f"\n{C.dim(f'{len(rows)} tool(s) · profile {box.profile}')}")
        return 0
    if args.self_test:
        rows = []
        for row in box.catalog():
            skill_id, tool_id = row["skill"], row["id"]
            payload = box.sample_for(skill_id, tool_id)
            if not payload:
                rows.append({"skill": skill_id, "tool": tool_id, "ok": False,
                             "reason": "no sample payload declared"})
                continue
            if not row["authorised"]:
                rows.append({"skill": skill_id, "tool": tool_id, "ok": None,
                             "reason": f"risk {row['risk']} not allowed by profile {box.profile}"})
                continue
            result = box.run(skill_id, tool_id, payload)
            rows.append({"skill": skill_id, "tool": tool_id, "ok": result.ok,
                         "ms": round(result.ms, 2),
                         "reason": (result.output or {}).get("advice") if result.ok
                         else (result.error or {}).get("message")})
        failed = [r for r in rows if r["ok"] is False]
        if args.json:
            emit({"tools": rows, "failed": len(failed),
                  "skipped": sum(1 for r in rows if r["ok"] is None)}, True)
        else:
            for row in rows:
                mark = (C.green("✔") if row["ok"] else C.red("✖") if row["ok"] is False
                        else C.dim("·"))
                print(f"  {mark} {row['skill']}/{row['tool']:<24} {C.dim(str(row['reason'])[:70])}")
            print(f"\n{C.dim(f'{len(rows)} tool(s) · {len(failed)} failing')}")
        return 0 if not failed else 7
    if not args.run:
        return fail(AngelError("tool needs --run <skill>/<tool> or --self-test"), args.json)
    skill_id, _, tool_id = args.run.partition("/")
    payload = json.loads(args.payload) if args.payload else {}
    try:
        result = box.run(skill_id, tool_id, payload)
    except AngelError as err:
        return fail(err, args.json)
    emit(result.to_dict(), args.json)
    if not result.ok:
        return 7
    # A tool that ran but reported "not ok" is a refusal, and a refusal must not
    # look like success to a shell: `workflow tool ... && deploy` has to stop.
    verdict_ok = (result.output or {}).get("ok", True)
    if verdict_ok is False:
        return 8 if (result.output or {}).get("risk") == "destructive" else 7
    return 0


# --------------------------------------------------------------------------
# scaffolding: register a new skill
# --------------------------------------------------------------------------
SKILL_TEMPLATE = """---
name: {id}
description: {description} Use when {when}.
metadata:
  origin: {origin}
  category: {category}
  phase: {phase}
  status: {status}
  version: 1
---

# {title}

{intro}

## When to Use

- {when_1}
- {when_2}

## When Not to Use

- {not_1}

## Procedure

1. {step_1}
2. {step_2}
3. {step_3}

## Exit Criteria

- [ ] {exit_1}
- [ ] {exit_2}

## Common Failures

| Failure | Fix |
|---|---|
| {fail_1} | {fix_1} |
"""

MANIFEST_TEMPLATE = {
    "id": "{id}",
    "category": "{category}",
    "description": "{description}",
    "phase": "{phase}",
    "verbs": ["{verb}"],
    "triggers": ["{trigger}"],
    "keywords": ["{keyword}"],
    "tools": [],
    "contracts": [],
    "requires": [],
    "routing": {"not_for": []},
    "acceptance": [{"id": "exit", "statement": "the skill's exit criteria are met", "kind": "review"}],
}


def cmd_new(args: argparse.Namespace) -> int:
    root = Path(args.root)
    reg = load(root)
    category = args.category
    try:
        reg.category(category)
    except AngelError as err:
        return fail(err, args.json)
    skill_id = args.id
    if not registry_mod_json_id_ok(skill_id):
        return fail(AngelError(f"invalid skill id {skill_id!r}",
                               hint="lowercase words separated by single hyphens"), args.json)
    if skill_id in reg.skills:
        return fail(AngelError(f"skill {skill_id!r} already exists",
                               hint="ids are stable: pick a new one"), args.json)
    folder = root / "skills" / category / skill_id
    if folder.exists():
        return fail(AngelError(f"folder already exists: {folder}"), args.json)

    description = args.description or f"{skill_id.replace('-', ' ').capitalize()} procedure."
    meta = {
        "id": skill_id, "category": category, "description": description,
        "when": args.when or "the task needs it",
        "origin": "original", "phase": args.phase, "status": "original",
        "title": skill_id.replace("-", " ").title(),
        "intro": "One paragraph on what this procedure buys and what it costs.",
        "when_1": args.when or "the task matches this skill's trigger",
        "when_2": "the work is repeatable and worth standardising",
        "not_1": "the task is a one-off exploration",
        "step_1": "State the trigger and the exit criteria before starting.",
        "step_2": "Do the smallest thing that satisfies the criteria.",
        "step_3": "Record the evidence that the criteria are met.",
        "exit_1": "The exit criteria are written down and checkable.",
        "exit_2": "Evidence is attached (command output, file, or a signed review).",
        "fail_1": "Starting without a trigger", "fix_1": "Read When to Use first",
        "verb": args.verb, "trigger": (args.when or skill_id).lower(),
        "keyword": skill_id.split("-")[0],
    }
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(SKILL_TEMPLATE.format(**meta), encoding="utf-8")
    manifest = json.loads(json.dumps(MANIFEST_TEMPLATE))
    for key, value in list(manifest.items()):
        if isinstance(value, str):
            manifest[key] = meta.get(value.strip("{}"), value)
        elif isinstance(value, list) and value and isinstance(value[0], str):
            manifest[key] = [meta.get(v.strip("{}"), v) for v in value]
    (folder / "skill.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.no_register:
        _register_in_registry(root, category, skill_id, description, meta["origin"], args.phase)

    result = {"created": str(folder), "registered": not args.no_register,
              "next": ["workflow validate", "edit SKILL.md", "add tools under tools/"]}
    emit(result, args.json)
    if not args.json:
        print(C.green("✔") + f" created {folder}")
        print(C.dim("next: workflow validate · edit SKILL.md · add tools/<name>.py"))
    return 0


def registry_mod_json_id_ok(skill_id: str) -> bool:
    import re
    return bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", skill_id or ""))


def _register_in_registry(root: Path, category: str, skill_id: str, description: str,
                          origin: str, phase: str) -> None:
    file = root / registry_mod.REGISTRY
    data = json.loads(file.read_text(encoding="utf-8"))
    for row in data["categories"]:
        if row.get("id") != category:
            continue
        entry = {"id": skill_id, "origin": origin, "status": "original",
                 "phase": phase, "description": description}
        row.setdefault("skills", []).append(entry)
        if skill_id in (row.get("pending") or []):
            row["pending"] = [p for p in row["pending"] if p != skill_id]
        break
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



# --------------------------------------------------------------------------
# argument parsing
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workflow",
        description="Angel workflow: skills as folders, contracts as promises, "
                    "protocols as hand-offs, everything journalled.",
    )
    parser.add_argument("--root", default=str(DEFAULT_ROOT),
                        help="path to the workflow package (default: the one containing this CLI)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--version", action="version", version=f"workflow {__version__}")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("list", help="list skills")
    p.add_argument("--phase")
    p.add_argument("--category")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="show one skill")
    p.add_argument("skill")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("plan", help="installed vs pending per category")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("validate", help="check the package against the standard")
    p.add_argument("--strict", action="store_true", help="warnings become failures")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("pack", help="build the distributable zip")
    p.add_argument("--out")
    p.set_defaults(func=cmd_pack)

    p = sub.add_parser("install", help="install the Ely extension")
    p.add_argument("--ely")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("where", help="paths and counts")
    p.set_defaults(func=cmd_where)

    p = sub.add_parser("route", help="map a need to skills")
    p.add_argument("--need", required=True)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--phase")
    p.add_argument("--category")
    p.add_argument("--min-score", type=float, default=2.5,
                   help="minimum score; a declared verb alone scores 2.2")
    p.add_argument("--explain", help="explain scoring for one skill id")
    p.set_defaults(func=cmd_route)

    p = sub.add_parser("run", help="route and execute, with budget and journal")
    p.add_argument("--need", required=True)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--phase")
    p.add_argument("--category")
    p.add_argument("--profile", default="standard", choices=sorted(tools.PROFILES))
    p.add_argument("--allow-destructive", action="store_true")
    p.add_argument("--no-tools", action="store_true", help="procedure only")
    p.add_argument("--dry-run", action="store_true", help="plan and authorise without executing")
    p.add_argument("--keep-going", action="store_true", help="continue after a failed step")
    p.add_argument("--budget-steps", type=int, default=12)
    p.add_argument("--budget-tools", type=int, default=40)
    p.add_argument("--budget-seconds", type=float, default=300.0)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("journal", help="inspect and verify run journals")
    p.add_argument("--run")
    p.add_argument("--all", dest="verify_all", action="store_true")
    p.add_argument("--tail", type=int, default=10)
    p.set_defaults(func=cmd_journal)

    p = sub.add_parser("protocol", help="list, sample or parse protocol messages")
    p.add_argument("--list", action="store_true")
    p.add_argument("kind", nargs="?")
    p.add_argument("--sample", action="store_true")
    p.add_argument("--file")
    p.add_argument("--stdin", action="store_true")
    p.set_defaults(func=cmd_protocol)

    p = sub.add_parser("contract", help="inspect and check contracts")
    p.add_argument("--list", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--diff", nargs=3, metavar=("NAME", "OLD", "NEW"))
    p.add_argument("--validate", nargs=2, metavar=("NAME", "VERSION"))
    p.add_argument("--file")
    p.set_defaults(func=cmd_contract)

    p = sub.add_parser("tool", help="list or run skill tools")
    p.add_argument("--list", action="store_true")
    p.add_argument("--run", metavar="SKILL/TOOL")
    p.add_argument("--self-test", action="store_true",
                   help="run every tool on its declared sample payload")
    p.add_argument("--payload")
    p.add_argument("--profile", default="standard", choices=sorted(tools.PROFILES))
    p.add_argument("--allow-destructive", action="store_true")
    p.set_defaults(func=cmd_tool)

    p = sub.add_parser("new", help="scaffold and register a new skill")
    p.add_argument("id")
    p.add_argument("--category", required=True)
    p.add_argument("--phase", default="implement", choices=list(registry_mod.PHASES))
    p.add_argument("--verb", default="implement", choices=list(router.VERBS))
    p.add_argument("--description")
    p.add_argument("--when")
    p.add_argument("--no-register", action="store_true")
    p.set_defaults(func=cmd_new)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    args.root = Path(args.root)
    try:
        return int(args.func(args))
    except AngelError as err:
        return fail(err, getattr(args, "json", False))
    except KeyboardInterrupt:  # pragma: no cover - interactive
        return 130
    except Exception as exc:  # noqa: BLE001 - last boundary
        from .errors import guard

        try:
            guard(lambda: (_ for _ in ()).throw(exc))
        except AngelError as err:  # pragma: no cover - defensive
            return fail(err, getattr(args, "json", False))
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
