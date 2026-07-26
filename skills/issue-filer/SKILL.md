---
name: issue-filer
description: Convert selected, evidence-backed findings from a GitHub branch review into deduplicated Bug or Feature Request issues. Use only when the user explicitly asks to create, file, or open GitHub issues from review findings or a structured branch-review report.
---

# File GitHub Review Issues

Create high-quality GitHub issues from selected review findings while preventing duplicates and unsupported claims.

## Require explicit write intent

Treat a request such as “create issues for all actionable findings” as authorization for those findings. Otherwise require the user to identify finding IDs or approve the proposed set before creating anything.

Do not create issues when the user asked only for review, recommendations, drafts, or a list of possible issues.

## Validate the input

1. Require the repository and a structured review report, preferably from `@branch-review`.
2. Require target and base commit SHAs so the evidence is immutable.
3. Accept only findings classified as `bug` or `feature-request`.
4. Reject or return for further review any finding without a location, evidence, impact, and recommendation.
5. Re-check material evidence when the report is stale, the branch moved, or the finding is low-confidence.
6. Merge findings that share one root cause or represent one inseparable capability.

## Check repository conventions

1. Read contribution guidance, issue templates, and relevant project documentation.
2. Inspect existing labels. Use an existing `bug` label for bugs and an existing `enhancement` or `feature` label for feature requests when available.
3. Never create new labels, milestones, or projects unless the user explicitly requests it.

## Prevent duplicates

Before each write:

1. Search open and closed issues using the proposed title, behavior, symbols, file paths, error text, and finding ID where useful.
2. Treat an issue as a duplicate when it describes the same root cause or requested capability, even if its wording differs.
3. Do not create a duplicate. Report the existing issue URL and why it matches.
4. Do not reopen, comment on, or modify the existing issue unless the user explicitly asks.

## Write the issue

Use a concise, outcome-oriented title. Do not prefix the title with `Bug:` or `Feature:` when labels already communicate the type.

For a bug, include:

```markdown
## Summary
## Observed behavior
## Expected behavior
## Evidence
## Impact
## Reproduction or triggering path
## Suggested direction
## Acceptance criteria
## Source review
```

For a feature request, include:

```markdown
## Problem
## Desired outcome
## Proposed scope
## Non-goals
## Acceptance criteria
## Alternatives considered
## Source review
```

Under `Source review`, include the finding ID, target branch and commit, base branch and commit, and relevant file links. Clearly label inferred reproduction steps or proposed designs; never present them as confirmed facts.

Create one issue at a time and capture its URL before continuing. If a write fails, stop creating dependent issues and report the failure.

## Report results

Return a table containing:

| Finding | Result | Issue | Notes |
|---|---|---|---|

Use `created`, `duplicate`, `skipped`, or `failed` as the result. Finish with counts for each result and disclose any labels or templates that could not be applied.

## Quality gate

Before each creation, verify that:

- The user authorized this finding.
- The finding is evidence-backed and still applicable.
- No matching issue already exists.
- The issue describes one root cause or capability.
- Acceptance criteria are verifiable.
- The body contains no credentials, private logs, or irrelevant review commentary.
