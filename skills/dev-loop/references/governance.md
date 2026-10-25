## Task-proportional context and assurance budget

- Select exactly the needed checkpoint: `status/observe`, `diagnose`, `plan/dispatch`, or `review/publish`. Do not launch a complete lifecycle or load sibling Skills because they are merely related.
- Reuse previously loaded Skill instructions and verified state. For read-only status or repeated `next` without changed evidence, retrieve the smallest current carrier/run delta; do not re-read whole Skill trees, full Issues/PR discussions, or unrelated repositories.
- Limit each tool response to pertinent fields, bounded log tails or relevant file ranges. Summarize large machine evidence in the durable ledger; show a short feature-centered result to the user. Do not truncate a necessary safety/decision fact.
- Distinguish isolated MOCK-only MVI, real integration, and production effect stages using the approved Feature Contract and actual reachable behavior. For MVI, implement the smallest tests and controls proving its accepted outcome, effect isolation and required boundaries. Classify extra production hardening separately; an attack requiring capabilities explicitly outside the accepted MVI threat model is not automatically an MVI blocker.
- Keep already-approved hard safety boundaries: never disclose secrets, bypass execution grants, execute destructive or external effects without authority, silently merge or release, or treat unknown risk as proven safe. A material change to the accepted threat model remains human-owned. Do not add a new review/Ask for routine in-contract fixes or deferred nonblocking hardening.

## Explain any human approval request

When actually requesting a human decision or handing off a user-run action, use `@human-review approval-brief`. Include **今回やった内容**, **今回承認してほしい内容**, **承認によって影響がある範囲**, and **否認した場合の対応** in the same message. Name the action/actor, target/revision and reason for the gate; distinguish completed work from proposals. Use the brief only to explain a needed decision, without an additional queue scan/write or confirmation for already authorized work. Preserve the stated denial response at continuation.

## Select the entrypoint

- New user requests: use requirements-and-acceptance.md. Previously authorized legacy runs: restore exact workstream/grant and perform only the selected existing operation.
- `merge-command-only`: for “このPRのマージコマンドだけ出して” or the former `@pr-merge` intent, read [references/merge-command.md](merge-command.md) and handle only the named PR. Do not start a repository review, create Issues or initiate a whole loop.
- Status/collection request: inspect the existing run; do not launch or resume work implicitly.
- Cleanup request: use `@workspace-cleanup` for the selected run/repository/host scope; inventory first, apply only eligible actions, and preserve unrelated work.

Before a new delegated plan or dispatch, inspect the applicable `@repo-handoff` execution-contract fields; load full supporting references only if the selected stage needs them. A status-only turn need not read the full execution contract. Use `@change-review` directly at review stage; the legacy `@branch-review` is an explicit-only compatibility alias.

Use the model, reasoning effort and variant configured by OpenCode for authorized launches and subsequent execution turns. Read `@opencode-bridge`'s `references/model-selection.md`, carry `model_policy: opencode-config`, omit explicit model/effort overrides and record runtime metadata when exposed. Do not replay older pinned-model requirements, interrupt busy sessions or alter selection during status/collection.

## Separate authority

Human: goals, material architecture/scope/compatibility/security decisions, risk acceptance, publication grants and final Ready/Merge actions.
Arca: elicit original requirements, produce human-approved Issue specifications and judge delivered user-visible behavior against original intent; no routine technical code review/correction ownership.
KAGARI/Task Orchestrator: execute exact approved Issue sets, run tests/technical review/corrections and own Task/Evidence/native Ask; OpenCode executes within Task authority.
MUSUBI: mobile-first view and reply UI for KAGARI's common Task/Ask state, not a separate execution or permission broker.

An implementation and its tests cannot jointly redefine ambiguous intent. Require human-authored/approved goals and stable AC IDs. Escalate material unknowns instead of selecting the easiest interpretation. Human ownership also includes priority and resource allocation; Arca must proactively detect consequential choices, not merely relay executor questions.

Apply `@human-review`'s `references/goal-alignment.md` at new workstreams, material changes and important PR/release milestones. Before each substantive turn's final, apply its `references/decision-sweep.md` to newly seen contracts, actual scope/resources, evidence and next action even without `NEEDS_DECISION`. Reuse a current nested sweep; unchanged pure observations are exempt. At significant scope/architecture milestones, route a bounded retrospective `missed-decision-audit` to a fresh reviewer context and collect its delta separately from implementation verification. Keep KAGARI native Ask ownership, MUSUBI UI responsibility and existing exact grants. Legacy SwitchBoard observations confer no action authority.

## Checkpoint semantics

For the default requirements/acceptance lane, combine approved bounded evidence and specification steps without one-substantive-stage-per-response throttling; stop at human alignment, exact Issue-set execution authorization and next-phase decisions. Existing legacy OpenCode runs retain their original operation grants and stage stops.

- `next`, `continue` or `Accept` applies only to the exact previously explained action, target, revision and grant. Present the four-field approval brief when this is a request for authority; a bare next/approve prompt has no implicit scope. Preserve concrete prior authorization and scoped denials. Re-read live evidence and repository gates immediately before acting.
- A prior plan/ledger, readiness result or notification is not executable authority. If identity/scope changes, show the new state and request the necessary decision.
- While a run is sent, running, waiting or delivery-unknown, inspect/reconcile it; never launch a duplicate.
- Next after a command handoff verifies user execution; it never performs Ready/Merge.
- Preserve completed independent work when another stream is blocked. Do not cross a new Issue set, next phase, scope change or release gate without the actual human-owned decision.

Restore the canonical state needed for the selected action. Record a checkpoint through `@repo-handoff` when newly verified facts materially change authority, run status, next action or recovery, not after unchanged reads. No carrier means `bootstrap`, no hidden tracking Issue. Always save/read back dispatch intent before sending; a failed necessary recording remains visible.

Own routine resource cleanup as the tail of the current checkpoint through `@workspace-cleanup`. Register newly created persistent resources with real identities, cleanup owner and trigger; mark reused resources borrowed/shared. After result collection, verified merge/retirement or a proved-unused failed start, release eligible owned resources without another confirmation. Keep execution completion and cleanup completion separate. Status-only and merge-command-only modes report cleanup candidates without performing cleanup.
