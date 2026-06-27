# Security Policy

See the organization security policy:
**https://github.com/shubhamhingne/.github/blob/main/SECURITY.md**

Report vulnerabilities privately — never in a public issue.

## Token handling

- **GitHub OAuth tokens are encrypted at rest.** They are encrypted (Fernet/AES) before being written
  to the database and decrypted only at the point of use; no column ever holds a plaintext token.
  Production must set `TOKEN_ENCRYPTION_KEY`.
- **The compiler never sees credentials.** Tokens live on the session in the identity layer and reach
  publishers only through the `CredentialProvider` port — the compilation core receives a project, not
  a token (see the [compiler boundary](docs/02-architecture/adr/0012-identity-federation-boundary.md)).
- Secret scanning (`gitleaks`, `detect-private-key`) runs in pre-commit to keep credentials out of the
  repository.
