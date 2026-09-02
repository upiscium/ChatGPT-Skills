---
name: repo-review
description: Review the merged state of a GitHub repository against documented product intent and produce evidence-backed Bug and Feature Request candidates plus explicit human decision requests, without creating issues. Use after pull requests are merged, or for a repository-wide product, architecture, implementation, integration, test, documentation, or completeness review of a default branch or specified merged commit.
---

# Review the Merged Repository

Assess the integrated product against authoritative intent after merge and produce structured candidates that `@issue-filer` can safely turn into the next Issues. Treat tests as evidence of behavior, never as the source of product requirements.

## Resolve the snapshot

1. Identify the repository and review branch or commit. Default to the repository's default branch only when unspecified.
2. Resolve the reviewed state to an immutable commit SHA.
3. Record recently merged PRs when they define the requested review window, but inspect the integrated repository rather than replaying PR reviews.
4. Read repository instructions, product goals, architecture documents, roadmaps, issue history, manifests, tests, CI configuration, and user-facing documentation.
5. Define the review scope and disclose inaccessible components or validation limitations.

## Establish review authority

1. Derive the product intent from, in descending authority: explicit human-approved decisions for this review, versioned product or architecture contracts, documented supported workflows, and accepted Issue or PR outcomes.
2. Record stable `O-*` objectives and the behaviors, invariants, compatibility requirements, and non-goals needed to satisfy them.
3. Mark each objective or contract as `confirmed` when directly supported by an authoritative source or `derived` when reconstructed from multiple sources. Cite that provenance.
4. Do not infer requirements from implementation structure, existing tests, or what would merely improve the repository.
5. When ambiguity, contradiction, architecture direction, scope choice, compatibility policy, or risk acceptance would materially change the finding, create a `D-*` human decision request instead of silently choosing or filing speculative work.

## Inspect the integrated product

1. Inventory major components, public interfaces, workflows, persistence boundaries, integrations, deployment configuration, tests, and documentation.
2. Trace important end-to-end user and operator workflows across component boundaries.
3. For each reviewed objective, define the observable acceptance contract before inspecting whether tests pass.
4. Identify failure modes that could violate the contract, then map each objective or invariant to implementation evidence and test evidence.
5. Compare implemented behavior with the contract and distinguish `satisfied`, `partial`, `violated`, `unverified`, and `decision-needed` outcomes.
6. Inspect integration gaps, regressions, inconsistent invariants, missing failure handling, obsolete paths, incomplete capabilities, and unintended scope.
7. Run appropriate tests and static checks when a local checkout is available and safe.
8. Check open and closed Issues and recent PRs so completed, accepted, duplicate, or intentionally excluded work is not proposed again.

## Classify findings

Use:

- `bug`: The merged product can produce incorrect, unsafe, inconsistent, regressive, or contract-violating behavior.
- `feature-request`: A concrete capability required by a documented objective or validated workflow is absent or materially incomplete.
- `non-issue`: A preference, speculative idea, question, duplicate, accepted tradeoff, or unsupported concern.

Assign priority `P0` through `P3` and confidence `high`, `medium`, or `low`.

Require a precise code path, contract, test result, log, or reproducible reasoning chain for every bug. Require a documented objective, user workflow, architectural dependency, or explicitly validated need for every feature request. Do not invent roadmap requirements.

Keep `D-*` decision requests outside `F-*` findings. They identify authority that only a human should exercise; they are not Issue candidates until resolved.

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
- Intent sources and authority:
- Product areas inspected:
- Workflows traced:
- Checks run:
- Existing issues searched:
- Limitations:

## Decision summary
- Product intent alignment: aligned | partial | violated | decision-needed
- Contract coverage:
- Test evidence: strong | partial | insufficient | not-run
- Highest risk areas:
- Human attention required:

## Objective traceability

| Objective / contract | Authority | Implementation evidence | Test evidence | Status |
|---|---|---|---|---|
| O-001 / AC-001 | confirmed \| derived | | | satisfied \| partial \| violated \| unverified \| decision-needed |

## Human decisions required

### D-001: <decision>
- Why human authority is required:
- Affected objectives or scope:
- Options and trade-offs:
- Safe fallback while unresolved:

## Findings

### F-001: <title>
- Classification: bug | feature-request | non-issue
- Priority: P0 | P1 | P2 | P3
- Confidence: high | medium | low
- Objective or contract:
- Location:
- Observed gap:
- Implementation evidence:
- Test evidence:
- Impact:
- Recommendation:
- Acceptance criteria:
- Downstream constraint: none | <action that must not proceed before a stated prerequisite>
- Clearing authority and admissible fallback: none | <who or what clears it; what remains safe meanwhile>
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
- Every actionable finding traces to a confirmed objective or clearly labels derived authority.
- Findings reflect integrated behavior, not patch aesthetics.
- Tests support or weaken a claim but never create its requirement.
- Existing Issues and completed work were checked for duplication.
- Multiple symptoms with one root cause are grouped.
- Bugs and missing capabilities are distinguished.
- Material direction, architecture, compatibility, scope, or risk choices are isolated as `D-*` requests rather than decided implicitly.
- Acceptance criteria are testable and outcome-oriented.
- Any action-binding finding preserves its prerequisite, clearing authority, and safe fallback instead of reducing them to advisory prose.
- The reviewed commit SHA and validation gaps are recorded.
