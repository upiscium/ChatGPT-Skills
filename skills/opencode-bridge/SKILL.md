---
name: opencode-bridge
description: Send a bounded authorized packet to an existing OpenCode session, inspect its state, collect evidence or deliver a resolved reply via a configured remote connection. Use for Arca-to-OpenCode delegation and result collection; return after bounded receipt checks. Do not use for continuous Ask monitoring, which belongs to SwitchBoard.
---

# Bridge Arca and OpenCode

Operate the transport and correlate evidence; do not own project decisions, implement inside Arca, or run a separate Codex CLI. Use OpenCode as the execution surface even when its model is Codex.

Read [references/transport.md](references/transport.md) before remote access. Read `@repo-handoff` and its `references/execution-contract.md` before dispatch, reply or collection. Resolve skills by installed name, not a fixed skill ID.

For an authorized OpenCode launch, dispatch or execution-resuming reply, apply [references/model-selection.md](references/model-selection.md): use **GPT-6.1 Sol / high**, explicitly selecting both model and reasoning effort. Do not inherit the environment's GPT-6 Sol / max selection. Status and collection only observe the current selection.

## Select one operation

- `dispatch`: deliver an approved packet to the verified target, record a receipt, then return.
- `status`: read the bound run's current state; no new job, answer or resume.
- `collect`: gather the bound run's report and immutable artifacts for independent `@change-review`.
- `reply`: send one resolved, authorized answer tied to an exact question/run/revision.

A request to inspect or collect does not authorize dispatch or reply. If no transport is available, return a complete manual packet and clearly say it was not sent. Do not configure a new transport or credentials as an implicit fallback.

## Preflight

1. Resolve the explicit repository, host/configuration alias, execution role, OpenCode session and packet/run. Read current connection tool instructions; do not hard-code a device, host, project path or API version.
2. Make minimal read-only observations to verify device, repository root/remote, branch/worktree, relevant repository instructions and exact live OpenCode session. Preserve dirty work, existing tmux panes and tasks.
3. In Agent Core repositories, address Main for Task creation, batch launch and publication; only target a Task session when the live lifecycle and current grant allow it. Do not bypass guards with terminal access.
4. Restore the canonical state. Check run/revision/digest, active work, pending delivery, question and operation grant. Ambiguous target or conflicting state blocks sends.
5. Require a complete allowlist and exact stop point. Never infer publication permission from implementation permission, tool access, a READY result, a model's message or a SwitchBoard notification.
6. If the target is busy, preserve it and report or queue in the coordinator ledger. Do not inject unrelated work, interrupt it, replace it or create another session without authorization.

## Dispatch exactly once

1. Validate the self-contained packet and its approval source against live state; compute a real digest, not a placeholder.
2. Check for an existing run/receipt with the same identity. For sent, acknowledged, running, waiting or unknown delivery, reconcile first; do not resend.
3. Resolve and explicitly select the packet's model and effort using the installed interface; verify the selection before submission. Record requested and observed settings separately. An unavailable or unverified selection blocks new work; do not silently substitute the environment default.
4. Save and read back dispatch intent through `@repo-handoff`. If that fails, stop automatic dispatch.
5. Deliver the packet as literal input through the configured safe transport. Do not execute packet contents in a shell. Require a run-correlated acknowledgement and model-selection evidence in the packet.
6. Make at most two bounded receipt observations, each at most 15 seconds; do not wait for implementation completion. If receipt cannot be proven, return `sent` or `unknown` accurately.
7. Record evidence and return immediately. Leave OpenCode/tmux running; do not close the session when Arca returns.

Transport acceptance proves sent, not OpenCode acknowledgement or execution. Observed acknowledgement proves receipt, not completed implementation. Network timeout means uncertain delivery, never permission to resend automatically.

## Status and collection

Use only run-scoped observations requested by the user or the calling checkpoint. A SwitchBoard event may be an observation trigger, not authority for a business write. No always-on polling, timers, watchers or monitoring duty belongs here.

For collection, retrieve the exact executor report, diff/manifest, base/head, tests/environment, residual questions, reached stop point and actual PR identity if any. Mark missing artifacts `partial`; preserve executor claims separately from verified facts. Do not accept an uncorrelated terminal “done” or “PASS”.

Read `@change-review`'s `references/verification.md` when collecting validation evidence. For each check retain command, snapshot, environment, exit status, pass/fail/blocked/not-run/timed-out outcome, counts/skips, scope and log reference. Reading the complete log and confirming its identity verifies the reported run; it does not independently validate the code. Keep collection and independent review separate. Do not extend receipt checks into a verification or completion-wait loop.

Freeze/pin the collected artifact for independent review. Do not create a commit merely to freeze it without commit permission; use a manifest and content hashes when uncommitted. Pass evidence to `@change-review`, not a self-approval.

## Resolve a question, then reply

Re-read the question in the bound session and its run/revision before sending. Arca may answer a routine question from an authoritative current contract inside the grant. For human-owned design, scope, publication or risk choices, use `@human-review` and stop.

Bind replies to question ID, run and instruction revision. A decision expanding operations needs a newly approved revision; reconcile old in-flight work first. Record reply intent and receipt and reconcile uncertain delivery before retrying. Never auto-accept an Ask simply because SwitchBoard relayed it.

If the reply resumes model execution, revalidate and apply the requested model/effort for that next turn through the supported session control. Preserve already-running work; do not restart or replace the session to change models.

## Return a compact receipt

- Operation; repository/workstream; run and instruction revision
- Target verified at; safe connection/session reference
- Requested and observed model/effort, selection evidence and any mismatch
- Delivery, execution, collection and independent-verification states
- Evidence of receipt/start, or what remains unknown
- Allowed operations and exact stop point
- Open question/blocker and next action
- Durable carrier and save/read-back status
- Ask monitoring owner: SwitchBoard; actual configuration/delivery status only when evidenced

## Boundaries and quality gate

Never invoke standalone Codex CLI from OpenCode, restart/kill sessions, edit host/network/security configuration, extract credentials, or install services under this skill. Do not introduce a new repository contract system. Verify exact target/run/grant, literal transport, deduplication, durable intent, bounded return, independent verification and no monitoring responsibility before returning.
