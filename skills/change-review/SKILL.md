---
name: change-review
description: Independently review one frozen prepublication change or GitHub pull request against approved intent, acceptance criteria and evidence. Use before authorized publication or merge, individually or as an isolated concurrent review. Produce findings and a pinned recommendation without changing code, publishing, approving or merging.
---

# Review a Frozen Change or Pull Request

Review independently from the implementation run. Treat intent as authority, tests as evidence and code as the mechanism under review. Keep correction work separate from post-merge product review and future Issue generation. Never treat an executor's PASS as independent approval.

For an independent review through OpenCode, use `@opencode-reviewer` to list the target runtime's roles, inspect their modes and launch the exact reviewer in a fresh context. This is the preferred configured route; a startup failure is not a reason to silently reuse the implementer or claim no independent reviewer is available. This skill still owns the review contract and verdict. Verify actual reviewer/session/model binding before accepting its report.

Read [references/prepublication.md](references/prepublication.md) for a frozen, not-yet-published change. Read `@repo-handoff` and its execution contract for delegated run identities and evidence provenance.

Read [references/verification.md](references/verification.md) to judge test quality and completion claims. It is the shared evidence policy for planning, collection and review; copy relevant requirements into executor packets. Adaptation provenance is in [references/superpowers-notice.md](references/superpowers-notice.md).

## Explain any human approval request

When actually requesting a human decision or handing off a user-run action, use `@human-review approval-brief`. Include **今回やった内容**, **今回承認してほしい内容**, **承認によって影響がある範囲**, and **否認した場合の対応** in the same message. Name the action/actor, target/revision and reason for the gate; distinguish completed work from proposals. Use the brief only to explain a needed decision, without an additional queue scan/write or confirmation for already authorized work. Preserve the stated denial response at continuation.

## Resolve the target and mode

- `prepublication`: require the repository, approved Issue/Task contract, run/revision, exact base and frozen change manifest/digest. A PR is not required. Inspect tracked and untracked content included in scope, deletions, generated files, submodules and binary evidence. Stop when the snapshot cannot be reproduced or changes while being read.
- `pr`: require the repository and PR number/URL; fetch metadata, linked Issues, complete patch/files, comments, reviews and checks. Pin exact base/head SHAs and PR state.
- If the target is only a branch, ask for a PR or frozen prepublication scope instead of manufacturing a PR.

Read repository instructions, contribution guidance, contract provenance, relevant implementation, tests and CI. State source-only versus locally validated scope and all inaccessible evidence. A claimed test run must name the snapshot and environment it validates.

## Keep recommendations and permission separate

- Prepublication verdict: `ready-for-publication-review|changes-required|blocked`. The ready verdict means review evidence can support a separate publication decision, never commit/push/Draft PR authority.
- PR verdict: `ready|changes-required|blocked`. A ready verdict is not Ready/Merge permission.
- Do not carry prepublication readiness forward as PR merge readiness. After authorized publication, verify snapshot equivalence, target/base, PR scope, CI and required review gates; reuse unchanged evidence only when equivalence is demonstrated.
- Respect repository-owned frozen manifests, Task lifecycle and publication gates. Never publish, commit or mutate the index to obtain a reviewable snapshot.
- Material ambiguity or incomplete required evidence blocks a positive verdict. Green tests and matching agent opinions do not clear human-owned choices.

## Preserve batch isolation

Review exactly one PR or frozen change per invocation. In prepublication mode, apply the same isolation rules using its manifest/digest in place of a PR/head. Parallel reviewers return deltas to the coordinator; they do not race to update an aggregate marker.

- Record the review batch ID and workstream ID when supplied, the shared base SHA, and every sibling PR head SHA known at dispatch time.
- Pin all findings and the recommendation to this PR's exact head. Never let another PR's implementation or tests satisfy this PR's acceptance criteria.
- Use read-only source access or a dedicated isolated checkout. Concurrent reviewers must not share a writable checkout, branch, generated outputs, or test state.
- Register any newly created review checkout/runtime with `@workspace-cleanup`, including its owner, real identity, source/evidence recovery pointer and report-collection release trigger. Borrowed implementation resources stay outside the cleanup set.
- Inspect declared dependencies and likely overlap with sibling PRs. Classify the recommendation as `base-stable` when it remains valid after independent sibling merges, or `base-sensitive` when merge order, shared contracts, or overlap can invalidate it.
- Report cross-PR concerns to the batch coordinator for integration analysis. Do not expand this review into a combined multi-PR verdict.

## Establish the review contract

Before using the diff or tests to judge correctness:

1. Resolve authority in descending order: explicit human-approved decisions, the linked Issue or Task contract, versioned product and architecture contracts, then the PR description for non-conflicting clarification.
2. Reconstruct the PR goal, stable `AC-*` acceptance criteria, invariants, compatibility requirements, and out-of-scope behavior. Record provenance as `human-approved`, `source-confirmed`, or `derived-unconfirmed`.
3. Treat implementation and tests as claims about the contract, never as sources that redefine it.
4. Assign risk `low`, `medium`, or `high` relative to the approved stage and actually reachable effects. Material public API or architecture changes, in-scope security boundaries, destructive behavior, real data migrations, distributed consistency, and non-trivial compatibility decisions are normally high risk. A hypothetical out-of-scope production attack is not automatically high-risk for an isolated MOCK-only MVI.
5. Stop with `blocked` and an explicit human decision when intent is materially ambiguous or contradictory, the PR changes approved scope, or an **in-scope** design or risk trade-off belongs to project authority. Record production-deferred hardening without blocking approved isolated MVI acceptance. Do not choose the most plausible interpretation merely because implementation and tests agree with it.

## Review the implementation

Use `@human-review`'s `references/goal-alignment.md` at material changes and important PR milestones, and its `references/decision-sweep.md` before the substantive review final. Check silent human-owned effects in the actual diff, not just flagged gates or passing tests. At a significant scope/architecture milestone, also apply its `missed-decision-audit` mode to a bounded historical decision window in this independent context (or a fresh reviewer if this reviewer made the original decision). Keep that retrospective classification separate from this change's correctness verdict; a missing approval log alone is not a verified violation.

Review in this order:

1. Confirm that the approved intent is still appropriate for the current project contract; escalate rather than revise it when human authority is required.
2. Check the diff against every `AC-*` criterion, invariant, non-goal, and compatibility requirement.
3. Derive meaningful failure modes from that contract.
4. Map each criterion and failure mode to test evidence, identifying missing, weak, circular, or misleading tests.
5. Inspect the complete `base...head` PR implementation or frozen prepublication delta, plus surrounding callers, data flow, state transitions, error paths, public contracts, configuration, and documentation.
6. Check that the implementation is necessary and sufficient for the goal, without unrelated scope expansion or hidden behavior changes.
7. Consider CI and prior review signals, but verify their claims against the contract and code.
8. Attribute actionable findings only to the PR or to unmet acceptance criteria of its linked Issues.
9. List unrelated pre-existing problems only as post-merge review leads; do not use them to block this PR unless the change makes them materially worse.

Separate contract compliance from implementation quality in the report. A tidy implementation of the wrong behavior fails the first; compliance alone does not prove robustness. These are review dimensions, not a requirement for two agents or repeated review of every small task.

Give an independent reviewer the approved intent, frozen artifacts, relevant raw evidence and scope. Keep implementer conclusions and the coordinator's preferred verdict out of the initial instructions. Distinguish author claims from observations; inspect the code and evidence independently. Prior findings may be supplied for a scoped re-review.

For every proposed test, identify the realistic defect it would detect. Exact-value or source-text assertions are not substitutes for exercising behavior. After corrections, recheck changed behavior and its affected callers; preserve unaffected valid evidence and avoid restarting the entire review without a concrete risk or required gate.

## Classify findings

Use:

- `blocking`: Must be corrected before merge because the PR is incorrect, unsafe, incomplete against required scope, or lacks essential validation.
- `non-blocking`: Worth improving but safe to defer without violating the linked Issue or contract.
- `question`: A decision or missing fact prevents a reliable conclusion.
- `post-merge-lead`: A pre-existing or broader product concern for `@repo-review`, not a PR defect.

Assign priority `P0` through `P3` and confidence `high`, `medium`, or `low`. Require a precise code path, contract, test result, or reproducible reasoning chain. Do not report style preferences as findings.

## Produce the review contract

```markdown
# Change Review

## Target
- Repository:
- Review batch and workstream:
- Mode: prepublication | pr
- Run / instruction revision:
- Frozen manifest / digest (prepublication):
- Pull request: number | not-created
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

## Review recommendation
- Decision: ready-for-publication-review (prepublication) | ready (PR) | changes-required | blocked
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

## Next gate contract
- Target action: publication decision for frozen <digest> | human merge of PR #<number> at <SHA>
- Authorization: separate and not granted by this review
- Status: stop | conditional | allowed
- Unresolved prerequisite: none | <required correction, check, approval, or decision>
- Clearing authority: <fresh change-review, required CI, repository protection, or named human decision>
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

Keep existing `PR-*` finding IDs when reviewing a PR. Use stable `CHG-*` IDs for prepublication findings; preserve an explicit mapping after publication rather than losing finding history. Omit `Required change` only for questions and post-merge leads.

## Emit a durable checkpoint

Return a pinned state delta with mode, run/revision, manifest/digest or PR/base/head, criterion evidence, verdict, base sensitivity, human decisions and next gate. A batch reviewer returns it to the sole coordinator writer; standalone reviews use `@repo-handoff` to record a **new or materially changed** result on the existing canonical carrier without changing unrelated runs or pending coordinator action. Unchanged rechecks reuse the previous marker. Read back any marker written, or expose `bootstrap|pending-write`. No review submission, approval or protected publication checkpoint is implied.

After the full required report/evidence is saved outside the cleanup set, let the coordinator invoke `@workspace-cleanup` for eligible review-only runtimes, panes and worktrees. This housekeeping does not require a passing review verdict or merge. Preserve the sole uncommitted source snapshot and shared/active consumers; include cleanup results or retained owner/reason/revisit trigger in the delta. Do not end a reviewer before its result handoff is durable.

For low-risk PRs with no unresolved authority question, `summary-only` may be recommended. Use `focused-review` for medium or high risk and name the exact contract, file, or trade-off the human should inspect. Use `decision-required` whenever project direction, architecture, public API, migration, security boundary, compatibility policy, material scope, or risk acceptance is unresolved.

`ready` means ready only at the reviewed base and head. A base-sensitive PR remains conditional on the stated merge order or a fresh review after its base changes.

## Preserve boundaries

- Do not create Issues from PR or prepublication correction findings.
- Do not approve, request changes on, post non-marker comments, merge, close, or modify the PR unless the user explicitly requests that separate write action. The automatic `codex-repo-state:v1` marker update on an existing carrier is the sole recording exception.
- Do not treat `ready` as authorization to merge.
- Do not treat the checkpoint payload or its automatic save as approval or as a substitute for `@repo-handoff` live revalidation.
- A deadline, reviewer convergence, existing implementation plan, delegated ownership, or precedent from another PR must not weaken a `stop` or `conditional` merge gate.
- Send post-merge leads to `@repo-review` only after the implementation is merged.

## Quality gate

Verify that:

- Every blocking finding was introduced by the PR or violates a linked Issue's acceptance criteria.
- The review contract was established before judging tests or implementation.
- Every `AC-*` criterion traces to implementation and test evidence or is explicitly unverified.
- Green tests were not treated as proof when the tests encode a derived or incorrect interpretation.
- The complete mode-specific change and relevant surrounding code were inspected; incomplete evidence is not a positive verdict.
- Base/head SHAs or a complete frozen manifest/digest make the report reproducible; no changing working tree was approved.
- Concurrent review evidence is isolated per PR, and known sibling heads and base sensitivity are recorded.
- Required corrections and verification steps are executable.
- The mode-specific recommendation follows from independently inspected evidence.
- Human-owned choices are escalated with focused evidence and a safe fallback, not silently resolved.
- The next gate has all seven fields plus separate authorization, pinned to the frozen digest or reviewed head SHA.
- Broader product concerns remain separate from PR correction work.
- The report includes enough pinned state for a new chat to restore this review from the PR carrier.
