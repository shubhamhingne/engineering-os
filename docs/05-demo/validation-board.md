# Validation board

The instrument for `v0.4 — Validation`. Not a bug tracker — a record of what real users *did*, the
evidence, and the decision it justifies. This is what turns observation into engineering work.

> **The one success metric:** *Can someone who has never met me successfully use Engineering OS to
> create a project?* Everything else is secondary.

## Metrics, in priority order

1. Can a stranger complete the workflow unassisted?
2. Time to the first "aha" moment.
3. % who return for a second session.
4. The step with the highest abandonment.
5. The request that appears repeatedly across users.

These say more about the product than another hundred backend tests.

## The No-Build rule

No feature is built unless it is supported by at least one of:

1. repeated user feedback,
2. observed user behavior,
3. a measurable operational need,
4. or a strategic product objective explicitly chosen.

When work resumes, every proposed build cites the board row (or rule #4) that justifies it. No row,
no build.

## Evidence thresholds — how much evidence reopens engineering

The gate says *evidence required*; this says *how much*. It prevents overreacting to one loud voice
while still responding fast to genuine patterns.

| Trigger | Engineering response |
|---|---|
| 1 user reports an issue | Investigate, don't build |
| 3+ independent users report the same issue | Prioritize |
| >30% drop-off at one workflow step | Highest-priority UX fix |
| Repeated request from multiple target users | Consider feature |
| Security / reliability regression | Immediate fix, regardless of demand |

## Waves

1. **Friendly users (5)** — find obvious bugs, confusing UX, verify deploy. Ask *"what did you
   expect / what confused you / where did you stop / if you quit, why?"* — never *"do you like it?"*
2. **Engineers who don't know you (10–15)** — send only a live URL + 60s demo + one sentence. Then
   observe. If you have to explain the workflow, that's the finding.
3. **Target audience** — indie hackers · solo founders · AI engineers · CTOs. Now feedback becomes
   product direction.

## Measure behavior, not opinions

Did they finish? · Where did they stop? · How long did it take? · What errored? · Did they return?

## Evidence scoreboard

The only dashboard for this phase — adoption, not engineering. No lines of code, test count, or
coverage; those served their purpose and are no longer the bottleneck.

| Metric | Target | Current |
|---|---|---|
| Live production URL | ✅ | ⏳ |
| Demo video | ✅ | ⏳ |
| Lighthouse performance | ≥ 90 | ⏳ |
| Accessibility (WCAG AA) | Pass | ⏳ |
| First external user | 1 | ⏳ |
| Users completing the workflow | 5 | ⏳ |
| Independent issues filed | 10 | ⏳ |
| Returning users | 3 | ⏳ |
| GitHub stars from strangers | 10 | ⏳ |
| Public article published | 1 | ⏳ |

## Board

| ID | Observation | Evidence | Decision |
|---|---|---|---|
| _V-001_ | _(example) 3/5 couldn't find Export_ | _session_ | _move Export to the primary action bar_ |
| _V-002_ | _(example) users expected README before PRD_ | _interviews_ | _reorder the generation flow_ |
| | | | |

*Rows above in italics are format examples — replace with real observations. Each justified build links back here.*

## When engineering resumes — the four questions

Every request is run through these before any code is written:

1. **Which board item or evidence justifies this?** (no row, no build)
2. **Specification change, or only implementation?** (the core is frozen — a spec change needs an ADR)
3. **Is there a smaller solution that addresses the observed problem?**
4. **How will we know the change worked?** (the behaviour we expect to move)

If those can't be answered, the recommendation is *don't build*.

## What to bring back (for the next engineering session)

What users tried to do · where they got stuck · what surprised you · deployment results ·
performance/accessibility numbers · the first real bug reports. From that, we prioritize on evidence,
not intuition.
