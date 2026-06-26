# 10 — Motion

Motion is functional: it orients, confirms, and shows continuity. It is never decorative
(Principle 6). If an animation doesn't help the user understand what changed, it's removed.

## Duration tokens

| Token | ms | Use |
|---|---|---|
| `duration-1` | 100 | Hover, focus, small state changes |
| `duration-2` | 150 | Buttons, toggles, tooltips |
| `duration-3` | 200 | Dropdowns, popovers, tabs |
| `duration-4` | 300 | Modals, drawers, route transitions |

Nothing exceeds 300ms in the app. Faster feels responsive; slower feels sluggish to power users.

## Easing tokens

| Token | Curve | Use |
|---|---|---|
| `ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | Most transitions (enter/move) |
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Elements entering |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving |

## Patterns

| Event | Motion |
|---|---|
| Hover | 100ms color/opacity; no movement |
| Dropdown/popover | 150–200ms fade + 4px rise (`ease-out`) |
| Modal/drawer | 300ms fade + scale(0.98→1) / slide |
| **AI streaming** | tokens append in place; a subtle cyan caret marks the live position |
| Success feedback | brief check + 150ms; toast, no confetti |
| Error feedback | input shake is **off**; instead, color + inline message (calm, not alarming) |

## Reduced motion (required)

Respect `prefers-reduced-motion: reduce`:

- Replace all movement/scale with instant or opacity-only transitions.
- Streaming still updates content but without the animated caret motion.
- No parallax, no auto-playing motion anywhere.

## What we explicitly avoid

- Decorative loops, bouncing, parallax, page-load hero animations.
- Motion that delays interaction (e.g. a 600ms modal the user must wait through).
- Attention-grabbing motion for non-critical events.

## Why restrained motion

This is a tool people use for hours. Motion that delights once annoys the hundredth time. Subtle,
fast, functional motion keeps the interface calm and respects the power user's pace (Principles 1 & 6).
