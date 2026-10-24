## Output format

For `restore`, `bootstrap`, or `audit`, return:

```markdown
# Repository Continuation State
- Repository:
- Canonical carrier:
- State status: `fresh` | `stale` | `conflicted` | `incomplete` | `reconstructed`
- Recording: `automatic|manual|none` / `saved|pending-write|bootstrap`
- Observed commit:
- Observed at:

## Current stage

## Workstreams
| Workstream | Issue / Task | Branch | PR / Head SHA | Status | Dependency | Next action |
|---|---|---|---|---|---|---|

## Human decisions and gates
<!-- preserve target action, status, prerequisite, authority, fallback, evidence and revalidation; actual approval requests include completed work, requested action, affected scope and denial handling -->

## Next action
- Action:
- Authorization:
- Prerequisite:
- Reverify immediately before acting:

## Evidence and drift
```

For `record`, return the intended marker and human summary before writing, then report `saved` or `pending-write` with the carrier URL and read-back verification. Automatic workflow checkpoints may write and verify without a separate prompt, but must never invent facts; restore and pin live state first. If the user asks only to continue, restore first and then automatically record the resulting checkpoint.

## Integrate with repository workflows

- `@dev-loop` should restore before acting on `next` and automatically record each changed substantive checkpoint, including newly blocked and terminal states; unchanged status is read-only.
- `@repo-status` should consume this record and flag missing, stale, or conflicting state.
- `@change-review`, `@repo-review`, `@patch-plan`, `@opencode-bridge`, `@repo-status`, and `@human-review` automatically record their owned fields or return deltas to the coordinator; no-code/no-merge/command-only boundaries remain in force.
- `@human-review review-queue` should read the durable decisions and list only the still-open human gates. Its `approval-brief` formatter alone does not scan or write state; the calling workflow owns any authorized recording.
- `@workspace-cleanup` records exact resource intent/results or returns a delta to the designated coordinator; its live ownership, recovery and repository gates remain separate from recording.
- `@handover` may link to the canonical carrier instead of duplicating GitHub-backed state.

## Preserve boundaries

- Do not modify code, branches, Tasks, Issue/PR content, labels, or non-marker comments during restore/bootstrap/audit. The automatic marked `codex-repo-state:v1` update on an existing carrier remains permitted and must be read back.
- Do not create a carrier, edit a PR body, change review/merge state, or post any non-marker comment without explicit authorization. The marked `codex-repo-state:v1` metadata update is the automatic-recording exception on an existing carrier.
- Do not turn a state record into an approval; human decisions, review gates, CI, branch protection, and merge authority remain separate.
- Do not expose security findings, credentials, personal data, or private logs; route restricted content to the security workflow.
- Do not infer that a PR is merged, a task is complete, or a decision is approved from an old marker alone.

## Quality gate

Before responding, verify that:

- the record is tied to a canonical Issue/PR and immutable snapshot;
- every workstream and gate has an explicit status and evidence or is labeled `unknown`;
- stale, conflicting, and reconstructed state is visible rather than silently repaired;
- the next action is subordinate to its prerequisite, authority, and live revalidation;
- no business or repository action write was performed without the required authorization; automatic marker writes are limited to the existing carrier and are read back;
- another chat can resume from the carrier URL and the returned packet without the original transcript.
