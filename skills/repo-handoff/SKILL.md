---
name: repo-handoff
description: Automatically persist and restore verified GitHub work state on existing Issues or PRs, including OpenCode runs, instruction revisions, authority, evidence and next gates. Use at repository-work checkpoints and when resuming in another chat or agent without relying on conversation history.
---

# Persist or Restore Repository State

Use a single existing Issue/PR as the durable `codex-repo-state:v1` carrier. Use `@handover` for non-repository context; link rather than duplicate canonical repository evidence. Restore live state before consequential action, preserve prior grants and competing writers, and never invent a tracking Issue or authority.

## Read only what the operation needs

- **Status/restore/audit:** read [checkpoint policy and carrier resolution](references/checkpoint-policy.md); if a record must be reconstructed, also [record and restore](references/record-and-restore.md).
- **New or changed checkpoint:** read [checkpoint policy](references/checkpoint-policy.md) and [state contract](references/state-contract.md), then [record and restore](references/record-and-restore.md) when performing the write.
- **Delegated execution/dispatch or review:** read the applicable [state contract](references/state-contract.md) and existing [execution contract](references/execution-contract.md). Do not load the execution contract for a pure unchanged status query.
- **Output, recovery, gates and quality:** read [output and quality](references/output-and-quality.md) when preparing a standalone handoff/report.

## Critical checkpoint invariant

Do **not** write a fresh marker for unchanged reads, repeated Next/status or re-opening an identical snapshot. Record newly discovered failure, material dependency/base change, authority/next-action change and critical recovery transitions. **Record the exact dispatch intent before sending**; this remains mandatory; save/read back the exact intent and reconcile unknown delivery before retrying. Preserve changed evidence: do not suppress evidence to meet a token budget.

Record on an existing carrier only; protect concurrent writers, keep secrets/private logs out of public markers, read back any performed write and label unknown/pending-write honestly. A marker is neither approval nor permission for code, publishing, ready/merge, host changes or deletions.
