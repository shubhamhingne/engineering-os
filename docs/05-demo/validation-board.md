# Validation board

The instrument for `v0.4 — Validation`. Not a bug tracker — a record of what real users *did*, the
evidence, and the decision it justifies. This is what turns observation into engineering work.

> **The one success metric:** *Can someone who has never met me successfully use Engineering OS to
> create a project?* Everything else is secondary.

## The No-Build rule

No feature is built unless it is supported by at least one of:

1. repeated user feedback,
2. observed user behavior,
3. a measurable operational need,
4. or a strategic product objective explicitly chosen.

When work resumes, every proposed build cites the board row (or rule #4) that justifies it. No row,
no build.

## Waves

1. **Friendly users (5)** — find obvious bugs, confusing UX, verify deploy. Ask *"what did you
   expect / what confused you / where did you stop / if you quit, why?"* — never *"do you like it?"*
2. **Engineers who don't know you (10–15)** — send only a live URL + 60s demo + one sentence. Then
   observe. If you have to explain the workflow, that's the finding.
3. **Target audience** — indie hackers · solo founders · AI engineers · CTOs. Now feedback becomes
   product direction.

## Measure behavior, not opinions

Did they finish? · Where did they stop? · How long did it take? · What errored? · Did they return?

## Board

| ID | Observation | Evidence | Decision |
|---|---|---|---|
| _V-001_ | _(example) 3/5 couldn't find Export_ | _session_ | _move Export to the primary action bar_ |
| _V-002_ | _(example) users expected README before PRD_ | _interviews_ | _reorder the generation flow_ |
| | | | |

*Rows above in italics are format examples — replace with real observations. Each justified build links back here.*

## What to bring back (for the next engineering session)

What users tried to do · where they got stuck · what surprised you · deployment results ·
performance/accessibility numbers · the first real bug reports. From that, we prioritize on evidence,
not intuition.
