"""Add a `sample` payload to every tool spec: the input its exit criteria need.

A tool that cannot show a known-good input is a tool nobody can verify. The sample
is also what `workflow tool --self-test` executes, so the suite is executable
documentation rather than a claim.
"""
import json
import pathlib

SAMPLES = {
    "agent-architecture-audit/layer-map": {"symptoms": ["agent ignores instructions",
                                                        "output is truncated"]},
    "agent-harness-construction/harness-score": {
        "tools": [{"id": "read", "input_schema": True,
                   "returns": ["status", "summary", "next_actions", "artifacts"]},
                  {"id": "edit", "input_schema": True,
                   "returns": ["status", "summary", "next_actions", "artifacts"]}],
        "system_prompt_chars": 4000, "max_prompt_chars": 6000,
        "has_recovery_contract": True},
    "autonomous-loop/loop-guard": {"loop": {
        "success_test": "npm test", "max_iterations": 10, "max_seconds": 3600,
        "max_cost": 5.0, "no_progress_after": 3, "checkpoint": "git commit",
        "gates": ["deploy"], "failure_policy": "revert the iteration on failure"}},
    "context-budget/budget-model": {"window": 200000, "components": [
        {"name": "system", "chars": 6000, "cap": 0.2},
        {"name": "skills", "chars": 24000, "cap": 0.3},
        {"name": "files", "chars": 40000, "cap": 0.3},
        {"name": "history", "chars": 20000, "cap": 0.2}]},
    "eval-harness/eval-summary": {"k": 3, "evals": {
        "auth_flow": {"attempts": ["pass", "pass", "pass"], "cost": 0.12},
        "pdf_parse": {"attempts": ["pass", "pass", "fail"], "cost": 0.30}}},
    "doc-writing/doc-lint": {"doc": {"path": "README.md", "audience": "developers adding an endpoint",
                                     "source_of_truth": "workflow/angel/cli.py",
                                     "examples_run": 2, "failure_section": True,
                                     "last_verified": "2026-11-05",
                                     "has_duplicated_truth": False, "words": 900}},
    "api-compatibility/compat-matrix": {
        "producers": [{"name": "api", "versions": ["1.0.0", "1.4.0", "2.0.0"]}],
        "consumers": [{"name": "web", "pins": {"api": 1}},
                      {"name": "mobile", "pins": {"api": 2}}]},
    "contract-design/contract-skeleton": {"name": "skill-report", "version": "1.2.0", "fields": [
        {"name": "skill", "type": "string", "required": True},
        {"name": "verdict", "type": "string", "required": True,
         "enum": ["pass", "fail", "blocked"]},
        {"name": "score", "type": "number", "required": False}]},
    "schema-evolution/bump-advisor": {"current": "1.1.0", "changes": [
        {"kind": "remove_field", "path": "findings"},
        {"kind": "add_optional_field", "path": "next_action"}]},
    "caching-policy/cache-review": {"caches": [
        {"name": "product_page", "key": ["product_id", "locale"], "ttl_seconds": 300,
         "tolerance_seconds": 600, "invalidation": "on product update",
         "bounded": True, "on_outage": "serve stale", "measured": True}]},
    "data-contracts/invariant-check": {
        "invariants": [{"field": "amount_cents", "rule": "min", "value": 0},
                       {"field": "email", "rule": "required"},
                       {"field": "status", "rule": "enum",
                        "value": ["active", "cancelled"]},
                       {"field": "id", "rule": "unique"}],
        "records": [{"id": 1, "amount_cents": 100, "email": "a@b.c", "status": "active"},
                    {"id": 2, "amount_cents": 0, "email": "d@e.f", "status": "cancelled"}]},
    "migration-safety/migration-plan": {
        "steps": [{"op": "add_column", "table": "orders", "column": "tenant",
                   "nullable": True, "rollback": "drop_column"},
                  {"op": "backfill", "table": "orders", "batched": True,
                   "idempotent": True, "resumable": True}],
        "stop_conditions": {"error_rate": 0.01, "lock_seconds": 5, "replication_lag": 2}},
    "query-review/query-smells": {"queries": [
        {"sql": "select id, total from orders where id = $1 limit 1",
         "rows_scanned": 1, "rows_returned": 1, "plan_node": "index_scan",
         "index_used": True, "executions": 1}]},
    "ai-regression-testing/regression-matrix": {
        "defects": [{"id": "BUG-12", "area": "auth", "fixed": True},
                    {"id": "BUG-31", "area": "checkout", "fixed": True}],
        "tests": [{"name": "auth_blocks_expired_token", "issue": "BUG-12",
                   "sandboxed": True},
                  {"name": "checkout_retries_once", "issue": "BUG-31",
                   "sandboxed": False}]},
    "build-fix/error-digest": {"command": "npm run build", "output": (
        "src/app.ts(12,5): error TS2322: Type 'string' is not assignable to type 'number'.\n"
        "src/util.ts(4,11): error TS2304: Cannot find name 'foo'.\n"
        "src/app.ts(20,3): error TS2322: Type 'string' is not assignable to type 'number'.\n"
        "Found 3 errors in 2 files.")},
    "code-review/diff-review": {"diff": (
        "--- a/src/app.py\n+++ b/src/app.py\n@@ -1,3 +1,6 @@\n def handler(user):\n"
        "+    if user is None:\n+        raise ValueError('user required')\n"
        "+    return user.id\n")},
    "coding-standards/style-scan": {"files": {
        "src/orders.py": "def total(xs):\n    r = 0\n    for x in xs:\n        r += x\n    return r\n",
        "src/util.py": "MAX_RETRIES = 3\n\n\ndef clamp(value, low, high):\n"
                       "    return max(low, min(value, high))\n"}},
    "e2e-testing/flake-report": {"runs": {
        "checkout flow": ["pass", "pass", "pass"],
        "login redirect": ["pass", "fail", "pass"]},
        "max_flake_rate": 0.1},
    "error-handling/silence-scan": {"files": {
        "src/safe.py": "try:\n    do_work()\nexcept ValueError as exc:\n"
                       "    log.warning('work failed', exc_info=exc)\n    raise\n",
        "src/bad.py": "try:\n    do_work()\nexcept Exception:\n    pass\n"}},
    "error-taxonomy/taxonomy-check": {"policy": {
        "E_TOOL_TIMEOUT": {"severity": "error", "retryable": True, "owner": "tool", "exit": 7},
        "E_SCHEMA_UNSUPPORTED": {"severity": "error", "retryable": False,
                                 "owner": "author", "exit": 2}}},
    "performance-optimizer/bench-compare": {
        "metric": "latency_ms", "before": [142, 138, 145, 140], "after": [96, 99, 94, 97]},
    "refactor-clean/dead-code-scan": {"symbols": [
        {"name": "format_legacy", "defined": True, "referenced": False, "tests": 0},
        {"name": "clamp", "defined": True, "referenced": True, "tests": 2}]},
    "tdd-workflow/coverage-gate": {"threshold": 0.8, "report": {
        "files": {"src/app.py": {"line": 0.91, "branch": 0.72}}}},
    "verification-loop/gate": {"allow_skips": ["security"], "phases": {
        "build": {"status": "pass", "command": "npm run build", "output": "ok"},
        "types": {"status": "pass", "command": "tsc --noEmit"},
        "lint": {"status": "pass", "command": "npm run lint"},
        "tests": {"status": "pass", "command": "npm test", "output": "42 passing"},
        "diff": {"status": "pass", "command": "git diff --check"}}},
    "error-recovery/recovery-audit": {"errors": [
        {"code": "E_TOOL_TIMEOUT", "message": "tool exceeded 10s",
         "hint": "the selector matched no element; check the page object",
         "retryable": True, "stop_condition": "after 3 attempts"},
        {"code": "E_TOOL_INPUT", "message": "payload missing field",
         "hint": "add the 'diff' field to the payload", "retryable": False}]},
    "failure-forensics/timeline": {"entries": [
        {"seq": 0, "kind": "run.start", "data": {"objective": "verify the change"}},
        {"seq": 1, "kind": "plan", "data": {"steps": 2}},
        {"seq": 2, "kind": "dispatch", "data": {"step_id": "s1", "skill": "verification-loop"}},
        {"seq": 3, "kind": "tool.call", "data": {"tool": "gate"}},
        {"seq": 4, "kind": "tool.result", "data": {"status": "ok"}},
        {"seq": 5, "kind": "result", "data": {"status": "ok"}},
        {"seq": 6, "kind": "verdict", "data": {"verdict": "pass"}},
        {"seq": 7, "kind": "run.end", "data": {"verdict": "pass"}}]},
    "incident-backlog/dedupe": {"reports": [
        {"code": "E_TOOL_TIMEOUT", "operation": "fetch", "component": "zev",
         "seen": 12, "severity": "high", "owner": "platform"},
        {"code": "E_TOOL_TIMEOUT", "operation": "fetch", "component": "zev",
         "seen": 3, "severity": "medium"},
        {"code": "E_SCHEMA_UNSUPPORTED", "operation": "validate", "component": "wev",
         "seen": 1, "severity": "low", "owner": "author"}]},
    "retry-policy/retry-plan": {"max_attempts": 3, "base_ms": 200, "codes": {
        "E_TOOL_TIMEOUT": {"retryable": True, "idempotent": True},
        "E_TOOL_INPUT": {"retryable": False, "idempotent": True},
        "E_PAYMENT_TIMEOUT": {"retryable": True, "idempotent": False}}},
    "changelog-discipline/changelog-lint": {"entries": [
        {"version": "0.3.0", "type": "breaking",
         "text": "skills are folders with a manifest instead of loose markdown files",
         "action": "run workflow validate --strict and add skill.json to local skills"},
        {"version": "0.3.0", "type": "added",
         "text": "workflow run executes a routed plan and writes a hash-chained journal"}]},
    "skill-audit/overlap-score": {"threshold": 0.5, "skills": [
        {"id": "code-review", "triggers": ["review this diff"], "keywords": ["review", "diff"],
         "verbs": ["review"], "phase": "review"},
        {"id": "security-review", "triggers": ["security review"], "keywords": ["security", "auth"],
         "verbs": ["review", "secure"], "phase": "review"},
        {"id": "tdd-workflow", "triggers": ["red green refactor"], "keywords": ["tdd", "test"],
         "verbs": ["test"], "phase": "test"}]},
    "skill-authoring/skill-lint": {"skill": {
        "id": "flaky-selector-fix", "category": "engineering",
        "frontmatter": {"description": "Repair selectors that match several elements. "
                                       "Use when a browser test passes locally and fails in CI."},
        "sections": ["When to Use", "When Not to Use", "Procedure", "Exit Criteria",
                     "Common Failures"],
        "manifest": {"phase": "test", "verbs": ["fix", "test"],
                     "triggers": ["flaky selector"], "tools": []}}},
    "accessibility-audit/contrast-check": {"pairs": [
        {"fg": "#1a1a1a", "bg": "#ffffff", "large": False},
        {"fg": "#767676", "bg": "#ffffff", "large": False},
        {"fg": "#ffffff", "bg": "#005fcc", "large": True}]},
    "message-schema/drift-check": {"code_fields": ["protocol", "version", "task_id",
                                                   "origin", "target", "msg_id", "ts",
                                                   "parent", "objective", "steps"],
                                   "schema": {"properties": {
                                       "protocol": {}, "version": {}, "task_id": {},
                                       "origin": {}, "target": {}, "msg_id": {}, "ts": {},
                                       "objective": {}, "steps": {}, "risks": {}}}},
    "protocol-design/protocol-skeleton": {
        "name": "xev-progress", "origin": "xev", "targets": ["yev"],
        "fields": [{"name": "step_id", "type": "string", "required": True},
                   {"name": "percent", "type": "number", "required": True},
                   {"name": "note", "type": "string", "required": False}]},
    "api-reconstruction/traffic-to-spec": {"min_samples": 2, "requests": [
        {"method": "GET", "path": "/users/123", "status": 200,
         "body": {"id": 123, "name": "ana", "role": "admin"}},
        {"method": "GET", "path": "/users/456", "status": 200,
         "body": {"id": 456, "name": "luis", "role": "member"}},
        {"method": "GET", "path": "/users/789", "status": 200, "body": {}}]},
    "binary-triage/triage-report": {"metadata": {
        "sha256": "9f2c0d1e4b5a6c7d8e9f0a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f",
        "kind": "pe", "arch": "x86_64", "size": 912384, "entropy": 6.1,
        "imports": ["kernel32.dll!CreateFileW", "kernel32.dll!WriteFile",
                    "ws2_32.dll!socket", "ws2_32.dll!connect", "user32.dll!MessageBoxA",
                    "advapi32.dll!RegOpenKeyExW", "kernel32.dll!Sleep",
                    "kernel32.dll!GetTickCount", "kernel32.dll!LoadLibraryA",
                    "kernel32.dll!GetProcAddress", "user32.dll!GetAsyncKeyState"],
        "sections_writable_executable": 0, "strings": ["https://example.invalid/beacon"]}},
    "reverse-engineering/artefact-triage": {"artefact": {
        "path": "capture.bin", "size": 40960, "head_hex": "1f8b0800",
        "strings": ["/api/v2/login", "X-Sig", "gzip"]}},
    "dependency-audit/dependency-report": {"imports": ["json", "re", "urllib"], "declared": [
        {"name": "requests", "pinned": True, "licence": "Apache-2.0",
         "last_release_days": 20, "transitive": 6, "install_scripts": False},
        {"name": "left-pad", "pinned": False, "licence": "MIT",
         "last_release_days": 900, "transitive": 0, "install_scripts": True}]},
    "safety-guard/classify-command": {"command": "git push --force origin main",
                                      "profile": "standard"},
    "secret-scan/scan-text": {"min_entropy": 3.6, "files": {
        "config/settings.py": "DEBUG = False\nDB_URL = 'postgres://app:hunter2@db/app'\n",
        "config/example.py": "DB_URL = 'postgres://user:password@db/app'  # example\n"}},
    "security-review/attack-surface": {"diff": (
        "--- a/api/routes.py\n+++ b/api/routes.py\n@@ -10,3 +10,8 @@\n"
        "+@app.route('/files')\n+def read_file():\n"
        "+    name = request.args['name']\n"
        "+    return open('uploads/' + name).read()\n")},
}


def main(root: pathlib.Path) -> int:
    patched = 0
    missing = []
    for manifest in sorted(root.glob("skills/*/*/skill.json")):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        changed = False
        for tool in data.get("tools", []):
            key = f"{data['id']}/{tool['id']}"
            if key not in SAMPLES:
                missing.append(key)
                continue
            tool["sample"] = SAMPLES[key]
            changed = True
        if changed:
            manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
            patched += 1
    print(f"patched {patched} manifests")
    if missing:
        print("without a sample:", ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(pathlib.Path(__file__).resolve().parents[1]))
