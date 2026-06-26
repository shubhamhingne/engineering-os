# 08 — Demo Script

A 5-minute walkthrough for an interview or talk. The goal is to demonstrate *judgment*, so the
script spends as much time on *why* as on *what*. Timings are guides.

## 0:00–0:45 — The problem

> "Strong engineers ship work that under-sells them. The hard part of a great repository isn't
> the code — it's the discipline around it: defining the problem, recording decisions, keeping
> docs honest. That discipline is expensive, so most people skip it, and their GitHub looks like
> a pile of demos instead of evidence of how they think. I felt this rebuilding my own portfolio."

Land the problem before the product. If they don't feel the pain, the demo won't matter.

## 0:45–1:15 — The solution, in one sentence

> "Engineering OS takes an idea to a documented, standards-compliant repository by walking it
> through the lifecycle great engineers already follow — and using AI to remove the friction,
> not to make the decisions."

State the positioning and the one boundary that defines it: *artifacts, not chat.*

## 1:15–3:00 — Live walkthrough (the core loop)

1. **New project** from a one-paragraph idea.
2. **Generate the Vision and PRD** — show streaming, then *edit one line* to make the point:
   "AI drafts; I decide. The output is a versioned artifact, not a chat message."
3. **Generate an ADR** — show the Context/Decision/Alternatives format.
4. **Export to GitHub** — one action creates a repo scaffolded with my `.github` standards plus
   these docs. Open the live repo.

The "aha" is the export: *idea to a real, standards-compliant repo, in minutes.*

## 3:00–4:00 — Architecture highlights

> "Three things I'd call out. One: it's a modular monolith with a hexagonal core — AI providers
> and GitHub sit behind ports, so swapping OpenAI for Anthropic is a new adapter, not a redesign.
> Two: the domain is modeled around artifacts and immutable versions, not conversations — that's
> the product thesis in the schema. Three: every AI call is observed — tokens, cost, latency,
> trace — because an unobserved AI action is a defect."

Show the C4 container diagram and the `generation_runs` table briefly.

## 4:00–4:30 — Why the design matters

> "Every major decision has a documented trade-off and a list of what I rejected and why —
> multi-agent, RAG, code-gen, offline-first. The interesting work was saying *not yet* to good
> ideas so the core could ship. That's in the failure log."

This is the slide that separates the candidate. Point to [05 — Failure Log](05-failure-log.md).

## 4:30–5:00 — Future and close

> "Today it's a workspace for one engineer. The direction is a team's shared engineering memory —
> the reasoning behind systems, captured by default instead of lost. I'm uncertain whether that's
> a feature or a company, and I'd rather name that uncertainty than pretend I know."

Close on the through-line: *artifact-first, durable, AI-assisted, opinionated — a coherent bet I
can defend.*

## Interviewer Q&A — be ready for

- "What's your riskiest assumption?" → lowering the cost of discipline changes behavior; unproven.
- "Why not just use ChatGPT?" → ephemeral output, no project model, no standards, no repo.
- "Where would this break at scale?" → extract the generation path; the port boundary makes it
  low-risk (ADR-0001 revisit criteria).
- "What did you cut and regret?" → none yet; the cuts were correct for the MVP, by design.
