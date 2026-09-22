---
name: issue-filer
description: Convert selected, evidence-backed findings from a merged GitHub repository review into deduplicated Bug or Feature Request issues. Use only when the user explicitly asks to create, file, or open GitHub issues from @repo-review findings or a comparable structured whole-repository review.
---

# File GitHub Review Issues

Create high-quality GitHub issues from selected review findings while preventing duplicates and unsupported claims.

## Require explicit write intent

Treat a request such as “create issues for all actionable findings” as authorization for those findings. Otherwise require the user to identify finding IDs or approve the proposed set before creating anything.

Do not create issues when the user asked only for review, recommendations, drafts, or a list of possible issues.

## Validate the input

1. Require the repository and a structured review report, preferably from `@repo-review`.
2. Require the reviewed branch and immutable merged commit SHA.
3. Accept only findings classified as `bug` or `feature-request`.
4. Reject or return for further review any finding without a location, evidence, impact, and recommendation.
5. Re-check material evidence when the report is stale, the reviewed branch moved, or the finding is low-confidence.
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
4. Do not reopen, add non-marker comments to, or modify the existing issue unless the user explicitly asks. The marked `codex-repo-state:v1` continuation update performed by `@repo-handoff` is the automatic-recording exception.

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

Under `Source review`, include the finding ID, reviewed branch and commit, related merged PRs when relevant, and commit-pinned file links. Clearly label inferred reproduction steps or proposed designs; never present them as confirmed facts.

When a caller supplies a `@repo-handoff` workflow ID or canonical carrier, preserve that durable reference in `Source review` and return the created Issue URL as the new workstream carrier. After each created or deduplicated Issue is identified, automatically persist the latest issue-filing state marker on the new or existing carrier and read it back. This marker records the result and next gate; it does not expand the user's authorization to create additional Issues or change their content.

If the source finding contains an action-binding constraint, preserve it as an explicit issue section with target action, status, unresolved prerequisite, clearing authority, admissible fallback, evidence snapshot, and required revalidation. Use `none` or `unknown` for missing fields. Do not weaken it into a note, suggestion, deferred owner task, or precedent-based exception.

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
- The reviewed branch and immutable merged commit are recorded.
- No matching issue already exists.
- The issue describes one root cause or capability.
- Acceptance criteria are verifiable.
- Every source constraint either survives with its complete operational role or is explicitly marked incomplete and returned for clarification.
- The body contains no credentials, private logs, or irrelevant review commentary.
- Any supplied workflow/carrier reference is preserved so a later `@repo-handoff restore` can connect the Issue to its originating review and workstream.
- The issue-filing result is automatically recorded and read back on an existing carrier; if no carrier or write path exists, return `bootstrap`/`pending-write` explicitly rather than claiming durable recovery.
