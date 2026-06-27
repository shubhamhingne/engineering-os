<div align="center">
  <h1>Engineering OS</h1>
  <p><em>A semantic compiler for software projects.</em></p>
  <p>It transforms structured project knowledge into engineering artifacts through a typed,
  dependency-driven compilation pipeline — with explicit planning, provenance, incremental
  execution, immutable build identity, and transport-independent publication.</p>
  <p>
    <strong>Status:</strong> <strong>v1.0</strong> — compiler model frozen ·
    <a href="docs/02-architecture/20-compiler-specification.md">specification</a> is the contract ·
    Built on the <a href="https://github.com/shubhamhingne/.github">org engineering standards</a>
  </p>
</div>

> **This repository is complete with respect to the v1.0 specification.** Future work explores the
> *consequences* of the model rather than extending it. New capability enters as *implementation*
> behind the existing contracts; the model itself changes only through a versioned amendment under
> the [specification's governance rule](docs/02-architecture/20-compiler-specification.md#governance).

> This README is the entry point. A new visitor should be able to navigate the entire project
> from here.

## Why Engineering OS?

Strong engineers ship work that under-sells them. The hard part of a great repository isn't the
code — it's the discipline around it: defining the problem, recording decisions, keeping docs
honest, applying consistent standards. Engineering OS lowers the cost of that discipline: it
guides a project through the lifecycle great engineers already follow and uses AI to remove the
friction — without making the decisions.

→ [The problem, in full](docs/04-case-study/01-problem.md)

## Navigate

| Section | Start here |
|---|---|
| 🎯 **Vision & Product** | [Vision](docs/01-product/01-product-vision.md) · [PRD](docs/01-product/02-prd.md) · [Personas](docs/01-product/04-personas.md) · [Metrics](docs/01-product/07-success-metrics.md) |
| 🏛 **Architecture** | [Why semantic compilation](docs/02-architecture/21-why-semantic-compilation.md) (design paper) · [Compiler Specification](docs/02-architecture/20-compiler-specification.md) · [Invariants](docs/02-architecture/19-compiler-invariants.md) · [Architecture History](ARCHITECTURE_HISTORY.md) · [System Architecture](docs/02-architecture/08-system-architecture.md) · [ADRs](docs/02-architecture/adr/) · [Domain](docs/02-architecture/10-domain-model.md) · [Database](docs/02-architecture/11-database-design.md) · [API](docs/02-architecture/12-api-specification.md) · [Security](docs/02-architecture/16-security-model.md) · [Observability](docs/02-architecture/17-observability.md) |
| 🎨 **Design System** | [Principles](docs/03-design-system/01-design-principles.md) · [Tokens](docs/03-design-system/02-design-tokens.md) · [Components](docs/03-design-system/07-component-library.md) · [Wireframes](docs/03-design-system/14-wireframes.md) · [UI/UX Pro Max](docs/03-design-system/17-ui-ux-pro-max.md) · [Workspace Spec](docs/03-design-system/18-workspace-design-spec.md) |
| 📖 **Case Study** | [Problem](docs/04-case-study/01-problem.md) · [Design Decisions](docs/04-case-study/03-design-decisions.md) · [Trade-offs](docs/04-case-study/04-trade-offs.md) · [Failure Log](docs/04-case-study/05-failure-log.md) · [Demo Script](docs/04-case-study/08-demo-script.md) |
| 🛠 **Developer Guide** | [Setup](docs/10-testing/developer-setup.md) · [Workflow](docs/10-testing/development-workflow.md) · [Coding Standards](docs/10-testing/coding-standards.md) · [Testing](docs/10-testing/testing-strategy.md) · [Release](docs/10-testing/release-process.md) · [Bootstrap](docs/10-testing/repository-bootstrap.md) |
| 🧭 **Decisions** | [Decision Log](docs/08-decisions/README.md) · [Tech Stack](docs/08-decisions/tech-stack.md) |
| 🗺 **Roadmap** | [MVP → v2 → v3](docs/01-product/06-roadmap.md) |
| 🤝 **Contributing** | [CONTRIBUTING](CONTRIBUTING.md) · [Standards](https://github.com/shubhamhingne/.github) |

## Repository structure

```
engineering-os/
├── apps/
│   ├── web/            Next.js frontend (skeleton)
│   └── api/            FastAPI backend (skeleton)
├── packages/
│   ├── ui/             shared component library
│   ├── config/         shared lint/format/TS config
│   └── types/          shared API contracts
├── tooling/
│   ├── scripts/        bootstrap · setup · verify · check-doc-links
│   └── generators/     scaffolding generators
├── docs/               01-product … 10-testing (unified blueprint)
├── design/             figma · wireframes · mockups · exports
├── tests/              cross-cutting / e2e
├── examples/           runnable examples
└── .github/            CI · Dependabot · labels (standards)
```

## Quickstart

```bash
git clone https://github.com/shubhamhingne/engineering-os.git
cd engineering-os
bash tooling/scripts/bootstrap.sh     # verify env · start infra · install · check docs
```

Full guide: [docs/10-testing/developer-setup.md](docs/10-testing/developer-setup.md).

## Product journey

```
Vision → PRD → Architecture → Narrative → Design System → Bootstrap → (Implementation) → (Release)
  ✅       ✅         ✅            ✅            ✅             ✅            next            then
```

> The repository currently contains **thinking and infrastructure, not application code** — by
> design. Every line of code that follows has a documented purpose and place.

## License

[MIT](LICENSE) © Shubham Hingne
