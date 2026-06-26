# 07 — Success Metrics

Metrics across three lenses: **product** (does it work for users), **engineering** (is it
healthy), and **portfolio** (does it advance the career goal — the real reason this exists now).

## North Star

> **Repositories shipped to standard per active user** — a project taken from idea to a
> pushed, standards-compliant GitHub repo.

It captures the whole loop in one number: if users complete repos, the product delivered value.

## Product metrics (AARRR)

| Stage | Metric | Target (early) |
|---|---|---|
| Activation | % of new users who create a first project | ≥ 60% |
| Activation | % who generate at least one artifact | ≥ 50% |
| Core value | % who export a repo to GitHub (the "aha") | ≥ 30% |
| Retention | % who return and start a 2nd project within 30 days | ≥ 25% |
| Referral | % of users whose exported repo links back to Engineering OS | track |
| Revenue | (deferred) — not a goal for MVP | — |

**Funnel health:** idea → vision → PRD → architecture → README → repo export. Track drop-off
at each step; the biggest drop is the top fix priority.

## Quality metrics

- **Artifact edit rate** — % of generated artifacts the user edits before accepting.
  *Healthy mid-range:* some editing means the output is a strong draft, not blindly accepted
  (too low = ignored; too high = poor quality).
- **Regeneration rate** — high regen on a step signals weak prompts for that artifact.
- **Time to first repo** — median minutes from sign-up to first pushed repo. Target: < 60 min.

## Engineering metrics

- CI green rate on `main`; p95 generation latency; error rate per generation.
- LLM cost per active user and per exported repo (must stay within budget).
- Uptime of the generation and GitHub-export paths.

## Portfolio metrics (why this matters *now*)

This is a flagship in a 90-day portfolio rebuild, so its success is also measured as a
**career artifact**:

- Reaches the internal Definition of Done at **≥ 90/100** review.
- Pinned on the profile; included as a featured product.
- Has a published **case study** (screenshots, architecture diagram, lessons learned).
- Demonstrably showcases the full stack (web, backend, AI, GitHub integration) in the MVP,
  with mobile and agents proven in v2.

## Guardrails (don't optimize these into the ground)

- Cost per repo must not exceed the value delivered.
- Generation speed must not be traded for visibly worse artifacts.
- Standards must stay opinionated; "more options" is not a success metric.
