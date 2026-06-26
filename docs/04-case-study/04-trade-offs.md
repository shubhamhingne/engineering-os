# 04 — Trade-offs

Directions Engineering OS consciously did **not** take. Each was plausible; each was rejected for
a reason, not by default. Naming the path not taken is how you show a decision was actually made.

## Why not a chat interface

A chat box is the obvious, familiar UX for an AI product. Rejected as the primary surface
because chat optimizes for conversation, and our value is *artifacts*. A chat-first product
quietly teaches users that the scrollback is the deliverable — the opposite of the positioning.
Chat may return later as an *input* to generation, never as the home screen.

## Why not a no-code builder

"Idea → working app, no code" is a hot category (v0, Bolt). Rejected because it optimizes for a
visible demo, not a maintainable, documented repository — and it attracts users who don't value
the engineering discipline that is our entire point. We would win a demo and lose the mission.

## Why not a VS Code extension first

Meeting engineers in their editor is attractive and lowers adoption friction. Rejected as the
*first* surface for two reasons: (1) the MVP is about the pre-code thinking, which doesn't belong
in the editor yet; (2) an extension constrains the workspace UX we need to design the artifact
flow well. A web app gives us room to get the core loop right first. An extension is a strong
*later* distribution channel.

## Why not mobile-first

The core work — writing and editing engineering artifacts — is a desktop, keyboard-heavy task.
Mobile-first would compromise the primary experience to serve a secondary context. Mobile earns
its place in v2 as a *companion* for review/approval, not as the primary client.

## Why not offline-first

Offline-first adds significant complexity (sync, conflict resolution, local models). The product
depends on hosted AI providers and GitHub, both online. Paying the offline-first tax to support a
use case the product fundamentally can't fulfill offline would be incoherent. Rejected.

## The meta-point

None of these are bad ideas in the abstract; several are good products *for a different thesis*.
They were rejected because they conflict with **this** product's thesis: artifact-first,
documentation-first, durable, for serious engineers. A decision you can't argue *against* isn't a
decision — these show the bet was made with eyes open. The ones that were close calls, rather
than clear rejections, are logged in [05 — Failure Log](05-failure-log.md).
