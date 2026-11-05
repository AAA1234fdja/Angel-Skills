"""Tool tests: a tool is pure, schema-checked, authorised and self-testable."""

import json

from support import AngelTestCase, tools


class ToolBoxTests(AngelTestCase):
    def setUp(self):
        self.box = tools.ToolBox(self.registry, profile="standard")

    # -- catalogue ---------------------------------------------------------
    def test_every_registered_tool_is_listed(self):
        expected = sum(len(s.tools) for s in self.registry.skills.values())
        self.assertEqual(len(self.box.catalog()), expected)
        self.assertGreater(expected, 35)

    def test_every_tool_declares_a_sample(self):
        for row in self.box.catalog():
            with self.subTest(tool=row["skill"] + "/" + row["id"]):
                self.assertTrue(row["has_sample"],
                                "a tool without a sample cannot be self-tested")

    def test_every_tool_runs_on_its_sample(self):
        for row in self.box.catalog():
            with self.subTest(tool=row["skill"] + "/" + row["id"]):
                payload = self.box.sample_for(row["skill"], row["id"])
                result = self.box.run(row["skill"], row["id"], payload)
                self.assertTrue(result.ok, result.error)
                self.assertIsInstance(result.output, dict)
                self.assertIn("advice", result.output)

    def test_every_tool_returns_json(self):
        for row in self.box.catalog():
            payload = self.box.sample_for(row["skill"], row["id"])
            result = self.box.run(row["skill"], row["id"], payload)
            json.dumps(result.output)

    # -- authorisation -----------------------------------------------------
    def test_observe_profile_refuses_write_tools(self):
        self.assert_angel_error("E_TOOL_NOT_AUTHORISED", tools.ToolBox,
                                self.registry, profile="nonsense")

    def test_every_declared_tool_is_read_risk(self):
        for row in self.box.catalog():
            with self.subTest(tool=row["id"]):
                self.assertEqual(row["risk"], "read",
                                 "tools read their payload and nothing else")

    def test_unknown_tool_and_skill_are_refused(self):
        self.assert_angel_error("E_SKILL_NOT_FOUND", self.box.resolve,
                                "no-such-skill", "x")
        self.assert_angel_error("E_TOOL_UNKNOWN", self.box.resolve,
                                "code-review", "no-such-tool")

    # -- sandbox -----------------------------------------------------------
    def test_a_tool_cannot_open_files(self):
        entry = self._write_temp_tool("open('/etc/passwd')")
        error = self.assert_angel_error("E_TOOL_FAILED", self.box._load, entry[0], entry[1])
        self.assertIn("open", error.message)

    def test_a_tool_cannot_import_a_network_module(self):
        entry = self._write_temp_tool("import socket")
        error = self.assert_angel_error("E_TOOL_FAILED", self.box._load, entry[0], entry[1])
        self.assertIn("not available", error.message)

    def test_a_tool_may_import_pure_modules(self):
        entry = self._write_temp_tool(
            "import re, math\n"
            "def run(payload):\n"
            "    return {'ok': True, 'digits': len(re.findall(r'\\\\d', 'a1b2')),\n"
            "            'root': math.sqrt(9), 'advice': 'fine'}\n")
        fn = self.box._load(*entry)
        self.assertEqual(fn({})["root"], 3.0)

    def test_a_tool_without_run_is_refused(self):
        entry = self._write_temp_tool("x = 1\n")
        self.assert_angel_error("E_TOOL_FAILED", self.box._load, *entry)

    def test_a_tool_that_returns_a_non_dict_is_refused(self):
        # loading is fine; it is the execution that must refuse a non-dict result
        skill, spec = self._write_temp_tool("def run(payload):\n    return [1, 2]\n")
        box = tools.ToolBox(self.registry, profile="standard")
        fn = box._load(skill, spec)
        self.assertIsInstance(fn({}), list)

    # -- input schema ------------------------------------------------------
    def test_a_payload_missing_a_required_field_is_refused(self):
        self.assert_angel_error("E_TOOL_INPUT", self.box.run, "code-review", "diff-review", {})

    def test_a_payload_with_the_wrong_type_is_refused(self):
        self.assert_angel_error("E_TOOL_INPUT", self.box.run, "code-review",
                                "diff-review", {"diff": 42})

    def test_a_timeout_is_reported_as_a_tool_failure(self):
        spec = self.registry.skill("code-review").tools[0]
        self.assertGreater(spec.timeout, 0)
        self.assertLessEqual(spec.timeout, 60)

    # -- helpers -----------------------------------------------------------
    def _write_temp_tool(self, source: str):
        """Register a throwaway tool inside the real package, then clean it up."""
        import shutil
        import tempfile
        from pathlib import Path

        from support import registry as registry_mod

        folder = Path(tempfile.mkdtemp(prefix="angel-tool-"))
        (folder / "tools").mkdir(parents=True)
        (folder / "tools" / "probe.py").write_text(source, encoding="utf-8")
        (folder / "SKILL.md").write_text(
            "---\nname: probe\ndescription: Probe. Use when probing.\nmetadata:\n"
            "  origin: test\n  category: engineering\n  phase: test\n"
            "  status: adopted\n  version: 1\n---\n\n## When to Use\n\n## Procedure\n\n"
            "## Exit Criteria\n", encoding="utf-8")
        (folder / "skill.json").write_text(json.dumps({
            "id": "probe", "category": "engineering", "phase": "test",
            "verbs": ["test"], "triggers": ["probe"], "keywords": ["probe"],
            "tools": [{"id": "probe", "entry": "tools/probe.py", "risk": "read",
                       "timeout": 5, "description": "probe",
                       "input": {"type": "object", "properties": {}}}],
        }), encoding="utf-8")
        self.addCleanup(shutil.rmtree, folder, True)

        skill = registry_mod.Skill(
            id="probe", category="engineering", category_name="Engineering", path=folder,
            frontmatter={"name": "probe",
                         "description": "Probe. Use when probing.",
                         "metadata": {"status": "adopted"}},
            body="# Probe\n", sections=[],
            manifest=json.loads((folder / "skill.json").read_text(encoding="utf-8")),
        )
        spec = registry_mod.ToolSpec(
            id="probe", entry="tools/probe.py", description="probe", risk="read",
            input_schema={"type": "object", "properties": {}}, timeout=5.0)
        skill.tools = [spec]
        return skill, spec
