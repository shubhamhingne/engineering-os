# 02 — Discovery

This documents how the problem was investigated and what shaped the product's direction. I am
explicit about what is evidence and what is assumption, because conflating the two is the most
common way product reasoning goes wrong.

## Research process

1. **Self-observation (primary, real).** I ran the full engineering lifecycle manually on my own
   portfolio for several days and logged where the friction actually was. The friction was not
   coding — it was producing and maintaining the *thinking* artifacts consistently.
2. **Competitor teardown (real).** I evaluated the adjacent tool categories against the specific
   job "idea → standards-compliant repository." Summarized in
   [05 — Competitive Analysis](../01-product/05-competitive-analysis.md).
3. **User hypotheses (assumption, not yet validated).** I have *not* run formal user interviews.
   The personas in [04 — Personas](../01-product/04-personas.md) are hypotheses grounded in my own
   experience and observation of how engineers present work on GitHub — not interview data.

> Stating this plainly matters: a portfolio piece that pretends to have user research it doesn't
> have is less credible, not more. The honest version is stronger.

## Competitor insight

The teardown produced the sharpest insight: **the market is crowded with tools that own one
slice of the lifecycle, and empty where the slices connect.** Chat owns drafting; coding tools
own code; generators own demos; PM tools own docs. The connective tissue — a project model that
carries an idea through to a maintainable repo with standards — is unowned. That gap is both the
opportunity and the risk (a gap can be empty because it's hard *or* because no one wants it).

## Insights that shaped the product

- **The artifact, not the conversation, is the unit of value.** People keep PRDs and ADRs; they
  don't keep chat logs. Modeling the domain around artifacts (not conversations) followed
  directly from this. See [10 — Domain Model](../02-architecture/10-domain-model.md).
- **Output must survive the tool.** If the value is trapped in the app, it isn't a portfolio
  asset. Everything must export to Git as plain Markdown (Principle 3).
- **Opinion beats configuration.** Engineers don't want to assemble a process; they want a good
  default they can override. This pushed toward an opinionated lifecycle, not a flexible toolkit.

## Open questions (unresolved)

- Will lowering the cost of discipline actually change behavior, or do engineers skip it because
  they don't value it (not because it's expensive)? **Unknown.** This is the riskiest assumption.
- Is "portfolio building" a strong enough wedge, or too narrow a market? Leaning narrow on
  purpose for the MVP, accepting the risk.
- How good must the generated artifacts be before users trust them as a starting point? To be
  learned from the artifact-edit-rate metric ([07 — Success Metrics](../01-product/07-success-metrics.md)).

The discovery did not produce certainty. It produced a clear, falsifiable hypothesis and a
narrow first bet — which is the most honest output discovery can give at this stage.
