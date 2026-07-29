---
name: repo-review
description: Review the merged state of a GitHub repository as a whole and produce evidence-backed Bug and Feature Request candidates for the next development loop without creating issues. Use after pull requests are merged, or when the user asks for a repository-wide product, architecture, implementation, integration, test, documentation, or completeness review of the current default branch or a specified merged commit.
---

# Review the Merged Repository

Assess the integrated product after merge and produce structured candidates that `@issue-filer` can safely turn into the next Issues.

## Resolve the snapshot

1. Identify the repository and review branch or commit. Default to the repository's default branch only when unspecified.
2. Resolve the reviewed state to an immutable commit SHA.
3. Record recently merged PRs when they define the requested review window, but inspect the integrated repository rather than replaying PR reviews.
4. Read repository instructions, product goals, architecture documents, roadmaps, issue history, manifests, tests, CI configuration, and user-facing documentation.
5. Define the review scope and disclose inaccessible components or validation limitations.

## Inspect the integrated product

1. Inventory major components, public interfaces, workflows, persistence boundaries, integrations, deployment configuration, tests, and documentation.
2. Trace important end-to-end user and operator workflows across component boundaries.
3. Compare implemented behavior with documented goals, existing contracts, supported configurations, and current product expectations.
4. Inspect integration gaps, regressions, inconsistent invariants, missing failure handling, obsolete paths, and incomplete capabilities.
5. Run appropriate tests and static checks when a local checkout is available and safe.
6. Check open and closed Issues and recent PRs so completed, accepted, duplicate, or intentionally excluded work is not proposed again.

## Classify findings

Use:

- `bug`: The merged product can produce incorrect, unsafe, inconsistent, regressive, or contract-violating behavior.
- `feature-request`: A concrete capability required by a documented objective or validated workflow is absent or materially incomplete.
- `non-issue`: A preference, speculative idea, question, duplicate, accepted tradeoff, or unsupported concern.

Assign priority `P0` through `P3` and confidence `high`, `medium`, or `low`.

Require a precise code path, contract, test result, log, or reproducible reasoning chain for every bug. Require a documented objective, user workflow, architectural dependency, or explicitly validated need for every feature request. Do not invent roadmap requirements.

## Produce the review contract

```markdown
# Repository Review

## Review target
- Repository:
- Branch:
- Commit:
- Review mode: full | scoped | since-merge
- Merge window or related PRs:

## Scope and validation
- Product areas inspected:
- Workflows traced:
- Checks run:
- Existing issues searched:
- Limitations:

## Summary

## Findings

### F-001: <title>
- Classification: bug | feature-request | non-issue
- Priority: P0 | P1 | P2 | P3
- Confidence: high | medium | low
- Location:
- Evidence:
- Impact:
- Recommendation:
- Acceptance criteria:
```

Use stable `F-*` IDs. Omit acceptance criteria only for non-issues. Include commit-pinned file links where possible.

## Preserve boundaries

- Do not reclassify unresolved PR feedback as a repository finding until the relevant code is merged.
- Do not create, edit, label, or comment on Issues.
- Do not modify code, branches, commits, or PRs.
- Route selected actionable findings to `@issue-filer`.
- Route security-sensitive findings to `@security-audit` rather than exposing vulnerability details in ordinary Issue candidates.

## Quality gate

Verify that:

- Every actionable finding exists in the reviewed merged commit.
- Findings reflect integrated behavior, not patch aesthetics.
- Existing Issues and completed work were checked for duplication.
- Multiple symptoms with one root cause are grouped.
- Bugs and missing capabilities are distinguished.
- Acceptance criteria are testable and outcome-oriented.
- The reviewed commit SHA and validation gaps are recorded.
