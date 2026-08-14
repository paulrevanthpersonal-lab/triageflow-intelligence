# Security and Privacy Notes

## Implemented controls

- Pydantic validates field length, types, and batch size at the API boundary.
- SQLite writes use parameterized statements.
- Browser output is rendered from controlled application data; user fields are not injected into the UI as executable HTML.
- The container runs as an unprivileged user and exposes a health check.
- GitHub Actions uses read-only repository permissions.
- The dataset is synthetic and contains no credentials, customer records, or employee information.

## Required before production

- OIDC authentication, role-based authorization, and tenant isolation
- TLS termination, rate limiting, request-size limits, and security headers
- Secrets management and encrypted database/storage layers
- PII detection and redaction before model processing or persistence
- Audit retention, access review, incident response, and deletion procedures
- Dependency scanning, signed releases, container scanning, and threat modeling

Never paste passwords, access tokens, private keys, or unapproved personal information into this demonstration.
