# Generate user-run merge commands

Read this reference for dev-loop merge-command-only or merge stages. This mode replaces the former standalone pr-merge skill. A legacy review may be evidence only after current target and full gates are revalidated.

Produce a self-contained command block for the user to run. Never mark a PR ready, merge it, enable auto-merge, or perform another GitHub action write. The skill must still automatically persist the neutral `codex-repo-state:v1` command-handoff marker on the existing PR or linked Issue carrier and read it back; that metadata-only write is not the merge operation.

## Require a reviewed target

Require:

- An explicit repository and PR number or canonical URL
- A `@change-review` decision of `ready` for that PR
- The exact reviewed head SHA, intended base branch and freshly revalidated base SHA
- A merge method selected by the user or unambiguously required by repository policy

Also require the preceding review's complete merge gate contract: target action, status, unresolved prerequisite, clearing authority, admissible fallback, evidence snapshot, and required live revalidation. Generate commands only when the contract is `allowed` and every prerequisite is resolved by its named authority. A `ready` label or prior review summary is not a substitute for this contract.

If the review is missing, stale, blocked, or tied to another head SHA, stop and request a fresh `@change-review`. Ask when multiple merge methods remain materially different.

## Generate the guarded command block

Substitute literal values for `OWNER/REPO`, `NUMBER`, `REVIEWED_HEAD_SHA`, `BASE_BRANCH`, and the selected merge flag. Quote values. Emit one Bash block that:

1. Enables `set -euo pipefail` and confirms `gh auth status`.
2. Reads the live PR state with `gh pr view`.
3. Aborts unless the PR is open, targets the expected base branch, and its live head exactly equals the reviewed head SHA.
4. Shows review decision, mergeability, merge-state status, and the PR URL for human confirmation.
5. Runs `gh pr checks NUMBER --repo OWNER/REPO --required --watch --fail-fast`.
6. Marks the PR ready only when its live `isDraft` value is `true`.
7. Re-reads and re-compares the head SHA immediately before merge.
8. Runs exactly one `gh pr merge` command using `--match-head-commit REVIEWED_HEAD_SHA` and exactly one of `--merge`, `--squash`, or `--rebase`.
9. Reads back `state`, `mergedAt`, `mergeCommit`, and `url` for verification.

These live checks are endpoint containment. Keep them even when the handoff artifact appears complete; do not infer current permission from an old artifact.

Use this structure:

```bash
set -euo pipefail

repo='OWNER/REPO'
pr='NUMBER'
reviewed_head='REVIEWED_HEAD_SHA'
expected_base='BASE_BRANCH'
reviewed_base='REVALIDATED_BASE_SHA'

gh auth status

# Verify the snapshot before each mutation. GitHub protections still enforce policy.
assert_snapshot() {
  test "$(gh pr view "$pr" --repo "$repo" --json state --jq '.state')" = 'OPEN'
  test "$(gh pr view "$pr" --repo "$repo" --json headRefOid --jq '.headRefOid')" = "$reviewed_head"
  test "$(gh pr view "$pr" --repo "$repo" --json baseRefName --jq '.baseRefName')" = "$expected_base"
  test "$(gh pr view "$pr" --repo "$repo" --json baseRefOid --jq '.baseRefOid')" = "$reviewed_base"
}
assert_snapshot

state="$(gh pr view "$pr" --repo "$repo" --json state --jq '.state')"
live_head="$(gh pr view "$pr" --repo "$repo" --json headRefOid --jq '.headRefOid')"
live_base="$(gh pr view "$pr" --repo "$repo" --json baseRefName --jq '.baseRefName')"

test "$state" = 'OPEN' || { echo "Blocked: PR state is $state" >&2; exit 1; }
test "$live_head" = "$reviewed_head" || { echo "Blocked: reviewed $reviewed_head, live $live_head" >&2; exit 1; }
test "$live_base" = "$expected_base" || { echo "Blocked: expected base $expected_base, live $live_base" >&2; exit 1; }

gh pr view "$pr" --repo "$repo" \
  --json url,isDraft,reviewDecision,mergeable,mergeStateStatus,headRefOid,baseRefName

gh pr checks "$pr" --repo "$repo" --required --watch --fail-fast

is_draft="$(gh pr view "$pr" --repo "$repo" --json isDraft --jq '.isDraft')"
if [ "$is_draft" = 'true' ]; then
  assert_snapshot
  gh pr ready "$pr" --repo "$repo"
fi

live_head="$(gh pr view "$pr" --repo "$repo" --json headRefOid --jq '.headRefOid')"
test "$live_head" = "$reviewed_head" || { echo "Blocked: head changed to $live_head" >&2; exit 1; }

assert_snapshot
# Re-check after Ready, which may trigger new required checks.
gh pr checks "$pr" --repo "$repo" --required --watch --fail-fast
assert_snapshot
gh pr merge "$pr" --repo "$repo" --MERGE_METHOD \
  --match-head-commit "$reviewed_head"

gh pr view "$pr" --repo "$repo" \
  --json state,mergedAt,mergeCommit,url
```

Replace `--MERGE_METHOD` with a literal supported flag; do not leave it as a variable or placeholder in the final command. Keep the live status output visible rather than suppressing it.

## Preserve repository protections

- Never emit `--admin`, `--auto`, `--delete-branch`, `--disable-auto`, force-push, review dismissal, branch updates, or commands that alter checks.
- Do not emit a command that approves the PR on the user's behalf.
- Do not claim that `reviewDecision` alone fully models repository approval rules; GitHub remains the enforcement authority.
- If required checks are absent by policy, explain why before omitting `--required`; do not silently weaken the gate.
- If a merge queue is required, explain that `gh pr merge` may enqueue rather than immediately merge. Do not add `--admin` to bypass it.
- Do not include secrets, tokens, or credential-export commands.

## Return the handoff

Before the command, include `@human-review approval-brief` in the same message: what was reviewed/verified; the exact Ready/Merge action the user would execute and its reviewed target; the affected base branch and evidenced CI/queue/deployment effects; and what happens if the user declines (no command execution, retain the PR/work and identify the next bounded handling). Describe known merge/recovery constraints without claiming reversibility or deployment behavior that was not verified. This explains the user-run handoff and adds no approval round.

Return:

````markdown
# PR Merge Command

- 今回やった内容:
- 今回承認してほしい内容（ユーザーが実行する操作）:
- 承認によって影響がある範囲:
- 否認した場合の対応:

- Repository:
- Pull request:
- Pull request URL:
- Reviewed head SHA:
- Expected base branch:
- Merge method:
- Review decision: ready
- Gate status: allowed
- Cleared prerequisite and authority:
- Evidence snapshot:
- Revalidation performed by command:
- Action: run the command block locally

```bash
# guarded command block
```

- Expected result: merged | merge-queue entry
- After running: reply `next` or provide the final command output for verification
````

For multiple PRs, emit separately labeled blocks in dependency-safe order. Never imply that concurrent execution is safe when one merge can change another PR's base assumptions.

Automatically persist and read back a `codex-repo-state:v1` checkpoint containing the reviewed PR, exact head SHA, command-generation gate, expected post-command state, and the next verification action. This metadata marker is not a merge approval and does not claim that the command was executed. If no carrier exists, return `bootstrap`; if the marker write is unavailable, return the exact payload as `pending-write`. After the user runs the command, `@dev-loop` or `@repo-handoff audit` must read the live PR and automatically record the resulting merge SHA.

## Quality gate

Verify that:

- No action-changing GitHub write was executed by this skill; the only permitted write is the automatic state marker on an existing carrier.
- The exact repository, PR, reviewed head SHA, base branch, and merge method are literal and unambiguous.
- The command aborts on stale review, changed base, closed PR, or failing required checks.
- The merge command contains `--match-head-commit` and no bypass flag.
- The upstream gate contract is complete, `allowed`, and pinned to the same target and head SHA.
- Draft-to-ready is conditional and verification follows the merge command.
- The output contains a durable-state checkpoint whose save/read-back status is explicit, without implying that the merge command was executed.

## CLI compatibility and races

Confirm the installed CLI's help before generating commands. References: https://cli.github.com/manual/gh_pr_merge , https://cli.github.com/manual/gh_pr_ready , https://cli.github.com/manual/gh_pr_checks , https://cli.github.com/manual/gh_pr_view .

Replace every placeholder with validated, shell-quoted literals. A changed base SHA stops the block even for base-stable reviews until revalidated. The head match is server-enforced; base and Ready checks are client-side and do not eliminate all races. Do not claim atomic base protection. If that guarantee is required, require repository-enforced up-to-date checks/merge queue or stop for a safe manual process.

For merge queues, explain the queue semantics and verify required checks have passed immediately before the merge request. GitHub may enable auto-merge when queue requirements are not yet met; if automatic enabling cannot be excluded or is forbidden by the user's grant, do not emit the merge mutation until a compliant path is established. Never add bypass flags or equate OPEN with queued without queue evidence. Unknown protection or check policy is a blocker, not proof that no checks are required.
