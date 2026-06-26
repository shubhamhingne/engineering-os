# 11 — Accessibility

Accessibility is a first-class requirement, not a later audit. Target: **WCAG 2.1 AA** across the
product. An inaccessible component is an unfinished component.

## Contrast

- Body and meaningful text ≥ **4.5:1**; large text and UI components ≥ **3:1**.
- Verified pairs in [03 — Color System](03-color-system.md). Muted text is used only where it
  still clears 4.5:1.
- Never convey information by color alone — pair with text, icon, or shape (e.g. status uses an
  icon + color, not color alone).

## Keyboard

- **Everything operable by keyboard** (Principle 4): tab order is logical; no keyboard traps.
- Visible **focus-visible** ring (`--focus-ring`, cyan, 2px) on every focusable element.
- Shortcuts ([09 — Navigation](09-navigation.md)) never override assistive-tech or browser keys.
- Esc closes overlays; Enter/Space activate controls per role.

## Focus management

- Opening a modal/drawer moves focus into it and traps focus until closed; closing returns focus
  to the trigger.
- Route changes move focus to the main heading or a skip target.
- A **skip-to-content** link is the first tab stop.

## Screen readers

- Semantic HTML first; ARIA only to fill gaps.
- Icon-only controls have `aria-label`; decorative icons are `aria-hidden`.
- Live regions announce async events: generation start/complete, save success, errors
  (`aria-live="polite"`; errors `assertive`).
- Streaming AI output is announced in digestible chunks, not token-by-token.

## Motion & reduced motion

- Honor `prefers-reduced-motion` ([10 — Motion](10-motion.md)); no essential information is
  conveyed only through motion.

## Touch & target sizing

- Interactive targets ≥ **44×44px** effective hit area (even where the visual is smaller, e.g.
  16px checkbox in a 44px row).
- Adequate spacing between adjacent targets to prevent mis-taps.

## Forms

- Every input has a programmatically associated label.
- Errors are announced, linked to the field, and described in text (not color alone).
- Required/optional state is explicit.

## Testing expectations (from Day 8+)

- Automated: axe checks in CI on key screens.
- Manual: keyboard-only pass and a screen-reader pass on every core flow before it ships.

## Why first-class

Accessibility and the product's principles align: keyboard-first, inspectable, calm, high-contrast
dark UI is *also* an accessible UI. Treating it as first-class costs little here and is a clear
senior-engineering signal.
