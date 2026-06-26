# 15 — User Flows

The key journeys, with **happy paths and failure paths**. A flow that only documents success is
half a design. Diagrams are Mermaid (version-controlled).

## Core flow — idea to repository

```mermaid
flowchart TD
    A[New project from idea] --> B[Generate Vision]
    B --> C{Review}
    C -->|edit| C
    C -->|accept| D[Generate PRD]
    D --> E{Review}
    E -->|edit| E
    E -->|accept| F[Generate Architecture + ADR]
    F --> G{Review}
    G -->|accept| H[Generate README]
    H --> I[Export repository]
    I --> J([Repo live on GitHub])
```

The loop is always **generate → review/edit → accept**: the human is editor-in-chief at every
step (Principle 1).

## Failure path — AI generation fails

```mermaid
flowchart TD
    A[Generate artifact] --> B{Provider responds?}
    B -->|timeout/error| C[Show calm error<br/>draft preserved]
    C --> D{User choice}
    D -->|Retry| A
    D -->|Switch model| E[Re-run with other provider]
    D -->|Edit manually| F[Open editor]
    B -->|rate/budget limit| G[Explain limit + reset time]
```

No work is lost; every failure offers a concrete next step ([12](12-empty-loading-error-states.md)).

## Failure path — GitHub authorization

```mermaid
flowchart TD
    A[Export repository] --> B{GitHub connected & valid?}
    B -->|no/expired| C[Prompt: Reconnect GitHub]
    C --> D[OAuth re-consent]
    D --> A
    B -->|name conflict| E[Ask to rename] --> A
    B -->|ok| F[Create repo + push] --> G([Repo URL])
```

## Auth flow

```mermaid
flowchart TD
    A[Sign in] --> B{Method}
    B -->|GitHub| C[OAuth] --> D[Session cookie]
    B -->|Email| E[Validate] --> D
    E -->|invalid| F[Inline error] --> A
    D --> G([Dashboard])
```

## Edge cases captured

- **Empty workspace** → onboarding empty state guides to the first project.
- **Mid-generation navigation** → run continues in background; result persists (no lost work).
- **Concurrent edits to one artifact** → last-saved wins in MVP (single-user); a new version is
  created, history preserved (no destructive overwrite).
- **Provider not configured** → generation is blocked with a clear path to Settings → Connect.

## Why document failure paths

Most of a real product's surface area is the unhappy path. Designing retries, re-auth, limits,
and "your work is safe" up front is what makes the product feel trustworthy — and is exactly the
rigor a Staff Engineer looks for in a portfolio.
