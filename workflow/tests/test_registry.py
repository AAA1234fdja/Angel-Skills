"""Registry tests: the catalogue and the disk must never disagree."""

import json

from support import REAL_ROOT, AngelTestCase, TempPackage, registry


class RegistryTests(AngelTestCase):
    def test_every_registered_skill_loads(self):
        self.assertGreaterEqual(len(self.registry.skills), 40)
        for skill in self.registry.skills.values():
            with self.subTest(skill=skill.id):
                self.assertEqual(skill.category, skill.manifest["category"])
                self.assertTrue((skill.path / "SKILL.md").is_file())

    def test_validate_is_green_on_the_real_package(self):
        report = self.registry.validate()
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])

    def test_every_skill_declares_a_phase_and_status(self):
        allowed_phases = set(json.loads(
            (REAL_ROOT / "categories.json").read_text(encoding="utf-8"))["rules"]["phases"])
        for skill in self.registry.skills.values():
            with self.subTest(skill=skill.id):
                self.assertIn(skill.phase, allowed_phases)
                status = skill.frontmatter.get("metadata", {}).get("status")
                self.assertIn(status, ("adopted", "original", "adapted", "experimental"),
                              f"{skill.id} status is {status!r}")

    def test_skill_ids_are_unique_and_match_folder_names(self):
        seen = {}
        for skill in self.registry.skills.values():
            with self.subTest(skill=skill.id):
                self.assertNotIn(skill.id, seen, f"duplicated by {seen.get(skill.id)}")
                seen[skill.id] = skill.category
                self.assertEqual(skill.path.name, skill.id)

    def test_a_skill_missing_from_the_registry_is_an_error(self):
        with TempPackage(["tdd-workflow"]) as root:
            stray = root / "skills" / "engineering" / "stray-skill"
            stray.mkdir(parents=True)
            (stray / "SKILL.md").write_text(
                "---\nname: stray-skill\ndescription: x. Use when x.\nmetadata:\n"
                "  origin: x\n  category: engineering\n  phase: test\n"
                "  status: adopted\n  version: 1\n---\n\n# x\n", encoding="utf-8")
            report = registry.load(root).validate()
            self.assertTrue(any("on disk but not registered" in e for e in report["errors"]),
                            report["errors"])

    def test_a_registered_skill_missing_on_disk_is_an_error(self):
        with TempPackage(["tdd-workflow", "code-review"]) as root:
            import shutil

            shutil.rmtree(root / "skills" / "engineering" / "code-review")
            report = registry.load(root).validate()
            self.assertTrue(any("no SKILL.md on disk" in e for e in report["errors"]),
                            report["errors"])
