---
name: dev-loop
description: Coordinate a checkpoint-based, issue-driven GitHub development loop across @repo-review, @issue-filer, @patch-plan, external Codex implementation, @branch-review, and @pr-merge. Use when the user asks to start, continue, resume, track, or advance the repository improvement cycle one stage at a time, especially when implementation instructions should be handed to Codex and the loop should wait for a `next` prompt before inspecting the resulting PR and continuing.
---

# Run the Development Loop

Coordinate the existing skills as a checkpointed state machine. Advance only through validated artifacts; do not implement the plan inside this skill.

## Use checkpoint mode

Complete at most one substantive stage per response, present its artifact and the exact next action, then stop.

- Treat `next`, `continue`, or an equivalent reply as authorization for only the single next action named in the previous loop ledger.
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
- Implementation plan
- Implementation branch and head SHA
- PR number, URL, base, and head SHA
- Latest `@branch-review` decision
- Merge commit SHA

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

Present the complete executable plan in a self-contained `Codex implementation instructions` block. It must include the Issue set, immutable base SHA, branch requirements, implementation tasks, validation, commit and PR requirements, and the required final PR number and URL.

Stop after presenting the instructions. Tell the user to submit them to Codex and reply `next` after Codex has created the PR.

### 4. `implementation`

Do not execute implementation in `@dev-loop`. On `next`, inspect GitHub for the PR produced by Codex:

- Match it by repository, linked Issue, expected base branch, and implementation branch when specified.
- Require a real PR number, canonical URL, head branch, and head SHA.
- If no unambiguous matching PR exists, remain in `implementation`, report what is missing, and wait again.
- If multiple PRs match, ask the user to select one.

### 5. `pr-review`

Use `@branch-review` against the exact PR head SHA.

- `changes-required`: produce a self-contained `Codex correction instructions` block containing only verified blocking findings, required changes, validation, and the same PR number. Stop and ask the user to send it to Codex, then reply `next` after the PR is updated.
- `blocked`: stop and report the external decision or dependency required.
- `ready`: present the exact PR, reviewed head SHA, checks, approvals, merge method if known, and proposed merge action. Stop before merging.

Re-run `@branch-review` after any head change.

### 6. `merge`

Use `@pr-merge` only after the user replies `next` to the exact merge action announced at the preceding `ready` checkpoint, or otherwise explicitly authorizes that specific PR merge.

Output transition: merged PR URL and resulting target-branch commit SHA.

### 7. `integrated-review`

Use `@repo-review` on the resulting merged commit or a user-defined merge window. This begins the next cycle; it does not automatically authorize new Issues.

## Maintain the loop ledger

At every response, report:

```markdown
# Development Loop
- Repository:
- Stage:
- Base or merged commit:
- Findings:
- Issues:
- Plan:
- Implementation branch:
- Pull request:
- Reviewed head SHA:
- Review decision:
- Merge commit:
- Next gate:
- Next action on `next`:
- Authorization needed:
```

Use canonical URLs and immutable SHAs. Mark absent artifacts as `not-created`, not inferred.

## Control scope and concurrency

- Prefer one primary Issue or one inseparable Issue group per implementation PR.
- Do not combine unrelated Issues merely to reduce PR count.
- Do not start dependent work before its prerequisite merge is present on the chosen base.
- Detect overlapping active PRs and shared files before planning parallel work.
- Rebase or update branches only when explicitly authorized and repository policy permits it.
- Never run an unbounded loop. Complete the requested stage, report the next gate, and stop when authorization or human judgment is required.
- Never implement code while using this skill. Produce Codex-ready implementation or correction instructions and wait for externally created GitHub artifacts.

## Preserve safety boundaries

- Review-only stages never imply permission to create Issues, change code, create a PR, or merge.
- Issue creation and merge retain their own explicit write requirements. A `next` reply satisfies them only when the immediately preceding ledger named the exact write target and action.
- Implementation delivery belongs to the external Codex run instructed by this skill.
- Never convert PR correction findings directly into Issues; resolve them in the same PR or defer them to a post-merge `@repo-review`.
- Route `SEC-*` findings through `@security-audit` and `@security-plan`; do not expose them in the ordinary loop.
- Do not bypass CI, approvals, branch protection, or repository policy.
- Do not mark Issues complete merely because a PR exists.

## Quality gate

Verify that:

- The current stage follows from live artifacts, not assumptions.
- Every transition records immutable SHAs and canonical URLs.
- No write occurred without the authorization required by the responsible skill.
- Every response completed no more than one substantive stage.
- Implementation and correction instructions are self-contained for a separate Codex run.
- `next` applies only to the previously announced action.
- Changed PR heads trigger a fresh review.
- Merge completion is verified before integrated review.
- The next action and blocking gate are explicit.
