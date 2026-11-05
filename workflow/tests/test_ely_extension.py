"""Ely extension tests: six commands, in both install layouts, against the real pack.

The extension is JavaScript running in an iframe with a sandboxed API, so it is
tested the way it actually runs: a mock `ely` object, every registered command
invoked, and the recorded output checked. A missing Node is a skip, not a failure.
"""

import json
import shutil
import subprocess
import tempfile

from support import REAL_ROOT, AngelTestCase, Path

HARNESS = Path(__file__).with_name("ely-harness.mjs")
BUNDLE_FILES = ("categories.json", "EXTENSION-STANDARD.md", "WORKFLOW.md")


def node_available() -> bool:
    return shutil.which("node") is not None


class ElyExtensionTests(AngelTestCase):
    def setUp(self):
        if not node_available():
            self.skipTest("node is not available")
        self.root = Path(tempfile.mkdtemp(prefix="angel-ely-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    # -- layouts -----------------------------------------------------------
    def _checkout_layout(self) -> Path:
        """The repository as it is: bundle at workflow/, extension at workflow/ely-extension/."""
        bundle = self.root / "workflow"
        shutil.copytree(REAL_ROOT / "skills", bundle / "skills")
        shutil.copytree(REAL_ROOT / "ely-extension", bundle / "ely-extension")
        for name in BUNDLE_FILES:
            shutil.copy(REAL_ROOT / name, bundle / name)
        return bundle / "ely-extension" / "main.js"

    def _installed_layout(self) -> Path:
        """After `workflow install --ely`: the bundle sits next to the extension."""
        dest = self.root / "IDE" / "ely-extensions" / "angel.workflow"
        shutil.copytree(REAL_ROOT / "skills", dest / "skills")
        for name in BUNDLE_FILES:
            shutil.copy(REAL_ROOT / name, dest / name)
        shutil.copy(REAL_ROOT / "ely-extension" / "main.js", dest / "main.js")
        return dest / "main.js"

    def _run(self, entry: Path) -> dict:
        relative = entry.relative_to(self.root)
        result = subprocess.run(["node", str(HARNESS), str(self.root), str(relative)],
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    # -- the extension itself ---------------------------------------------
    def test_the_manifest_declares_six_commands_with_no_network(self):
        manifest = json.loads(
            (REAL_ROOT / "ely-extension" / "ely-extension.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "angel.workflow")
        self.assertEqual(manifest["version"], "0.3.0")
        commands = {c["id"] for c in manifest["contributes"]["commands"]}
        self.assertEqual(commands, {
            "angel.workflow.list", "angel.workflow.phase", "angel.workflow.skill",
            "angel.workflow.tools", "angel.workflow.validate", "angel.workflow.standard",
        })
        permissions = set(manifest["permissions"])
        self.assertNotIn("network", permissions)
        self.assertNotIn("workspace:write", permissions)

    def test_manifest_commands_match_the_registered_ones(self):
        manifest = json.loads(
            (REAL_ROOT / "ely-extension" / "ely-extension.json").read_text(encoding="utf-8"))
        declared = {c["id"] for c in manifest["contributes"]["commands"]}
        for layout in ("checkout", "installed"):
            with self.subTest(layout=layout):
                entry = self._checkout_layout() if layout == "checkout" else self._installed_layout()
                payload = self._run(entry)
                self.assertEqual(set(payload["commands"]), declared)
                self.assertEqual(payload["failures"], [])

    def test_checkout_layout_lists_and_validates_the_whole_pack(self):
        payload = self._run(self._checkout_layout())
        titles = [doc["title"] for doc in payload["documents"]]
        self.assertIn("Workflow · skills", titles)
        self.assertIn("Workflow · validation", titles)
        self.assertIn("EXTENSION-STANDARD.md", titles)
        listing = next(d for d in payload["documents"] if d["title"] == "Workflow · skills")
        self.assertGreater(listing["chars"], 5000)
        status = [m for m in payload["messages"] if "status" in m][-1]["status"]
        self.assertIn("✔ workflow", status)
        self.assertIn(f"{len(self.registry.skills)} skills", status[2])

    def test_installed_layout_finds_its_own_bundle(self):
        payload = self._run(self._installed_layout())
        titles = [doc["title"] for doc in payload["documents"]]
        self.assertIn("Workflow · skills", titles)
        self.assertEqual(payload["failures"], [])
        warnings = [m for m in payload["messages"]
                    if m.get("kind") == "warn" and "categories" in m.get("message", "")]
        self.assertEqual(warnings, [], "the bundle was not found in the installed layout")

    def test_the_phase_command_sends_only_one_phase(self):
        payload = self._run(self._checkout_layout())
        chats = [m["chat"] for m in payload["messages"] if "chat" in m]
        self.assertTrue(chats, "the phase command sent nothing to the chat")
        header = chats[0].splitlines()[0]
        self.assertTrue(header.startswith("# Phase context: "), header)
        phase = header.split(": ", 1)[1]
        for skill in self.registry.skills.values():
            if skill.id in chats[0]:
                self.assertEqual(skill.phase, phase,
                                 f"{skill.id} ({skill.phase}) leaked into a {phase} context")

    def test_the_tools_command_reports_the_composition(self):
        payload = self._run(self._checkout_layout())
        document = next((d for d in payload["documents"] if d["title"].startswith("tools · ")), None)
        self.assertIsNotNone(document, "the tools command produced no document")
        self.assertGreater(document["chars"], 200)

    def test_the_extension_does_not_reference_a_missing_bundle_constant(self):
        source = (REAL_ROOT / "ely-extension" / "main.js").read_text(encoding="utf-8")
        self.assertNotIn("${BUNDLE}", source)
        self.assertIn("resolveBundle", source)
