---
name: patch-plan
description: Convert evidence-backed branch-review findings and their GitHub Bug or Feature Request issues into a self-contained, Codex-executable implementation plan without changing code or issues. Use when the user wants the next implementation instructions, patch plan, work breakdown, or technical execution plan after @branch-review, @issue-filer, or a comparable structured review and issue set.
---

# Plan Review Patches

Turn selected review findings and their issue outcomes into an implementation plan that a new Codex instance can execute without the original conversation.

Read [references/patch-plan-template.md](references/patch-plan-template.md) before writing the final plan.

## Establish the target

1. Identify the repository, implementation base branch or commit, selected `F-*` findings, and corresponding issue URLs or numbers.
2. Resolve the implementation base to an immutable commit SHA.
3. Read repository instructions and re-inspect affected code, callers, tests, configuration, contracts, and relevant issues.
4. Confirm each finding and issue still applies. Mark it `active`, `already-fixed`, `stale`, `duplicate`, `closed`, `blocked`, or `out-of-scope`.
5. Ask only for missing decisions that can materially change scope, architecture, compatibility, migration, or rollout.

Accept a structured review without created issues when the user explicitly wants a draft plan. Record the issue as `not-filed`; never create it.

If the inputs contain `SEC-*` findings, vulnerability details, containment, credential rotation, or exploit-sensitive work, exclude those items and use `@security-plan`. Do not copy restricted security details into this plan.

## Form implementation units

Group active work by root cause, change boundary, and dependency rather than making one task per issue.

- Combine findings repaired by one invariant or shared component.
- Separate unrelated bugs and capabilities even when they share an issue.
- Separate product decisions from implementation work.
- Preserve every source finding ID and issue link.
- Assign stable implementation IDs such as `IMP-001`.
- Distinguish required work from optional follow-ups.

For feature requests, verify the user outcome, proposed scope, non-goals, and compatibility expectations. For bugs, verify the incorrect behavior, expected behavior, triggering path, and regression boundary.

## Design executable work

For each implementation unit:

1. State the intended behavior or invariant.
2. Identify the narrowest complete change that addresses the root cause.
3. Specify files, modules, symbols, APIs, configuration, and commands only when verified against the implementation base.
4. Describe data, schema, API, compatibility, migration, deployment, and documentation effects when applicable.
5. Define tests that fail before the change and pass after it when practical.
6. Define observable completion criteria and trace them to source acceptance criteria.
7. Record dependencies, blockers, risks, and explicit non-goals.

When evidence is insufficient for exact instructions, add a bounded Phase 0 discovery task with a decision output. Do not invent paths, APIs, commands, or architecture.

## Order the plan

Sequence work by dependency and risk:

1. Discovery or decisions that block design
2. Shared contracts, types, or migrations
3. Core implementation
4. Integrations and callers
5. Tests and documentation
6. Rollout, monitoring, cleanup, and rollback

Keep independent implementation units separable so Codex can implement and validate them incrementally. Call out safe commit or PR boundaries when useful, without creating them.

## Preserve boundaries

- Produce instructions only. Do not edit code, issues, labels, pull requests, branches, or commits.
- Do not silently expand scope beyond selected findings and issues.
- Do not treat an issue's suggested solution as verified architecture.
- Do not reopen, close, comment on, or modify stale or duplicate issues.
- Do not include credentials, private logs, personal data, or restricted security details.

## Quality gate

Before responding, verify that:

- Every implementation task traces to an active finding, issue, dependency, or acceptance criterion.
- Target repository, branch, and immutable commit SHA are recorded.
- Root causes and dependencies determine the work breakdown.
- Exact technical details are verified or clearly marked as discovery.
- Bugs and feature requests retain their distinct behavioral contracts.
- Tests cover success, failure, regression, and integration behavior where applicable.
- Compatibility, migration, rollout, observability, rollback, and documentation are addressed or explicitly unnecessary.
- The plan states what Codex must not change.
- Another Codex instance can execute the plan without the review conversation.
