# Delegated execution contract v1

Use across patch-plan, dev-loop, opencode-bridge and change-review. Copy the resolved packet into the handoff: the executor must not need Arca's installed skills or original conversation. Do not replace repository-owned Agent Core contracts with this format.

## Instruction packet

- Identity: workflow/workstream IDs, globally unique run ID, instruction revision, exact packet digest and immutable packet reference.
- Target: repository and Issue, Task if applicable, backend/version, expected base SHA, branch/worktree, execution role (Main or Task), safe connection reference.
- Model policy: `model_policy: opencode-config`; use OpenCode's configured model, effort and variant without CLI/API/prompt overrides. Copy `@opencode-bridge`'s model-selection policy into the packet. Record configured values separately from observed execution metadata and evidence; missing observations stay `unknown` and are not by themselves a dispatch blocker. Never convert observations into a pinned-model instruction.
- Reviewer binding, when applicable: review kind, immutable review target, listed exact agent name/mode, configuration fingerprint or observation time, invocation route, fresh reviewer session and parent if any, requested versus observed agent, native model policy and observed model/variant, and independence from the implementation run. Keep safe runtime references resolvable without publishing private host coordinates or security findings. A requested role or process name is not observed reviewer execution.
- Authority: human-approved goal/source/revision, stable AC IDs, invariants, non-goals, design latitude, unresolved decisions.
- Operation allowlist: investigate, edit, test, commit, push, Draft PR, executor-report writes. Mark each `allowed|not-authorized|conditional`, with exact approval source and prerequisites. Approval to plan or dispatch alone is not permission to edit or publish.
- Stop point: exact artifact/action after which execution stops. Ready, Merge and release are excluded from the standard grant. Routine cleanup is a separate coordinator-owned housekeeping step after evidence collection, limited to `@workspace-cleanup` eligibility; it never grants disposal of unique work or bypass of repository finalization. These skills never delegate Ready/Merge.
- Resource lifecycle: newly owned versus borrowed/shared resources, creation receipts and actual identity evidence, safe private locator references, consumers/dependencies, cleanup owner, routine-cleanup authority, release trigger, evidence recovery destination and retained-resource revisit event. Register persistent processes/tmux resources/worktrees before/after creation; keep real host coordinates out of public records.
- Execution gate: target action, `stop|conditional|allowed`, prerequisite, clearing authority, admissible fallback, evidence snapshot, immediate revalidation.
- Work: bounded steps, expected/must-not-touch paths, dependencies, tests and acceptance criteria.
- Delivery: frozen diff/manifest, validation and environment evidence; branch/head if present; PR number/URL only when actually authorized and created.
- Recovery: canonical carrier, coordinator writer, run-scoped executor-report destination if authorized; question ID/revision and safe fallback on interruption.
- Human-question contract: before asking for authority, return completed work and verification limits, exact requested action/actor and target/revision, affected scope, denial handling and the reason/source for the human gate. Copy these requirements into the executor packet; it must not depend on Arca's installed `@human-review` skill. Existing grants remain valid and routine questions resolved by the contract need no new approval.
- Monitoring: Ask monitor/notification owner `SwitchBoard`; safe correlation reference or `unknown`. No watcher or polling duty for Arca or OpenCode.

Unknown operation authority means do not perform it. Even investigation-only work needs authority for expensive or side-effectful checks. Do not force a PR for an implementation-only stop.

Compute the digest over exact canonical packet bytes excluding its own digest field; record encoding and algorithm (for example UTF-8/SHA-256). Never invent a checksum. A material change needs a new approved revision. Reconcile uncertain delivery of an old revision before sending its replacement.

## Receipt and result

Report run/revision/digest, verified target binding, sent time and message/request ID when available.

Also report `opencode-config` policy, observed model/effort/variant, evidence and observation time. A configured value is not observed execution evidence. Preserve historical settings and mismatches, but do not replay an older pinned model into a new authorized turn. Leave running sessions and their current selection intact; do not relaunch or duplicate work to change models.

Keep separate axes:

| Axis | Values |
|---|---|
| Delivery | prepared, intent-recorded, sent, acknowledged, unknown |
| Execution | not-observed, running, waiting-question, reported-complete, failed, unknown |
| Collection | not-collected, partial, collected |
| Independent verification | not-reviewed, pass, changes-required, blocked |

Transport success proves only sent. Acknowledged requires run-correlated receipt evidence; started requires separate execution evidence. Completion text is an executor claim until reviewed. Preserve timestamps and last-known facts when disconnected.

Executor results include actual scope, changed paths, base/head or frozen manifest hashes, validation commands/results/environment, unrun checks, residual risks, questions, stop point reached, artifact locations and record-write status. Only the coordinator records independent verification; reviewers return pinned evidence deltas.

Include resource ownership and cleanup handoff in executor results. After durable collection, the designated cleanup owner releases eligible resources and records each `cleaned|already-absent|retained|blocked|unknown` result separately from execution/review status. Retained resources require an owner, reason and concrete revisit trigger. Keep evidence and cleanup-intent/results outside the deletion set; reconcile uncertain actions before retrying.

Apply `@change-review`'s `references/verification.md` to result claims. Record each check's exact snapshot, command, environment, exit status, outcome, scope, counts/skips and readable evidence reference. Preserve original evidence provenance and applicability; copying a claim into a new checkpoint does not make it fresh or independently verified. Retain compact failed-hypothesis records and finding dispositions when they prevent repeated investigation, along with the next discriminating check. Keep raw/private logs out of public carriers.

## Question and reply

Bind a question to run/revision, question ID and current target snapshot. Answer contract-resolvable questions only from a cited, still-applicable contract inside the grant. Escalate human-owned decisions with the four-field approval brief, options when needed, recommendation, blocked action and safe fallback. Preserve the explained request and `approved|denied|deferred|open` outcome separately; denial blocks that action and does not grant an alternate operation. The coordinator must expand a bare executor Ask into an evidence-backed brief before asking the user. A SwitchBoard notice does not answer a question. Send only a resolved authorized answer; scope/authority changes need a revised packet. Reconcile uncertain reply delivery instead of blindly retrying.
