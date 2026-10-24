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
