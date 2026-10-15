---
name: opencode-bridge
description: Send a bounded authorized packet to an existing OpenCode session, inspect its state, collect evidence or deliver a resolved reply via a configured remote connection. Use for Arca-to-OpenCode delegation and result collection; return after bounded receipt checks. Do not use for continuous Ask monitoring, which belongs to SwitchBoard.
---

# Bridge Arca and OpenCode

Operate the transport and correlate evidence; do not own project decisions, implement inside Arca, or run a separate Codex CLI. Use OpenCode as the execution surface even when its model is Codex.

For listing reviewer roles or starting an authorized independent review, route startup to `@opencode-reviewer`. It owns fresh reviewer-session creation and mode-compatible invocation; this bridge remains responsible for bounded transport/status/collection conventions. Do not guess Reviewer names, send a subagent through an incompatible `run --agent` path, or replace the implementer's active session.

Read [references/transport.md](references/transport.md) before remote access. Read `@repo-handoff` and its `references/execution-contract.md` before dispatch, reply or collection. Resolve skills by installed name, not a fixed skill ID.

For an authorized OpenCode launch, dispatch or execution-resuming reply, apply [references/model-selection.md](references/model-selection.md): use the model, reasoning effort and variant already configured by OpenCode. Omit model/effort overrides from CLI arguments, API fields and packets. Observe the actual selection without changing it.

## Explain any human approval request

When actually requesting a human decision or handing off a user-run action, use `@human-review approval-brief`. Include **今回やった内容**, **今回承認してほしい内容**, **承認によって影響がある範囲**, and **否認した場合の対応** in the same message. Name the action/actor, target/revision and reason for the gate; distinguish completed work from proposals. Use the brief only to explain a needed decision, without an additional queue scan/write or confirmation for already authorized work. Preserve the stated denial response at continuation.

## Select one operation

- `dispatch`: deliver an approved packet to the verified target, record a receipt, then return.
- `status`: read the bound run's current state; no new job, answer or resume.
- `collect`: gather the bound run's report and immutable artifacts for independent `@change-review`.
- `reply`: send one resolved, authorized answer tied to an exact question/run/revision.
- `cleanup`: route the selected run's resource inventory and eligible release to `@workspace-cleanup`; do not turn a status request into cleanup.

A request to inspect or collect does not authorize dispatch or reply. If no transport is available, return a complete manual packet and clearly say it was not sent. Do not configure a new transport or credentials as an implicit fallback.

## Preflight

1. Resolve the explicit repository, host/configuration alias, execution role, OpenCode session and packet/run. Read current connection tool instructions; do not hard-code a device, host, project path or API version.
2. Make minimal read-only observations to verify device, repository root/remote, branch/worktree, relevant repository instructions and exact live OpenCode session. Preserve dirty work, existing tmux panes and tasks.
3. In Agent Core repositories, address Main for Task creation, batch launch and publication; only target a Task session when the live lifecycle and current grant allow it. Do not bypass guards with terminal access.
4. Restore the canonical state. Check run/revision/digest, active work, pending delivery, question and operation grant. Ambiguous target or conflicting state blocks sends.
5. Require a complete allowlist and exact stop point. Never infer publication permission from implementation permission, tool access, a READY result, a model's message or a SwitchBoard notification.
6. If the target is busy, preserve it and report or queue in the coordinator ledger. Do not inject unrelated work, interrupt it, replace it or create another session without authorization.

For persistent resources created through the transport, apply `@workspace-cleanup`'s resource record: creation evidence, real IDs, ownership, consumers, cleanup owner, release trigger and recovery reference. Mark existing sessions/servers `borrowed` or `shared`; using them does not make them disposable.

## Dispatch exactly once

Check the packet's goal/outcome/non-goal/resource record against the granted scope using `@human-review`'s `references/goal-alignment.md` when a preflight trigger applies. On collection or a substantive dispatch/reply checkpoint, apply its `references/decision-sweep.md` before returning: compare actual delivered contracts, scope, responsibility and resource changes with the packet even if the executor reported no Ask. Preserve status-only mode; unchanged observation needs no new sweep. Return a candidate delta to the coordinator without silently revising the packet or granting operations.

1. Validate the self-contained packet and its approval source against live state; compute a real digest, not a placeholder.
2. Check for an existing run/receipt with the same identity. For sent, acknowledged, running, waiting or unknown delivery, reconcile first; do not resend.
3. Carry `model_policy: opencode-config`; omit model/effort overrides and let OpenCode resolve the selection. Record exposed configuration and observed execution separately. Missing metadata remains `unknown`; an actual unavailable-model error is a blocker, never permission to substitute another model.
4. Save and read back dispatch intent through `@repo-handoff`. If that fails, stop automatic dispatch.
5. Deliver the packet as literal input through the configured safe transport. Do not execute packet contents in a shell. Require a run-correlated acknowledgement and observed model metadata when available; do not ask the executor to select a model.
6. Make at most two bounded receipt observations, each at most 15 seconds; do not wait for implementation completion. If receipt cannot be proven, return `sent` or `unknown` accurately.
7. Record evidence and return immediately. Leave OpenCode/tmux running during outstanding execution; returning after receipt is not a cleanup trigger. Record the resource owner and completion/collection trigger so later checkpoints can release it.

Transport acceptance proves sent, not OpenCode acknowledgement or execution. Observed acknowledgement proves receipt, not completed implementation. Network timeout means uncertain delivery, never permission to resend automatically.

## Status and collection

Use only run-scoped observations requested by the user or the calling checkpoint. A SwitchBoard event may be an observation trigger, not authority for a business write. No always-on polling, timers, watchers or monitoring duty belongs here.

For collection, retrieve the exact executor report, diff/manifest, base/head, tests/environment, residual questions, reached stop point and actual PR identity if any. Mark missing artifacts `partial`; preserve executor claims separately from verified facts. Do not accept an uncorrelated terminal “done” or “PASS”.

Read `@change-review`'s `references/verification.md` when collecting validation evidence. For each check retain command, snapshot, environment, exit status, pass/fail/blocked/not-run/timed-out outcome, counts/skips, scope and log reference. Reading the complete log and confirming its identity verifies the reported run; it does not independently validate the code. Keep collection and independent review separate. Do not extend receipt checks into a verification or completion-wait loop.

Freeze/pin the collected artifact for independent review. Do not create a commit merely to freeze it without commit permission; use a manifest and content hashes when uncommitted. Pass evidence to `@change-review`, not a self-approval.

After terminal output and required artifacts are durably collected, invoke `@workspace-cleanup` for this run's disposable owned runtime/panes/helpers. Preserve the implementation worktree until its own recovery and completion conditions pass. Keep reused/shared or concretely needed continuation sessions with an owner, reason and revisit trigger. This is collection housekeeping; no extra confirmation is needed for eligible resources within the existing grant. A status-only observation, timeout or uncertain completion does not trigger termination.

## Resolve a question, then reply

Re-read the question in the bound session and its run/revision before sending. Arca may answer a routine question from an authoritative current contract inside the grant. For human-owned design, scope, publication or risk choices, prepare `@human-review approval-brief` from the exact question and verified run context, then stop that action. Do not forward a bare Ask/Accept prompt: explain completed work, requested permission, affected scope and denial handling before requesting a reply. Preserve any denial against that question/revision rather than auto-accepting or selecting a different option.

Bind replies to question ID, run and instruction revision. A decision expanding operations needs a newly approved revision; reconcile old in-flight work first. Record reply intent and receipt and reconcile uncertain delivery before retrying. Never auto-accept an Ask simply because SwitchBoard relayed it.

If the reply resumes model execution, preserve OpenCode's native selection and omit model/effort overrides for that turn. Do not replay an older packet's pinned model. Preserve already-running work; do not restart or replace the session to change models.

## Return a compact receipt

- Operation; repository/workstream; run and instruction revision
- Target verified at; safe connection/session reference
- Model policy `opencode-config`; observed model/effort, evidence or `unknown`
- Delivery, execution, collection and independent-verification states
- Evidence of receipt/start, or what remains unknown
- Allowed operations and exact stop point
- Open question/blocker and next action
- Durable carrier and save/read-back status
- Owned resource references; cleanup results or retention reason/owner/revisit trigger
- Ask monitoring owner: SwitchBoard; actual configuration/delivery status only when evidenced

## Boundaries and quality gate

Never invoke standalone Codex CLI from OpenCode, restart/kill sessions as a dispatch or timeout workaround, edit host/network/security configuration, extract credentials, or install services under this skill. Release terminal owned resources only through `@workspace-cleanup` after its gates pass; preserve active and borrowed sessions. Do not introduce a new repository contract system. Verify exact target/run/grant, literal transport, deduplication, durable intent, bounded return, independent verification, cleanup disposition and no monitoring responsibility before returning.
