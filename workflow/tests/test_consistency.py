"""Consistency tests: every referenced path, command and contract must exist.

These are the tests that keep the package honest as it grows. Each one fails when a
skill cites something that is no longer true — which is the failure mode that turns
a catalogue into folklore.
"""

import json
import re

from support import REAL_ROOT, AngelTestCase, contracts

BACKTICKED_COMMAND = re.compile(r"`(workflow [a-z][a-z-]*(?: [^`]*)?)`")


class ReferenceTests(AngelTestCase):
    def test_every_skill_file_has_the_required_sections(self):
        rules = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))["rules"]
        required = rules["requiredSections"]
        for skill in self.registry.skills.values():
            with self.subTest(skill=skill.id):
                for heading in required:
                    self.assertIn(heading, skill.body,
                                  f"{skill.id} has no '## {heading}' section")

    def test_every_description_states_a_trigger_and_fits_the_limit(self):
        rules = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))["rules"]
        limit = rules["maxDescriptionChars"]
        for skill in self.registry.skills.values():
            with self.subTest(skill=skill.id):
                description = skill.description
                self.assertIn("Use when", description)
                self.assertLessEqual(len(description), limit)

    def test_every_skill_body_respects_the_line_budget(self):
        rules = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))["rules"]
        budget = rules["maxBodyLines"]
        for skill in self.registry.skills.values():
            with self.subTest(skill=skill.id):
                self.assertLessEqual(len(skill.body.splitlines()), budget)

    def test_every_tool_entry_point_exists_and_compiles(self):
        compile_errors = []
        for skill in self.registry.skills.values():
            for spec in skill.tools:
                path = skill.path / spec.entry
                with self.subTest(tool=f"{skill.id}/{spec.id}"):
                    self.assertTrue(path.is_file(), f"missing {path}")
                    try:
                        compile(path.read_text(encoding="utf-8"), str(path), "exec")
                    except SyntaxError as exc:  # pragma: no cover - failure path
                        compile_errors.append(f"{skill.id}/{spec.id}: {exc}")
        self.assertEqual(compile_errors, [])

    def test_every_tool_schema_is_inside_the_supported_subset(self):
        from angel import jsonschema

        for skill in self.registry.skills.values():
            for spec in skill.tools:
                with self.subTest(tool=f"{skill.id}/{spec.id}"):
                    problems = jsonschema.check_schema(spec.input_schema)
                    self.assertEqual(problems, [])

    def test_every_declared_contract_resolves(self):
        found = contracts.discover(REAL_ROOT)
        for skill in self.registry.skills.values():
            for reference in skill.contracts:
                name, _, version = reference.partition("@")
                with self.subTest(skill=skill.id, reference=reference):
                    self.assertIn(name, found)
                    if version:
                        self.assertIn(version, [c.version for c in found[name]])

    def test_every_registered_category_has_a_description_and_gate(self):
        data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
        for category in data["categories"]:
            with self.subTest(category=category["id"]):
                self.assertTrue(category["description"])
                self.assertTrue(category["gate"])
                self.assertIn(category["status"], ("activa", "pendiente"))

    def test_no_category_is_left_pending(self):
        data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
        pending = [c["id"] for c in data["categories"] if c["status"] != "activa"]
        self.assertEqual(pending, [], f"pending categories: {pending}")

    def test_referenced_workflow_commands_exist_in_the_cli(self):
        cli = (REAL_ROOT / "angel" / "cli.py").read_text(encoding="utf-8")
        known = set(re.findall(r'add_parser\("([a-z]+)"', cli))
        seen = set()
        for skill in self.registry.skills.values():
            for command in BACKTICKED_COMMAND.findall(skill.body):
                word = command.split()[1]
                seen.add(word)
                with self.subTest(skill=skill.id, command=command):
                    self.assertIn(word, known,
                                  f"{skill.id} references a command that does not exist")
        self.assertTrue(seen, "no skill documents a command: suspicious")

    def test_the_standard_and_the_main_document_exist_and_are_linked(self):
        data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
        standard = REAL_ROOT / data["standard"]
        main = REAL_ROOT / data["main"]
        self.assertTrue(standard.is_file(), standard)
        self.assertTrue(main.is_file(), main)
        self.assertIn("EXTENSION-STANDARD.md", main.read_text(encoding="utf-8"))

    def test_the_readme_documents_the_current_version(self):
        from angel import __version__

        readme = (REAL_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(__version__, readme)
        changelog = (REAL_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(__version__, changelog)

    def test_no_skill_cites_a_path_that_does_not_exist(self):
        missing = []
        pattern = re.compile(r"`(skills/[\w/-]+)`")
        for skill in self.registry.skills.values():
            for cited in pattern.findall(skill.body):
                if not (REAL_ROOT / cited).exists():
                    missing.append(f"{skill.id} cites {cited}")
        self.assertEqual(missing, [])
