# 17 — UI/UX Pro Max Standard

The bar for every screen in Engineering OS: it should belong beside Linear, GitHub, Notion,
Vercel, and Cursor — while reflecting our own calm, dense, keyboard-first identity
([principles](01-design-principles.md)). Functional is the floor; *product-grade* is the bar.

> This standard is **enforced**, not aspirational. A screen that fails it is incomplete, the
> same way a feature missing tests is incomplete.

## The ten rules

1. **No generic CRUD UI.** No plain tables, default cards, or naked forms. Every screen has a
   deliberate visual hierarchy and a reason for its layout.
2. **Named inspiration.** Each screen documents which product(s) influenced its interaction
   patterns, and why (table below). Understand, don't copy.
3. **Compose from the design system.** Next.js + React + Tailwind + **shadcn/ui** (on **Radix**
   primitives) + **Framer Motion** (purposeful) + **Lucide** + CSS-variable theming. No ad-hoc
   styling; components extend or compose the system.
4. **Every screen earns one "wow" moment** — a small, functional interaction that rewards the
   user (streaming generation timeline, live token/cost counter, smooth version diff, fuzzy
   command palette). Never flashy for its own sake.
5. **Empty states are product features** — explain the value, suggest the next action, include a
   primary CTA and a subtle visual cue. The first-run experience is designed, not defaulted.
6. **Loading is part of the experience** — skeletons that match the content layout, progressive
   loading, streaming AI output, step-by-step progress. A bare spinner is a defect.
7. **Rich artifact workspace**, not a textarea — see the workspace layout below.
8. **Motion reinforces state** — it communicates *save complete*, *generation started*, *version
   created*, *export finished*. Motion that conveys nothing is removed.
9. **Accessibility is built in** — keyboard nav, focus states, screen-reader labels, WCAG AA,
   reduced-motion. Part of implementation, never a later pass ([a11y](11-accessibility.md)).
10. **Every UI PR ships design evidence** — before/after screenshots, a short recording, updated
    design notes, an a11y checklist, and responsive validation.

## Per-screen inspiration (and why)

| Screen | Inspiration | What we take |
|---|---|---|
| Dashboard | Linear | Calm density, fast keyboard nav, quiet hierarchy |
| Command Palette | Raycast | Fuzzy search, action-first, shortcut discovery |
| Artifact editor / docs | Notion | Block-clean editing, focused writing surface |
| Repository explorer | GitHub | Familiar file/tree mental model |
| Settings | Vercel | Grouped, scannable, low-drama configuration |
| Activity feed | GitHub | Legible event stream, glanceable |
| Search | Arc | Fast, forgiving, keyboard-driven |
| AI generation | Cursor | Streaming, inline, provenance visible |

## The rich artifact workspace (target layout)

```
┌───────────────────────────────────────────────────────────────┐
│  Project · breadcrumb                                          │
├──────────────┬──────────────────────────────┬─────────────────┤
│  Tabs        │  Main editor                 │  AI panel       │
│  Vision      │  Markdown · Diff · Preview    │  prompt (v)     │
│  PRD         │  (version-aware)              │  provider/model │
│  README      │                              │  tokens · cost  │
│  ADR         │                              │  latency        │
│  Activity    ├──────────────────────────────┤  [ Generate ]   │
│              │  Sidebar: versions · metadata │  streaming      │
└──────────────┴──────────────────────────────┴─────────────────┘
```

- **Left:** artifact tabs (typed, from ADR-0004).
- **Center:** editor with Markdown / Diff / Preview modes; diff when switching versions.
- **Right (inspect):** prompt version, provider/model, live tokens·cost·latency (Principle 3),
  generate action with streaming.

## Evaluation rubric (the gate)

A UI feature is complete only when the answer is "yes" to all:

| Dimension | Question |
|---|---|
| Product | Does it solve the user's problem clearly? |
| UX | Is the workflow obvious? |
| Visual | Does it look premium (vs. Linear/Vercel/Cursor)? |
| Motion | Does animation communicate state? |
| Accessibility | Can everyone use it (AA, keyboard, SR, reduced-motion)? |
| Performance | Will it feel fast (skeletons, streaming, no jank)? |
| Engineering | Is it componentized and maintainable (design-system only)? |
| Portfolio | Would this screen impress a hiring manager? |

## Per-feature UI workflow

```
Feature → UX review → interaction design → component design → implementation
        → a11y review → performance review → visual QA → documentation → commit
```

No UI feature skips a stage. The [design checklist](16-design-checklist.md) is the
implementation-time gate; this rubric is the review-time gate.

## Current gap (honest status)

The slice #1–2 artifact editor is a plain `textarea` + a basic version list — **below this
standard**. It is functional and tested but CRUD-grade. Elevating it to the workspace layout
above is tracked as a dedicated UI slice.
