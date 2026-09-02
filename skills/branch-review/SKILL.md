---
name: branch-review
description: Review one GitHub pull request against authoritative intent and acceptance contracts as an isolated, batch-safe quality gate, producing traceable findings, human decision escalations, base-sensitivity evidence, and a merge recommendation without changing the PR. Use individually or concurrently to validate Issue implementation, merge readiness, or PR regressions.
---

# Review a Pull Request

Review an issue-driven implementation before merge. Treat intent as authority, tests as evidence, and code as the mechanism under review. Keep PR correction work separate from post-merge product review and future Issue generation.

## Resolve the target

1. Require a repository and PR URL or number. If only a branch is supplied, ask for its PR.
2. Fetch the PR metadata, description, linked issues, changed files, complete patch, review state, comments, and available check status.
3. Record the PR number and URL, state, base and head branches, and immutable base and head SHAs.
4. Read repository instructions, contribution guidance, linked Issue acceptance criteria, manifests, tests, CI configuration, and relevant documentation.
5. State whether the review is source-only or includes locally run validation.

## Preserve batch isolation

Review exactly one PR per invocation, including when several independent PRs are reviewed concurrently.

- Record the review batch ID and workstream ID when supplied, the shared base SHA, and every sibling PR head SHA known at dispatch time.
- Pin all findings and the recommendation to this PR's exact head. Never let another PR's implementation or tests satisfy this PR's acceptance criteria.
- Use read-only source access or a dedicated isolated checkout. Concurrent reviewers must not share a writable checkout, branch, generated outputs, or test state.
- Inspect declared dependencies and likely overlap with sibling PRs. Classify the recommendation as `base-stable` when it remains valid after independent sibling merges, or `base-sensitive` when merge order, shared contracts, or overlap can invalidate it.
- Report cross-PR concerns to the batch coordinator for integration analysis. Do not expand this review into a combined multi-PR verdict.

## Establish the review contract

Before using the diff or tests to judge correctness:

1. Resolve authority in descending order: explicit human-approved decisions, the linked Issue or Task contract, versioned product and architecture contracts, then the PR description for non-conflicting clarification.
2. Reconstruct the PR goal, stable `AC-*` acceptance criteria, invariants, compatibility requirements, and out-of-scope behavior. Record provenance as `human-approved`, `source-confirmed`, or `derived-unconfirmed`.
3. Treat implementation and tests as claims about the contract, never as sources that redefine it.
4. Assign risk `low`, `medium`, or `high`. Public API or architecture changes, security boundaries, destructive behavior, data migrations, distributed consistency, and non-trivial compatibility decisions are normally high risk.
5. Stop with `blocked` and an explicit human decision when intent is materially ambiguous or contradictory, the PR changes approved scope, or a design or risk trade-off belongs to project authority. Do not choose the most plausible interpretation merely because implementation and tests agree with it.

## Review the implementation

Review in this order:

1. Confirm that the approved intent is still appropriate for the current project contract; escalate rather than revise it when human authority is required.
2. Check the diff against every `AC-*` criterion, invariant, non-goal, and compatibility requirement.
3. Derive meaningful failure modes from that contract.
4. Map each criterion and failure mode to test evidence, identifying missing, weak, circular, or misleading tests.
5. Inspect the complete `base...head` implementation and surrounding callers, data flow, state transitions, error paths, public contracts, configuration, and documentation.
6. Check that the implementation is necessary and sufficient for the goal, without unrelated scope expansion or hidden behavior changes.
7. Consider CI and prior review signals, but verify their claims against the contract and code.
8. Attribute actionable findings only to the PR or to unmet acceptance criteria of its linked Issues.
9. List unrelated pre-existing problems only as post-merge review leads; do not use them to block this PR unless the change makes them materially worse.

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
- Review batch and workstream:
- Pull request:
- Pull request URL:
- State:
- Base branch and commit:
- Head branch and commit:
- Linked issues:
- Sibling PR heads at dispatch:

## Scope and validation
- Authoritative intent:
- Contract provenance:
- Acceptance criteria and non-goals:
- Risk tier: low | medium | high
- Inspected:
- Checks run:
- Existing CI/review signals:
- Limitations:

## Merge recommendation
- Decision: ready | changes-required | blocked
- Rationale:
- Human review mode: summary-only | focused-review | decision-required
- Base sensitivity: base-stable | base-sensitive

## Decision interface
- Intent alignment: pass | fail | decision-needed
- Acceptance contract: <satisfied>/<total>; <partial or unverified criteria>
- Test evidence: strong | partial | insufficient
- Implementation and scope: pass | concern | fail
- Critical findings:
- Human decisions required:
- Focused review locations:
- Cross-PR concerns:

## Requirement traceability

| Criterion | Implementation evidence | Test evidence | Status |
|---|---|---|---|
| AC-001 | | | `satisfied` / `partial` / `violated` / `unverified` |

## Merge gate contract
- Target action: merge PR #<number> at head <SHA>
- Status: stop | conditional | allowed
- Unresolved prerequisite: none | <required correction, check, approval, or decision>
- Clearing authority: <fresh branch-review, required CI, repository protection, or named human decision>
- Admissible fallback: <correction packet, wait, or no merge>
- Evidence snapshot: <head SHA and checked signals>
- Reverify before action: <live head, base, checks, approvals, and mergeability>

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

For low-risk PRs with no unresolved authority question, `summary-only` may be recommended. Use `focused-review` for medium or high risk and name the exact contract, file, or trade-off the human should inspect. Use `decision-required` whenever project direction, architecture, public API, migration, security boundary, compatibility policy, material scope, or risk acceptance is unresolved.

`ready` means ready only at the reviewed base and head. A base-sensitive PR remains conditional on the stated merge order or a fresh review after its base changes.

## Preserve boundaries

- Do not create Issues from PR findings.
- Do not approve, request changes on, comment on, merge, close, or modify the PR unless the user explicitly requests that separate write action.
- Do not treat `ready` as authorization to merge.
- A deadline, reviewer convergence, existing implementation plan, delegated ownership, or precedent from another PR must not weaken a `stop` or `conditional` merge gate.
- Send post-merge leads to `@repo-review` only after the implementation is merged.

## Quality gate

Verify that:

- Every blocking finding was introduced by the PR or violates a linked Issue's acceptance criteria.
- The review contract was established before judging tests or implementation.
- Every `AC-*` criterion traces to implementation and test evidence or is explicitly unverified.
- Green tests were not treated as proof when the tests encode a derived or incorrect interpretation.
- The complete PR and relevant surrounding code were inspected.
- Base and head SHAs make the report reproducible.
- Concurrent review evidence is isolated per PR, and known sibling heads and base sensitivity are recorded.
- Required corrections and verification steps are executable.
- The merge recommendation follows from the findings.
- Human-owned choices are escalated with focused evidence and a safe fallback, not silently resolved.
- The merge gate contract contains all seven fields and remains pinned to the reviewed head SHA.
- Broader product concerns remain separate from PR correction work.
