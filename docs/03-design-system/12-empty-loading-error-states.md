# 12 — Empty, Loading & Error States

The states that separate a polished product from a demo. Every view that fetches or generates
data must design all three — they are not afterthoughts.

## Empty states

An empty state is an onboarding opportunity, not a dead end. Each has: a calm focal icon, a
one-line explanation, and a **primary action**.

| Surface | Message | Action |
|---|---|---|
| No projects | "No projects yet. Start from an idea." | **New project** |
| No artifacts | "This project has no artifacts. Generate your first." | **Generate Vision** |
| No runs | "No generations yet." | (passive) |
| No repository | "Not exported to GitHub yet." | **Export repository** |
| Search no-results | "No matches for '…'." | Clear / refine |

Never show a blank pane. Empty ≠ nothing-to-say.

## Loading states

- **Skeletons**, not spinners, for content regions (lists, cards, editor) — they preserve layout
  and reduce perceived wait.
- **Inline spinners** only for in-button actions (e.g. "Export") with the button width preserved.
- **AI generation** is a *streaming* state, not a blank spinner: the generation timeline shows
  progress and tokens appear live ([13 — Micro-interactions](13-micro-interactions.md)).
- Optimistic UI for cheap, reversible actions (e.g. local edits); never for irreversible ones
  (repo creation waits for confirmation).

## Error states

Calm, specific, recoverable. Tell the user **what happened, why (if known), and what to do next**.

| Failure | Message | Recovery |
|---|---|---|
| AI generation failed | "Generation failed (provider timeout). Your draft is safe." | **Retry** · switch model |
| Rate / budget limit | "Daily generation limit reached." | Explain limit · when it resets |
| GitHub auth expired | "GitHub connection expired." | **Reconnect GitHub** |
| Repo export failed | "Couldn't create the repository (name exists)." | Rename · retry (idempotent) |
| Network/unknown | "Something went wrong. No changes were lost." | **Retry** · contact/support link |

### Error principles
- **Never lose work.** Partial generations and edits persist; the message says so explicitly.
- **No raw stack traces** to users; log the detail, show a human message ([17 — Observability](../02-architecture/17-observability.md)).
- **Match severity to tone** — a recoverable timeout is not styled like a catastrophe (Principle 6).
- Errors are announced to assistive tech ([11](11-accessibility.md)).

## Why these are designed up front

Most products design the happy path and bolt on states later, producing jarring blanks and scary
errors. Designing all three now means every wireframe ([14](14-wireframes.md)) already accounts
for them — and the product feels trustworthy under real conditions, where things fail.
