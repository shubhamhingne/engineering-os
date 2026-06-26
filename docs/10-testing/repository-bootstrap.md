# Repository Bootstrap

How this repository was stood up from the organization standards — and how to bootstrap the next
flagship the same way.

## Inheritance model (important)

The `.github` repository provides two kinds of standards. They are applied differently:

| Kind | Examples | How applied here |
|---|---|---|
| **Inherited** (automatic) | `CONTRIBUTING`, `SECURITY`, `CODE_OF_CONDUCT`, issue forms, PR template | Apply automatically from `shubhamhingne/.github`; **not duplicated**. This repo adds short pointer `CONTRIBUTING.md`/`SECURITY.md` for visibility. |
| **Copied** (per-repo) | `.editorconfig`, `.pre-commit-config.yaml`, `CODEOWNERS`, `dependabot.yml`, `release.yml`, `labels.yml`, CI workflows | **Vendored into this repo**, because GitHub does not inherit config files. |

> This is the senior nuance: we don't blindly duplicate everything (that reintroduces drift). We
> inherit what GitHub inherits and copy only what it can't. See the
> [standards repo README](https://github.com/shubhamhingne/.github).

## What was created

- **Docs blueprint:** `docs/01-product … 10-testing` (the unified flagship structure).
- **Skeleton:** `apps/{web,api}`, `packages/{ui,config,types}`, `tooling/{scripts,generators}`,
  `tests/`, `examples/`, `design/`.
- **Standards:** copied configs above + monorepo `web-ci`/`api-ci` workflows + `label-sync`.
- **Root config:** `package.json` (workspaces), `pnpm-workspace.yaml`, `docker-compose.yml`,
  `.gitignore`.

## Bootstrapping the next flagship

```bash
# from the .github repo
bash scripts/bootstrap-repo.sh /path/to/new-flagship
```

Then: create the docs blueprint folders, copy the doc structure, enable branch protection
([guide](https://github.com/shubhamhingne/.github/blob/main/docs/BRANCH_PROTECTION.md)),
set the social preview, and run the label sync. The full list is the
[Repository Creation Checklist](https://github.com/shubhamhingne/.github/blob/main/docs/REPOSITORY_CREATION_CHECKLIST.md).

## Verifying the bootstrap

```bash
python3 tooling/scripts/check-doc-links.py   # all doc links resolve
bash tooling/scripts/verify-environment.sh   # toolchain present
```
