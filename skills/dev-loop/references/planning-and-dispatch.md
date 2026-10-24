## Resolve context

Pin repository, base/integration branch/SHA, selected Issues/Tasks, contracts/risk/non-goals, dependencies and waves, backend/version, unique branches/worktrees, run/revision/digest, connection/session references, `opencode-config` model policy and observed model/effort, grant/stop point, snapshot or PR/base/head, independent review, merge evidence, carrier/writer and next gate.

Choose `agent-core` when live repository instructions own Main/Task lifecycle; otherwise `generic-worktree`. Do not combine their mutation procedures or invent a new contract system. Retain unknown fields explicitly.

## Stages

### 1. Intent or merged review

For new capabilities use `@blueprint` to establish approved design/ACs. For integrated product findings use `@repo-review` on a merged immutable commit. Keep design decisions separate from actionable findings; no Issue creation is implicit.

### 2. Issue filing

Use `@issue-filer` only for the explicitly selected findings or approved design units. Goal approval is not publication or implementation approval. Retain Issue URLs and provenance; deduplicate without rewriting existing Issue content.

### 3. Planning

Use `@patch-plan` for selected filed Issues. Require a Workstream Contract: goal/source, stable ACs, invariants, non-goals, risk, human authority, design latitude and unresolved choices.

For an unexplained failure, first use `@debug-investigate` to produce evidence or a bounded investigation packet. Do not dispatch a guessed repair. Keep investigation and eventual repair within their respective grants.

Build the dependency/conflict graph (`parallel|ordered|combined|blocked`), isolate ownership and assign waves. A packet must state run/revision, allowed operations and exact stop point, plus resource ownership, coordinator cleanup grant/triggers and evidence-retention destination. Choose investigation-only, implementation/tests, or expressly authorized publication; never assume commit/push/Draft PR for every task.

In Agent Core, map each stream to one canonical numeric Issue-backed Task whose Issue carries the full contract. Main owns init, guarded Issue-start/resume, readiness evidence and multi-Task batch safety checks; launch exactly one Task Orchestrator per ready parallel-safe Task. Do not use raw Git mutations or generic SubAgents as substitutes.

In generic mode, require a committed root `/.worktrees/` entry and `git check-ignore .worktrees/` before any worktree. If absent, stop at separately authorized setup-PR instructions; its merge is human-executed. Refresh base after verification. Use only `<repository-root>/.worktrees/<workstream-id>`, unique branches and one executor per stream.

Present a complete OpenCode packet. Stop before dispatch unless dispatch itself was the explicitly selected stage with an already approved complete packet.

### 4. Dispatch

Use `@opencode-bridge dispatch` with the exact authorized packet and verified Main/Task/generic session. It saves dispatch intent, sends once, performs bounded receipt checks and returns without waiting for implementation completion. Leave OpenCode/tmux alive while work is outstanding; carry their cleanup owner and release trigger to collection.

Keep dispatch and execution distinct. If connection unavailable before any send, return a manual handoff. If delivery uncertain, do not offer a replacement send/manual submission until reconciled.
