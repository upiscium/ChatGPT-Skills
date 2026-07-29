---
name: branch-review
description: Review a GitHub pull request as the quality gate before merge, producing evidence-backed blocking findings, non-blocking observations, and a merge recommendation without creating issues or changing the PR. Use when the user asks to review a PR, validate an issue implementation, assess whether a pull request is ready to merge, or inspect regressions introduced by a PR.
---

# Review a Pull Request

Review an issue-driven implementation before merge. Keep PR correction work separate from post-merge product review and future Issue generation.

## Resolve the target

1. Require a repository and PR URL or number. If only a branch is supplied, ask for its PR.
2. Fetch the PR metadata, description, linked issues, changed files, complete patch, review state, comments, and available check status.
3. Record the PR number and URL, state, base and head branches, and immutable base and head SHAs.
4. Read repository instructions, contribution guidance, linked Issue acceptance criteria, manifests, tests, CI configuration, and relevant documentation.
5. State whether the review is source-only or includes locally run validation.

## Review the implementation

1. Inspect the complete `base...head` change set and surrounding implementation.
2. Trace affected callers, data flow, state transitions, error paths, public contracts, configuration, tests, and documentation.
3. Check that the PR addresses its linked Issues completely without unrelated scope expansion.
4. Verify tests protect the changed behavior and meaningful failure paths.
5. Consider available CI and prior review signals, but verify claims against code.
6. Attribute actionable findings only to the PR or to unmet acceptance criteria of its linked Issues.
7. List unrelated pre-existing problems only as post-merge review leads; do not use them to block this PR unless the change makes them materially worse.

## Classify findings

Use:

- `blocking`: Must be corrected before merge because the PR is incorrect, unsafe, incomplete against required scope, or lacks essential validation.
- `non-blocking`: Worth improving but safe to defer without violating the linked Issue or contract.
- `question`: A decision or missing fact prevents a reliable conclusion.
- `post-merge-lead`: A pre-existing or broader product concern for `@repo-review`, not a PR defect.

Assign priority `P0` through `P3` and confidence `high`, `medium`, or `low`. Require a precise code path, contract, test result, or reproducible reasoning chain. Do not report style preferences as findings.

## Produce the review contract

```markdown
# Pull Request Review

## Target
- Repository:
- Pull request:
- Pull request URL:
- State:
- Base branch and commit:
- Head branch and commit:
- Linked issues:

## Scope and validation
- Intended outcome:
- Inspected:
- Checks run:
- Existing CI/review signals:
- Limitations:

## Merge recommendation
- Decision: ready | changes-required | blocked
- Rationale:

## Findings

### PR-001: <title>
- Classification: blocking | non-blocking | question | post-merge-lead
- Priority: P0 | P1 | P2 | P3
- Confidence: high | medium | low
- Location:
- Evidence:
- Impact:
- Required change:
- Verification:
```

Use stable `PR-*` IDs. Omit `Required change` only for questions and post-merge leads.

## Preserve boundaries

- Do not create Issues from PR findings.
- Do not approve, request changes on, comment on, merge, close, or modify the PR unless the user explicitly requests that separate write action.
- Do not treat `ready` as authorization to merge.
- Send post-merge leads to `@repo-review` only after the implementation is merged.

## Quality gate

Verify that:

- Every blocking finding was introduced by the PR or violates a linked Issue's acceptance criteria.
- The complete PR and relevant surrounding code were inspected.
- Base and head SHAs make the report reproducible.
- Required corrections and verification steps are executable.
- The merge recommendation follows from the findings.
- Broader product concerns remain separate from PR correction work.
