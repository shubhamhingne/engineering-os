# 03 — User Stories

Stories for the MVP, grouped by epic. Format: *As a … I want … so that …*, with acceptance
criteria. Out-of-scope stories are listed at the end for the v2 backlog.

## Epic 1 — Account & access

**US-1.1** — As a developer, I want to sign in with GitHub, so that I can connect my repos
without a separate account.
- [ ] GitHub OAuth completes and creates/links an account.
- [ ] Email/password sign-up is also available.
- [ ] Sessions persist; sign-out works.

## Epic 2 — Project workspace

**US-2.1** — As a developer, I want to create a project from a short idea description, so that
I can start the lifecycle immediately.
- [ ] I can enter a title and a free-text idea.
- [ ] The project is saved and appears in my project list.

**US-2.2** — As a developer, I want to see all my projects and their lifecycle stage, so that
I know what to work on next.
- [ ] Project list shows title, last updated, and current stage.

## Epic 3 — AI artifact generation

**US-3.1** — As a developer, I want the system to draft a Product Vision from my idea, so that
I start with structure instead of a blank page.
- [ ] Vision is generated and displayed as editable Markdown.
- [ ] I can regenerate or edit, and changes are saved.

**US-3.2** — As a developer, I want to generate a PRD from the vision, so that requirements
and scope are explicit.
- [ ] PRD references the vision; sections are editable.

**US-3.3** — As a developer, I want an architecture overview and at least one ADR, so that key
decisions are recorded.
- [ ] Architecture overview and an ADR are generated and editable.

**US-3.4** — As a developer, I want a README generated from my artifacts, so that the repo is
documented from day one.
- [ ] README reflects the project's vision, features, and stack.

**US-3.5** — As a cost-conscious developer, I want to choose the AI model per generation, so
that I can trade cost for quality.
- [ ] A model selector is available; the choice is applied and recorded.

## Epic 4 — GitHub scaffolding

**US-4.1** — As a developer, I want to connect GitHub, so that the workspace can create repos
for me.
- [ ] GitHub is connected with the minimum required scope.

**US-4.2** — As a developer, I want to export my project to a new GitHub repository, so that it
ships with standards and my docs in place.
- [ ] A new repo is created and pushed with: README, LICENSE, `.github` standards, and the
      project's `docs/` artifacts.
- [ ] The repo URL is shown on success; failures are reported clearly.

## Epic 5 — Persistence & continuity

**US-5.1** — As a developer, I want my projects and artifacts to persist, so that I can return
later without losing work.
- [ ] All artifacts reload across sessions and devices.

## v2 backlog (out of scope now)

- As a developer, I want an agent to complete an entire lifecycle stage with checkpoints.
- As a developer, I want a code-review assistant that checks a diff against the standards.
- As a mobile user, I want a companion app to review and approve artifacts on the go.
- As a team lead, I want shared workspaces and roles.
