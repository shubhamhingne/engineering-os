# 13 — Micro-interactions

Small, functional feedback that confirms the system heard the user. Subtle by mandate
(Principle 6); each earns its place by communicating state.

## Principles for micro-interactions

- **Confirm, don't celebrate.** Feedback says "done," not "🎉".
- **Immediate.** Feedback begins within one frame of the action.
- **Reversible-friendly.** Destructive actions confirm; everything else is undoable where possible.

## Catalogue

| Interaction | Behavior |
|---|---|
| Button press | 100ms color deepen; no bounce |
| Save | Button → inline spinner → check, then revert; "Saved" in `aria-live` |
| Copy (ID, code) | Icon flips to check for 1s; tooltip "Copied" |
| Toggle/switch | 150ms thumb slide; immediate state |
| Hover on row | Subtle `surface-raised` tint + reveal row actions |
| Drag to reorder | (if used) grab cursor, placeholder gap, no exaggerated motion |
| Form validation | On blur: inline message appears; field border → `--danger`; no shake |
| Tab switch | 200ms underline slides to active tab |

## AI-specific micro-interactions (the signature moments)

| Interaction | Behavior |
|---|---|
| Generation start | Provider/model chip + a cyan "streaming" indicator appear |
| Streaming | Tokens append in place with a subtle cyan caret at the live edge |
| Token/cost ticker | Mono counter increments live (tabular nums) — makes cost *felt*, not hidden |
| Generation done | Caret fades; "done" chip shows total tokens · cost · latency |
| AI vs human edit | A version tagged `ai` or `human` in the diff/history (provenance, Principle 3) |

These reinforce "everything is inspectable": the user *sees* the machine working and what it cost,
in real time, calmly.

## What we avoid

- Celebratory confetti, sounds, mascots, or playful copy.
- Motion that blocks or delays the next action.
- Feedback that competes with content for attention.

## Why micro-interactions matter here

For a daily tool, these tiny confirmations are the texture of trust: the user always knows the
system registered their action and what the AI is doing and costing. Done right, they're barely
noticed — which is exactly the goal.
