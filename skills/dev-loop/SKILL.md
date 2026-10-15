---
name: dev-loop
description: Coordinate Arca planning, authorized OpenCode delegation, independent change review and human-executed merge through one verified checkpoint at a time. Use to start, resume or advance parallel Issue workstreams with next, collect a run, or generate only guarded Ready/Merge commands. Ask monitoring belongs to SwitchBoard, not this skill.
---

# Coordinate the Development Loop

Own orchestration and verification, not implementation or continuous monitoring. Use `@opencode-bridge` for authorized OpenCode transport. Keep a complete manual packet fallback when the selected connection is unavailable and no send is uncertain.

## Explain any human approval request

When actually requesting a human decision or handing off a user-run action, use `@human-review approval-brief`. Include **今回やった内容**, **今回承認してほしい内容**, **承認によって影響がある範囲**, and **否認した場合の対応** in the same message. Name the action/actor, target/revision and reason for the gate; distinguish completed work from proposals. Use the brief only to explain a needed decision, without an additional queue scan/write or confirmation for already authorized work. Preserve the stated denial response at continuation.

## Select the entrypoint

- Normal loop: restore the current workstream and perform only the requested or previously announced stage.
- `merge-command-only`: for “このPRのマージコマンドだけ出して” or the former `@pr-merge` intent, read [references/merge-command.md](references/merge-command.md) and handle only the named PR. Do not start a repository review, create Issues or initiate a whole loop.
- Status/collection request: inspect the existing run; do not launch or resume work implicitly.
- Cleanup request: use `@workspace-cleanup` for the selected run/repository/host scope; inventory first, apply only eligible actions, and preserve unrelated work.

Read `@repo-handoff` and its execution-contract reference before planning or dispatch. Use `@change-review` directly; the legacy `@branch-review` is an explicit-only compatibility alias.

Use the model, reasoning effort and variant configured by OpenCode for authorized launches and subsequent execution turns. Read `@opencode-bridge`'s `references/model-selection.md`, carry `model_policy: opencode-config`, omit explicit model/effort overrides and record runtime metadata when exposed. Do not replay older pinned-model requirements, interrupt busy sessions or alter selection during status/collection.

## Separate authority

Human: goals, material architecture/scope/compatibility/security decisions, risk acceptance, publication grants and final Ready/Merge actions.
Arca: recover contracts, prepare packets, coordinate authorized dispatch, collect evidence, independently review and expose decisions.
OpenCode: implement and validate only inside the current run grant through repository-owned APIs. Never launch standalone Codex CLI inside OpenCode.
SwitchBoard: ongoing Ask detection and notifications. Arca/OpenCode have no Ask watcher/polling responsibility; a notice is not approval or a resolved answer. Do not claim SwitchBoard setup or delivery without evidence.

An implementation and its tests cannot jointly redefine ambiguous intent. Require human-authored/approved goals and stable AC IDs. Escalate material unknowns instead of selecting the easiest interpretation. Human ownership also includes priority and resource allocation; Arca must proactively detect consequential choices, not merely relay executor questions.

Apply `@human-review`'s `references/goal-alignment.md` at new workstreams, material changes and important PR/release milestones. Before each substantive turn's final, apply its `references/decision-sweep.md` to newly seen contracts, actual scope/resources, evidence and next action even without `NEEDS_DECISION`. Reuse a current nested sweep; unchanged pure observations are exempt. At significant scope/architecture milestones, route a bounded retrospective `missed-decision-audit` to a fresh reviewer context and collect its delta separately from implementation verification. Keep SwitchBoard/MUSUBI monitoring ownership and existing stage/operation grants.

## Checkpoint semantics

Complete at most one substantive stage per response, record it and stop. A stage may contain the explicitly selected independent batch, never undisclosed later waves.

- `next`, `continue` or `Accept` applies only to the exact previously explained action, target, revision and grant. Present the four-field approval brief when this is a request for authority; a bare next/approve prompt has no implicit scope. Preserve concrete prior authorization and scoped denials. Re-read live evidence and repository gates immediately before acting.
- A prior plan/ledger, readiness result or notification is not executable authority. If identity/scope changes, show the new state and request the necessary decision.
- While a run is sent, running, waiting or delivery-unknown, inspect/reconcile it; never launch a duplicate.
- Next after a command handoff verifies user execution; it never performs Ready/Merge.
- Preserve completed independent work when another stream is blocked. Do not run continuously through multiple stages.

Restore canonical state at entry and record each substantive checkpoint automatically through `@repo-handoff`. Existing carriers bootstrap automatically. No carrier means `bootstrap`, no hidden tracking Issue. Save/read back dispatch intent before sending. Recording failures are visible, never implied saved.

Own routine resource cleanup as the tail of the current checkpoint through `@workspace-cleanup`. Register newly created persistent resources with real identities, cleanup owner and trigger; mark reused resources borrowed/shared. After result collection, verified merge/retirement or a proved-unused failed start, release eligible owned resources without another confirmation. Keep execution completion and cleanup completion separate. Status-only and merge-command-only modes report cleanup candidates without performing cleanup.

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

### 5. Execution status and collection

On the next requested checkpoint use bridge status/collect. Preserve sent, acknowledged, running, waiting-question, reported-complete and unknown separately. Routine contract-resolvable questions may be answered within the grant through a separately authorized reply; human-owned choices go to `@human-review`.

Collect run-correlated snapshot/manifest, validation evidence, actual operations and stop point. PR absence is expected for prepublication grants, not automatic failure. If publication was authorized/required, verify the actual PR number, URL, branch and SHA; never invent one. Match Issue/Task/backend lifecycle and approved scope.

After durable collection, release eligible completed runtimes/helpers and report retained continuation sessions/worktrees with owner and next use. Do not delete the sole frozen prepublication artifact or a worktree still needed by a sibling/reviewer. Apply `@workspace-cleanup` rather than leaving every completed process alive by default.

Apply `@change-review`'s `references/verification.md`: report exactly which behavior/check passed on which snapshot, and retain blocked, unrun or timed-out checks. Collection may finish while independent verification is still pending; do not turn an executor report into a verified completion claim.

### 6. Independent change review and correction

Use `@change-review` in prepublication or PR mode. Require the order Intent → ACs → Failure Model → Test Evidence → Implementation → Scope. Executor PASS is not independent evidence.

Use `@opencode-reviewer` for configured OpenCode independent-review execution, including security-focused roles with `@security-audit`. List effective roles in the target context, inspect their modes, and verify a fresh review session's actual role/model. A review-stage request authorizes its normal isolated startup; do not add a confirmation solely for starting the reviewer. Preserve repository-owned KUMIKI/KAGARI or Agent Core review gates. A failed default-agent fallback or an implementer's self-review does not satisfy this stage; record the precise startup blocker and compatible next action.

Read [references/review-feedback.md](references/review-feedback.md) when handling findings or reviewer suggestions. Verify each suggestion against the contract and current code before including it in a correction packet. Keep separate contract-compliance and code-quality conclusions without requiring a fresh agent for every small step. See [references/superpowers-notice.md](references/superpowers-notice.md) for the adapted source.

Before concurrent review, create a Review Batch Manifest: batch/workstream IDs, exact snapshots or PR/head, common base, contracts, siblings, dependencies, overlap and isolation. Bound concurrency; give each reviewer one snapshot and no shared writable checkout. Reviewers return deltas; only the coordinator writes aggregate state.

Preserve per-stream results and base sensitivity. Perform a coordinator cross-stream interference check; independent ready verdicts alone do not prove a wave jointly safe.

- Changes required: prepare a bounded correction packet on the same workstream, with findings, tests, existing PR if any, revised instruction identity and unchanged or newly approved operation grant. Dispatch at its next explicit checkpoint.
- Blocked: expose the exact decision/evidence gap, options and safe fallback.
- Prepublication ready: show `ready-for-publication-review` and the separate publication gate. Never commit/push/create PR merely because review passed.
- PR ready: show exact reviewed head/base, CI/approvals, risk/human decisions and proposed user-run merge handoff.

Low risk may be summary-only; medium/high risk identifies focused contract/files/trade-offs. High-risk human-owned decisions need explicit current-snapshot confirmation. Re-review changed heads or frozen snapshots; revalidate base-sensitive siblings after merges. Preserve unchanged valid evidence.

### 7. Authorized publication

Only enter on an exact publication grant for the reviewed frozen snapshot. Revalidate the digest, contract and repository lifecycle before delegating through OpenCode. Grant only named commit/push/Draft PR operations and stop at the stated point. Agent Core Main retains publication ownership.

Collect actual published identities; verify equivalence to the reviewed snapshot and current PR/CI gates through `@change-review`. Publication approval and prepublication review do not grant merge readiness.

### 8. Merge command and verification

Read [references/merge-command.md](references/merge-command.md). Generate commands only for the named PR with current PR-mode review and cleared gates. Never execute Ready/Merge or delegate them to OpenCode.

Present dependency-safe commands; defer later dependent blocks until earlier merges are verified. On subsequent `next`, verify live merged or queue state. A queue entry is not a merge. Record actual merge SHA and revalidate affected sibling assumptions.

### 9. Integrated review

Use `@repo-review` on the verified merged commit, checking product intent and cross-PR behavior. A new review does not authorize new Issues. Later waves need refreshed bases and dependency/batch revalidation.

After merge verification or explicit workstream retirement, run `@workspace-cleanup` through the live repository's designated finalization/cleanup owner. Remove eligible linked worktrees and owned runtime leftovers; retain branches/history by default. A missing or blocked repository cleanup API is a concrete retained item, not permission for a raw lifecycle bypass. Revisit previously retained resources at their next recorded trigger.

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
