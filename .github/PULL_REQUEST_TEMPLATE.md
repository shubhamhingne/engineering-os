<!-- Implementation PRs trace to evidence (the No-Build rule). For a pure chore/docs PR, say so and
     delete the Evidence block. A feature/UX change without evidence will be asked to justify itself. -->

## Evidence
- **Board item:** <!-- e.g. V-017 -->
- **Observed:** <!-- what real users actually did -->
- **Impact:** <!-- how many / how much, e.g. "36% failed to complete the workflow" -->

## Change
- **Decision:** <!-- the *smallest* change that addresses the observation -->
- **Specification or implementation?** <!-- frozen core → requires an ADR amending the spec -->

## Success metric
- <!-- the behaviour we expect to move, e.g. "completion 64% → >85%" -->

## Checklist
- [ ] Traces to a [validation-board](../docs/05-demo/validation-board.md) row (or a chosen strategic objective)
- [ ] Preserves the frozen compiler core (fingerprint unchanged for unrelated work)
- [ ] Tests added / updated · lint clean
