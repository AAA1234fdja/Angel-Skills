"""Protocol tests: a malformed message is rejected before it is processed."""

import json

from support import AngelTestCase, Path, WORKFLOW, protocols


class EnvelopeTests(AngelTestCase):
    def test_every_protocol_round_trips(self):
        for kind in protocols.CONSUMERS:
            with self.subTest(protocol=kind):
                message = protocols.make(kind, **self.payload_for(kind))
                wire = message.to_dict()
                json.dumps(wire)  # must be serialisable
                parsed = protocols.parse(wire)
                self.assertEqual(parsed.protocol, kind)
                self.assertEqual(protocols.digest(parsed), protocols.digest(message))

    def payload_for(self, kind: str) -> dict:
        return {
            "isa-plan": {"task_id": "t1", "objective": "verify the change",
                         "steps": [{"id": "s1", "skills": ["verification-loop"],
                                    "phase": "verify", "verb": "verify", "tools": []}]},
            "yev-dispatch": {"task_id": "t1", "step_id": "s1", "skills": ["verification-loop"],
                             "tools": ["gate"],
                             "criteria": [{"id": "c1", "statement": "gate ran"}]},
            "zev-evidence": {"task_id": "t1", "origin": "zev", "target": "wev",
                             "claims": [{"statement": "x", "source": "y"}]},
            "xev-result": {"task_id": "t1", "step_id": "s1", "status": "ok",
                           "outputs": {"ok": True}},
            "wev-verdict": {"task_id": "t1", "step_id": "s1", "verdict": "pass",
                            "score": 1.0, "findings": []},
            "ely-meta": {"task_id": "t1", "objective_met": True, "coverage": 1.0},
        }[kind]

    def test_unknown_protocol_is_rejected(self):
        error = self.assert_angel_error(
            "E_PROTOCOL_UNKNOWN", protocols.parse,
            {"protocol": "made-up", "version": "1.0", "task_id": "t",
             "origin": "isa", "target": "yev"})
        self.assertIn("isa-plan", error.hint)

    def test_unknown_version_is_rejected(self):
        self.assert_angel_error(
            "E_PROTOCOL_VERSION", protocols.parse,
            {"protocol": "isa-plan", "version": "99.0", "task_id": "t",
             "origin": "isa", "target": "yev"})

    def test_wrong_target_is_rejected(self):
        self.assert_angel_error(
            "E_PROTOCOL_TARGET", protocols.parse,
            {"protocol": "isa-plan", "version": "1.0", "task_id": "t",
             "origin": "isa", "target": "xev", "objective": "x",
             "steps": [{"id": "s1", "skills": ["tdd-workflow"]}]})

    def test_missing_envelope_field_is_rejected(self):
        self.assert_angel_error(
            "E_PROTOCOL_MALFORMED", protocols.parse,
            {"protocol": "isa-plan", "version": "1.0", "origin": "isa", "target": "yev"})

    def test_plan_without_steps_is_rejected(self):
        self.assert_angel_error(
            "E_PROTOCOL_MALFORMED", protocols.parse,
            {"protocol": "isa-plan", "version": "1.0", "task_id": "t", "origin": "isa",
             "target": "yev", "objective": "something real", "steps": []})

    def test_plan_with_duplicate_step_ids_is_rejected(self):
        self.assert_angel_error(
            "E_PROTOCOL_MALFORMED", protocols.parse,
            {"protocol": "isa-plan", "version": "1.0", "task_id": "t", "origin": "isa",
             "target": "yev", "objective": "something real",
             "steps": [{"id": "s1", "skills": ["tdd-workflow"]},
                       {"id": "s1", "skills": ["code-review"]}]})

    def test_result_error_status_requires_an_error_object(self):
        self.assert_angel_error(
            "E_PROTOCOL_MALFORMED", protocols.parse,
            {"protocol": "xev-result", "version": "1.0", "task_id": "t", "origin": "xev",
             "target": "wev", "step_id": "s1", "status": "error"})

    def test_pass_verdict_cannot_carry_a_critical_finding(self):
        self.assert_angel_error(
            "E_PROTOCOL_MALFORMED", protocols.parse,
            {"protocol": "wev-verdict", "version": "1.0", "task_id": "t", "origin": "wev",
             "target": "yev", "step_id": "s1", "verdict": "pass", "score": 1.0,
             "findings": [{"severity": "critical", "message": "secret in the diff"}]})

    def test_score_outside_the_unit_interval_is_rejected(self):
        for score in (-0.1, 1.5):
            with self.subTest(score=score):
                self.assert_angel_error(
                    "E_PROTOCOL_MALFORMED", protocols.parse,
                    {"protocol": "wev-verdict", "version": "1.0", "task_id": "t",
                     "origin": "wev", "target": "yev", "step_id": "s1",
                     "verdict": "fail", "score": score})

    def test_invalid_verdict_word_is_rejected(self):
        self.assert_angel_error(
            "E_PROTOCOL_MALFORMED", protocols.parse,
            {"protocol": "wev-verdict", "version": "1.0", "task_id": "t", "origin": "wev",
             "target": "yev", "step_id": "s1", "verdict": "probably fine", "score": 0.5})

    def test_digest_ignores_identity_and_time(self):
        first = protocols.make("xev-result", task_id="t", step_id="s1", status="ok")
        second = protocols.make("xev-result", task_id="t", step_id="s1", status="ok",
                                msg_id="0" * 12, ts=0.0)
        self.assertEqual(protocols.digest(first), protocols.digest(second))

    def test_digest_changes_with_the_content(self):
        first = protocols.make("xev-result", task_id="t", step_id="s1", status="ok")
        second = protocols.make("xev-result", task_id="t", step_id="s1", status="error",
                                error={"code": "E_TOOL_FAILED", "message": "boom"})
        self.assertNotEqual(protocols.digest(first), protocols.digest(second))
        self.assertRegex(protocols.digest(first), r"^[0-9a-f]{16}$")

    def test_label_is_human_readable(self):
        message = protocols.make("wev-verdict", task_id="t", step_id="s1",
                                 verdict="fail", score=0.25)
        text = protocols.label(message)
        self.assertIn("wev-verdict", text)
        self.assertIn("fail", text)
        self.assertIn("wev->yev", text)

    def test_protocol_samples_exist_for_every_protocol(self):
        for kind in protocols.CONSUMERS:
            with self.subTest(protocol=kind):
                sample = protocols.sample(kind)
                parsed = protocols.parse(json.loads(json.dumps(sample)))
                self.assertEqual(parsed.protocol, kind)

    def test_schemas_on_disk_match_the_runtime(self):
        contracts = WORKFLOW / "contracts"
        if not contracts.is_dir():
            self.skipTest("no contracts directory")
        names = {p.parent.name for p in contracts.glob("*/*.schema.json")}
        self.assertTrue({"isa-plan", "message-digest", "skill-report"} <= names)

    def test_contract_for_isa_plan_accepts_a_real_plan(self):
        from support import contracts as contracts_mod

        contract = contracts_mod.resolve(WORKFLOW, "isa-plan")
        plan = protocols.sample("isa-plan")
        contract.validate({k: v for k, v in plan.items()
                           if k in ("objective", "steps", "budget", "risks")})
