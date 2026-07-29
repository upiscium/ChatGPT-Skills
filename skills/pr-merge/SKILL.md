---
name: pr-merge
description: Safely merge a GitHub pull request after an evidence-backed @branch-review by revalidating the exact head commit, required checks, approvals, mergeability, and repository policy, then report the merge result without performing unrelated changes. Use only when the user explicitly asks to merge, land, or complete a reviewed PR.
---

# Merge a Reviewed Pull Request

Treat merge as a guarded write operation, not an automatic consequence of a positive review.

## Require explicit authority

Require an explicit request to merge a specific repository PR. A `ready` recommendation from `@branch-review`, an approval, or passing CI is not by itself authorization.

Resolve ambiguous repository or PR references before any write.

## Establish the reviewed state

1. Fetch the current PR, base and head branches, head SHA, mergeability, draft state, reviews, unresolved conversations when available, and required checks.
2. Require a `@branch-review` report with decision `ready` for the same PR and exact current head SHA.
3. If the head SHA changed after review, stop and require a fresh `@branch-review`.
4. Confirm the PR is open, not draft, and targets the intended branch.
5. Confirm linked Issues and intended closing behavior.

## Enforce merge gates

Do not merge when any of these applies:

- The review decision is `changes-required` or `blocked`.
- Any blocking `PR-*` finding remains unresolved.
- Required checks are pending, cancelled, skipped unexpectedly, or failing.
- Required approvals are missing or a changes-requested review remains active.
- The PR has conflicts, is not mergeable, or violates branch protection.
- The base branch or repository policy changed in a way that invalidates the review.
- The PR contains unexpected commits, files, or scope since review.
- Security-sensitive changes lack the required private review path.

Do not dismiss reviews, bypass protection, use administrator override, force-push, update the branch, or alter checks to make a merge possible.

## Select the merge method

1. Follow explicit user direction.
2. Otherwise follow repository contribution guidance and enabled repository policy.
3. If multiple methods remain valid and the choice materially affects history, ask the user.
4. Never guess a merge method that discards intentionally separate commits.

Record `merge`, `squash`, or `rebase` and the reason.

## Merge and verify

1. Re-fetch the PR immediately before the write and verify the head SHA again.
2. Perform exactly one merge action.
3. Fetch the resulting PR state and target-branch commit.
4. Verify that the PR is merged and capture the merge or resulting commit SHA.
5. Inspect linked Issue state without modifying it. Report Issues that did not close as expected.
6. Do not delete the source branch unless the user explicitly requested it or a verified repository policy performs it automatically.

## Report

Return:

```markdown
# PR Merge Result
- Repository:
- Pull request:
- Pull request URL:
- Reviewed head SHA:
- Target branch:
- Merge method:
- Result: merged | blocked | failed
- Resulting commit SHA:
- Linked issue status:
- Follow-up:
```

For a blocked or failed merge, state the exact gate, current head SHA, and safe next action. Never claim success without reading back the merged PR state.

## Quality gate

Verify that:

- The user explicitly authorized this exact merge.
- The positive review matches the current head SHA.
- Required CI, approvals, mergeability, and branch policy passed.
- No protection or review control was bypassed.
- The merge result and resulting commit were read back.
- The output contains enough information for `@repo-review` to review the integrated state.
