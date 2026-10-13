# Resource records and eligibility

Attach resource records to the existing run. Keep a resolvable private locator map when public state uses opaque references. Record facts before creation and bind actual identifiers immediately afterward; recording alone does not grant authority.

## Minimal record

```json
{
  "resource_id": "<unique resource ID>",
  "run_id": "<owning run>",
  "kind": "opencode-runtime|opencode-session|rdc-process|tmux-pane|tmux-session|git-worktree|temp-artifact",
  "connection_ref": "<safe configured reference>",
  "locator_ref": "<resolvable private locator>",
  "ownership": "owned|borrowed|shared|unknown",
  "created_by": "<coordinator or executor>",
  "cleanup_owner": "<single designated owner>",
  "creation_evidence_ref": "<creation receipt or unknown>",
  "identity_evidence_ref": "<current immutable identity evidence or unknown>",
  "depends_on": [],
  "consumers": [],
  "release_trigger": "<report saved, merge verified, or explicit retirement>",
  "recovery_ref": "<read-back durable evidence outside cleanup set or unknown>",
  "cleanup_authority_ref": "<workflow housekeeping grant or explicit request>",
  "state": "active|eligible|cleaned|already-absent|retained|blocked|unknown",
  "retention_reason": "none",
  "revisit_trigger": "<next concrete workflow event or none>",
  "last_verified_at": "<UTC or unknown>"
}
```

Use the existing repository's record shape if it already provides equivalent fields. Add this information to older v1 markers without rewriting history. Missing creation or cleanup fields mean `unknown`, not disposable. Preserve cleanup tombstones so later chats do not recreate an intentionally removed resource from an old session reference.

## Private identity details

| Kind | Bind and revalidate |
|---|---|
| OpenCode session/runtime | Actual session ID; server/process identity; effective directory; associated requests and child sessions; whether runtime serves other sessions; terminal status and report location |
| OS/RDC-launched process | Host/boot identity, PID plus process start identity, executable/cwd and owner; related child processes. Keep RDC's async call ID separate from the OS PID. A reused PID fails identity matching. |
| tmux | Server socket and server lifetime identity, exact session/window/pane IDs, pane process identity, containing and linked sessions/windows, clients and unrelated panes. A name or pane number without its server identity is insufficient. |
| Git worktree | Canonical path, owning common Git directory, registration entry, branch/ref and HEAD, main/linked status, locks, consumers, recovery ref and required repository finalization evidence |
| Temporary artifact | Canonical path under the recorded owned directory, creation manifest/type, sole owner, needed output hashes and preserved copies; reject replaced paths, symlink escapes and unexpected mounts |

Do not expose command lines containing credentials, transcripts, private paths or host coordinates in public markers. Retain enough private mapping for a subsequent authorized operator to revalidate the same object.

## Resource-specific decisions

| Situation | Decision |
|---|---|
| Completed owned reviewer; report saved; no active tools/children/consumers | Release its runtime and owned pane; keep session history and pinned evidence |
| Completed one-shot helper with output preserved | Release it; a planned possible future task is not a reason to retain an otherwise disposable helper |
| Owned tmux pane in a shared session | Consider only that pane; preserve siblings and linked windows; do not infer ownership of parents |
| Shared OpenCode server, user-attached pane or reused main session | Retain while any consumer remains; only its designated owner can release the fully reconciled shared resource |
| Clean implementation worktree after verified integration/retirement, source retained and gate clear | Remove using supported non-force/guarded route |
| Disposable clean review/test worktree with pinned recoverable source and saved report | Remove after collection even if the main implementation is not merged |
| Dirty/untracked/unknown ignored files, pending task stash, unique detached commit or locked worktree | Retain; preserve/resolve data and the relevant gate before reconsidering |
| Complete-looking output but unknown delivery, live children, pending Ask or disconnected host | Retain as active/unknown; reconnect and reconcile without duplicate work |
| Legacy artifact lacks reliable provenance | Inventory only until ownership/recovery is reconstructed or the user resolves the exact resource decision |
| Exact recorded resource is confirmed absent | Record `already-absent`; do not remove a replacement with a similar name/path |

Cleanup readiness is per resource, not per PR verdict. Do not wait for a PASS verdict to release a completed reviewer whose findings are saved. Do not remove the sole uncommitted prepublication snapshot just because review passed. A copied summary is insufficient when raw evidence or the full report is required for continuation.

Use an existing durable private artifact destination when no public carrier is appropriate. Save and read back necessary content and exact recovery pointers before closing a sole terminal copy or deleting files. If preservation cannot be verified, retain the resource and identify that concrete blocker. The retained copy must not itself be inside the cleanup dependency set.
