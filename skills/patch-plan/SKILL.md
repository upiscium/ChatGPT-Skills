---
name: patch-plan
description: Convert evidence-backed pull-request review findings and their GitHub Bug or Feature Request issues into a self-contained, Codex-executable implementation and delivery plan. Use when the user wants the next implementation instructions, patch plan, work breakdown, or technical execution plan after @branch-review, @issue-filer, or a comparable structured PR review and issue set, including a required follow-up PR with its number and URL reported.
---

# Plan Review Patches

Turn selected review findings and their issue outcomes into an implementation plan that a new Codex instance can execute without the original conversation.

Read [references/patch-plan-template.md](references/patch-plan-template.md) before writing the final plan.

## Establish the target

1. Identify the repository, source review PR number and URL, implementation base branch or commit, selected `F-*` findings, and corresponding issue URLs or numbers.
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
7. Delivery through a follow-up pull request

Keep independent implementation units separable so Codex can implement and validate them incrementally. Define safe commit boundaries and a single coherent follow-up PR unless the work cannot be reviewed or deployed safely as one PR.

## Require implementation delivery

Make the generated plan instruct the implementation executor to:

1. Create a dedicated implementation branch from the verified base commit.
2. Implement only the selected plan scope and run the required validation.
3. Commit the completed changes and push the implementation branch.
4. Create a follow-up GitHub pull request against the planned target branch.
5. Link the source review PR and every addressed issue in the PR body without claiming automatic closure unless repository conventions support it.
6. Include a concise change summary, validation evidence, compatibility or migration notes, known limitations, and rollback guidance in the PR body.
7. Return the created PR number and canonical URL in the final implementation report. Treat missing PR number or URL as incomplete delivery.

If PR creation is blocked by permissions, authentication, branch protection, or repository policy, require the executor to stop after preserving pushed work when safe and report the exact blocker, branch name, and next action. Never invent a PR number.

## Preserve boundaries

- Produce instructions only. This planning skill must not edit code, issues, labels, pull requests, branches, or commits; the resulting plan must assign implementation and PR creation to the later executor.
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
- The plan requires a follow-up PR and a final report containing its real number and canonical URL.
- Another Codex instance can execute the plan without the review conversation.
