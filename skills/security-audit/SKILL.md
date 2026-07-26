---
name: security-audit
description: Perform an evidence-backed defensive security audit of a specific GitHub branch, commit, or branch diff using threat modeling and technology-appropriate checks. Use when the user asks for a security review, vulnerability audit, attack-surface analysis, secure-design assessment, dependency or supply-chain review, or security regression review of repository code or configuration.
---

# Audit a GitHub Branch for Security

Audit the requested repository state defensively. Produce a private-ready remediation report; never publish vulnerability details or create GitHub issues automatically.

Read [references/security-review-guide.md](references/security-review-guide.md) before beginning the audit.

## Establish scope

1. Identify the repository, target branch or commit, and optional base branch.
2. Resolve every reviewed ref to an immutable commit SHA.
3. Determine whether to review a diff, the full target snapshot, or both.
4. Read repository instructions, architecture documentation, manifests, lockfiles, tests, CI/CD configuration, deployment files, and security policy.
5. Record inaccessible components and external systems as coverage limitations.

Do not claim a whole system is secure from a source-only or branch-limited review.

## Build a threat model

Identify:

- Protected assets and sensitive data
- Actors, privilege levels, and administrative capabilities
- Entry points, parsers, APIs, files, messages, and external inputs
- Trust boundaries and data flows
- Security assumptions and attacker prerequisites
- Abuse cases relevant to the system

Prioritize reachable attack paths over checklist completeness.

## Trace security-sensitive behavior

1. Follow untrusted data from source to validation, authorization, storage, execution, and output.
2. Inspect authentication and authorization at every privilege boundary.
3. Inspect error paths, fallback behavior, race conditions, resource limits, and cleanup.
4. Check dependencies, build provenance, CI permissions, release workflows, and configuration defaults.
5. Run relevant security tests and analyzers when execution is available, authorized, and safe. Treat tool output as leads requiring source confirmation.
6. Inspect the full surrounding implementation. Never infer exploitability from a suspicious line alone.

Do not generate destructive proof-of-concept payloads, access real secrets, or test production systems unless the user separately provides explicit authorization and scope.

## Classify findings

Assign:

- Severity: `critical`, `high`, `medium`, `low`, or `informational`
- Confidence: `high`, `medium`, or `low`
- Status: `confirmed`, `probable`, `needs-validation`, or `not-a-finding`

Map to CWE or an applicable verification requirement when the mapping is defensible. Do not force a taxonomy match.

A confirmed or probable finding must include a reachable source-to-impact chain, required preconditions, concrete evidence, and a remediation strategy. Separate missing evidence from absence of vulnerability.

## Produce the report

Use this structure:

```markdown
# Security Audit

## Audit target
- Repository:
- Target branch or ref:
- Target commit:
- Base branch or ref:
- Base commit:
- Review mode:

## Scope and methodology
## System and threat model
## Attack surface
## Executive summary

## Findings

### SEC-001: <outcome-oriented title>
- Severity:
- Confidence:
- Status:
- CWE / control mapping:
- Location:
- Preconditions:
- Source-to-impact path:
- Evidence:
- Security impact:
- Remediation:
- Validation:

## Defense-in-depth improvements
## Positive security controls
## Coverage gaps and residual risk
```

Use stable sequential IDs. Distinguish exploitable defects from hardening opportunities. Include positive controls so later reviewers know which defenses were verified.

## Handle disclosure safely

- Do not pass security findings automatically to `@issue-filer`.
- Do not create a regular GitHub issue containing vulnerability details without the user's explicit decision about repository visibility and audience.
- Redact credentials, tokens, personal data, and unnecessary exploit details.
- For likely critical or high findings, lead with containment and private remediation guidance.

## Quality gate

Before responding, verify that:

- Findings are grounded in inspected code, configuration, or reproducible test evidence.
- Trust boundaries and attacker prerequisites are explicit.
- Severity reflects realistic impact and reachability.
- Suggested fixes address the root cause.
- Validation steps can demonstrate that the vulnerability is closed.
- The report states what was not reviewed.
