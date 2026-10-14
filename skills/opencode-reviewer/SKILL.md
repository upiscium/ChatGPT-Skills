---
name: opencode-reviewer
description: List and inspect installed OpenCode reviewer roles, select an appropriate exact role, and launch or collect an isolated code or security review with verified agent binding and OpenCode-configured model selection. Use for independent reviews through OpenCode, reviewer startup failures, or explicit Reviewer-role requests. Provides interim routing until the repository's KUMIKI/KAGARI lifecycle owns it.
---

# Launch an Independent OpenCode Reviewer

Own role discovery, isolated reviewer startup and receipt evidence. Let `@change-review` or `@security-audit` define review scope, evidence standards and report format. A role name alone does not establish independence or a successful review.

Read [references/launch.md](references/launch.md) before starting a process or sending a review. Read `@opencode-bridge`'s transport and model-selection references, and `@repo-handoff`'s execution contract. Resolve installed skills by name, never fixed IDs.

## Explain any human approval request

When actually requesting a human decision or handing off a user-run action, use `@human-review approval-brief`. Include **今回やった内容**, **今回承認してほしい内容**, **承認によって影響がある範囲**, and **否認した場合の対応** in the same message. Name the action/actor, target/revision and reason for the gate; distinguish completed work from proposals. Use the brief only to explain a needed decision, without an additional queue scan/write or confirmation for already authorized work. Preserve the stated denial response at continuation.

## Select one operation

- `list`: inspect available roles and recommend the matching role; do not launch, send or change configuration.
- `start`: start the requested independent review on the verified target, confirm bounded receipt and return. An explicit independent-review request includes this normal reviewer startup; do not ask again merely because a fresh reviewer session is needed.
- `status` / `collect`: inspect the recorded reviewer session and its pinned artifacts; do not start another reviewer implicitly.
- `cleanup`: use `@workspace-cleanup` on this review's recorded resources; preserve output and verify eligibility before release.

Use this as the preferred OpenCode reviewer route for this user's independent code and security reviews when the configured connection is available. Scope or authority uncertainty still matters; routine role selection and startup do not require new approval. Never treat a listing/status request as launch permission.

## Bind the target and discover roles

1. Resolve the selected connection, repository, exact review directory, immutable base/head or frozen manifest, and review kind. Preserve active implementation sessions and dirty work. Use repository-approved snapshot/worktree handling; this skill creates no replacement Task or lifecycle.
2. Read applicable repository instructions first. A live KUMIKI/KAGARI or Agent Core reviewer API/call graph takes precedence over generic startup; use its supported role discovery and launch binding without bypassing its gates.
3. Inspect `opencode --version`, installed help, and `opencode agent list` in the **same directory and environment** that will run the review. With an attached server, list its effective agents too. Do not assume RDC's initial directory, another worktree, or a config file on disk represents the target runtime.
4. Inspect each candidate with the installed `opencode debug agent <exact-name>` or supported server agent endpoint. Record exact name/case, description, mode, configured model/effort and effective permission rules. Do not dump full provider configuration, credentials or unrelated session transcripts.
5. Use the read-only helper `scripts/list_reviewers.mjs` when Node or Bun is already available: `bun <skill-root>/scripts/list_reviewers.mjs <absolute-review-directory> [exact-role ...]`. It lists names/modes and inspects reviewer candidates. Run it through the same already-approved environment wrapper as OpenCode. If it cannot parse the installed output, inspect native output or the supported structured API; do not install a runtime or conclude that no role exists from a failed filter.

Prefer a listed security-focused reviewer for security scope, and a listed correctness/contract reviewer for ordinary changes. `reviewer` and `security-reviewer` are observed names, not universal constants. Inspect descriptions before deciding; `verifier` or `build` is not an automatic replacement. Select the clear best match without asking the user to make a routine choice. Report a missing/unsuitable role precisely instead of inventing one.

## Select a supported invocation

- Prefer the supported session/message API when available: use a fresh reviewer session and an explicit `agent`, checked against the installed schema; omit `model`, `variant` and reasoning-effort overrides. OpenCode 1.18.30 supports registered subagent reviewer roles through this API without changing their mode or permissions.
- For `primary` / `all` roles, a supported CLI launch may use `--agent <exact-role>`; omit model and variant options.
- For `subagent` roles, **do not use `opencode run --agent <role>` on 1.18.30**: it falls back to the default agent. Use the verified API route, or a repository-approved fresh parent invoking the exact reviewer through the supported Task/@ mechanism. Verify the actual child role and model; the parent is only a dispatcher.
- Do not change a role's mode, prompt or permissions to force startup. Do not retry through a more privileged agent after denial. Preserve native role restrictions and any stricter session restriction.

Use the model, reasoning effort and variant configured by OpenCode for the reviewer. Preserve role-specific settings and native fallback/default behavior; do not copy inspected model values into an explicit override. Record exposed configured and actual values separately. If the runtime reports an unavailable configured model, report that blocker without substituting one or changing configuration.

A full TUI's `--agent` argument is not proof of the active reviewer. Verify the actual role from UI/runtime metadata, and observe model/effort without changing the TUI selection. Missing model metadata remains `unknown`; do not confuse it with a failed role binding.

## Prepare an independent packet

Include run/revision/digest, immutable review target, approved intent and ACs, non-goals, relevant raw evidence, review kind, chosen role, `model_policy: opencode-config`, operation grant, report format and exact stop point. State that model/effort overrides are omitted. Copy the applicable review instructions into the packet; OpenCode must not need Arca's installed skills. Require any human-owned question to return work completed, exact requested action/actor, affected scope and denial handling, bound to its question/run/revision, so the coordinator can explain it before seeking approval.

- Create a fresh context separate from the implementer. Do not resume or fork the implementation conversation into a reviewer. Resume only a verified reviewer session for the same authorized review/re-review.
- Supply facts and artifacts rather than the implementer's preferred verdict or Arca's diagnosis. Prior findings are appropriate for an explicitly scoped re-review.
- Default to reading the frozen source and reporting findings. No edits, commits, push, PR/Issue writes, approval, merge, deployment or global configuration changes. Run checks only when the grant, effective permissions and an isolated execution surface permit them; source-only review remains explicitly source-only.
- Preserve each reviewer's snapshot and output independently. Return deltas to one coordinator, never concurrent writes to aggregate state. Sanitize public security checkpoints; keep vulnerability details and raw logs private.

## Launch once and return

1. Reconcile existing reviewer bindings and uncertain sends for this run before creating a new session. Verify the chosen target, role and actual permissions; inspect native model settings when exposed without overriding them. Do not duplicate a running review.
2. Reuse a verified configured server when suitable and record it as borrowed/shared. If the authorized review needs its own runtime, register the planned resource with `@workspace-cleanup`, then start a dedicated OpenCode process in the approved review directory. A loopback-only `serve` process is a normal reviewer runtime, not a global service installation; bind its actual returned address/process identity, cleanup owner, consumers and release trigger. Register any new tmux pane or review worktree too. Keep credentials with the configured transport and do not weaken authentication, expose a network listener, or alter host configuration.
3. Create the isolated reviewer session through the supported interface; record its real ID, role read-back, exposed model metadata, source snapshot and a safe runtime reference. A terminal/tmux name or RDC PID is not an OpenCode session ID. Save and read back dispatch intent through `@repo-handoff` on the existing carrier. Without a carrier, keep a self-contained `bootstrap` receipt and make the durability limitation visible; do not invent a tracking Issue.
4. Submit literal packet data once with the explicit role and no model/variant/effort override. Use asynchronous submission when supported. Preserve the request/session identifiers even on timeout.
5. Make at most two receipt observations, each at most 15 seconds. Check session/request and assistant metadata for the actual agent, provider/model and variant. HTTP acceptance proves `sent`; it does not prove the reviewer started or completed. Mark missing observations `unknown`. Never ask the model to self-identify as proof.
6. Return promptly with the session alive while review work is outstanding. Record cleanup after durable report collection; do not retain the runtime indefinitely just because receipt checks ended. Do not wait for full review completion or take over ongoing Ask monitoring. SwitchBoard/MUSUBI owns notifications. A receipt timeout never permits automatic resend or session termination.

A verified role mismatch, default-agent fallback, unavailable model or permission error is a failed reviewer start, even when the process exists or exits zero. Retain any submitted run and report its state. Correct only evidenced invocation mistakes; reconcile delivery before a bounded retry. Never reinterpret a failed reviewer launch as a positive independent verdict.

After preserving startup-error evidence, use `@workspace-cleanup` for newly owned leftovers only when no request, child or uncertain submission remains. Failure is not a reason to leave a proved-unused dedicated server running forever.

## Collect and report

Collect the exact bound review report and raw evidence, confirm target freshness and actual role/model, and apply the originating review skill's quality gate. A reviewer `COMPLETED` status alone is not a valid security or publication verdict. Missing coverage stays explicit. If new code changes the target, invalidate affected conclusions and prepare only the required re-review.

Save and read back the full required report/evidence outside the cleanup set, then invoke `@workspace-cleanup` for the owned reviewer runtime, pane and disposable review worktree. A `changes-required` verdict does not require keeping a completed reviewer process alive. Preserve session history, active children, shared servers and any sole uncommitted snapshot; record a concrete retention reason/owner/trigger for exceptions. A pending publication or merge gate does not by itself block release of disposable review resources.

Return a compact receipt:

- Review kind and immutable target; run/revision/digest
- Listed role, description/mode and configuration fingerprint or evidence time
- Invocation route; safe runtime and actual reviewer session references
- Requested versus observed agent; `opencode-config` policy and observed model/variant/effort with evidence or `unknown`
- Delivery, execution, collection and review-result states separately
- Findings/report reference or exact startup blocker; next action
- Carrier/save status, or `bootstrap`/`pending-write`
- Resource references and cleanup outcome; retained resources with owner/reason/revisit trigger

KUMIKI/KAGARI can later replace this startup layer. Preserve the reviewer binding and report contract, adopt its live APIs when available, and do not use this interim skill to weaken repository-owned isolation or publication gates.
