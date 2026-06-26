# Release Process

Follows the organization
**[Release Process](https://github.com/shubhamhingne/.github/blob/main/docs/RELEASE_PROCESS.md)**
(SemVer + Conventional Commits + auto-generated notes). This page records the repo-specific bits.

## Versioning this monorepo

- The repository is versioned as a whole at the MVP stage: one `vMAJOR.MINOR.PATCH` tag for
  Engineering OS. `apps/web` and `apps/api` ship together.
- Version is derived from Conventional Commits since the last tag (`feat` → minor, `fix` → patch,
  `feat!`/`BREAKING CHANGE` → major).
- Independent per-package versioning (web/api/ui) is deferred until they have separate consumers.

## Cutting a release

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

1. Tag on `main`.
2. GitHub Release is created; notes auto-generate from PR labels (`.github/release.yml`).
3. Review/edit the notes for narrative, then publish.
4. Deploy is triggered by the tag (see [deployment](../02-architecture/15-deployment-architecture.md)).

## Pre-1.0

While pre-1.0, minor versions may include breaking changes (standard SemVer 0.x semantics).
`v1.0.0` is cut when the MVP is feature-complete and stable in real use.

## Changelog

Release notes are the changelog (auto-generated from labels). A standalone `CHANGELOG.md` is
optional and, if added, follows Keep a Changelog.
