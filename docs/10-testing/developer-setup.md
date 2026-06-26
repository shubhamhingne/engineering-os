# Developer Setup

Goal: **clone → productive in under 15 minutes.** If any step here takes longer or is unclear,
that's a bug in this document — fix it.

## Prerequisites

| Tool | Version | Check |
|---|---|---|
| Node | ≥ 20 | `node -v` |
| pnpm | ≥ 9 | `pnpm -v` |
| Python | ≥ 3.12 | `python3 --version` |
| Docker | latest | `docker --version` |
| Git | ≥ 2.40 | `git --version` |

Run `bash tooling/scripts/verify-environment.sh` to check all of these at once.

## One-command bootstrap

```bash
git clone https://github.com/shubhamhingne/engineering-os.git
cd engineering-os
bash tooling/scripts/setup-dev.sh
```

`setup-dev.sh` will (once implemented): start infrastructure (`docker compose up -d`), install
web and api dependencies, copy `.env.example` → `.env`, and run health checks.

## Manual steps (until scripts are filled in)

```bash
docker compose up -d                 # postgres + redis
cp apps/api/.env.example apps/api/.env   # configure secrets
pnpm install                          # web + shared packages
(cd apps/api && pip install -e ".[dev]")  # api
```

## Run

```bash
pnpm --filter web dev        # web → http://localhost:3000
(cd apps/api && uvicorn ...) # api → http://localhost:8000  (command finalized in impl)
```

## Verify your setup

```bash
pnpm check:docs              # documentation links resolve
pnpm --filter web test       # web tests
(cd apps/api && pytest -q)   # api tests
```

> This document is a skeleton: exact commands are finalized when implementation lands (Day 9+).
> The **contract** — one clone, one bootstrap command, productive in 15 minutes — is fixed now.
