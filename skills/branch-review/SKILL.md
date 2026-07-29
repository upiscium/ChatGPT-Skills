---
name: branch-review
description: Review a specific GitHub pull request and produce evidence-backed Bug and Feature Request candidates without creating issues or submitting a GitHub review. Use when the user asks to inspect, assess, audit, or review a PR, its changed files, proposed behavior, implementation quality, or regressions introduced by a pull request.
---

# Review a GitHub Pull Request

Review the requested pull request and return a structured report that another skill can safely convert into GitHub issues.

## Resolve the review target

1. Require a repository and pull request URL or number. If only a branch is supplied, ask for the PR; do not silently fall back to a branch review.
2. Fetch the PR metadata, description, linked issues, changed-file inventory, patch, review state, and available check status.
3. Record the PR number and URL, base and head branches, and immutable base and head commit SHAs.
4. Detect draft, closed, merged, or superseded PRs and state how that limits the review.
5. Read applicable repository instructions and context, including `AGENTS.md`, contribution guidance, manifests, tests, CI configuration, issue requirements, and documentation relevant to the changed area.

## Inspect the implementation

1. Review the PR's complete `base...head` change set and inventory changed files.
2. Inspect the complete surrounding implementation for every material change. Do not review patches in isolation.
3. Trace affected callers, data flow, state transitions, error paths, configuration, public interfaces, tests, and documentation.
4. Run relevant tests or static checks when a local checkout is available and execution is safe. Otherwise state that validation was source-only.
5. Compare behavior with the PR description, linked issues, acceptance criteria, documentation, tests, API contracts, and established project patterns.
6. Attribute only findings introduced by the PR or required for its stated outcome. Record unrelated pre-existing problems separately as out-of-scope observations, not actionable PR findings.
7. Inspect available CI and review signals, but verify claims against code rather than treating a passing check or prior approval as proof of correctness.

## Classify findings

Use one of these classifications:

- `bug`: A PR change can produce incorrect, unsafe, inconsistent, regressive, or contract-violating behavior.
- `feature-request`: A concrete capability required by the PR's stated outcome, linked issue, or acceptance criteria is absent or materially incomplete.
- `non-issue`: A suggestion, preference, question, or weakly supported concern that should not become an issue yet.

Do not label personal style preferences as bugs. Do not invent product requirements to justify feature requests.

Assign:

- Priority: `P0` critical, `P1` high, `P2` medium, or `P3` low.
- Confidence: `high`, `medium`, or `low`.

Require a precise code path, contract, test result, log, or reproducible reasoning chain for every `bug`. Require a documented objective, user workflow, or architectural need for every `feature-request`. Downgrade unsupported claims to `non-issue`.

## Produce the review contract

Return Markdown with this structure:

```markdown
# Pull Request Review

## Review target
- Repository:
- Pull request:
- Pull request URL:
- Base branch:
- Base commit:
- Head branch:
- Head commit:
- PR state: draft | open | closed | merged

## Scope and validation
- PR intent and linked issues:
- Inspected:
- Checks run:
- Existing CI/review signals:
- Limitations:

## Summary

## Findings

### F-001: <short title>
- Classification: bug | feature-request | non-issue
- Priority: P0 | P1 | P2 | P3
- Confidence: high | medium | low
- Location: <path and symbol or lines>
- Evidence:
- Impact:
- Recommendation:
- Acceptance criteria:
```

Use stable, sequential finding IDs. Omit `Acceptance criteria` only for `non-issue`. Include exact commit URLs or file references when available.

If no actionable issue candidates exist, state that explicitly. Never create, edit, label, or comment on GitHub issues, and never approve, request changes on, or comment on the PR while using this skill.

## Quality gate

Before responding, verify that:

- Every actionable finding is supported by inspected evidence.
- Every actionable finding was introduced by the PR or blocks its stated acceptance criteria.
- The report distinguishes existing defects from missing capabilities.
- Multiple symptoms with one root cause are grouped.
- Completed or intentionally excluded work is not requested again.
- The PR number, URL, state, and base and head commit SHAs are recorded.
- Linked issue requirements and available CI signals were considered.
- Validation gaps and inaccessible files are disclosed.
