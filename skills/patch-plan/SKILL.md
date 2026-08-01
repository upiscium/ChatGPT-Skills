---
name: patch-plan
description: Convert one or more selected GitHub Bug or Feature Request issues into self-contained, Codex-executable implementation workstreams with dependency-aware parallelization, repository-local .worktrees isolation, and follow-up pull requests. Use when the user wants to start the next issue-driven development cycle, exploit Codex SubAgents safely, plan concurrent work from @issue-filer results, or require every workstream to create and report its PR.
---

# Plan Review Patches

Turn selected Issues into an implementation plan that a new Codex instance can execute without the original review conversation.

Read [references/patch-plan-template.md](references/patch-plan-template.md) before writing the final plan.

## Establish the target

1. Identify the repository, selected Issue URLs or numbers, originating `F-*` findings when available, and the implementation base branch or commit.
2. Resolve the implementation base to an immutable commit SHA.
3. Read repository instructions and re-inspect affected code, callers, tests, configuration, contracts, and relevant issues.
4. Confirm each finding and issue still applies. Mark it `active`, `already-fixed`, `stale`, `duplicate`, `closed`, `blocked`, or `out-of-scope`.
5. Ask only for missing decisions that can materially change scope, architecture, compatibility, migration, or rollout.

Require filed Issues for an execution-ready plan. If the user supplies findings without Issues, produce only a draft and mark Issue creation as a blocker.

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

## Build the workstream graph

Map implementation units into workstreams before writing tasks.

For each pair of candidate workstreams, inspect:

- Direct Issue or architectural dependencies
- Expected files, modules, symbols, generated artifacts, and tests
- Shared APIs, schemas, migrations, configuration, lockfiles, and build files
- Ordering requirements and whether one workstream changes the assumptions of another
- Active branches or PRs touching the same boundaries

Classify the relationship as:

- `parallel`: No material dependency or likely conflicting write boundary
- `ordered`: One workstream must be merged before the other is replanned or implemented
- `combined`: Changes share one root cause or cannot be reviewed and validated independently
- `blocked`: A product decision or external dependency prevents scheduling

Assign stable workstream IDs such as `WS-001` and dependency waves starting at `Wave 1`.

Do not claim exact file-level independence when the files have not been verified. Put uncertain overlap into a discovery task or serialize it.

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

Within each workstream, sequence work by dependency and risk:

1. Discovery or decisions that block design
2. Shared contracts, types, or migrations
3. Core implementation
4. Integrations and callers
5. Tests and documentation
6. Rollout, monitoring, cleanup, and rollback
7. Delivery through a follow-up pull request

Run workstreams in the same wave concurrently. Start a later wave only after its prerequisite PRs are merged and its base SHA is refreshed.

Prefer one primary Issue or one inseparable Issue group per workstream and PR. Do not combine unrelated Issues to reduce PR count.

## Prepare SubAgent execution

For every parallel workstream, produce a separate self-contained instruction packet that can be assigned to one Codex SubAgent without access to the other packets.

Require the implementation coordinator to:

1. Allocate at most one active SubAgent per workstream, bounded by available concurrency.
2. Before creating the first worktree, resolve the repository root with `git rev-parse --show-toplevel` and inspect the root `.gitignore`.
3. Require the exact anchored entry `/.worktrees/`. Verify it with `git check-ignore .worktrees/`. If it is absent, stop normal implementation, add it through a minimal setup PR, merge that PR, refresh the common base SHA, and only then create worktrees.
4. Create every worktree inside `<repository-root>/.worktrees/<workstream-id>` from the refreshed verified base SHA. Do not use a sibling directory, `/tmp`, a workspace-global directory, or another external path.
5. Give each SubAgent a unique branch and its assigned repository-local worktree.
6. Prevent SubAgents from editing the coordinator's working tree or another workstream's branch.
7. Preserve workstream scope and report unexpected overlap before continuing.
8. Collect results, validation evidence, branch names, head SHAs, and PR URLs without merging branches locally.
9. Run cross-workstream integration checks after all PRs in a wave exist, when a safe combined test surface is available.

Use worktree commands equivalent to:

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
grep -qxF '/.worktrees/' .gitignore
git check-ignore .worktrees/
git worktree add ".worktrees/WS-001" -b '<unique-branch>' '<verified-base-sha>'
```

Do not let `mkdir`, `git worktree add`, or a SubAgent silently create worktrees before the ignore prerequisite passes.

If fewer SubAgent slots are available than parallel workstreams, queue the remaining workstreams within the same wave rather than combining their scope.

## Require implementation delivery

Make the generated plan instruct each workstream executor to:

1. Create a dedicated implementation branch from the verified base commit, named according to repository conventions and clearly associated with the primary Issue.
2. Implement only the selected plan scope and run the required validation.
3. Commit the completed changes and push the implementation branch.
4. Create a follow-up GitHub pull request against the planned target branch.
5. Link every addressed Issue and the originating repository review or merged PR when available. Use closing keywords only when the PR fully satisfies the Issue and repository conventions support them.
6. Include a concise change summary, validation evidence, compatibility or migration notes, known limitations, and rollback guidance in the PR body.
7. Return the workstream ID, created PR number, canonical URL, head branch, and head SHA. Treat any missing identity as incomplete delivery.

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
- Parallel workstreams have no unresolved dependencies or likely shared write boundaries.
- Every workstream has an isolated branch or worktree, bounded scope, and separate PR.
- Every worktree path is under the repository root's `.worktrees/` directory, and the committed root `.gitignore` contains `/.worktrees/` before worktrees are created.
- Ordered work is divided into waves and later-wave base SHAs are refreshed after prerequisite merges.
- Another Codex instance can execute the plan without the review conversation.
