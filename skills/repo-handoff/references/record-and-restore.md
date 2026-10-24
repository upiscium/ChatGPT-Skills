## Record workflow

1. Read the current carrier and live repository metadata. Pin the branch, base/head SHAs, PR state, checks, review decision, linked Issue, and relevant task state.
2. Compare with the previous marker. Expected SHA evolution is a new observation that invalidates affected old reviews/gates, not a conflict to erase. Unexpected carrier/workflow identity or divergent predecessor chains require conflict reconciliation; preserve both records rather than overwriting.
3. Serialize only durable facts and decisions. Exclude transient thoughts, secrets, speculative plans, and anything not needed to resume.
4. Announce the carrier and concise update before writing; show the full marker only for explicit repair, a user request, or `pending-write`. Automatic recording may use the connector; command-only workflows may emit an exact user-run update as `pending-write`. Never claim a record was saved when only a block was generated.
5. After a successful write, read the carrier back and verify the marker, sequence, timestamp, and referenced SHAs. Report the canonical URL and the resulting state.

When a workflow is read-only, it may write the narrow state marker only for newly verified material state or drift; unchanged observations are no-write. It must not modify product-facing Issue/PR content or review state. A failed write leaves the previous valid state untouched and returns a retry or manual-application path. Do not silently drop the checkpoint because the workflow's substantive result is read-only.

## Restore workflow

1. Resolve the repository and requested branch/PR/Issue, then fetch live metadata at an immutable commit.
2. Find the newest valid non-conflicting `codex-repo-state:v1` predecessor chain on the canonical carrier. Respect writer ownership and carrier transfers; report competing chains rather than selecting by timestamp. Legacy markers without event IDs need live reconstruction before a transition.
3. Revalidate every action-binding field against live state: repository, branch, Issue/PR number, PR state, base/head SHA, required checks, approvals, task lifecycle, and merge result.
4. Mark the record `fresh`, `stale`, `conflicted`, `incomplete`, or `reconstructed`. Never treat a stale or conflicted record as permission to write, merge, or dispatch work.
5. Fill missing live facts from the repository and Issues/PRs, clearly labeling reconstructed fields. Preserve the last durable decisions but do not resurrect a closed or superseded action.
6. Return a self-contained recovery packet with the current stage, workstream table, human decisions, blockers, evidence, next action, and the exact revalidation required before it can proceed.

If no marker exists on an existing canonical carrier, label the reconstruction and automatically save/read back its first marker. If no carrier exists, return `No durable repository handoff found` and a `bootstrap` packet; only creating a new carrier requires separate approval.

For delegated runs, restore run/revision/digest, exact session binding, operation grant and stop point. Verify the binding through a current read-only observation before sending. An unreachable session means `unknown`, not failed or safe to resend. Old v1 markers without these fields cannot prove authorization or absence of prior dispatch. Preserve executor-reported claims separately from Arca-verified evidence.

Restore the four-field approval explanation and exact decision source/scope too. Use `@human-review approval-brief` only when actually asking for an unresolved decision, including a proposed new carrier. Do not invoke its queue scan or writes just for formatting. Preserve denied/deferred/approved outcomes; `next` cannot reopen a denied action or supply missing scope. Reconstruct missing legacy explanation from evidence and ask only for a still-unresolved material decision, never blanket reapproval of a concrete prior grant.

Restore resource and cleanup records too. Reconcile pending/unknown cleanup actions against live identity before retrying; never recreate a cleaned runtime from an old session reference. Legacy resources without ownership evidence remain unknown until reconstructed. Report resources whose revisit trigger is now reached to the calling workflow; restore/audit/status alone do not terminate or delete them.

Ask monitoring and notifications belong to SwitchBoard. Arca and OpenCode do not install watchers, poll indefinitely or promise surveillance after a turn. A notification may trigger an authorized status check but is never approval, an answer or completion proof. Record a safe correlation reference and known delivery status; do not imply SwitchBoard is configured without evidence.
