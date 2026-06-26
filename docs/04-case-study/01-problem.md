# 01 — The Problem

## Why Engineering OS exists

I built Engineering OS because I lived the problem it solves. Rebuilding my own engineering
portfolio, I noticed that the hard part was never writing code — it was the *discipline around*
the code: defining the problem, recording decisions, keeping documentation honest, and applying
consistent standards across repositories. That discipline is what separates a senior engineer's
work from a junior's, and almost nothing helps you do it consistently.

## The frustration, stated precisely

Capable engineers routinely produce work that under-represents their ability:

- They skip the thinking. Vision, requirements, and architecture live in their head, so the
  *why* is gone within weeks — from the repo and from their own memory.
- They document last, if at all. PRDs and ADRs are written after the fact, when the reasoning
  has already faded, so they end up shallow or absent.
- Their tools don't connect. Product thinking in one app, planning in another, code in the IDE,
  AI in a chat tab, standards in a bookmark folder. No tool enforces the lifecycle end to end.

The result is a portfolio that looks like a pile of unfinished demos — which is a poor proxy for
the engineer who built it.

## Why existing tools are insufficient

This is not a gap a single existing category fills:

- **AI chat assistants** (ChatGPT, Claude) produce excellent drafts, but the output is
  ephemeral — a message in a scrollback, not a versioned artifact tied to a project.
- **AI coding tools** (Cursor, Copilot) start *after* the thinking. They accelerate code; they
  don't help you decide what to build or record why.
- **App generators** (v0, Bolt) optimize for a working demo, not a maintainable, documented,
  standards-compliant repository.
- **Product/PM tools** (Notion, Linear) hold documents and tasks but are manual, not AI-native
  to engineering artifacts, and they don't scaffold a repo.

Each owns a slice. None owns the loop from *idea* to *a repository a Staff Engineer would
respect*. That loop is the problem.

## What I am NOT claiming

I am not claiming engineers can't already do this — they can, manually, with enough discipline.
The claim is narrower and more honest: **the discipline is too expensive to apply consistently,
so most people don't.** Engineering OS lowers that cost. Whether lowering the cost is enough to
change behavior is the central product hypothesis, and it is not yet proven (see
[02 — Discovery](02-discovery.md)).

> Cross-references: the structured version of this problem is in
> [PRD §Problem](../01-product/02-prd.md) and [Vision](../01-product/01-product-vision.md).
