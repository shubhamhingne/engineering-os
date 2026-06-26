# Performance evidence

Per-slice performance budgets and reports. Targets are tied to the shipped workspace UI; reports
are captured on a machine running the app (`pnpm dev` / `pnpm build`).

## Budgets (Day 12 — workspace)

| Metric | Target |
|---|---|
| Initial load | < 2 s |
| Artifact switch | < 150 ms |
| Save response | < 300 ms |
| Generation feedback (first stage) | < 100 ms |
| Animation | 60 FPS |
| Lighthouse — Performance | > 95 |
| Lighthouse — Accessibility | 100 |

## To capture (on a Node machine)

```bash
pnpm --filter web build && pnpm --filter web start
npx lighthouse http://localhost:3000 --output html --output-path docs/06-media/performance/lighthouse.html
npx next build   # bundle analysis output
```

Drop `lighthouse.html`, a bundle report, and Web Vitals here as each slice ships.
