# Delegated execution contract v1

Use across patch-plan, dev-loop, opencode-bridge and change-review. Copy the resolved packet into the handoff: the executor must not need Arca's installed skills or original conversation. Do not replace repository-owned Agent Core contracts with this format.

## Instruction packet

- Identity: workflow/workstream IDs, globally unique run ID, instruction revision, exact packet digest and immutable packet reference.
- Target: repository and Issue, Task if applicable, backend/version, expected base SHA, branch/worktree, execution role (Main or Task), safe connection reference.
- Authority: human-approved goal/source/revision, stable AC IDs, invariants, non-goals, design latitude, unresolved decisions.
- Operation allowlist: investigate, edit, test, commit, push, Draft PR, executor-report writes. Mark each `allowed|not-authorized|conditional`, with exact approval source and prerequisites. Approval to plan or dispatch alone is not permission to edit or publish.
- Stop point: exact artifact/action after which execution stops. Ready, Merge, release and cleanup are excluded from the standard grant. These skills never delegate Ready/Merge.
- Execution gate: target action, `stop|conditional|allowed`, prerequisite, clearing authority, admissible fallback, evidence snapshot, immediate revalidation.
- Work: bounded steps, expected/must-not-touch paths, dependencies, tests and acceptance criteria.
- Delivery: frozen diff/manifest, validation and environment evidence; branch/head if present; PR number/URL only when actually authorized and created.
- Recovery: canonical carrier, coordinator writer, run-scoped executor-report destination if authorized; question ID/revision and safe fallback on interruption.
- Monitoring: Ask monitor/notification owner `SwitchBoard`; safe correlation reference or `unknown`. No watcher or polling duty for Arca or OpenCode.

Unknown operation authority means do not perform it. Even investigation-only work needs authority for expensive or side-effectful checks. Do not force a PR for an implementation-only stop.

Compute the digest over exact canonical packet bytes excluding its own digest field; record encoding and algorithm (for example UTF-8/SHA-256). Never invent a checksum. A material change needs a new approved revision. Reconcile uncertain delivery of an old revision before sending its replacement.

## Receipt and result

Report run/revision/digest, verified target binding, sent time and message/request ID when available. Keep separate axes:

| Axis | Values |
|---|---|
| Delivery | prepared, intent-recorded, sent, acknowledged, unknown |
| Execution | not-observed, running, waiting-question, reported-complete, failed, unknown |
| Collection | not-collected, partial, collected |
| Independent verification | not-reviewed, pass, changes-required, blocked |

Transport success proves only sent. Acknowledged requires run-correlated receipt evidence; started requires separate execution evidence. Completion text is an executor claim until reviewed. Preserve timestamps and last-known facts when disconnected.

Executor results include actual scope, changed paths, base/head or frozen manifest hashes, validation commands/results/environment, unrun checks, residual risks, questions, stop point reached, artifact locations and record-write status. Only the coordinator records independent verification; reviewers return pinned evidence deltas.

## Question and reply

Bind a question to run/revision, question ID and current target snapshot. Answer contract-resolvable questions only from a cited, still-applicable contract inside the grant. Escalate human-owned decisions with options, recommendation, blocked action and safe fallback. A SwitchBoard notice does not answer a question. Send only a resolved authorized answer; scope/authority changes need a revised packet. Reconcile uncertain reply delivery instead of blindly retrying.
