---
name: accessibility-audit
description: Audit a UI against WCAG 2.2 AA: contrast, focus order, target size, semantics and keyboard paths. Use when shipping an interface, reviewing a design, or when a user reports they cannot operate something.
metadata:
  origin: ECC · skills/accessibility
  category: product
  phase: review
  status: adopted
  version: 1
---

# Accessibility Audit

Accessibility is a correctness requirement: an interface a person cannot operate is
broken, not unpolished. WCAG 2.2 AA is the bar because it is testable.

## When to Use

- Shipping or reviewing an interface.
- A user reports they cannot operate something.
- A design system is being defined.

## When Not to Use

- Non-interactive documents with no structure requirement.
- As a substitute for testing with real assistive technology on critical flows.

## Procedure

1. **Keyboard first**: can every action be reached and performed without a mouse?
   Is the focus order logical? Is focus always visible?
2. **Semantics**: real buttons, real labels, headings in order, landmarks, language
   declared. ARIA only when no native element fits.
3. **Contrast**: text 4.5:1, large text 3:1, non-text UI 3:1 — measured with
   `contrast-check`, not by eye.
4. **Target size**: 24 by 24 CSS pixels minimum (WCAG 2.2), with the spacing
   exceptions.
5. **Motion and timing**: respect reduced motion, allow pausing, no content that
   flashes.
6. **Forms**: labels tied to inputs, errors announced, not colour-only.
7. **Test with a screen reader** on the critical flow and record what it announced.

## Exit Criteria

- [ ] Every interactive element is reachable and operable by keyboard.
- [ ] Focus order matches visual order and focus is visible.
- [ ] Contrast ratios measured for every text/background pair.
- [ ] Targets meet the 24 by 24 CSS pixel minimum.
- [ ] Reduced-motion preference respected.
- [ ] One screen-reader pass on the critical flow, recorded.

## Common Failures

| Failure | Fix |
|---|---|
| A `div` with a click handler | Use a button |
| Placeholder as the only label | A real `label` element |
| Focus outline removed for aesthetics | Style it, never remove it |
| Colour as the only error signal | Add text and an icon |
| Contrast judged by eye | Measure |
| ARIA everywhere | Native semantics first |
