---
name: review-github-branch
description: Review a specific GitHub repository branch against a base branch or as a standalone snapshot, then produce evidence-backed Bug and Feature Request candidates without creating issues. Use when the user asks to inspect, assess, audit, or review branch contents, a branch diff, an implementation state, or a named commit on GitHub.
---

# Review a GitHub Branch

Review the requested code and return a structured report that another skill can safely convert into GitHub issues.

## Resolve the review target

1. Identify the repository, target branch, and base branch.
2. Use the repository's default branch as the base only when the user does not specify one.
3. Resolve both branches to commit SHAs and record them. Never treat a moving branch name as sufficient evidence.
4. If the target and base resolve to the same commit, clarify whether the user wants a full snapshot review.
5. Read applicable repository instructions and context, including `AGENTS.md`, contribution guidance, manifests, tests, CI configuration, and documentation relevant to the changed area.

## Inspect the implementation

1. Compare `base...target` and inventory changed files.
2. Inspect the complete surrounding implementation for every material change. Do not review patches in isolation.
3. Trace affected callers, data flow, state transitions, error paths, configuration, public interfaces, tests, and documentation.
4. Run relevant tests or static checks when a local checkout is available and execution is safe. Otherwise state that validation was source-only.
5. Compare behavior with explicit requirements, documentation, tests, API contracts, and established project patterns.

## Classify findings

Use one of these classifications:

- `bug`: An implementation can produce incorrect, unsafe, inconsistent, or contract-violating behavior.
- `feature-request`: A concrete capability required by the project's stated purpose or workflow is absent or materially incomplete.
- `non-issue`: A suggestion, preference, question, or weakly supported concern that should not become an issue yet.

Do not label personal style preferences as bugs. Do not invent product requirements to justify feature requests.

Assign:

- Priority: `P0` critical, `P1` high, `P2` medium, or `P3` low.
- Confidence: `high`, `medium`, or `low`.

Require a precise code path, contract, test result, log, or reproducible reasoning chain for every `bug`. Require a documented objective, user workflow, or architectural need for every `feature-request`. Downgrade unsupported claims to `non-issue`.

## Produce the review contract

Return Markdown with this structure:

```markdown
# Branch Review

## Review target
- Repository:
- Target branch:
- Target commit:
- Base branch:
- Base commit:
- Review mode: diff | snapshot

## Scope and validation
- Inspected:
- Checks run:
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

If no actionable issue candidates exist, state that explicitly. Never create, edit, label, or comment on GitHub issues while using this skill.

## Quality gate

Before responding, verify that:

- Every actionable finding is supported by inspected evidence.
- The report distinguishes existing defects from missing capabilities.
- Multiple symptoms with one root cause are grouped.
- Completed or intentionally excluded work is not requested again.
- The target and base commit SHAs are recorded.
- Validation gaps and inaccessible files are disclosed.
