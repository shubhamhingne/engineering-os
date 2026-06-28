# Developer-experience KPIs

The contributor's path is itself a measured surface. Mission: a first-time contributor goes from
clone to an open PR in under 30 minutes.

| KPI | Value | Note |
|---|---|---|
| Local setup commands | **1** | `make setup` |
| Commands to first green test | **2** | `make setup` → `make test` |
| Manual file edits to run | **0** | works on defaults (fake providers, SQLite) |
| Time to first test pass | install + ~1s | suite runs in ~1s; install time is network-bound |
| End-to-end demo | **1** command | `make example` (in-process, no server/keys) |
| Required services to start | **0** | the example needs no Postgres/Redis/Docker |
| Onboarding doc | [CONTRIBUTING](../../CONTRIBUTING.md) | clone → setup → run → test → PR |

What's deliberately easy: no API key (fake AI provider), no GitHub app (fake OAuth), no database
server (SQLite), no Node (the example is backend-only). A contributor touches the real architecture
within minutes and the compiler core is clearly marked frozen, so they know what's safe to change.
