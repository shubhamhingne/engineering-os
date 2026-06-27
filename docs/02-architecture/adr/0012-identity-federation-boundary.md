# 0012 — Identity, GitHub federation, and the compiler boundary

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0003](0003-authentication.md), [ADR-0009](0009-semantic-build-system.md), [ADR-0011](0011-explainability-compiler-passes.md)

## Context

The compiler can turn an idea into a published GitHub repo, but anyone could publish as anyone —
there was no identity. The missing piece is proving a user is allowed to act and to publish.

The risk in adding authentication is that it leaks *inward*. If the compiler starts taking a
`User`, a session, or a token, it stops being a pure project→artifacts function and can no longer
run in a CLI, a CI job, a batch run, or a test without a logged-in user. The compiler has reached a
level of conceptual integrity worth protecting (ADR-0011); authentication must wrap it, not enter it.

## Decision

Add identity as **application-layer services around the compiler**, GitHub-first.

**Identity.** One minimal `User` (`id`, `github_id`, `username`, `avatar_url`) — no passwords, no
email, no profile editing. A `UserSession` holds the GitHub access token, scoped to the session
(never on the User, never in the compiler). The opaque session id is an HttpOnly cookie.

**Federation.** A single provider behind an `OAuthProvider` port (`authorize_url` / `exchange_code`
/ `fetch_identity`). `GitHubOAuthProvider` is the real adapter; a `FakeOAuthProvider` makes the
whole flow runnable in tests and local dev with no GitHub app — the same fake/real split as the AI
provider. The flow is: GitHub OAuth → application session → GitHub access token.

**Authorization.** Deliberately flat: a user owns a project, or `403`. No teams, roles, or sharing.
Enforced in exactly one dependency, `get_owned_project` (404 if absent, 403 if not yours); every
project-scoped route depends on it.

**The boundary, made structural.** The request path is:

```
authenticate()  →  authorize(project)  →  compiler.compile(project)  →  publish(bundle, credential)
```

The compiler receives a `Project`. It never receives a `User`, session, OAuth, or permissions.

**The `CredentialProvider` seam.** Publishing needs the user's GitHub token, but `GitHubPublisher`
must not learn that OAuth exists. So a `CredentialProvider` port sits between them:
`get_publishing_credential(publisher_type) -> token`. The session's token is wrapped as a
`GitHubCredentialProvider`; the endpoint asks it for a credential and builds the client from that.
A future `GitLabCredentialProvider` slots in without touching the publisher or the compiler — the
same dependency inversion the renderers/publishers split established.

## Alternatives considered

- **Email/password first, GitHub as a linked federation.** Rejected for now: the users already work
  through GitHub, and publishing *needs* a GitHub token regardless — local accounts would be an
  unrelated identity system to build and secure. Local accounts make sense when this becomes a
  collaboration platform; today it is a publishing platform.
- **Pass the `User`/token into the compiler.** Rejected: it destroys the compiler's usability in
  CLI/CI/tests and entangles identity with compilation. This ADR exists largely to forbid it.
- **Authentication as a `CompilerPass`.** Rejected: a pass transforms project knowledge; identity
  decides *whether* to run the compiler and *where* to publish, not *what* it compiles.

## Trade-offs

- (+) The compiler stays a pure `project → artifacts` function — runnable headless, unchanged.
- (+) One authorization choke point; ownership can't be forgotten on a route.
- (+) Publishers remain OAuth-agnostic; new providers are new adapters.
- (−) Sessions are server-side rows (a read per request) rather than stateless JWTs — simpler and
  revocable now, a caching concern only at far larger scale.
- (−) GitHub-only login excludes users without a GitHub account — acceptable for the current
  audience; the `OAuthProvider` port leaves room for more.

## Consequences

- Projects are now owned; `GET /projects` is scoped to the caller and cross-user access is `403`.
- The GitHub token lives on the session and reaches the publisher only through the credential port.
- `RepositorySyncPass` (the next compiler addition) will receive a token *handed in* by this outer
  layer rather than reaching for identity itself — the one seam that touches remote state.

## Future revisit

The **typed `CompilerContext`** is the next internal refactor (ADR-0011) — startup-time validation
of each pass's declared inputs. Then `RepositoryState` via a `RepositorySyncPass`. Local accounts,
teams, and roles wait until the product becomes collaborative.
