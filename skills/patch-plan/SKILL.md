---
name: patch-plan
description: Convert selected GitHub Bug or Feature Request Issues into self-contained, dependency-aware parallel implementation workstreams using the repository's guarded Agent Core lifecycle when available or isolated generic worktrees otherwise, with one traceable follow-up PR per workstream. Use to plan an issue-driven development cycle or concurrent Codex execution.
---

# Plan Review Patches

Turn selected Issues into an implementation plan that a new Codex instance can execute without the original review conversation.

Read [references/patch-plan-template.md](references/patch-plan-template.md) before writing the final plan.

## Select the execution backend

Inspect repository instructions before prescribing branches, worktrees, agents, or publication commands.

- Use `agent-core` mode when the repository declares a guarded Task lifecycle, Task State, Main/Task Orchestrator boundaries, or stable repository-local lifecycle APIs such as `agent::task-start-from-issue`.
- Use `generic-worktree` mode only when no repository-owned orchestration lifecycle applies.
- Record the selected mode and the exact repository evidence or Agent Core version that selected it.
- In `agent-core` mode, repository instructions and guarded lifecycle APIs own Task creation, worktrees, commits, publication, integration, and cleanup. Do not emit raw Git or GitHub mutations as substitutes.
- Never assume that one Templates release has the same commands as another. Re-read the installed repository contract and use only its advertised stable APIs.

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

In `agent-core` mode, map every runnable workstream to exactly one authoritative numeric GitHub Issue-backed Task. The Issue must contain the complete Task intent and acceptance contract required by the repository; an external implementation packet may clarify execution but must not become a second authority. If inseparable Issues lack one canonical Issue that defines their combined scope, block execution until the Issue contract is consolidated or serialize them instead of inventing a multi-Issue Task.

For feature requests, verify the user outcome, proposed scope, non-goals, and compatibility expectations. For bugs, verify the incorrect behavior, expected behavior, triggering path, and regression boundary.

## Build the workstream graph

Map implementation units into workstreams before writing tasks.

For each pair of candidate workstreams, inspect:

- Direct Issue or architectural dependencies
- Expected files, modules, symbols, generated artifacts, and tests
- Shared APIs, schemas, migrations, configuration, lockfiles, and build files
- Ordering requirements and whether one workstream changes the assumptions of another
- Active branches or PRs touching the same boundaries
- In `agent-core` mode, declared Task dependencies, scopes, coordination surfaces, and external resources

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

## Prepare Agent Core execution

In `agent-core` mode, produce one self-contained Main Orchestrator batch packet plus one Task record per workstream. Follow the live repository contract; when it exposes the current Templates lifecycle, require the coordinator to:

1. Initialize the Main session from the default-branch worktree and stop on any initialization failure.
2. From the default-branch worktree, create each explicitly selected new Issue's Task only through `just agent::task-start-from-issue <numeric-issue> <slug>`. Run the matching initial contract check and retain the complete `status: READY`, `mode: initial`, Task ID, worktree, and contract checksum evidence. Creating a Task does not authorize starting another Issue.
3. For an existing already-launched resumable Task, use only the repository's resume readiness path. Never recreate, rehydrate, reset, or replace it to manufacture readiness. Treat non-resumable or post-publication states through the Main-owned lifecycle instead of starting a replacement Task.
4. When at least two explicit Tasks are ready, run the repository's batch safety check, such as `just agent::batch-plan <task...>`. Treat its dependency, scope, coordination-surface, and external-resource conflicts as serialization constraints. Do not auto-discover additional Tasks.
5. Launch exactly one Task Orchestrator per parallel-safe Task, up to available concurrency, with that Task's complete readiness handoff. Do not launch generic implementation SubAgents in place of Task Orchestrators.
6. Keep each Task Orchestrator inside its assigned Task worktree. It may delegate its own bounded Work Units only according to the repository call graph and must prepare exactly its own Draft PR.
7. Preserve partial progress: one blocked, failed, or decision-waiting Task does not cancel or rewrite independent Tasks. Continue only work that the batch plan still marks parallel-safe.
8. Leave merge, post-merge finalization, and cleanup with the Main/human authorities defined by the repository.

Do not also apply the generic worktree setup below in `agent-core` mode.

## Prepare generic SubAgent execution

In `generic-worktree` mode, produce a separate self-contained instruction packet for every parallel workstream that can be assigned to one Codex SubAgent without access to the other packets.

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

0. Read the workstream execution contract before changing code. If its status is `stop` or `conditional`, perform only the admissible fallback until the named authority clears the prerequisite; never reinterpret the constraint from surrounding prose.

1. Acquire its dedicated branch and worktree through the selected execution backend. In `agent-core` mode, use the Task already created by the guarded lifecycle; in `generic-worktree` mode, create them from the verified base according to repository conventions.
2. Implement only the selected plan scope and run the required validation.
3. Commit and push only through repository-owned guarded APIs when `agent-core` mode applies; otherwise use the permitted generic workflow.
4. Create or prepare a follow-up Draft PR through the selected backend against the planned target branch.
5. Link every addressed Issue and the originating repository review or merged PR when available. Use closing keywords only when the PR fully satisfies the Issue and repository conventions support them.
6. Include a concise change summary, validation evidence, compatibility or migration notes, known limitations, and rollback guidance in the PR body.
7. Return the workstream ID, Agent Core Task ID and lifecycle status when applicable, created PR number, canonical URL, head branch, and head SHA. Treat any missing required identity as incomplete delivery.

If PR creation is blocked by permissions, authentication, branch protection, or repository policy, require the executor to stop after preserving pushed work when safe and report the exact blocker, branch name, and next action. Never invent a PR number.

## Preserve boundaries

- Produce instructions only. This planning skill must not edit code, issues, labels, pull requests, branches, or commits; the resulting plan must assign implementation and PR creation to the later executor.
- In `agent-core` mode, never bypass Task lifecycle, worktree ownership, Task State, publication, integration, or cleanup guards with raw Git/GitHub commands or generic SubAgents.
- Do not silently expand scope beyond selected findings and issues.
- Do not treat an issue's suggested solution as verified architecture.
- Do not reopen, close, comment on, or modify stale or duplicate issues.
- Do not include credentials, private logs, personal data, or restricted security details.

## Quality gate

Before responding, verify that:

- Every implementation task traces to an active finding, issue, dependency, or acceptance criterion.
- The selected execution backend is evidence-backed, and only one backend's worktree and publication procedure is emitted.
- Every Agent Core workstream maps to one authoritative Issue-backed Task with complete readiness evidence; multi-Task execution uses the repository batch safety result before concurrent launch.
- Every constrained workstream carries a complete execution contract and requires live revalidation before code, PR, or merge actions that depend on it.
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
- Agent Core worktrees are created only by its guarded lifecycle; generic worktrees are under the repository root's `.worktrees/` directory and require the committed root `.gitignore` entry `/.worktrees/` before creation.
- Ordered work is divided into waves and later-wave base SHAs are refreshed after prerequisite merges.
- Another Codex instance can execute the plan without the review conversation.
