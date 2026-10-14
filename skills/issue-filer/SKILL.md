---
name: issue-filer
description: Create deduplicated Bug or Feature Request Issues from explicitly selected merged-repository findings or human-approved blueprint design units. Use only when the user asks to file those Issues; preserve design revision, acceptance criteria and approval boundaries without authorizing execution.
---

# File GitHub Review Issues

Create high-quality GitHub Issues from selected review findings or approved design units while preventing duplicates and unsupported claims. Do not turn PR/prepublication correction findings into new Issues; keep them with the active change.

## Explain any human approval request

When actually requesting a human decision or handing off a user-run action, use `@human-review approval-brief`. Include **今回やった内容**, **今回承認してほしい内容**, **承認によって影響がある範囲**, and **否認した場合の対応** in the same message. Name the action/actor, target/revision and reason for the gate; distinguish completed work from proposals. Use the brief only to explain a needed decision, without an additional queue scan/write or confirmation for already authorized work. Preserve the stated denial response at continuation.

## Require explicit write intent

Treat a request such as “create issues for all actionable findings” as authorization for those findings. Otherwise require the user to identify finding IDs or approve the proposed set before creating anything.

Do not create issues when the user asked only for review, recommendations, drafts, or a list of possible issues.

## Validate the input

1. Require the repository and either a structured merged-state review (`F-*`) or human-approved `@blueprint` design units (`DES-*`) with a stable brief revision and approval source.
2. For review findings, require reviewed branch and immutable merged SHA. For design units, require approved outcome, scope, non-goals, stable ACs, dependencies and current repository snapshot. Never fabricate a bug finding or merged-review origin for a new capability.
3. Accept only findings classified as `bug` or `feature-request`.
4. Reject findings missing location/evidence/impact/recommendation, and design units missing approval provenance or testable acceptance. Keep unresolved material choices as blockers or separately approved discovery scope, not executable assumptions.
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

Under `Source review` or `Source design`, include the F/DES ID, source revision/approval scope, inspected branch/SHA, related artifacts and pinned evidence. Preserve stable AC IDs. Clearly label proposed designs and inferred reproduction; never present them as confirmed facts. Filing permission is not dispatch, implementation, commit, push or PR permission.

When a caller supplies a `@repo-handoff` workflow ID or canonical carrier, preserve that durable reference in `Source review` and return the created Issue URL as the new workstream carrier. After each created or deduplicated Issue is identified, automatically persist the latest issue-filing state marker on the new or existing carrier and read it back. This marker records the result and next gate; it does not expand the user's authorization to create additional Issues or change their content.

If the source finding contains an action-binding constraint, preserve it as an explicit issue section with target action, status, unresolved prerequisite, clearing authority, admissible fallback, evidence snapshot, and required revalidation. Use `none` or `unknown` for missing fields. Do not weaken it into a note, suggestion, deferred owner task, or precedent-based exception.

Create one issue at a time and capture its URL before continuing. If a write fails, stop creating dependent issues and report the failure.

## Report results

Return a table containing:

| Finding / Design unit | Result | Issue | Notes |
|---|---|---|---|

Use `created`, `duplicate`, `skipped`, or `failed` as the result. Finish with counts for each result and disclose any labels or templates that could not be applied.

## Quality gate

Before each creation, verify that:

- The user authorized this finding.
- The finding is evidence-backed and still applicable.
- The appropriate source is recorded: merged review SHA, or approved design revision and current repository snapshot.
- No matching issue already exists.
- The issue describes one root cause or capability.
- Acceptance criteria are verifiable.
- Every source constraint either survives with its complete operational role or is explicitly marked incomplete and returned for clarification.
- The body contains no credentials, private logs, or irrelevant review commentary.
- Any supplied workflow/carrier reference is preserved so a later `@repo-handoff restore` can connect the Issue to its originating review and workstream.
- The issue-filing result is automatically recorded and read back on an existing carrier; if no carrier or write path exists, return `bootstrap`/`pending-write` explicitly rather than claiming durable recovery.
