## Choose the operation

Infer one operation from the request and state it explicitly:

- `restore`: read the latest durable record and reconstruct the current stage, workstreams, gates, decisions, and next action.
- `record`: explicitly repair, backfill, or inspect a checkpoint; routine workflow checkpoints use automatic recording instead.
- `bootstrap`: reconstruct state when no durable record exists, without pretending it has been saved.
- `audit`: compare recorded and live facts, reporting drift without substantive actions; record only actionable drift or a new material finding under the metadata policy.

Restore, bootstrap, and audit do not change product, Issue, PR, branch, or task content. Automatic state recording is a narrowly-scoped metadata write to an already selected canonical carrier and applies only when verified material state has changed. It does not require a separate user prompt, and `next` does not authorize any business or repository action beyond the one previously announced. Creating a new carrier or changing Issue/PR content, labels, status, reviewers, branches, code, or merge state still requires the responsible workflow's explicit authorization.

### Automatic checkpoint policy

Record the latest verified state only when a new fact changes what the next actor may or must do, or when a recoverability-critical boundary is reached. Examples:

- first actionable carrier selection, a new or revised plan, authority decision, blocking prerequisite, or material dependency/base change;
- dispatch-intent recording **before** send, acknowledged/uncertain delivery, run collection, changed review outcome, publication identity and merge verification;
- a newly discovered failure, material scope change, cleanup result, or handoff that changes the next action.

Do **not** write a fresh marker for unchanged reads, duplicate `next`/status responses, a re-opened but identical snapshot, or a failed read with no new actionable evidence. `bootstrap` without an existing carrier is an in-chat reconstruction, not a write. Reuse the valid prior event ID and explicitly say "unchanged" when relevant. If a new observation exposes meaningful drift, write its delta; do not suppress evidence to meet a token budget. Do not force a full repository rescan just to decide whether the marker changed.

`@btw` side questions and non-repository conversations are exempt; neither changes the main workflow nor updates its marker.

Use the existing canonical Issue or PR and update only neutral continuation metadata and its human summary. Prefer append-only successor records with event and predecessor IDs. Edit only an exclusively owned marker with a supported compare-and-swap guard; never use blind last-writer-wins. Read back the exact event and report its sequence, timestamp and URL. On an existing unambiguous carrier, the first marker is also automatic and needs no additional recording approval. Without a carrier, return `bootstrap`; never create a hidden tracking Issue. On write failure, return the exact sanitized marker as `pending-write` and do not claim durable recovery.

Automatic recording is not approval. It must never execute or imply Issue creation, PR creation, code publication, Ready/Merge/Close, release, security disclosure, or risk acceptance. Record resource ownership and cleanup outcomes, but let `@workspace-cleanup` act only under the calling workflow's housekeeping grant or explicit cleanup request; a marker alone does not authorize deletion.

An ordinary progress comment is not a protected repository publication checkpoint, Task State mutation, contract approval or readiness attestation. If repository policy restricts the marker itself, obey it and return `pending-write`; never relabel a protected action as metadata. `audit` does no substantive actions but may record its observation under this policy.

## Own the record without clobbering concurrent work

- Nominate one coordinator writer per workflow. Concurrent review workers return pinned deltas to that coordinator, not shared-marker writes. A standalone observer preserves unrelated runs, authority and pending next actions.
- Executors may append immutable run-scoped `codex-executor-report:v1` reports only when that report write is authorized. They must not edit the coordinator marker or mark their own output independently verified.
- Read immediately before writing; include a unique event ID and predecessor ID. Divergent successors, duplicate sequence numbers or conflicting writers are `conflicted`, not ordered by timestamp alone. Stop affected write-producing transitions and reconcile instead of overwriting either record.
- Before external dispatch, save and read back the exact run's dispatch intent. If this cannot be established, do not send automatically. A manual packet may be returned as not sent and not durable.
- Reconcile an uncertain event/request ID before retrying any write or dispatch. Network failure does not prove the original action did not happen.
- Preserve predecessor/successor carrier links when moving Issue → PR → Issue. Store only safe opaque connection/session references in public records, never host coordinates, private paths, tokens or terminal transcripts.

Read [references/execution-contract.md](execution-contract.md) for planning, dispatch, collection or review of delegated work. This shared format supplements, and never replaces, repository-owned lifecycle contracts.

For workflows creating persistent processes, tmux resources or worktrees, retain `@workspace-cleanup`'s resource ledger: creator/owner, actual identity evidence, safe locator reference, consumers, recovery pointer, release trigger and cleanup disposition. Reused resources stay borrowed/shared. Persist cleanup intent and results outside the removal set; retain cleaned/already-absent tombstones. Private resource locators and raw logs stay in the approved resolvable private record.

## Locate the canonical carrier

Use one canonical carrier for each workstream and identify it in the output:

1. An existing implementation Issue while work is planned or being executed.
2. The active PR for the same workstream while it is in review or awaiting merge.
3. The linked Issue or designated tracking Issue after merge and during integrated review.
4. If no carrier exists, produce a bootstrap block and ask the user to select an existing Issue/PR or explicitly authorize creating one. Do not invent a hidden tracking Issue.

For a parallel wave, keep per-workstream records on their own Issue/PR carriers and optionally maintain one aggregate record only when a parent/tracking Issue already exists or its creation is explicitly approved. Do not use an unrelated PR or Issue as an aggregate carrier.

Keep a valid predecessor chain and a monotonically increasing sequence per carrier; identify the newest non-conflicting record, not merely the newest comment. Never overwrite an unmarked human comment. Do not place credentials, tokens, private logs, or full conversation transcripts in a public record.
