# 05 — Failure Log

Ideas that were considered and consciously **rejected or deferred**. Each entry records why it
was tempting, why it didn't make the cut, and the condition under which it returns. A short MVP
scope is only credible if you can show what you left out and that you knew you were doing it.

> Discipline: the MVP is *idea → artifacts → scaffolded repo*. Anything that didn't directly
> serve that loop was cut, no matter how appealing.

### 1. Multi-agent MVP
**Tempting:** "AI agents that autonomously complete each lifecycle stage" demos beautifully.
**Rejected for MVP:** non-deterministic, hard to observe, expensive, and easy to get wrong in
ways that erode trust. It would dominate the build and risk the core loop.
**Revisit:** v2, with human checkpoints and full observability (already in the roadmap).

### 2. Plugin marketplace
**Tempting:** ecosystem and network effects.
**Rejected:** marketplaces need a stable core and an audience first; building one for a product
with zero users is cart-before-horse.
**Revisit:** v3, once the artifact/template model is proven and there's demand to extend it.

### 3. Visual workflow editor
**Tempting:** a node-graph for composing the lifecycle looks powerful and impressive.
**Rejected:** enormous UI surface for a flexibility users haven't asked for; conflicts with
"opinionated default over configuration."
**Revisit:** only if users demonstrably outgrow the fixed lifecycle.

### 4. Live collaboration / co-editing
**Tempting:** real-time multiplayer is table-stakes-feeling in modern tools.
**Rejected:** CRDT/OT sync is a product in itself; the MVP is single-user by design.
**Revisit:** v3 with team workspaces, where it actually has users to serve.

### 5. Vector database in the MVP
**Tempting:** "RAG over your project" sounds modern and capable.
**Rejected:** the MVP's context fits in a prompt; a vector store adds infra, cost, and failure
modes for value we can't yet justify. Premature sophistication.
**Revisit:** when project knowledge bases grow beyond what fits in context (v2 knowledge base).

### 6. Code generation in the MVP
**Tempting:** "it also writes the app" widens appeal.
**Rejected:** that's Cursor/Copilot's job and a different, crowded fight. Our gap is the thinking,
not the code. Adding it would blur the positioning and balloon scope.
**Revisit:** possibly never as a core feature; more likely as a thin "scaffold starter code" step.

### 7. Teams, roles, and billing in the MVP
**Tempting:** monetization and "real product" signaling.
**Rejected:** multi-tenancy and billing are heavy and serve users we don't have yet. The MVP
proves value for one user first.
**Revisit:** v3, after single-user value is demonstrated.

### 8. Auto-deploy the generated project
**Tempting:** "idea → deployed app" is a jaw-dropping demo.
**Rejected:** deployment is a deep, provider-specific rabbit hole orthogonal to our value
(documented, standards-compliant repos). It would consume the build.
**Revisit:** maybe as an integration, never as core.

### 9. Custom / fine-tuned model
**Tempting:** a proprietary model feels like a moat.
**Rejected:** contradicts provider-agnosticism (Principle 5); training/serving cost is
unjustifiable pre-PMF; frontier models already exceed our needs.
**Revisit:** only with scale and a clear, measured quality gap that prompting can't close.

### 10. Offline-first / local models
**Tempting:** privacy and "works anywhere."
**Rejected:** the product depends on hosted AI and GitHub; offline-first taxes the whole codebase
for a use case it can't truly fulfill. (Also in [04 — Trade-offs](04-trade-offs.md).)
**Revisit:** unlikely; reconsider only for a privacy-driven enterprise variant.

### 11. Gamification / streaks
**Tempting:** engagement mechanics are easy to add.
**Rejected:** wrong audience. Serious engineers find streak-badges patronizing; it would cheapen
the brand. Engagement should come from usefulness, not dopamine loops.
**Revisit:** no plan.

### 12. Self-hosting / on-prem in the MVP
**Tempting:** appeals to security-conscious teams.
**Rejected:** distribution, support, and config burden for an audience the MVP isn't targeting.
**Revisit:** v3, if enterprise demand is real.

## What this log demonstrates

Twelve plausible features, each cut on purpose, each with a revisit condition. The hard part of
product engineering is not generating ideas — it's saying *not yet* to good ones so the core
ships. That judgment is the point of this document.
