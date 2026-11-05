"""Catalogue rules: the checks that keep a growing catalogue from rotting.

Three rules arrived with the 0.5 batch and each one exists because the catalogue
grew: an `acceptance` list that is validated rather than decorative, a `sample` on
every tool (the denominator of `tool --self-test`), and a phase/verb vocabulary
wide enough to name what a skill actually does. A rule that is only documented is
a suggestion, so each one is tested here by breaking it on purpose.
"""

from __future__ import annotations

import json
import shutil
import tempfile

from support import REAL_ROOT, AngelTestCase, Path, unittest

from angel import registry, router, tools


def _copy_skill(root: Path, skill_id: str, mutate) -> None:
    """Copy one real skill into a throwaway package and mutate its manifest."""
    source = next(REAL_ROOT.glob(f"skills/*/{skill_id}"))
    target = root / "skills" / source.parent.name / skill_id
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    manifest = json.loads((target / "skill.json").read_text(encoding="utf-8"))
    mutate(manifest)
    (target / "skill.json").write_text(json.dumps(manifest), encoding="utf-8")


class TempCatalogue:
    def __init__(self, skill_id: str) -> None:
        self.skill_id = skill_id
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self.path = Path(tempfile.mkdtemp(prefix="angel-rules-"))
        data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
        for category in data["categories"]:
            category["skills"] = [s for s in category["skills"]
                                  if s["id"] == self.skill_id]
        (self.path / "categories.json").write_text(json.dumps(data), encoding="utf-8")
        shutil.copy(REAL_ROOT / "EXTENSION-STANDARD.md", self.path / "EXTENSION-STANDARD.md")
        _copy_skill(self.path, self.skill_id, lambda m: None)
        return self.path

    def __exit__(self, *exc) -> None:
        if self.path and self.path.exists():
            shutil.rmtree(self.path, ignore_errors=True)


def _errors(root: Path) -> list[str]:
    return registry.load(root).validate()["errors"]


class AcceptanceTests(AngelTestCase):
    def test_every_skill_added_in_05_declares_machine_readable_criteria(self):
        new_skills = ("release-readiness", "api-design", "threat-model",
                      "data-retention", "alert-design", "flaky-test-triage",
                      "dependency-graph", "prototype-spike")
        for skill_id in new_skills:
            with self.subTest(skill=skill_id):
                manifest = json.loads(next(REAL_ROOT.glob(
                    f"skills/*/{skill_id}/skill.json")).read_text(encoding="utf-8"))
                criteria = manifest.get("acceptance") or []
                self.assertTrue(criteria, "no acceptance list")
                for criterion in criteria:
                    self.assertIn(criterion["kind"],
                                  ("tool", "command", "test", "review", "artifact"))
                    self.assertTrue(criterion["statement"].strip())

    def test_each_new_skill_proves_itself_with_a_tool_that_exists(self):
        for skill in self.registry.skills.values():
            criteria = skill.manifest.get("acceptance") or []
            tool_kinds = [c for c in criteria if c.get("kind") == "tool"]
            if not tool_kinds:
                continue
            with self.subTest(skill=skill.id):
                declared = {t.id for t in skill.tools}
                for criterion in tool_kinds:
                    self.assertIn(criterion["tool"], declared)

    def test_an_unknown_acceptance_kind_is_an_error(self):
        with TempCatalogue("release-readiness") as root:
            _copy_skill(root, "release-readiness",
                        lambda m: m.update(acceptance=[{"id": "x",
                                                        "statement": "something",
                                                        "kind": "vibes"}]))
            errors = _errors(root)
            self.assertTrue(any("kind 'vibes'" in e for e in errors), errors)

    def test_an_acceptance_criterion_naming_a_missing_tool_is_an_error(self):
        def mutate(manifest):
            manifest["acceptance"] = [{"id": "x", "statement": "the gate agrees",
                                       "kind": "tool", "tool": "no-such-tool"}]
        with TempCatalogue("release-readiness") as root:
            _copy_skill(root, "release-readiness", mutate)
            errors = _errors(root)
            self.assertTrue(any("no-such-tool" in e for e in errors), errors)

    def test_duplicate_acceptance_ids_and_empty_statements_are_errors(self):
        def mutate(manifest):
            manifest["acceptance"] = [
                {"id": "dup", "statement": "one", "kind": "review"},
                {"id": "dup", "statement": "  ", "kind": "review"}]
        with TempCatalogue("release-readiness") as root:
            _copy_skill(root, "release-readiness", mutate)
            errors = _errors(root)
            self.assertTrue(any("duplicate id" in e for e in errors), errors)
            self.assertTrue(any("no statement" in e for e in errors), errors)


class SampleTests(AngelTestCase):
    def test_every_shipped_tool_has_a_sample(self):
        for skill in self.registry.skills.values():
            for spec in skill.tools:
                with self.subTest(tool=f"{skill.id}/{spec.id}"):
                    self.assertTrue(spec.sample, "without a sample it cannot be self-tested")

    def test_a_tool_without_a_sample_fails_validation(self):
        with TempCatalogue("dependency-graph") as root:
            _copy_skill(root, "dependency-graph",
                        lambda m: [t.pop("sample", None) for t in m["tools"]])
            errors = _errors(root)
            self.assertTrue(any("no sample payload" in e for e in errors), errors)

    def test_the_self_test_denominator_matches_the_catalogue(self):
        """`tool --self-test` reports a count; that count must be every tool."""
        box = tools.ToolBox(self.registry, profile="standard")
        catalog = box.catalog()
        declared = sum(len(skill.tools) for skill in self.registry.skills.values())
        self.assertEqual(len(catalog), declared)
        counts = {}
        for row in catalog:
            result = box.run(row["skill"], row["id"],
                             box.sample_for(row["skill"], row["id"]))
            with self.subTest(tool=f"{row['skill']}/{row['id']}"):
                self.assertTrue(result.ok, result.error)
                # every tool reports a verdict; a diagnostic that cannot say
                # `ok: false` would not be a diagnostic
                self.assertIn("advice", result.output)
            counts[row["skill"]] = counts.get(row["skill"], 0) + 1
        self.assertEqual(sum(counts.values()), declared)


class VocabularyTests(AngelTestCase):
    def test_every_phase_declared_in_the_registry_is_a_known_phase(self):
        data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
        for phase in data["rules"]["phases"]:
            self.assertIn(phase, registry.PHASES)
        for skill in self.registry.skills.values():
            self.assertIn(skill.phase, registry.PHASES, skill.id)

    def test_every_verb_declared_by_a_skill_can_be_routed(self):
        for skill in self.registry.skills.values():
            for verb in skill.manifest.get("verbs") or []:
                with self.subTest(skill=skill.id, verb=verb):
                    self.assertIn(verb, router.VERBS)

    def test_the_two_phase_orderings_are_the_same_ordering(self):
        self.assertEqual(tuple(registry.PHASES), tuple(router.PHASE_ORDER))

    def test_shipping_is_its_own_act_and_routes(self):
        self.assertIn("ship", router.VERBS)
        self.assertIn("ship", router.PHASE_ORDER)
        self.assertEqual(len(router.PHASE_ORDER), len(set(router.PHASE_ORDER)))
        result = router.route(self.registry, "can we ship this release today")
        self.assertEqual(result.skill_ids[0], "release-readiness")

    def test_each_new_skill_routes_from_its_own_trigger(self):
        cases = {
            "release-readiness": "is it safe to deploy, what is the rollback plan",
            "api-design": "define the endpoint surface and its idempotency",
            "threat-model": "threat model this new trust boundary",
            "data-retention": "how long do we keep personal data, purge policy",
            "alert-design": "design an alert for checkout failures on call",
            "flaky-test-triage": "the test is flaky and failed once passed on retry",
            "dependency-graph": "find the circular dependency in the module graph",
            "prototype-spike": "run a spike with a timebox on feasibility",
        }
        for skill_id, need in cases.items():
            with self.subTest(skill=skill_id, need=need):
                self.assertEqual(router.route(self.registry, need).skill_ids[0], skill_id)


class NewSkillContentTests(AngelTestCase):
    """The eight new skills must obey the same standard as the rest of the pack."""

    NEW = ("release-readiness", "api-design", "threat-model", "data-retention",
           "alert-design", "flaky-test-triage", "dependency-graph", "prototype-spike")

    def test_every_new_skill_has_a_tool_a_sample_and_an_exit_criterion(self):
        for skill_id in self.NEW:
            skill = self.registry.skill(skill_id)
            with self.subTest(skill=skill_id):
                self.assertTrue(skill.tools)
                self.assertTrue(all(t.sample for t in skill.tools))
                self.assertIn("Exit Criteria", skill.sections)
                self.assertIn("When Not to Use", skill.sections)
                self.assertTrue(skill.triggers)

    def test_every_new_tool_is_pure_and_read_risk(self):
        for skill_id in self.NEW:
            skill = self.registry.skill(skill_id)
            for spec in skill.tools:
                source = (skill.path / spec.entry).read_text(encoding="utf-8")
                with self.subTest(tool=f"{skill_id}/{spec.id}"):
                    self.assertEqual(spec.risk, "read")
                    for forbidden in ("import os", "import socket", "open(",
                                      "subprocess", "requests"):
                        self.assertNotIn(forbidden, source)

    def test_every_new_tool_reports_a_denominator_and_an_advice(self):
        box = tools.ToolBox(self.registry, profile="standard")
        for skill_id in self.NEW:
            skill = self.registry.skill(skill_id)
            for spec in skill.tools:
                result = box.run(skill_id, spec.id,
                                 box.sample_for(skill_id, spec.id))
                with self.subTest(tool=f"{skill_id}/{spec.id}"):
                    self.assertTrue(result.ok, result.error)
                    self.assertIn("ok", result.output)
                    self.assertTrue(result.output["advice"])

    def test_the_diagnostic_tools_can_say_no(self):
        """A reviewer that always passes is not a reviewer."""
        box = tools.ToolBox(self.registry, profile="standard")
        failing = {
            ("release-readiness", "release-gate"): {"blocked": "communication"},
            ("dependency-graph", "dependency-audit"): {"cycle": "infra.db"},
            ("threat-model", "threat-coverage"): {"empty": "boundaries"},
        }
        for (skill_id, tool_id), expectation in failing.items():
            sample = box.sample_for(skill_id, tool_id)
            if "blocked" in expectation:
                for gate in sample["gates"]:
                    if gate["id"] == expectation["blocked"]:
                        gate["status"] = "blocked"
            if "cycle" in expectation:
                sample["edges"] = [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]
            if "empty" in expectation:
                sample = {"boundaries": []}
            result = box.run(skill_id, tool_id, sample)
            with self.subTest(tool=f"{skill_id}/{tool_id}"):
                self.assertTrue(result.ok, result.error)
                self.assertFalse(result.output["ok"], "the tool passed a broken input")

    def test_changelog_lint_now_requires_an_audience(self):
        box = tools.ToolBox(self.registry, profile="standard")
        without = {"entries": [{"version": "1.0.0", "type": "added",
                                "text": "new endpoint"}]}
        result = box.run("changelog-discipline", "changelog-lint", without)
        self.assertTrue(result.ok, result.error)
        self.assertFalse(result.output["ok"])
        self.assertTrue(any("audience" in p for p in result.output["problems"]))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
