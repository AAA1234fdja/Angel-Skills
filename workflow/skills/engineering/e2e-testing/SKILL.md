---
name: e2e-testing
description: End-to-end flows with page objects, stable locators and explicit quarantine for flaky tests. Use when a change touches a user flow that unit tests cannot cover, or a defect reached production through an integration seam.
metadata:
  origin: ECC · skills/e2e-testing
  category: engineering
  phase: test
  status: adopted
  version: 1
---

# E2E Testing

An end-to-end test costs a hundred times a unit test and fails for reasons that
are not the code. It is justified only when the risk lives in the **real
integration**: login, payment, permissions, navigation across screens.

## When to Use

- The change crosses UI, network and persistence.
- A defect reached production and unit tests never saw it.
- A critical flow needs proof of life before a release.

## When Not to Use

- Pure or domain logic: that is a unit test (`tdd-workflow`).
- API contracts that can be tested without a browser.
- To "raise coverage": E2E is not a coverage metric.

## Procedure

1. **Choose the flow by risk**, not by convenience: the one whose failure costs
   money, data or access.
2. **One file per flow**, with a name that states the user capability
   ("user pays with card", not "checkout test").
3. **Page objects**: each screen is a class with locators and actions. Tests
   contain no selectors; page objects contain no assertions.
4. **Stable locators**: `data-testid` or accessible role. Never CSS classes, never
   long XPath, never translatable text.
5. **No fixed waits.** `waitForTimeout` is forbidden: wait for a condition — a
   specific response, a visible element, an expected URL.
6. **Clean state per test**: own data, no dependence on execution order.
7. **Repeat to detect flakiness**: run the file ten times. One failure in ten means
   the test is broken, not the product.
8. **Explicit quarantine**: a flaky test is marked with an issue number, never
   silently skipped and never retried until it passes.
9. **Failure artefacts on**: screenshot, trace and video only on failure.

## Exit Criteria

- [ ] Every critical flow touched has a test that passes ten times out of ten.
- [ ] Zero selectors in test files — all in page objects.
- [ ] Zero fixed waits.
- [ ] Flaky tests are quarantined with an open issue; `flake-report` shows no
      unexplained instability.
- [ ] The exact command and result are quoted in the pull request.

## Common Failures

| Failure | Fix |
|---|---|
| `waitForTimeout(5000)` to "let it load" | Wait for the real condition |
| Selector by CSS class or translated text | `data-testid` or accessible role |
| Tests sharing a user and a database | Data per test, explicit cleanup |
| `retries: 3` to hide flakiness | Diagnose the race; retries only in CI, with traces |
| An E2E test for a pure function | Unit test, a hundred times cheaper |
| Screenshots on every test | Only on failure: the rest is noise and disk |
