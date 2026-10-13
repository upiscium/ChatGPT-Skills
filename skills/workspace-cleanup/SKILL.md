---
name: workspace-cleanup
description: Inventory and safely clean up workflow-owned OpenCode runtimes, RDC-launched processes, tmux panes and sessions, temporary files and Git worktrees after results are collected or work is completed. Use for explicit cleanup requests, post-review or post-merge housekeeping, failed-start leftovers, and retained-resource recovery. Verify ownership, inactivity and recoverability; preserve shared, active, dirty and unknown resources.
---

# Clean Up Owned Workspace Resources

Close the resource lifecycle as part of finishing work. A completed answer, idle terminal or merged PR does not by itself make every associated resource disposable. Run cleanup in the selected environment through its configured connection; do not assume a host, path or tool version.

Read [references/resources.md](references/resources.md) for resource records and eligibility, and [references/operations.md](references/operations.md) before executing cleanup. Use `@repo-handoff` for the existing repository carrier and `@opencode-bridge`'s transport rules for remote access. Resolve installed skills by name.

## Choose one operation

- `inventory`: inspect the selected host/repository/run and report resources, ownership and unknowns; no termination or deletion.
- `plan`: produce a concrete per-resource action/retain table with current evidence; no termination or deletion.
- `apply`: execute only the verified eligible actions in the selected scope, then re-read state. An explicit cleanup request includes this bounded plan-and-apply flow; do not require an extra confirmation for each ordinary eligible item.

At ordinary workflow completion/collection checkpoints, routine cleanup of that workflow's verified disposable resources is included in the authorized work. Carry this policy into the execution packet; the coordinator performs cleanup after collecting evidence, not a reviewer killing its own transport. An explicit preserve/no-cleanup instruction or repository lifecycle restriction takes precedence. Creating/editing this skill, a status-only request or an inventory request is not a request to clean a live host now.

This policy permits releasing owned temporary resources. It does not authorize discarding unique work, terminating someone else's session, deleting OpenCode history, deleting remote branches, removing shared services, or weakening repository gates. Ask only for the specific additional decision actually needed; complete unrelated eligible cleanup first.

## Register resources when creating them

Track resources that can outlive the creating call; do not create ledger entries for every already-exited read-only command.

1. Record run/workstream, creator and cleanup owner, resource kind, connection reference, purpose, planned cleanup trigger and recovery destination before creation.
2. Immediately bind the returned real identifiers and creation evidence: OpenCode session ID, process identity, tmux server/pane IDs, canonical worktree path/common Git directory/HEAD, and dependencies as applicable. Do not infer these from a label or RDC call handle.
3. Mark reused resources `borrowed` or `shared`, never owned just because this run used them. Only newly created, evidenced resources start as `owned`.
4. Persist the resource record through the existing workflow carrier or approved durable private ledger. Keep private locators out of public markers. If recording fails, retain the local receipt and report incomplete recovery; do not launch replacement resources merely to obtain a cleaner record.

Restore this ledger at the next checkpoint. For legacy leftovers, reconstruct ownership from creation/run records and live bindings. Age, name prefix, low CPU, shell idleness, a PR number or presence under `.worktrees` is not ownership proof. Keep unverified legacy candidates `unknown` and show the narrow evidence/decision needed.

## Evaluate each resource

Require all of the following for `eligible`:

- Scope and authority match the selected run/resource; current identity still matches creation evidence.
- It is exclusively owned, or every owner has released a genuinely shared resource through its designated owner.
- Its work is terminal, output has been collected and saved outside the deletion set, and no active request, Ask, tool, child process, attached user or sibling run still needs it.
- Recovery evidence is readable: pinned source/commits, reports and necessary logs or artifacts survive cleanup. No unpreserved tracked, untracked, ignored, staged, detached-HEAD or stash-only work will be lost.
- The resource-specific trigger is reached, and the live repository's cleanup/finalization gate permits the action.

Classify independently as `eligible`, `retained`, `blocked` or `unknown`. An idle reusable implementation session may be retained only with a concrete next use/owner and revisit event; do not default to keeping every session forever. A terminal reviewer runtime can be released after its report is durably collected even if the reviewed PR remains open. An implementation worktree normally remains until verified integration or explicit retirement; a disposable review/test worktree can be removed earlier when its pinned source and evidence are recoverable.

Cleanup does not imply cancellation. Preserve running, waiting and delivery-unknown work. If the user explicitly requests cancellation of a selected run, use its supported cancellation path under that separate authority, preserve partial evidence, then reevaluate cleanup only after quiescence is observed. A receipt timeout or missing connection is never permission to terminate.

## Apply in dependency order

1. Build the exact action/retain table, dependency set and current evidence snapshot. Save necessary results and a cleanup-intent record outside resources to be removed, and read it back. A supported durable private bootstrap ledger is enough when no Issue/PR carrier exists; do not create a tracking Issue or publicize raw logs.
2. Coordinate with the resource owner to prevent a new dispatch into the cleanup set. Use an existing lease/guard when available; otherwise revalidate immediately before each action. If ownership or activity cannot be reconciled, retain that resource. Do not claim atomic safety from a stale snapshot.
3. Gracefully release eligible owned OpenCode runtimes and RDC-launched auxiliary processes, preserving session history. Verify exit before removing their terminal or directory. Keep the RDC connector/agent, shared OpenCode servers and unrelated processes alive.
4. Remove only eligible owned tmux panes first. Remove a window/session only if its complete current membership and all effects, including linked windows, are within the released set. Never kill a tmux server or select by a name pattern.
5. From outside the target directory, remove eligible Git worktrees through the live repository's guarded API; in generic repositories use non-force `git worktree remove`. Leave branches by default. Use the operation reference for ignored files, detached commits, locks and repository metadata.
6. Remove only recorded disposable temporary artifacts whose evidence is already preserved. Do not sweep system temp directories, caches, logs or unrelated paths.
7. Re-read authoritative state for each action, record `cleaned|already-absent|retained|blocked|unknown`, and save the result. Keep partial progress; an action failure is not a reason to increase force or repeat the whole batch.

On timeout, preserve the exact action/identifier and reconcile whether it already completed before retrying. On changed identity, stop that action without substituting the new occupant. Run at most two bounded post-action observations per resource, each at most 15 seconds; leave unresolved state visible rather than starting a watcher.

## Completion hooks

- After reviewer collection: preserve the report, then release the owned reviewer runtime, terminal and disposable review worktree when eligible. A review may require changes while its completed review process is still safe to release.
- After implementation collection: release completed one-shot helpers/runtime when no continuation consumer needs them; retain the implementation worktree and any concrete continuation session until their own trigger is reached.
- After verified merge/retirement: invoke the repository's supported finalization/cleanup route and dispose of eligible worktree/runtime leftovers. Do not make branch deletion or source-history deletion a hidden consequence of merge.
- After failed startup: preserve the failure evidence and release only resources proved to have no submitted/in-flight work.
- At restore/next: reconcile retained resources when their recorded trigger is reached. Do not add background monitoring or start cleanup during a read-only status request.

Treat housekeeping as the tail of the current authorized checkpoint, not a new implementation wave. Report work completion and cleanup completion separately. Do not promise later automatic cleanup without an actual supported scheduler.

## Return a compact receipt

Report scope/connection, run and cleanup owner, action time, evidence/recovery references, record-save status, and one row per resource:

| Resource / exact safe reference | Ownership | Result / action | Evidence | Retention reason / owner / revisit trigger |
|---|---|---|---|---|

Summarize released processes, panes/sessions and worktrees. Report disk savings only if measured. For every retained/blocked/unknown item give a concrete next condition; do not hide it behind an overall success. Do not claim Adam or another host is clean from a partial inventory.
