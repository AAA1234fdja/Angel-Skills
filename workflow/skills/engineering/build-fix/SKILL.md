---
name: build-fix
description: Incremental repair of build, type and lint failures, one error per cycle with the root cause before the patch. Use when the build fails, the type checker refuses, or the linter blocks the close.
metadata:
  origin: ECC · agent build-error-resolver + commands/build-fix
  category: engineering
  phase: verify
  status: adopted
  version: 1
---

# Build Fix

A broken build is not fixed by patching around it: it is fixed by understanding
the first error. The rest are usually consequences. Hence one error per cycle.

## When to Use

- Compilation failure, type error, module resolution failure.
- A blocking lint rule that prevents closing the task.
- A dependency broken by a version change or a merge.

## When Not to Use

- Environment failures (missing binary, SDK, credentials): fix the environment.
- Failures in vendored or generated code: regenerate.
- A failing test that is right about the code: the loop is `tdd-workflow`, not this one.

## Procedure

1. **Reproduce with an exact command** and keep the full output. No reproduction,
   no diagnosis — only guessing.
2. **Read the first error**, not the last. Copy the message and the path.
3. **State the root cause in one sentence.** If you cannot, gather more context:
   the function signature, the dependency version, the commit that introduced it
   (`git log -S`).
4. **Apply the smallest patch that removes the cause**, not the symptom. No `any`,
   no `# type: ignore`, no `--no-verify`.
5. **Re-run the same command.** If the error count did not drop, the patch was
   wrong: revert and return to step 3.
6. **Repeat** until zero, then run the full suite (other failures may be masked).
7. If the patch changes a public interface, say so: it is a contract change.
7. **Confirm nothing else moved**: `git diff --stat` against the pre-fix state. A patch that fixes the build and quietly changes three files is two changes.

## Exit Criteria

- [ ] The command that failed now exits 0, and its output is quoted.
- [ ] Zero new suppressions (`any`, `ignore`, `expect-error`, `--no-verify`).
- [ ] The root cause is written in the commit message.
- [ ] The full suite is still green.
- [ ] A public interface change is documented in the diff.

## Common Failures

| Failure | Fix |
|---|---|
| Silencing the error with a cast | Fix the real type at its source |
| Fixing ten errors at once | One per cycle, verifying each time |
| Reinstalling dependencies "just in case" | Only when the error points at the tree |
| Loosening the compiler config to pass | Config changes are their own PR with a reason |
| Committing with `--no-verify` | Forbidden: the hook exists for a reason |
| Fix that also reformats the file | One cause, one patch; reformat separately |
