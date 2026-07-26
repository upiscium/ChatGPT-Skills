# Security Review Guide

Use this guide to route the audit. Apply only sections relevant to the repository.

## Baseline method

1. Decompose the application, data flows, actors, assets, and trust boundaries.
2. Identify and rank threats and abuse cases.
3. Trace implemented mitigations and missing controls.
4. Validate findings and residual risk.

Use current official guidance when available:

- OWASP Threat Modeling Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- MITRE CWE: https://cwe.mitre.org/
- NIST Secure Software Development Framework: https://csrc.nist.gov/projects/ssdf

Standards guide coverage; they do not replace reachability analysis.

## Universal review areas

- Authentication, session handling, authorization, tenancy, and privilege changes
- Input validation, output encoding, injection, unsafe parsing, and deserialization
- Secret storage, key handling, cryptography, randomness, and certificate validation
- Filesystem paths, uploads, archives, temporary files, and permission boundaries
- Network requests, redirects, SSRF, DNS assumptions, TLS, and proxy trust
- Logging, error disclosure, audit trails, privacy, and sensitive-data retention
- Resource exhaustion, unbounded work, denial of service, retries, and rate limits
- Concurrency, race conditions, state transitions, rollback, and cleanup
- Dependency provenance, lockfiles, update policy, artifact integrity, and licensing risk
- CI/CD tokens, workflow permissions, untrusted pull requests, build scripts, and releases
- Secure defaults, debug modes, deployment configuration, and environment separation

## Native and systems software

- Memory lifetime, ownership, bounds, integer conversion, and undefined behavior
- Unsafe FFI boundaries, allocator assumptions, and error propagation
- Privilege separation, syscalls, device access, IPC, and sandbox boundaries
- Binary and data-format parsing, malformed inputs, and partial reads or writes

## Web services and applications

- Route-level authorization, object-level access, CSRF, CORS, cookies, and cache behavior
- Query construction, template rendering, browser sinks, and content-type handling
- Webhooks, replay protection, idempotency, request signing, and multi-tenant isolation

## Infrastructure and containers

- Container privileges, capabilities, host mounts, device access, and image pinning
- Kubernetes RBAC, service accounts, admission policy, secrets, and network policy
- IaC state, public exposure, firewall rules, identity policy, and encryption settings
- Backup, restore, disaster recovery, credential rotation, and observability access

## AI and agent systems

- Prompt injection, tool authorization, data exfiltration, and cross-user context leakage
- Untrusted model output crossing into commands, code, queries, or external actions
- Model and dataset provenance, artifact integrity, unsafe deserialization, and evaluation gaps
- Human approval boundaries, least privilege, rate and cost controls, and auditability

## Evidence rules

- Treat scanner alerts, vulnerable-version matches, and secret-pattern matches as leads.
- Confirm that the affected component is reachable and the unsafe behavior is not mitigated.
- Cite exact paths and symbols. Use line references only when stable for the reviewed commit.
- State when runtime configuration or deployment context is required to determine impact.
- Never copy an active credential into the report; identify its location and redact its value.
