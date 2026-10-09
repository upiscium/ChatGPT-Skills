---
name: patch-plan
description: Convert selected filed GitHub Issues into dependency-aware OpenCode execution packets with explicit operation grants and stop points. Use to plan parallel implementation through the live repository Agent Core lifecycle or isolated generic worktrees, including prepublication delivery without assuming commit, push or PR authorization.
---

# Plan Review Patches

Turn selected filed Issues into self-contained OpenCode execution packets. `@blueprint` owns approved design and ACs; this skill owns how the selected Issue is executed. `@opencode-bridge` transports packets; it does not decide scope or grant operations.

Read [references/patch-plan-template.md](references/patch-plan-template.md) and `@repo-handoff`'s `references/execution-contract.md` before writing the plan. Copy resolved contract fields into the packet; an executor must not need these installed skills.

Read `@change-review`'s `references/verification.md` when specifying tests or completion evidence. Copy the applicable rules into the packet. See [references/superpowers-notice.md](references/superpowers-notice.md) for the adapted planning source.

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

Before emitting workstreams, restore any `codex-repo-state:v1` record on the selected Issue/PR with `@repo-handoff` and revalidate its base SHA. Include the chosen carrier, workflow ID, current state status, and the state-record update points in the plan. Automatically persist the planning snapshot and read it back before returning. If no carrier exists, return `bootstrap`; never invent a hidden tracking Issue. A missing marker on an existing carrier is bootstrapped automatically.

If the inputs contain `SEC-*` findings, vulnerability details, containment, credential rotation, or exploit-sensitive work, exclude those items and use `@security-plan`. Do not copy restricted security details into this plan.

## Define authority and stop point

Every packet must include workflow/workstream/run ID, approved instruction revision, immutable packet reference/digest, exact target/session role, operation allowlist and approval source. Use OpenCode only; never instruct it to launch standalone Codex CLI.

Include the OpenCode model requirement from `@opencode-bridge`'s `references/model-selection.md`: **GPT-6.1 Sol / high** unless the user overrides it. Carry the resolved provider/model ID and variant, or mark their target-specific resolution pending before dispatch. Require explicit selection of both settings and observed evidence; never let an omitted field inherit GPT-6 Sol / max. Copy this requirement into every independent and manual packet.

Choose the requested delivery scope, never a blanket default:
- Investigation only: bounded questions/evidence; no code or publication.
- Implementation and tests: deliver a frozen manifest/diff and evidence, stop before unapproved commit/push/Draft PR.
- Publication: only specifically authorized operations and reviewed snapshot, through repository guards; stop at the named Draft PR or earlier artifact.

Planning approval is not dispatch authority. Goal approval is not architecture/risk or publication permission. Unknown operations remain not-authorized. Ready/Merge stays user-executed outside the packet. Include the seven-field execution gate even for an allowed stream, and retain the exact unresolved human decisions.

Require run-correlated receipt and result formats. Arca coordinates and independently verifies; OpenCode implements; SwitchBoard owns Ask monitoring/notifications. Do not add monitoring loops to Arca or OpenCode or require a new monitoring service before otherwise authorized work. Connection configuration is separate from this generic skill.

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

### Make each unit executable without overprescribing

- Size tasks by independently verifiable outcomes and review boundaries, not a fixed number of minutes, lines or agent calls. Keep setup and documentation with the behavior they support.
- Identify each changed component's responsibility and the interfaces it consumes and produces. Pin names, types and values only when the approved contract or inspected code pins them. Preserve ordinary implementation latitude.
- Give each step an observable result. Verification steps name a verified command, expected result and evidence to retain. Avoid vague instructions such as “test thoroughly”; do not transcribe the complete implementation into the plan.
- Inspect the relevant baseline before attributing failures to the change. Preserve existing failures and environment blockers separately. An unrelated baseline failure need not block independent authorized work; a failure that prevents validating the changed behavior leaves that criterion unverified.
- For an unexplained bug, use `@debug-investigate` or include its bounded method in Phase 0: reproduce, trace the first incorrect boundary, compare a working case, test one discriminating hypothesis, and record the result before selecting a repair. Investigation does not grant host changes or instrumentation edits.
- Prefer a failing behavioral regression before a bug fix when practical. Record why it fails; a broken fixture or missing dependency is not the intended regression. Preserve existing work when adding tests later; never delete code to satisfy test-first ceremony.
- Require tests to detect named behavioral defects using independently derived expectations. Avoid assertions that merely pin editable budgets, warning margins, prose or implementation text. Test the behavior across the chosen boundary instead. Low-impact prose or value changes may need no new automated test.
- Choose focused checks plus required repository gates. Add broader integration checks for a concrete interaction risk; do not multiply full-suite runs or reviewers per small task without a reason.

Before handing off, check AC coverage, consistent interfaces across tasks, unresolved assumptions, failure cases and proportionality. Copy the necessary design constraints into every independent packet without turning each packet into a second design authority.

## Order the plan

Within each workstream, sequence work by dependency and risk:

1. Discovery or decisions that block design
2. Shared contracts, types, or migrations
3. Core implementation
4. Integrations and callers
5. Tests and documentation
6. Rollout, monitoring, cleanup, and rollback
7. Delivery at the authorized stop point: frozen prepublication evidence or separately authorized Draft PR

Run workstreams in the same wave concurrently. Start a later wave only after its prerequisite PRs are merged and its base SHA is refreshed.

Prefer one primary Issue or one inseparable Issue group per workstream and PR. Do not combine unrelated Issues to reduce PR count.

## Prepare Agent Core execution

In `agent-core` mode, produce one self-contained Main Orchestrator batch packet plus one Task record per workstream. Follow the live repository contract; when it exposes the current Templates lifecycle, require the coordinator to:

1. Initialize the Main session from the default-branch worktree and stop on any initialization failure.
2. From the default-branch worktree, create each explicitly selected new Issue's Task only through `just agent::task-start-from-issue <numeric-issue> <slug>`. Run the matching initial contract check and retain the complete `status: READY`, `mode: initial`, Task ID, worktree, and contract checksum evidence. Creating a Task does not authorize starting another Issue.
3. For an existing already-launched resumable Task, use only the repository's resume readiness path. Never recreate, rehydrate, reset, or replace it to manufacture readiness. Treat non-resumable or post-publication states through the Main-owned lifecycle instead of starting a replacement Task.
4. When at least two explicit Tasks are ready, run the repository's batch safety check, such as `just agent::batch-plan <task...>`. Treat its dependency, scope, coordination-surface, and external-resource conflicts as serialization constraints. Do not auto-discover additional Tasks.
5. Launch exactly one Task Orchestrator per parallel-safe Task, up to available concurrency, with that Task's complete readiness handoff. Do not launch generic implementation SubAgents in place of Task Orchestrators.
6. Keep each Task Orchestrator inside its assigned Task worktree. It may delegate its own bounded Work Units only according to the repository call graph, then stop at the packet's authorized boundary. Draft PR preparation/publication is not automatic.
7. Preserve partial progress: one blocked, failed, or decision-waiting Task does not cancel or rewrite independent Tasks. Continue only work that the batch plan still marks parallel-safe.
8. Leave merge, post-merge finalization, and cleanup with the Main/human authorities defined by the repository.

Do not also apply the generic worktree setup below in `agent-core` mode.

## Prepare generic SubAgent execution

In `generic-worktree` mode, produce a separate self-contained instruction packet for every parallel workstream that can be assigned to one Codex SubAgent without access to the other packets.

Require the implementation coordinator to:

1. Allocate at most one active SubAgent per workstream, bounded by available concurrency.
2. Before creating the first worktree, resolve the repository root with `git rev-parse --show-toplevel` and inspect the root `.gitignore`.
3. Require the exact anchored entry `/.worktrees/` in the committed root `.gitignore`. Verify it with `git check-ignore .worktrees/`. If absent, stop and propose a separately authorized minimal setup PR. Ready/Merge is user-executed; verify the merge, refresh the base SHA, and only then create worktrees.
4. Create every worktree inside `<repository-root>/.worktrees/<workstream-id>` from the refreshed verified base SHA. Do not use a sibling directory, `/tmp`, a workspace-global directory, or another external path.
5. Give each SubAgent a unique branch and its assigned repository-local worktree.
6. Prevent SubAgents from editing the coordinator's working tree or another workstream's branch.
7. Preserve workstream scope and report unexpected overlap before continuing.
8. Collect results, validation evidence, branch names, head SHAs, and PR URLs without merging branches locally.
9. Run authorized cross-workstream integration checks on pinned frozen results or PRs when a safe isolated combined test surface exists; do not require unauthorized PR publication just to test.

Use worktree commands equivalent to:

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
rg -xF '/.worktrees/' .gitignore
git show '<verified-base-sha>:.gitignore' | rg -xF '/.worktrees/'
git check-ignore .worktrees/
git worktree add ".worktrees/WS-001" -b '<unique-branch>' '<verified-base-sha>'
```

Do not let `mkdir`, `git worktree add`, or a SubAgent silently create worktrees before the ignore prerequisite passes.

If fewer SubAgent slots are available than parallel workstreams, queue the remaining workstreams within the same wave rather than combining their scope.

## Require scoped implementation delivery

Instruct the executor to:
1. Revalidate the grant and live repository gate before any mutation. With a stop/conditional gate, perform only the named admissible fallback.
2. Acquire the dedicated branch/worktree only through the selected backend. Preserve existing tasks and dirty work; do not recreate a Task to manufacture readiness.
3. Implement and validate only authorized scope. Report scope drift and human-owned choices instead of deciding them silently.
4. Deliver the exact frozen snapshot/manifest and test/environment evidence for independent `@change-review`. Do not create a commit just to obtain an immutable reference without commit authority.
5. Commit, push or create/prepare a Draft PR only when individually permitted and repository lifecycle gates are satisfied. A passed review is not publication permission.
6. If a PR is authorized and created, report real number, canonical URL, branch and head SHA, Issue/Task mapping, goal/AC coverage, non-goals, risk, validation and limitations. Never invent an identity.
7. If no publication was authorized, report `not-created; outside grant` and the reached prepublication stop. This is successful scoped delivery, not a missing-PR failure.
8. Return a run/revision/digest-bound executor report. The coordinator automatically records verified state through `@repo-handoff`; an executor may append only its own immutable report when authorized, never overwrite coordinator state. Preserve claims versus verified facts.
9. Stop at the exact granted boundary. Do not run Ready/Merge, release, cleanup, host reconfiguration or Ask monitoring.

For blocked publication, preserve permitted work and report exact blocker, branch/snapshot and next gate. A marker write failure is `pending-write`, not permission to change the carrier or claim durable recovery.

## Preserve boundaries

- Produce instructions only. This planning skill must not edit code, Issue/PR content, labels, branches, or commits; the resulting plan must assign implementation and PR creation to the later executor. The only permitted write is the automatic `codex-repo-state:v1` metadata marker on an existing carrier.
- In `agent-core` mode, never bypass Task lifecycle, worktree ownership, Task State, publication, integration, or cleanup guards with raw Git/GitHub commands or generic SubAgents.
- Do not silently expand scope beyond selected findings and issues.
- Do not make the external implementation packet or chat ledger the only continuation source; require the canonical Issue/PR state record or label the workstream `incomplete`.
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
- Delivery matches the operation grant and stop point; actual PR number/URL are required only when PR creation was authorized and completed.
- Parallel workstreams have no unresolved dependencies or likely shared write boundaries.
- Every workstream has isolated ownership and bounded scope, with one separate eventual PR when publication is authorized.
- Agent Core worktrees are created only by its guarded lifecycle; generic worktrees are under the repository root's `.worktrees/` directory and require the committed root `.gitignore` entry `/.worktrees/` before creation.
- Ordered work is divided into waves and later-wave base SHAs are refreshed after prerequisite merges.
- OpenCode can execute the resolved packet without the review conversation or Arca's installed skills, without launching a separate Codex CLI.
- The plan identifies the durable carrier and records how a later chat restores each workstream and its dependency wave.
- The latest planning state was automatically saved and read back, or is explicitly marked `bootstrap`/`pending-write` with the recovery consequence.
