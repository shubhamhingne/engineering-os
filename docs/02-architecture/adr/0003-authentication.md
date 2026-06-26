# 0003 — Authentication & GitHub authorization

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** ADR-0002, [16 — Security model](../16-security-model.md)

## Context

Users sign in and, to export repositories, the product must act on their behalf against the
GitHub API. We must separate **authentication** (who the user is) from **authorization to
GitHub** (a scoped, revocable capability), and store any third-party tokens safely.

## Decision

- **Authentication:** email/password **and** GitHub OAuth, both resulting in a first-party
  **HTTP-only, secure, same-site session cookie**. Passwords hashed with Argon2id.
- **GitHub authorization:** a **separate OAuth grant** requesting the **minimum scope** needed
  to create repositories and push (`repo` or finer-grained equivalents). The GitHub token is
  **encrypted at rest** (envelope encryption) and never sent to the browser.
- Sessions are server-validated; logout revokes the session. GitHub can be disconnected
  independently, deleting the stored token.

## Alternatives considered

- **JWT access tokens in the browser (localStorage).** Stateless, simple. Rejected: XSS token
  theft risk and no easy server-side revocation. HTTP-only cookies + server sessions are safer.
- **GitHub OAuth as the only sign-in.** Simplest. Rejected: excludes users who want to evaluate
  before connecting GitHub, and couples identity to a capability that should be revocable
  separately.
- **GitHub App (installation tokens) instead of OAuth.** Finer permissions and short-lived
  tokens — attractive. Deferred, not rejected: more setup than the MVP needs; revisit for v2 to
  reduce token blast radius (see below).

## Trade-offs

- (+) Identity and GitHub capability are decoupled and independently revocable.
- (+) HTTP-only cookies remove client-side token theft via XSS.
- (−) Server-side sessions add state (stored in Redis/DB) vs. stateless JWT.
- (−) OAuth user tokens are broader and longer-lived than GitHub App installation tokens.

## Consequences

- A `Provider`/credential store holds encrypted GitHub tokens, scoped per user.
- The browser never holds a GitHub token; all GitHub calls are server-side.
- CSRF protection required for cookie-based auth (same-site + token).

## Future revisit criteria

Migrate GitHub authorization to a **GitHub App** (installation tokens, per-repo permissions,
short-lived) when: external/multi-user growth raises token blast-radius concerns, or users
request least-privilege per-repo access. The `GitHubPort` abstraction makes this an adapter
change, not a redesign.
