# Contributing

This repository follows the organization-wide engineering standards in
**[shubhamhingne/.github](https://github.com/shubhamhingne/.github)** — Conventional Commits,
`type/short-description` branches, the PR template, and the code-review checklist all apply here.

> **Goal:** a first-time contributor can go from a clone to an open pull request in under 30 minutes.

## From clone to PR

```bash
# 1. Setup (needs Python 3.12 — see .python-version)
git clone https://github.com/shubhamhingne/engineering-os && cd engineering-os
make setup                      # creates the venv and installs the API (editable)

# 2. Run it
make example                    # end-to-end demo, in-process, no server/keys needed
make dev                        # or serve the API at http://localhost:8000

# 3. Verify before you push
make test                       # ruff + the full test suite (must pass — CI gates on this)

# 4. Branch, commit (Conventional Commits), open a PR
git switch -c feat/my-change
```

## The compiler core is frozen

The compilation model is governed by a
[specification](docs/02-architecture/20-compiler-specification.md#governance). Before changing
anything under `modules/compiler/`, answer: **does this change the specification, or only the
implementation?** A specification change needs an ADR; everything else must preserve the existing
[invariants](docs/02-architecture/19-compiler-invariants.md) (the compiler fingerprint must not move
for unrelated work).

## Where things are

- Backend: [`apps/api/src/engineering_os/`](apps/api/src/engineering_os/) · tests in `apps/api/tests/`.
- Architecture: [specification](docs/02-architecture/20-compiler-specification.md) ·
  [invariants](docs/02-architecture/19-compiler-invariants.md) · [ADRs](docs/02-architecture/adr/).
- Beta hardening: [readiness register](docs/08-decisions/beta-readiness-register.md) ·
  [quality dashboard](docs/quality/dashboard.md).
- Developer docs: [`docs/10-testing/`](docs/10-testing/).

## Good first issues

Look for the `good first issue` label. Strong starters come from the
[readiness register](docs/08-decisions/beta-readiness-register.md) — items marked Medium or
Nice-to-have (e.g. the lockfile, more examples, runbooks).

## Standards in this repo

- **Tests required.** New behavior needs a test; prefer *semantic* tests (assert meaning, not markup).
- **Lint clean.** `ruff check` must pass; pre-commit runs `ruff`, `gitleaks`, and `detect-private-key`.
- **No secrets, ever.** Token handling is documented in [SECURITY.md](SECURITY.md).
