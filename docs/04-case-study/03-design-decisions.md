# 03 — Design Decisions

The *product* stances behind Engineering OS (the *technical* decisions are in the
[ADRs](../02-architecture/adr/)). Each is a deliberate position with a cost, not a neutral choice.

## Artifact-first (not conversation-first)

**Decision:** the domain is modeled around versioned artifacts; a chat is at most an input.

**Reasoning:** value the user keeps is the PRD, the ADR, the README — not the dialogue that
produced them. A conversation-first model optimizes for engagement; an artifact-first model
optimizes for *output the user owns*. The latter aligns with the actual job.

**Cost:** we give up the familiar, low-friction chat UX that users already understand. We are
betting that a structured workspace is worth that friction.

## Documentation-first (not code-first)

**Decision:** the product produces and prioritizes the thinking documents before any code.

**Reasoning:** the thinking is the part engineers skip and the part that proves seniority. A
code-first tool would compete head-on with Copilot/Cursor and address the wrong gap.

**Cost:** "documentation tool" is a harder sell than "it writes code." We accept a narrower,
more discerning audience in exchange for owning a real gap.

## Git-native (not a walled garden)

**Decision:** everything exports to Git as plain Markdown; the database is an index/cache.

**Reasoning:** if the output can't leave the tool, it can't be a portfolio asset, and the user is
locked in. Git-native makes the output durable and the tool trustworthy (Principle 3).

**Cost:** we forfeit lock-in as a retention mechanism. Retention must be earned by usefulness,
not by hostage-taking. That's a harder but healthier business.

## Provider-agnostic (not single-model)

**Decision:** AI providers sit behind one port; the model is the user's choice (Principle 5).

**Reasoning:** model quality, price, and availability change monthly. Hard-coding a provider
makes the product fragile to a market we don't control, and creates lock-in we just argued
against. Agnosticism is insurance and a values statement.

**Cost:** more code to maintain (adapters), and we can't deeply exploit any one provider's
proprietary features. Worth it.

## Standards-driven (not blank-slate)

**Decision:** exported repos inherit opinionated engineering standards from a real `.github` repo.

**Reasoning:** consistency *is* the product. A blank-slate generator produces inconsistent repos;
the value is that every output meets a bar. Opinion is a feature here, not a limitation.

**Cost:** our opinions won't fit everyone. We accept being wrong for some users in exchange for
being unusually right for our target user.

## The through-line

Every stance trades short-term ease (chat, code, lock-in, single-model, flexibility) for
long-term value to a *serious* engineer (ownership, durability, consistency). That is a coherent
bet, and it is the bet I would defend in a review. It could be the wrong bet — the section on
[trade-offs](04-trade-offs.md) and the [failure log](05-failure-log.md) make the alternatives,
and the risk, explicit.
