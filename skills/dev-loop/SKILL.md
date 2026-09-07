---
name: dev-loop
description: Coordinate an intent-driven, checkpoint-based GitHub development loop with human-owned decisions, repository-aware Agent Core or generic execution, parallel Issue workstreams, concurrent isolated PR reviews, and user-owned Draft-to-Ready-to-Merge actions. Use to start, continue, resume, track, or advance one or more issue-driven workstreams while waiting for `next` at each verified checkpoint.
---

# Run the Development Loop

Coordinate the existing development skills as a checkpointed state machine. Advance only through validated artifacts. Do not implement product code in this skill, do not mark PRs ready, do not merge PRs, and do not display merge command blocks unless the user explicitly invokes `@pr-merge` separately.

## Authority model

Keep project authority with the human and use AI for bounded verification and execution planning.

- Human authority: product direction, approved intent, architecture, scope, public API policy, compatibility, migration, destructive behavior, security-boundary choices, material trade-offs, risk acceptance, and merge action.
- Skill authority: reconstruct explicit contracts, inspect relevant code and GitHub state, model failure modes, assess tests/CI, review implementation and scope, prepare Codex instructions, and compress evidence into a decision interface.
- Never let implementation + tests + review silently redefine an ambiguous requirement. Escalate material ambiguity instead.

## Checkpoint mode

Complete at most one substantive stage per response, present its artifact, record the exact next gate, then stop.

- `next`, `continue`, or equivalent authorizes only the single next action named in the previous ledger.
- Before acting on `next`, re-read live GitHub state and verify repository, Issue, PR, branch, base SHA, and head SHA.
- The previous ledger is routing context, not authority.
- If live state changed or the previous checkpoint became ambiguous, report the new state and stop before write-producing or externally delegated work.
- Never run continuously until no Issues remain.

## Resolve live context

Track at least:

- repository and default/integration branch;
- execution backend: `agent-core` or `generic-worktree`;
- immutable reviewed/implementation base SHA;
- authoritative goal, `AC-*` criteria, non-goals, compatibility/invariants, risk tier, and contract provenance;
- unresolved human `D-*` decisions;
- workstream IDs, dependency waves, overlap/conflict classification;
- Task IDs/worktrees/lifecycle state for Agent Core repositories;
- implementation branches and head SHAs;
- PR numbers/URLs/base/head;
- `@branch-review` verdict and base sensitivity;
- verified merge commit SHA after the user merges.

Always reconstruct these from live repository/GitHub state when resuming.

## State machine

### 1. `merged-review`

Run `@repo-review` on the integrated branch or a specified merged commit.

Require commit-pinned, intent-first review. Findings must trace to authoritative objectives/contracts. Keep human `D-*` decisions separate from actionable `F-*` findings.

Transition: selected actionable findings.

### 2. `issue-filing`

Use `@issue-filer` only after explicit authorization for the displayed findings.

Approval to file a finding approves the stated goal/acceptance criteria only. It does not approve unstated architecture, compatibility, migration, security, destructive, or risk choices.

Transition: canonical Issue numbers/URLs.

### 3. `planning`

Use `@patch-plan`.

Require a `Workstream Contract` for each runnable unit:

- authoritative goal/source;
- stable `AC-*` criteria;
- invariants and compatibility requirements;
- explicit non-goals;
- risk tier: low/medium/high;
- provenance: human-authored, human-approved, or derived-unconfirmed;
- delegated design latitude;
- unresolved human decisions.

Stop for human direction when planning requires architecture, public API, migration, security boundary, destructive behavior, non-trivial compatibility, material scope, or risk-acceptance decisions.

#### Agent Core backend

When the repository exposes a guarded Agent Core lifecycle:

- use repository-owned lifecycle APIs as the sole authority for Task creation, worktree allocation, Task State, commit/publication, integration, and cleanup;
- map each workstream to exactly one authoritative numeric Issue-backed Task;
- use one Task, one lifecycle-owned worktree, one Task Orchestrator, and one PR per workstream;
- run the repository batch-safety API before parallel Task launch;
- use resume readiness for existing resumable Tasks;
- never substitute raw `git worktree`, direct Task State edits, generic SubAgent writes, or raw publication commands.

#### Generic worktree backend

Only when no repository-owned lifecycle applies:

- use repository-local `<repo>/.worktrees/<workstream-id>`;
- verify the committed root `.gitignore` contains `/.worktrees/` before creating worktrees;
- if missing, create a prerequisite setup workstream/PR first;
- never use sibling, temporary, or workspace-global managed worktrees;
- one writable branch/worktree per implementation agent.

Produce self-contained Codex implementation instructions per workstream. Stop and wait for external implementation.

### 4. `implementation`

`@dev-loop` does not implement code.

On `next`, inspect live GitHub state for the expected PRs and map them back to their workstreams/contracts.

For each workstream verify:

- linked Issue/Task;
- expected base;
- branch and exact head SHA;
- goal and `AC-*` coverage;
- lifecycle identity/status in Agent Core mode;
- real PR number and canonical URL.

Track workstreams independently as `queued`, `running`, `pr-open`, `blocked`, or `failed`. Preserve completed PRs when siblings are blocked or incomplete.

### 5. `pr-review`

Run one isolated `@branch-review` per exact PR head. Independent reviews may run concurrently.

Required review order:

`Intent → Acceptance Contract → Failure Model → Test Evidence → Implementation → Scope`

For a parallel wave, pin a `Review Batch Manifest` containing shared base SHA, PR/head per workstream, sibling heads, declared dependencies, overlap expectations, and merge constraints.

After per-PR reviews, perform a coordinator-level cross-PR interference check. A collection of isolated `ready` verdicts is not automatically joint merge safety.

Outcomes:

- `changes-required`: emit a self-contained Codex correction packet for that exact PR/head and stop;
- `blocked`: present the exact human decision/dependency, options/trade-offs, evidence, and safe fallback;
- `ready`: present a concise merge decision interface pinned to the reviewed head.

Risk-based human review:

- low: summary-only unless ambiguity exists;
- medium: focused review of named contracts/files/trade-offs;
- high: explicit human confirmation of named architecture/API/migration/security/compatibility/destructive/risk points before merge readiness.

Re-review only PRs whose head changed or whose base-sensitive assumptions were invalidated by sibling merges.

### 6. `human-merge-wait`

This stage replaces automatic merge-command handoff.

When a PR is `ready`:

- do not invoke `@pr-merge` automatically;
- do not print `gh pr ready`, `gh pr merge`, merge scripts, or equivalent Draft-to-Ready-to-Merge commands;
- do not execute any Ready/Merge write;
- present only the exact PR URL/number, reviewed head SHA, expected base, review result, checks/evidence state, required merge order, and any remaining human gate;
- state that the user owns Draft → Ready → Merge in their normal workflow;
- stop.

If the user explicitly asks for merge commands or explicitly invokes `@pr-merge`, that separate skill may generate them. This is opt-in and is not part of the normal `@dev-loop` path.

On the following `next`:

1. fresh-read the PR and target branch;
2. verify the expected PR actually merged (or entered a required merge queue);
3. verify the merged head/base relationship and record the resulting merge commit SHA;
4. re-check remaining PR mergeability, dependencies, and base-sensitive review assumptions;
5. request fresh review only for affected PRs.

If the PR is still open, report that state and remain in `human-merge-wait`; do not re-display merge commands.

Transition: verified merged PR URL and target-branch commit SHA.

### 7. `integrated-review`

After the relevant wave is merged, run `@repo-review` on the resulting merged commit or requested merge window.

Verify integrated behavior against the same objectives/acceptance contracts, including cross-PR effects that isolated reviews could miss.

This begins the next cycle but does not automatically authorize Issue creation.

## Parallelism and scope control

- Prefer one primary Issue (or inseparable Issue group) per workstream/PR.
- Preserve the same Workstream Contract and `AC-*` IDs through planning, implementation, correction, PR review, and integrated review.
- Run independent workstreams in the same wave concurrently when the repository's safety gate permits it.
- Classify pairwise relationships as `parallel`, `ordered`, `combined`, or `blocked`.
- Serialize shared schemas, migrations, public contracts, generated artifacts, lockfiles, or likely overlapping files unless safe ownership boundaries are demonstrated.
- Do not start dependent work until the prerequisite merge is present on the chosen base.
- Preserve partial progress; one blocked Task/PR must not erase independent completed work.

## Worktree/session safety

Before any external Codex instruction that assumes a specific checkout, require verification of:

- `pwd` / repository root;
- current branch;
- exact HEAD;
- `git worktree list`;
- expected Task/workstream identity.

If the active Codex sandbox is pinned to a stale or different worktree, stop. Do not edit a sibling worktree indirectly and do not create a replacement worktree merely to escape sandbox authority. Resume in a fresh session rooted at the already prepared canonical worktree.

## Handover threshold

Long development/review sessions must not be driven into context exhaustion.

When conversation history is becoming dense enough that exact SHAs, Task identities, review evidence, or the next `next` action may be lost or conflated:

- stop at the nearest safe checkpoint before starting another substantial stage;
- tell the user that `@handover` + New Chat is safer;
- produce/retain a precise loop ledger so the handover can preserve the next action;
- prefer warning early enough to create a complete handover, not after the next `next` fails from context loss.

Do not hand over in the middle of a write-producing lifecycle transition when the current chat can safely finish and record the terminal evidence first.

## Loop ledger

Every response should preserve a concise ledger:

```markdown
# Development Loop
- Repository:
- Stage:
- Base or merged commit:
- Execution backend/version:
- Active wave:
- Contract authority:
- Risk tier:
- Human decisions required:
- Next gate:
- Next action on `next`:
- Authorization needed:
- Gate status: stop | conditional | allowed
- Evidence snapshot:
- Reverify before action:

| Workstream | Issues | Task | Contract | Risk | Depends on | Status | Branch | PR | Head SHA | Review | Base sensitivity | Merge SHA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Use canonical URLs and immutable SHAs. Mark absent artifacts `not-created`; do not infer them.

## Safety boundaries

- Review-only stages do not authorize Issue creation, code changes, PR writes, Ready, or Merge.
- `next` never authorizes Ready/Merge writes.
- Implementation belongs to the external Codex run instructed by this skill.
- In Agent Core repositories, implementation must enter through Main and the guarded Task lifecycle.
- A SubAgent owns only its assigned workstream.
- PR correction findings stay in that PR; broader issues wait for post-merge `@repo-review`.
- Route `SEC-*` findings through `@security-audit` / `@security-plan`.
- Never bypass CI, approvals, branch protection, repository policy, or release gates.
- Do not mark Issues complete merely because a PR exists.

## Quality gate

Before reporting a transition, verify:

- live artifacts, not conversation assumptions, determine the current stage;
- repository/backend contracts are re-read when versions change;
- Agent Core and generic-worktree commands are never mixed;
- every workstream has authoritative intent, stable acceptance criteria, non-goals, provenance, risk, and delegated design latitude;
- tests are evidence against the contract, not the source of requirements;
- reviews are pinned to immutable head SHAs and follow the required review order;
- concurrent review results include a cross-PR interference pass;
- generic worktrees are repository-local and `/.worktrees/` is ignored;
- Agent Core worktrees remain lifecycle-owned;
- human-owned decisions are explicitly escalated;
- normal `@dev-loop` never emits Draft/Ready/Merge commands;
- after user merge, `next` performs fresh merge/base verification before advancing;
- long-session handover is proposed before context quality becomes unsafe;
- no response advances more than one substantive stage.
