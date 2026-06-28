# examples

## `seed.py` — the whole pipeline in one run

```bash
make example            # or:  python examples/seed.py   (after `make setup`)
```

No server, no GitHub app, no API key — it drives the API in-process with the fake OAuth + AI
providers. Output:

```
created project '…': Acme API
  generated vision  v1 (285 chars)
  generated prd     v1 (321 chars)
  generated readme  v1 (615 chars)
explanations: 3 entities, e.g. tech:FastAPI, topic:authentication, topic:billing
manifest 9adcc4a88b23 · 6 artifacts
```

It walks the full path: sign in → create a project → compile Vision/PRD/README from the
`KnowledgeGraph` → explain every entity → produce the immutable build manifest. The same happy path
is covered by the test suite (`tests/test_e2e.py`), so this example can't silently rot.

## Against a running server

After `make dev` (or `docker compose up`), the same flow is available over HTTP at
`http://localhost:8000` — see the OpenAPI docs at `/docs`.
