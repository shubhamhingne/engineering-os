# 16 — Design Checklist

The gate every screen and component passes before it's considered done. If any box is unchecked,
it isn't finished. This operationalizes the whole design system into a repeatable review.

## Tokens & consistency
- [ ] Uses **tokens only** — no hard-coded colors, spacing, radii, or durations.
- [ ] Colors carry meaning (action = blue, AI = cyan, status = semantic); no decorative color.
- [ ] Spacing is on the 4px grid; no off-scale values.
- [ ] Typography uses the defined scale; Inter for UI, JetBrains Mono for code/metrics.

## Layout & navigation
- [ ] Fits the app shell; chrome unchanged from other screens.
- [ ] One clear primary action; secondary actions are visually quieter.
- [ ] Reachable and operable from the command palette where relevant.
- [ ] Responsive behavior defined for `md`/`lg`/`xl`.

## States (all required)
- [ ] **Empty** state with guidance + a primary action.
- [ ] **Loading** state (skeleton for content, inline spinner for actions, streaming for AI).
- [ ] **Error** state: specific, calm, recoverable, "no work lost."
- [ ] Success feedback is confirming, not celebratory.

## AI transparency (Principle 3)
- [ ] Provider, model, prompt version, tokens, cost, and latency are visible for any generation.
- [ ] AI vs. human provenance is recorded and shown in history/diff.

## Interaction
- [ ] All six interactive states implemented (default/hover/active/focus/disabled/loading).
- [ ] Fully keyboard-operable; logical tab order; visible focus ring.
- [ ] Micro-interactions subtle and functional; motion ≤ 300ms.

## Accessibility (WCAG AA)
- [ ] Contrast meets AA (text ≥ 4.5:1, UI ≥ 3:1).
- [ ] Icon-only controls have `aria-label` + tooltip.
- [ ] No info by color alone; focus management correct for overlays.
- [ ] `prefers-reduced-motion` respected; touch targets ≥ 44px.
- [ ] Async events announced via live regions.

## Content
- [ ] Copy is calm and specific; no marketing language, no hype.
- [ ] Errors say what happened and what to do next.
- [ ] Numbers/metrics use tabular mono.

## Brand alignment
- [ ] Consistent with the [Engineering Brand Book](https://github.com/shubhamhingne/.github) —
      feels like it belongs beside the GitHub profile and the other flagships.

---

> Use this checklist in design review (now) and again in implementation review (Day 8+). It is the
> single artifact that makes "production-grade design" objective instead of a matter of taste.
