## Ledger

Report concise common fields and one row per stream:

| Workstream | Issue/Task | Run/revision | Grant/stop | Delivery/execution | Snapshot or PR/head | Review | Next gate |
|---|---|---|---|---|---|---|---|

Also include stage/backend/base, active wave, carrier/save status, focused human decisions and the exact next action with target, `stop|conditional|allowed`, prerequisite, clearing authority, fallback, evidence and revalidation. Preserve these fields even if summarizing.

Include cleanup owner/status, resources actually released, and each retained/blocked/unknown resource's reason and revisit trigger. A completed implementation is not proof that cleanup completed.

## Boundaries and quality gate

- No implementation inside Arca; no unbounded loop or Ask monitoring. No separate Codex CLI.
- No raw lifecycle bypass, shared writable checkout, undisclosed task, unauthorized publication, Ready/Merge or security disclosure. Routine owned-resource cleanup is allowed only through `@workspace-cleanup` and the live repository gates; no force deletion or disposal of unique work.
- Source-only inspection, status and notifications never imply a new business write. Neutral marker updates are the narrow recording exception.
- Keep correction findings in the same change; broader leads go to post-merge repo-review. Route restricted SEC work through security skills.
- Every transition must be run/snapshot-bound, evidence-backed, within authority and durable or explicitly incomplete. A new chat must recover routing without recovering permissions from prose.
