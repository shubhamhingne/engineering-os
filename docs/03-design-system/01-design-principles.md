# 01 — Design Principles

Engineering OS is a tool serious engineers use daily. It should feel like Linear, GitHub,
Vercel, and Notion: calm, dense, fast, and out of the way. These principles are explicit and
testable — "clean" and "modern" are not principles, they're wishes.

## The six principles

### 1. Documentation before decoration
Information density beats visual flourish. A screen earns its pixels by surfacing useful
content, not by looking impressive. When in doubt, show more signal, less chrome.

### 2. Progressive disclosure
Default to the simple path; reveal advanced controls (model params, prompt internals, raw
diffs) only when the user asks. The first screen a user sees is never the busiest.

### 3. Everything is inspectable
Every AI output exposes its provenance: prompt version, provider, model, tokens, cost, latency.
Trust is built by making the machine legible (Principle 4 of the architecture).

### 4. Keyboard first
Every major workflow has a shortcut and is reachable from a command palette. The mouse is
optional, never required. Engineers live on the keyboard; the product respects that.

### 5. Git-native mental model
Projects, artifacts, versions, and history map to concepts engineers already hold. Versioning
is visible; nothing is a hidden, unrecoverable mutation. The UI mirrors the domain.

### 6. Calm interfaces
No decorative animation, no attention-grabbing motion, no notification noise. Motion is
functional (orientation, feedback) and subtle. The interface is quiet so the work is loud.

## How principles resolve conflicts

When two pulls compete, this is the priority order:

> **Clarity > Density > Speed > Aesthetics.**

Example: if a denser layout hurts comprehension, comprehension wins. If an animation would look
nice but adds latency or noise, it's cut (Principles 1 and 6).

## Anti-patterns (explicitly rejected)

- Marketing-style hero animations inside the app.
- Hiding cost or provider details to look "magical" (violates Principle 3).
- Mouse-only actions with no keyboard equivalent (violates Principle 4).
- Modal-heavy flows that interrupt rather than disclose (violates Principle 2).

## Trade-off acknowledged

A dense, keyboard-first, decoration-light product is **less immediately approachable** to a
casual visitor than a colorful, animated one. That is a deliberate trade: we optimize for the
daily power user (our persona), not the first-15-seconds impression. The marketing site, not the
app, carries the wow.
