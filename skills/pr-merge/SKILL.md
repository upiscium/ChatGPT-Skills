---
name: pr-merge
description: Generate a guarded GitHub CLI command block that lets the user mark a reviewed pull request ready and merge it manually after an evidence-backed @branch-review. Use when the user wants commands for Draft-to-Ready-to-Merge, wants to land or complete a reviewed PR without connector writes, or needs a copy-pasteable merge handoff pinned to the reviewed head SHA. Never execute the ready or merge commands.
---

# Generate PR Merge Commands

Produce a self-contained command block for the user to run. Never mark a PR ready, merge it, enable auto-merge, or perform another GitHub write.

## Require a reviewed target

Require:

- An explicit repository and PR number or canonical URL
- A `@branch-review` decision of `ready` for that PR
- The exact reviewed head SHA and intended base branch
- A merge method selected by the user or unambiguously required by repository policy

If the review is missing, stale, blocked, or tied to another head SHA, stop and request a fresh `@branch-review`. Ask when multiple merge methods remain materially different.

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

Use this structure:

```bash
set -euo pipefail

repo='OWNER/REPO'
pr='NUMBER'
reviewed_head='REVIEWED_HEAD_SHA'
expected_base='BASE_BRANCH'

gh auth status

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
  gh pr ready "$pr" --repo "$repo"
fi

live_head="$(gh pr view "$pr" --repo "$repo" --json headRefOid --jq '.headRefOid')"
test "$live_head" = "$reviewed_head" || { echo "Blocked: head changed to $live_head" >&2; exit 1; }

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

Return:

````markdown
# PR Merge Command
- Repository:
- Pull request:
- Pull request URL:
- Reviewed head SHA:
- Expected base branch:
- Merge method:
- Review decision: ready
- Action: run the command block locally

```bash
# guarded command block
```

- Expected result: merged | merge-queue entry
- After running: reply `next` or provide the final command output for verification
````

For multiple PRs, emit separately labeled blocks in dependency-safe order. Never imply that concurrent execution is safe when one merge can change another PR's base assumptions.

## Quality gate

Verify that:

- No GitHub write was executed by this skill.
- The exact repository, PR, reviewed head SHA, base branch, and merge method are literal and unambiguous.
- The command aborts on stale review, changed base, closed PR, or failing required checks.
- The merge command contains `--match-head-commit` and no bypass flag.
- Draft-to-ready is conditional and verification follows the merge command.
