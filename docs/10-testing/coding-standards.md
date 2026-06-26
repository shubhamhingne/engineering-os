# Coding Standards

Consistency lowers the cost of every future change. These standards are enforced by tooling
where possible (the machine, not the reviewer, catches formatting).

## Universal

- **Names reveal intent.** No `data2`, `tmp`, `helper3`. A name is documentation.
- **Small, single-purpose functions and modules.**
- **Comments explain *why*, not *what*.** The code says what.
- **Errors are handled, never swallowed.** No empty `catch` / bare `except`.
- **No secrets, ever.** Config via environment; secrets via a manager.
- **Tests live beside the code** they test; behavior changes ship with tests.

## Frontend — `apps/web`, `packages/ui` (TypeScript)

- **TypeScript strict mode**; no `any` without a written reason.
- **Feature-first** structure ([folder structure](../02-architecture/13-folder-structure.md)).
- Components consume **design tokens only** ([design system](../03-design-system/02-design-tokens.md)) — no hard-coded colors/spacing.
- Format with **Prettier**, lint with **ESLint** (configs from `packages/config`).
- Prefer server components / data fetching at the edge; keep client components lean.
- Accessibility is non-negotiable ([a11y](../03-design-system/11-accessibility.md)).

## Backend — `apps/api` (Python)

- **Python 3.12, full type hints**; `mypy` clean.
- **Hexagonal dependency rule (enforced):** `modules/` and `ports/` must **never** import from
  `adapters/`. Dependencies point inward. This keeps providers replaceable.
- Format + lint with **Ruff** (`ruff format`, `ruff check`).
- All external calls (AI, GitHub, DB) go through a **port**; never call a vendor SDK from a module.
- Pydantic for boundaries (request/response, settings); SQLAlchemy in the DB adapter only.

## Shared contracts — `packages/types`

- API types are **generated from the OpenAPI spec**, not hand-written, so web and api can't drift.

## Architectural invariants (reviewed in every PR)

| Invariant | Why |
|---|---|
| No business logic in UI/controllers | Testability, clean layering |
| No vendor SDK in `modules/` | Provider replaceability (Principle 5) |
| Artifact versions are immutable | History integrity (Principle 3) |
| Every AI call goes through the observed adapter | Observability (Principle 4) |

## Enforcement

Formatting and linting are automated (pre-commit + CI). Reviewers focus on **design and
correctness**, not style — the machine owns style so humans own judgment.
