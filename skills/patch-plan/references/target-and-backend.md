## Select the execution backend

Inspect repository instructions before prescribing branches, worktrees, agents, or publication commands.

- Use `agent-core` mode when the repository declares a guarded Task lifecycle, Task State, Main/Task Orchestrator boundaries, or stable repository-local lifecycle APIs such as `agent::task-start-from-issue`.
- Use `generic-worktree` mode only when no repository-owned orchestration lifecycle applies.
- Record the selected mode and the exact repository evidence or Agent Core version that selected it.
- In `agent-core` mode, repository instructions and guarded lifecycle APIs own Task creation, worktrees, commits, publication, integration, and cleanup. Do not emit raw Git or GitHub mutations as substitutes.
- Never assume that one Templates release has the same commands as another. Re-read the installed repository contract and use only its advertised stable APIs.

## Establish the target

1. Identify the repository, selected Issue URLs or numbers, originating `F-*` findings when available, and the implementation base branch or commit.
2. Resolve the implementation base to an immutable commit SHA.
3. Read repository instructions and re-inspect affected code, callers, tests, configuration, contracts, and relevant issues.
4. Confirm each finding and issue still applies. Mark it `active`, `already-fixed`, `stale`, `duplicate`, `closed`, `blocked`, or `out-of-scope`.
5. Ask only for missing decisions that can materially change scope, architecture, compatibility, migration, or rollout.

Require filed Issues for an execution-ready plan. If the user supplies findings without Issues, produce only a draft and mark Issue creation as a blocker.

Before emitting workstreams, restore any `codex-repo-state:v1` record on the selected Issue/PR with `@repo-handoff` and revalidate its base SHA. Include the chosen carrier, workflow ID, current state status, and the state-record update points in the plan. Persist and read back a **new or materially changed** planning snapshot; if its contract, plan, authority and next action are unchanged, reuse the existing marker without writing. If no carrier exists, return `bootstrap`; never invent a hidden tracking Issue. A missing marker on an existing carrier is bootstrapped automatically.

If the inputs contain `SEC-*` findings, vulnerability details, containment, credential rotation, or exploit-sensitive work, exclude those items and use `@security-plan`. Do not copy restricted security details into this plan.
