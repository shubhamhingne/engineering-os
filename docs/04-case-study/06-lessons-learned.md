# 06 — Lessons Learned

A living document. Captured during the product-and-architecture phase, before implementation —
which is itself one of the lessons. These are reflections, not achievements.

## On scope

- **A narrow MVP is a design skill, not a limitation.** The hardest and most valuable decision so
  far was cutting twelve plausible features ([05](05-failure-log.md)) down to one loop. Saying
  "not yet" well is harder than saying "yes," and it's what makes a solo build shippable.
- **Scope discipline compounds.** Every feature deferred removed downstream architecture,
  testing, and documentation burden. Cutting the vector DB didn't save one decision — it saved a
  dozen.

## On process

- **Separating product from implementation clarified both.** Defining the product (Day 4) before
  the architecture (Day 5) before any code meant each phase had a clean input. When I was tempted
  to design schema during the PRD, stopping made both documents better.
- **Standards before code pays immediately.** Building the `.github` standards first meant
  Engineering OS inherits CI, issue forms, and a lifecycle for free. The first repo proved the
  standards; the standards will shape every repo after.
- **Writing the reasoning down changes the reasoning.** Several decisions got *better* the moment
  I had to justify them in an ADR or trade-off doc. Forcing the "why not" surfaced weak arguments
  I'd otherwise have shipped.

## On honesty

- **Admitting what's unvalidated is more credible than hiding it.** The personas are hypotheses,
  not interview data, and saying so ([02](02-discovery.md)) makes the rest of the analysis
  trustworthy. A portfolio that overclaims research reads as junior.
- **The riskiest assumption deserves a name.** "Lowering the cost of discipline will change
  behavior" might be wrong. Stating it as the central, unproven bet is more senior than asserting
  certainty.

## On engineering judgment

- **Opinion is a feature.** The instinct to make everything configurable is usually a failure to
  decide. Choosing strong defaults (lifecycle, standards) is the harder, better move.
- **Avoid premature sophistication.** Multi-agent, RAG, fine-tuned models — each is "modern" and
  each was wrong for the MVP. Reaching for sophistication before the simple version is proven is a
  common senior-engineer trap I had to actively resist.

## On implementation (Day 9 — first vertical slice)

- **The architecture survived contact with code.** Building one workflow end-to-end (create →
  generate Vision → edit → save → reopen) against the documented hexagon worked without rework:
  the `AIProviderPort` + fake adapter made the generation logic testable with zero network, and
  the module/adapter split held. The design paid for itself on day one of coding.
- **A fake adapter is the highest-leverage test tool.** Putting the AI behind a port meant the
  whole workflow is deterministically testable (11 passing tests) without a provider or a key.
  This is the concrete payoff of "providers are replaceable" — it's a *testability* win, not just
  a vendor-flexibility one.
- **Environment ≠ target.** The documented stack targets Python 3.12, but the only local
  interpreter was 3.9. Rather than fake the result, I made the type hints version-agnostic so the
  tests actually run and prove the slice — honesty over a green screenshot I couldn't stand behind.
- **A vertical slice exposes the real seams.** Persistence, validation, error handling, and
  observability all showed up in one small workflow — exactly as intended. The slice is small but
  it touched every layer, which is the point.

## What I would do differently already

- I would have written this case-study narrative *in parallel* with the work from day one, not
  inserted it later — the reasoning is freshest at the moment of decision, and reconstructing it
  afterward loses fidelity. (This document now starts at decision-time going forward.)

> This file is updated as the project progresses. Implementation and release will add lessons
> about the gap between the design on paper and the system in production.
