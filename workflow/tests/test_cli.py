"""CLI tests: the published surface of the package, exercised as a user would.

Each test shells out to ``python3 -m angel.cli`` so the exit code — which is the
part a harness or CI actually reads — is part of what is verified.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

from support import REAL_ROOT, AngelTestCase, Path


class CliTests(AngelTestCase):
    def cli(self, *args: str, root: Path | str | None = None) -> subprocess.CompletedProcess:
        command = [sys.executable, "-m", "angel.cli", "--root", str(root or REAL_ROOT), *args]
        env = dict(os.environ, PYTHONPATH=str(REAL_ROOT))
        return subprocess.run(command, cwd=str(REAL_ROOT), env=env, capture_output=True,
                              text=True, timeout=120)

    # -- read-only commands ------------------------------------------------
    def test_help_lists_every_documented_command(self):
        result = self.cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("list", "show", "plan", "validate", "pack", "install", "where",
                        "route", "run", "journal", "protocol", "contract", "tool", "new"):
            self.assertIn(command, result.stdout)

    def test_list_names_every_skill(self):
        result = self.cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        for skill in self.registry.skills.values():
            self.assertIn(skill.id, result.stdout)

    def test_show_prints_one_skill(self):
        result = self.cli("show", "tdd-workflow")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("tdd-workflow", result.stdout)
        self.assertIn("Exit Criteria", result.stdout)

    def test_show_of_an_unknown_skill_exits_4(self):
        self.assertEqual(self.cli("show", "not-a-skill").returncode, 4)

    def test_validate_is_green_and_exit_zero(self):
        result = self.cli("validate", "--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validate_json_is_machine_readable(self):
        result = self.cli("--json", "validate")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["skills"], len(self.registry.skills))

    def test_route_need_is_deterministic_and_json(self):
        first = json.loads(self.cli("--json", "route", "--need",
                                    "the build is broken").stdout)
        second = json.loads(self.cli("--json", "route", "--need",
                                     "the build is broken").stdout)
        self.assertEqual(first, second)
        self.assertEqual(first["steps"][0]["skill"], "build-fix")

    def test_route_explain_reports_a_score(self):
        payload = json.loads(self.cli("--json", "route", "--explain", "code-review",
                                      "--need", "review the diff").stdout)
        self.assertGreater(payload["score"], 0)

    def test_protocol_list_and_sample(self):
        listed = json.loads(self.cli("--json", "protocol", "--list").stdout)
        self.assertGreaterEqual(len(listed), 6)
        sample = json.loads(self.cli("--json", "protocol", "isa-plan", "--sample").stdout)
        self.assertRegex(sample["digest"], r"^[0-9a-f]{16}$")
        self.assertEqual(sample["message"]["protocol"], "isa-plan")

    def test_contract_check_is_green(self):
        result = self.cli("contract", "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0 problem(s)", result.stdout)

    def test_tool_self_test_runs_every_tool(self):
        result = self.cli("--json", "tool", "--self-test")
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["failed"], 0)
        self.assertGreater(payload["tools"].__len__(), 35)

    def test_tool_run_with_an_explicit_payload(self):
        payload = json.dumps({"command": "git push --force origin main"})
        result = self.cli("--json", "tool", "--run", "safety-guard/classify-command",
                          "--payload", payload)
        self.assertEqual(result.returncode, 8,
                         "a destructive refusal exits 8, not 0: a shell chain must stop")
        body = json.loads(result.stdout)
        self.assertEqual(body["output"]["risk"], "destructive")
        self.assertFalse(body["output"]["allowed"])

    def test_tool_that_advises_no_change_exits_7(self):
        payload = json.dumps({"errors": [{"code": "E_X", "message": "boom"}]})
        result = self.cli("--json", "tool", "--run", "error-recovery/recovery-audit",
                          "--payload", payload)
        self.assertEqual(result.returncode, 7, result.stdout)

    # -- write commands in a throwaway package -----------------------------
    def test_new_registers_a_skill_that_validates_and_routes(self):
        with tempfile.TemporaryDirectory(prefix="angel-new-") as tmp:
            root = Path(tmp)
            (root / "categories.json").write_text(
                (REAL_ROOT / "categories.json").read_text(encoding="utf-8"), encoding="utf-8")
            shutil.copytree(REAL_ROOT / "skills", root / "skills")
            shutil.copy(REAL_ROOT / "EXTENSION-STANDARD.md", root / "EXTENSION-STANDARD.md")
            shutil.copy(REAL_ROOT / "WORKFLOW.md", root / "WORKFLOW.md")
            shutil.copytree(REAL_ROOT / "contracts", root / "contracts")

            created = self.cli("--json", "new", "flaky-selector-fix", "--category", "engineering",
                               "--phase", "test", "--verb", "fix",
                               "--description", "Repair a selector that matches several nodes.",
                               "--when", "a browser test passes locally and fails in CI",
                               root=root)
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            self.assertTrue((root / "skills" / "engineering" / "flaky-selector-fix"
                             / "SKILL.md").is_file())

            validated = self.cli("--json", "validate", root=root)
            body = json.loads(validated.stdout)
            self.assertEqual(body["errors"], [], body["errors"])

            routed = json.loads(self.cli("--json", "route", "--need",
                                         "run flaky-selector-fix here", root=root).stdout)
            self.assertEqual(routed["steps"][0]["skill"], "flaky-selector-fix")

    def test_pack_writes_a_zip_that_contains_the_standard(self):
        with tempfile.TemporaryDirectory(prefix="angel-pack-") as tmp:
            out = Path(tmp) / "workflow.zip"
            result = self.cli("--json", "pack", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.is_file())
            self.assertGreater(out.stat().st_size, 50_000)
            listing = subprocess.run(["unzip", "-Z1", str(out)], capture_output=True,
                                     text=True, check=False)
            if listing.returncode == 0:
                self.assertIn("WORKFLOW.md", listing.stdout)
                self.assertIn("skills/engineering/tdd-workflow/SKILL.md", listing.stdout)

    def test_journal_all_verifies(self):
        result = self.cli("journal", "--all")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("corrupt", result.stdout.lower())
