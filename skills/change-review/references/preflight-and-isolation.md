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
