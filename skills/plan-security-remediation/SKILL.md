---
name: plan-security-remediation
description: Convert selected findings from a security audit into a private-ready, Codex-executable remediation and patch implementation plan without modifying code or publishing vulnerability details. Use when the user asks how to fix SEC findings, prepare a security patch, plan vulnerability remediation, sequence containment and permanent fixes, or write implementation instructions from an audit report.
---

# Plan Security Remediation

Turn verified security findings into a safe, testable patch plan. Preserve confidentiality and separate immediate containment from durable remediation.

Read [references/security-remediation-plan-template.md](references/security-remediation-plan-template.md) before producing the final plan.

## Resolve inputs

1. Require the repository, patch base branch or commit, and the selected security findings.
2. Prefer the structured `SEC-*` report produced by `$audit-github-branch-security`.
3. Resolve the patch base to an immutable commit SHA.
4. Re-read affected code, callers, tests, configuration, deployment files, and repository instructions.
5. Confirm that each finding still applies to the patch base. Mark stale, fixed, or unverified findings instead of planning against outdated evidence.

If a critical fact is missing, ask only the questions that can change the remediation architecture, compatibility, containment, or rollout.

## Normalize remediation units

Group findings by root cause and change boundary:

- Combine multiple symptoms fixed by one invariant or shared component.
- Separate independent privilege boundaries, migrations, credential rotations, or deployment changes.
- Preserve every source finding ID in the resulting remediation unit.

Assign stable remediation IDs such as `REM-001`.

## Design the response

For each remediation unit:

1. State the violated security invariant and desired invariant.
2. Identify the narrowest complete fix. Avoid symptom-only checks and deny lists when a structural boundary can remove the class of vulnerability.
3. Identify compatibility, data migration, API, deployment, and operational consequences.
4. Define safe regression tests that demonstrate the vulnerable path is closed without exposing destructive payloads or real secrets.
5. Add defense-in-depth work separately from the root-cause patch.
6. Define runtime signals that would detect failed rollout, exploitation attempts, or authorization regressions.

Do not prescribe exact paths, symbols, APIs, or commands unless they were verified in the repository. Mark unavoidable assumptions.

## Separate remediation horizons

Use only the horizons that apply:

- `Immediate containment`: Reversible configuration, access, key, feature, or deployment action to reduce exposure before a patch.
- `Permanent patch`: Code and configuration changes that restore the security invariant.
- `Recovery and rotation`: Credential rotation, session invalidation, data repair, artifact rebuild, or incident follow-up.
- `Defense in depth`: Additional controls that reduce recurrence or blast radius but do not replace the root fix.

For critical or high findings, place containment before ordinary implementation work. State operational risk when containment may cause downtime or data loss; do not perform it.

## Build a Codex-executable plan

Order tasks by dependency. Include:

- Files, modules, symbols, and configuration to inspect or change
- Intended behavior and invariants
- Explicit non-goals and components Codex must not modify
- Schema, API, deployment, or compatibility changes
- Unit, integration, negative, abuse-case, and end-to-end tests
- Validation commands when verified
- Rollout, monitoring, rollback, and cleanup
- Per-task and per-phase completion criteria

Start with a regression test when it can safely encode the failure. Do not require weaponized exploit code as a test fixture.

## Preserve disclosure boundaries

- Produce the plan only in the current authorized context or requested private artifact.
- Redact credentials, personal data, private keys, tokens, and unnecessary exploit details.
- Do not create issues, pull requests, patches, commits, advisories, or external messages.
- Do not pass the plan to `$file-github-review-issues`.
- Distinguish details safe for a normal engineering ticket from restricted remediation details.

## Output

Use `references/security-remediation-plan-template.md`. Omit irrelevant sections, but always include target SHAs, source finding IDs, assumptions, implementation phases, tests, rollout, rollback, and definition of done.

## Quality gate

Before responding, verify that:

- Every task traces to a selected finding, security invariant, or rollout risk.
- The plan fixes root causes rather than only visible symptoms.
- Immediate containment does not masquerade as the permanent fix.
- Tests cover authorized and unauthorized behavior.
- Failure modes default safely where appropriate.
- Compatibility, migration, recovery, and observability are addressed.
- Another Codex instance can execute the plan without the audit conversation.
- Sensitive details are minimized and clearly classified.
