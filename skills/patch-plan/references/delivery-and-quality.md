## Require scoped implementation delivery

Instruct the executor to:
1. Revalidate the grant and live repository gate before any mutation. With a stop/conditional gate, perform only the named admissible fallback.
2. Acquire the dedicated branch/worktree only through the selected backend. Preserve existing tasks and dirty work; do not recreate a Task to manufacture readiness.
3. Implement and validate only authorized scope. Report scope drift and human-owned choices instead of deciding them silently.
4. Deliver the exact frozen snapshot/manifest and test/environment evidence for independent `@change-review`. Do not create a commit just to obtain an immutable reference without commit authority.
5. Commit, push or create/prepare a Draft PR only when individually permitted and repository lifecycle gates are satisfied. A passed review is not publication permission.
6. If a PR is authorized and created, report real number, canonical URL, branch and head SHA, Issue/Task mapping, goal/AC coverage, non-goals, risk, validation and limitations. Never invent an identity.
7. If no publication was authorized, report `not-created; outside grant` and the reached prepublication stop. This is successful scoped delivery, not a missing-PR failure.
8. Return a run/revision/digest-bound executor report. The coordinator automatically records verified state through `@repo-handoff`; an executor may append only its own immutable report when authorized, never overwrite coordinator state. Preserve claims versus verified facts.
9. Stop at the exact granted boundary and hand resource identities/results to the cleanup owner. Do not run Ready/Merge, release, unassigned cleanup, host reconfiguration or Ask monitoring. The coordinator performs granted routine cleanup after evidence collection; the executor must not destroy its own evidence/transport before handoff.

For blocked publication, preserve permitted work and report exact blocker, branch/snapshot and next gate. A marker write failure is `pending-write`, not permission to change the carrier or claim durable recovery.

## Preserve boundaries

- Produce instructions only. This planning skill must not edit code, Issue/PR content, labels, branches, or commits; the resulting plan must assign implementation and PR creation to the later executor. The only permitted write is the automatic `codex-repo-state:v1` metadata marker on an existing carrier.
- In `agent-core` mode, never bypass Task lifecycle, worktree ownership, Task State, publication, integration, or cleanup guards with raw Git/GitHub commands or generic SubAgents.
- Do not silently expand scope beyond selected findings and issues.
- Do not make the external implementation packet or chat ledger the only continuation source; require the canonical Issue/PR state record or label the workstream `incomplete`.
- Do not treat an issue's suggested solution as verified architecture.
- Do not reopen, close, comment on, or modify stale or duplicate issues.
- Do not include credentials, private logs, personal data, or restricted security details.

## Quality gate

Before responding, verify that:

- Every implementation task traces to an active finding, issue, dependency, or acceptance criterion.
- The selected execution backend is evidence-backed, and only one backend's worktree and publication procedure is emitted.
- Every Agent Core workstream maps to one authoritative Issue-backed Task with complete readiness evidence; multi-Task execution uses the repository batch safety result before concurrent launch.
- Every constrained workstream carries a complete execution contract and requires live revalidation before code, PR, or merge actions that depend on it.
- Target repository, branch, and immutable commit SHA are recorded.
- Root causes and dependencies determine the work breakdown.
- Exact technical details are verified or clearly marked as discovery.
- Bugs and feature requests retain their distinct behavioral contracts.
- Tests cover success, failure, regression, and integration behavior where applicable.
- Compatibility, migration, rollout, observability, rollback, and documentation are addressed or explicitly unnecessary.
- The plan states what Codex must not change.
- Delivery matches the operation grant and stop point; actual PR number/URL are required only when PR creation was authorized and completed.
- Parallel workstreams have no unresolved dependencies or likely shared write boundaries.
- Every workstream has isolated ownership and bounded scope, with one separate eventual PR when publication is authorized.
- Agent Core worktrees are created only by its guarded lifecycle; generic worktrees are under the repository root's `.worktrees/` directory and require the committed root `.gitignore` entry `/.worktrees/` before creation.
- Ordered work is divided into waves and later-wave base SHAs are refreshed after prerequisite merges.
- OpenCode can execute the resolved packet without the review conversation or Arca's installed skills, without launching a separate Codex CLI.
- The plan identifies the durable carrier and records how a later chat restores each workstream and its dependency wave.
- The latest planning state was automatically saved and read back, or is explicitly marked `bootstrap`/`pending-write` with the recovery consequence.
