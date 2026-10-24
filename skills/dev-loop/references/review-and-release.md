### 6. Independent change review and correction

Use `@change-review` in prepublication or PR mode. Require the order Intent → ACs → Failure Model → Test Evidence → Implementation → Scope. Executor PASS is not independent evidence.

Use `@opencode-reviewer` for configured OpenCode independent-review execution, including security-focused roles with `@security-audit`. List effective roles in the target context, inspect their modes, and verify a fresh review session's actual role/model. A review-stage request authorizes its normal isolated startup; do not add a confirmation solely for starting the reviewer. Preserve repository-owned KUMIKI/KAGARI or Agent Core review gates. A failed default-agent fallback or an implementer's self-review does not satisfy this stage; record the precise startup blocker and compatible next action.

Read [references/review-feedback.md](review-feedback.md) when handling findings or reviewer suggestions. Verify each suggestion against the contract and current code before including it in a correction packet. Keep separate contract-compliance and code-quality conclusions without requiring a fresh agent for every small step. See [references/superpowers-notice.md](superpowers-notice.md) for the adapted source.

Before concurrent review, create a Review Batch Manifest: batch/workstream IDs, exact snapshots or PR/head, common base, contracts, siblings, dependencies, overlap and isolation. Bound concurrency; give each reviewer one snapshot and no shared writable checkout. Reviewers return deltas; only the coordinator writes aggregate state.

Preserve per-stream results and base sensitivity. Perform a coordinator cross-stream interference check; independent ready verdicts alone do not prove a wave jointly safe.

- Changes required: prepare a bounded correction packet on the same workstream, with findings, tests, existing PR if any, revised instruction identity and unchanged or newly approved operation grant. Dispatch at its next explicit checkpoint.
- Blocked: expose the exact decision/evidence gap, options and safe fallback.
- Prepublication ready: show `ready-for-publication-review` and the separate publication gate. Never commit/push/create PR merely because review passed.
- PR ready: show exact reviewed head/base, CI/approvals, risk/human decisions and proposed user-run merge handoff.

Low risk may be summary-only; medium/high risk identifies focused contract/files/trade-offs. High-risk human-owned decisions need explicit current-snapshot confirmation. Re-review changed heads or frozen snapshots; revalidate base-sensitive siblings after merges. Preserve unchanged valid evidence.

### 7. Authorized publication

Only enter on an exact publication grant for the reviewed frozen snapshot. Revalidate the digest, contract and repository lifecycle before delegating through OpenCode. Grant only named commit/push/Draft PR operations and stop at the stated point. Agent Core Main retains publication ownership.

Collect actual published identities; verify equivalence to the reviewed snapshot and current PR/CI gates through `@change-review`. Publication approval and prepublication review do not grant merge readiness.

### 8. Merge command and verification

Read [references/merge-command.md](merge-command.md). Generate commands only for the named PR with current PR-mode review and cleared gates. Never execute Ready/Merge or delegate them to OpenCode.

Present dependency-safe commands; defer later dependent blocks until earlier merges are verified. On subsequent `next`, verify live merged or queue state. A queue entry is not a merge. Record actual merge SHA and revalidate affected sibling assumptions.

### 9. Integrated review

Use `@repo-review` on the verified merged commit, checking product intent and cross-PR behavior. A new review does not authorize new Issues. Later waves need refreshed bases and dependency/batch revalidation.

After merge verification or explicit workstream retirement, run `@workspace-cleanup` through the live repository's designated finalization/cleanup owner. Remove eligible linked worktrees and owned runtime leftovers; retain branches/history by default. A missing or blocked repository cleanup API is a concrete retained item, not permission for a raw lifecycle bypass. Revisit previously retained resources at their next recorded trigger.
