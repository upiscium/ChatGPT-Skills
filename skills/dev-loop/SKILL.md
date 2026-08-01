---
name: dev-loop
description: Coordinate a checkpoint-based, issue-driven GitHub development loop with dependency-aware parallel Codex SubAgent workstreams across @repo-review, @issue-filer, @patch-plan, external implementation, @branch-review, and manual @pr-merge command handoffs. Use when the user asks to start, continue, resume, track, or advance multiple independent Issues concurrently while waiting for `next` at each verified checkpoint.
---

# Run the Development Loop

Coordinate the existing skills as a checkpointed state machine. Advance only through validated artifacts; do not implement the plan inside this skill.

## Use checkpoint mode

Complete at most one substantive stage per response, present its artifact and the exact next action, then stop.

- Treat `next`, `continue`, or an equivalent reply as authorization for only the single next action named in the previous loop ledger. It never authorizes Codex to execute ready or merge writes.
- Before acting on `next`, re-read live GitHub state and verify that repository, Issue, PR, branch, and SHAs still match the announced action.
- If the target changed or the previous checkpoint is ambiguous, do not act; show the updated state and request confirmation.
- Never interpret `next` as permission for an unannounced action, a different PR, or multiple loop iterations.
- Never run continuously until no Issues remain.

## Resolve loop context

Identify:

- Repository and default or integration branch
- Current immutable base or merged commit SHA
- Active review report and `F-*` findings
- Selected Issue numbers and URLs
- Workstream IDs, dependency waves, and conflict classifications
- Per-workstream implementation plans
- Per-workstream branches and head SHAs
- Per-workstream PR numbers, URLs, bases, and head SHAs
- Per-workstream `@branch-review` decisions
- Per-workstream merge commit SHAs

Read current GitHub state instead of trusting stale conversation text. When resuming, locate the latest valid artifact and continue from the first incomplete stage.

## Use the state machine

### 1. `merged-review`

Use `@repo-review` on the integrated branch or merged commit. Require a commit-pinned repository review before proposing new work.

Output transition: actionable `F-*` findings selected for filing.

### 2. `issue-filing`

Use `@issue-filer`. Creating Issues requires explicit user authorization for the selected findings.

Output transition: created or deduplicated Issue numbers and URLs.

### 3. `planning`

Use `@patch-plan` for the selected filed Issues.

Require `@patch-plan` to construct a dependency and conflict graph, combine only inseparable Issues, and partition independent work into waves and workstreams.

Present a `Parallel Codex execution packet` containing:

- The coordinator instructions and verified common base SHA
- One self-contained `Codex implementation instructions — WS-*` block per workstream
- Dependencies and wave membership
- Unique branch and isolated worktree requirements
- A repository-local worktree root at `<repository-root>/.worktrees/`
- Initial proof that the committed root `.gitignore` contains `/.worktrees/`, or a prerequisite setup PR when it does not
- Expected write boundaries and explicit `must not touch` boundaries
- Per-workstream validation, commit, PR, and reporting requirements

Instruct the external Codex coordinator to resolve the repository root first. Before spawning implementation SubAgents or creating any worktree, require it to verify the exact root `.gitignore` entry `/.worktrees/` with `git check-ignore .worktrees/`. If missing, remain in planning and produce a minimal setup-PR instruction; after that PR is merged, refresh the base SHA and resume. Then spawn one SubAgent per runnable workstream, up to available concurrency. Excess workstreams remain queued in the same wave. Never make multiple SubAgents share a writable checkout or branch.

Stop after presenting the packet. Tell the user to submit it to Codex and reply `next` after Codex has created the wave's PRs or reported a blocked workstream.

### 4. `implementation`

Do not execute implementation in `@dev-loop`. On `next`, inspect GitHub for every PR expected from the active wave:

- Match each PR by workstream, linked Issue, expected base branch, and implementation branch.
- Require a real PR number, canonical URL, head branch, and head SHA for every completed workstream.
- Track workstreams independently as `queued`, `running`, `pr-open`, `blocked`, or `failed`.
- If some workstreams are incomplete, preserve completed PRs and remain at the active wave rather than discarding progress.
- If multiple PRs match one workstream, ask the user to resolve only that ambiguity.

### 5. `pr-review`

Use `@branch-review` against each exact PR head SHA. Independent PR reviews may run concurrently.

- `changes-required`: produce a self-contained `Codex correction instructions — WS-*` block containing only that PR's verified blocking findings, required changes, validation, and PR number. Independent correction packets may be sent to separate SubAgents.
- `blocked`: stop and report the external decision or dependency required.
- `ready`: present the exact PR, reviewed head SHA, checks, approvals, merge method if known, and proposed merge action. Stop before merging.

Re-run `@branch-review` for any workstream whose head changed. Do not invalidate unchanged workstreams.

### 6. `merge-command`

Use `@pr-merge` only for PRs explicitly named in the preceding ready checkpoint. Revalidate every PR separately, then produce its guarded `gh` Draft-to-Ready-to-Merge command block. Never execute the block.

Present commands in dependency and conflict-safe order. Stop after the command handoff and tell the user to run only the stated block, then reply `next` or provide its output. Do not emit later dependent blocks until earlier merges are verified. Independent blocks may be presented together only when base-sensitive review assumptions cannot invalidate one another.

On the following `next`, read live GitHub state and verify the PR is merged or entered the required merge queue. Record the resulting target-branch commit SHA when merged. Re-check remaining PR mergeability and base-sensitive review assumptions after each verified merge; require a fresh `@branch-review` when they no longer hold.

Output transition: per-workstream verified merged PR URLs and resulting target-branch commit SHAs.

### 7. `integrated-review`

Use `@repo-review` on the resulting merged commit or a user-defined merge window. This begins the next cycle; it does not automatically authorize new Issues.

## Maintain the loop ledger

At every response, report the common ledger and a workstream table:

```markdown
# Development Loop
- Repository:
- Stage:
- Base or merged commit:
- Findings:
- Active wave:
- Next gate:
- Next action on `next`:
- Authorization needed:

| Workstream | Issues | Depends on | Status | Branch | PR | Head SHA | Review | Merge SHA |
|---|---|---|---|---|---|---|---|---|
```

Use canonical URLs and immutable SHAs. Mark absent artifacts as `not-created`, not inferred.

## Control scope and concurrency

- Prefer one primary Issue or one inseparable Issue group per workstream and PR.
- Schedule all independent workstreams in the same wave concurrently, bounded by available SubAgent slots.
- Use distinct branches and isolated worktrees under `<repository-root>/.worktrees/<workstream-id>` for concurrent SubAgents. Never place managed worktrees in sibling, temporary, or workspace-global directories.
- Classify pairwise relationships as `parallel`, `ordered`, `combined`, or `blocked`.
- Serialize work that shares mutable schemas, migrations, public contracts, generated artifacts, lockfiles, or likely overlapping files unless safe ownership boundaries are verified.
- Do not start dependent work before its prerequisite merge is present on the chosen base.
- Detect overlapping active PRs and shared files before planning parallel work.
- Rebase or update branches only when explicitly authorized and repository policy permits it.
- Never run an unbounded loop. Complete the requested stage, report the next gate, and stop when authorization or human judgment is required.
- Never implement code while using this skill. Produce Codex-ready implementation or correction instructions and wait for externally created GitHub artifacts.

## Preserve safety boundaries

- Review-only stages never imply permission to create Issues, change code, create a PR, or merge.
- Issue creation retains its explicit write requirement. Draft-to-ready and merge are user-executed commands; `next` requests command generation or post-run verification, never those writes themselves.
- Implementation delivery belongs to the external Codex run instructed by this skill.
- A SubAgent may own only its assigned workstream. It must not edit another workstream's branch or worktree.
- Never convert PR correction findings directly into Issues; resolve them in the same PR or defer them to a post-merge `@repo-review`.
- Route `SEC-*` findings through `@security-audit` and `@security-plan`; do not expose them in the ordinary loop.
- Do not bypass CI, approvals, branch protection, or repository policy.
- Do not mark Issues complete merely because a PR exists.

## Quality gate

Verify that:

- The current stage follows from live artifacts, not assumptions.
- Every transition records immutable SHAs and canonical URLs.
- Every workstream has stable identity, Issue mapping, branch, ownership, and status.
- The committed root `.gitignore` contains `/.worktrees/` before any repository-local worktree is created.
- Parallel workstreams have verified non-overlapping write boundaries or an explicit integration strategy.
- Dependent work is assigned to later waves and rebased on verified merged commits.
- No write occurred without the authorization required by the responsible skill, and no Draft-to-Ready-to-Merge write was executed by `@dev-loop` or `@pr-merge`.
- Every response completed no more than one substantive stage.
- Implementation and correction instructions are self-contained for a separate Codex run.
- `next` applies only to the previously announced action.
- Changed PR heads trigger a fresh review.
- Merge completion is verified before integrated review.
- The next action and blocking gate are explicit.
