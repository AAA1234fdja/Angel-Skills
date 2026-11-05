"""Tests for the error policy: a code is a contract, not a string."""

from support import POLICY, AngelTestCase


class PolicyTests(AngelTestCase):
    def test_every_entry_has_the_four_fields(self):
        self.assertGreater(len(POLICY), 20)
        for code, entry in POLICY.items():
            with self.subTest(code=code):
                self.assertTrue(code.startswith("E_"), code)
                self.assertIn(entry["severity"], ("info", "warn", "error", "fatal"))
                self.assertIsInstance(entry["retryable"], bool)
                self.assertIn(entry["owner"],
                              ("user", "author", "producer", "caller", "tool", "runtime"))
                self.assertIsInstance(entry["exit"], int)

    def test_only_transient_failures_are_retryable(self):
        transient = {"E_TOOL_TIMEOUT", "E_TOOL_BUSY"}
        for code, entry in POLICY.items():
            if entry["retryable"]:
                with self.subTest(code=code):
                    self.assertIn(code, transient,
                                  "a non-transient code marked retryable causes loops")

    def test_exit_codes_are_unique_per_family(self):
        families = {"E_TOOL_TIMEOUT": 7, "E_TOOL_INPUT": 7, "E_CONTRACT_INVALID": 6,
                    "E_PROTOCOL_MALFORMED": 5, "E_SKILL_NOT_FOUND": 4,
                    "E_TOOL_DESTRUCTIVE": 8, "E_BUDGET_EXCEEDED": 9,
                    "E_GATE_FAILED": 10, "E_JOURNAL_CORRUPT": 11}
        for code, expected in families.items():
            with self.subTest(code=code):
                self.assertEqual(POLICY[code]["exit"], expected)

    def test_fatal_codes_are_never_retryable(self):
        for code, entry in POLICY.items():
            if entry["severity"] == "fatal":
                with self.subTest(code=code):
                    self.assertFalse(entry["retryable"])

    def test_recovery_blocks_always_answer_three_questions(self):
        from angel.errors import AngelError

        error = AngelError("something", hint="try the other thing", context={"k": "v"})
        recovery = error.recovery()
        self.assertTrue(recovery["root_cause_hint"])
        self.assertIn("safe_retry", recovery)
        self.assertTrue(recovery["stop_condition"])

    def test_payload_is_json_serialisable(self):
        from angel.errors import AngelError

        payload = AngelError("bad input", hint="add the field").to_dict()
        self.assertIn("code", payload)
        self.assertIn("recovery", payload)
        self.assertEqual(payload["recovery"]["root_cause_hint"], "add the field")
        self.assertFalse(payload["retryable"])
