---
name: repo-status
description: Explain a project's current position through five evidence-backed views — implemented and usable capabilities, work in progress, work not started, position on the overall roadmap, and the currently planned next action — while checkpointing verified repository state. Use when the user asks where a project stands, what they can use now, what is being built, what is still untouched, how far the roadmap has progressed, or what comes next. Distinguish implemented code from actual availability and agreed next steps from recommendations. Do not use as a defect-finding review or a conversation handover.
---

# Summarize Repository Status

Give the user a current map of the project in five views: what they can use, what is being built, what has not started, where the roadmap stands, and what is planned next. Lead with user-visible behavior and purpose; use repository mechanics as supporting evidence. Observe product and development state without advancing the work.

## Explain any human approval request

When actually requesting a human decision or handing off a user-run action, use `@human-review approval-brief`. Include **今回やった内容**, **今回承認してほしい内容**, **承認によって影響がある範囲**, and **否認した場合の対応** in the same message. Name the action/actor, target/revision and reason for the gate; distinguish completed work from proposals. Use the brief only to explain a needed decision, without an additional queue scan/write or confirmation for already authorized work. Preserve the stated denial response at continuation.

## Pin the snapshot

1. Identify the repository, default or requested branch, and review scope from the request and verified context. Ask only if the target remains ambiguous. When a project spans repositories, state which components were inspected; do not extrapolate one repository's status to the whole project.
2. Resolve the inspected state to an immutable commit SHA and record the observation time.
3. Read only the repository instructions, architecture/roadmap sections, entrypoints, tests and release/deployment evidence necessary for the requested feature/area. Expand to other documents if a material gap remains; do not inventory every subsystem for a focused status question.
4. Inspect relevant open and recently closed Issues, open and recently merged pull requests, implementation branches, and repository-native task state when available. Record which refs, releases, and environments each claim applies to; inspect active branch code when its state differs from the main snapshot.
5. State inaccessible sources and freshness limitations. Do not fill gaps from memory or infer live status from stale conversation text.
6. Search the canonical Issue/PR carriers for the latest `codex-repo-state:v1` record. Revalidate it against the inspected commit and mark it `fresh`, `stale`, `conflicted`, `incomplete`, or `reconstructed`; never treat the record alone as live authority.
7. Before returning, persist only a **changed, actionable** status snapshot through `@repo-handoff` on an existing canonical carrier. Repeated read-only status with no new state reuses the previous marker and makes no write. Preserve the coordinator's verified next checkpoint; record recommendations separately. If no carrier exists, return `bootstrap` rather than inventing a hidden Issue.

## Reconstruct intended architecture

Apply `@human-review`'s `references/goal-alignment.md` to the approved objective, measurable product/research outcome, non-goals, known resource envelope and current work. Show material alignment gaps within the five views without replacing the agreed next action. Technical success is not scientific acceptance or user availability. Before a substantive final, use its `references/decision-sweep.md` to detect newly seen choices even without a flag; unchanged pure observation is exempt. Report candidates and evidence needs within status scope, without launching work or turning the snapshot into an unsolicited approval request.

Derive the system's documented goals, major components, responsibility boundaries, primary end-to-end flows, and milestones. Prefer accepted design records and current code over old plans. When sources disagree, report the conflict and identify which source appears authoritative; do not silently choose a convenient narrative.

If no authoritative overall design exists, say so and provide only a code-derived component map labeled as an inference.

## Separate implementation, availability, and activity

Group behavior by user-visible capability or architectural responsibility rather than listing files. Scope rows to a specific feature slice or version: a usable feature can coexist with an enhancement in progress. For each slice and inspected ref, assign one implementation state:

- `implemented`: reachable through the intended production path and supported by code plus meaningful validation or observed integration evidence
- `partial`: substantial implementation exists, but integration, required behavior, validation, migration, or acceptance work remains
- `planned`: accepted work item or roadmap scope, with no substantial implementation found in the inspected refs
- `absent`: required by the accepted target design, but no implementation or tracked delivery plan was found
- `unknown`: evidence is insufficient or contradictory
- `out-of-scope`: intentionally excluded from the current target

Documentation, a closed Issue, an isolated helper, or a merged PR is not by itself proof that a capability is operational. Trace the production entrypoint and current integrated code. Conversely, do not call an undocumented but working capability absent when code and tests establish it.

Assess availability separately: usable in a named release/environment or supported source checkout, usable with stated prerequisites, not yet available, or unknown. Cite the entrypoint and validation or release/deployment evidence appropriate to the product. A library or CLI need not be deployed to a server, but passing source tests do not establish availability in a hosted production service. Do not run a deployment or change an environment to prove availability.

Map the evidence to the user's three capability views:

- **Implemented and usable:** name what the user can do, where/how it is available, and any setup, access, feature-flag, or environment conditions. Include an `implemented` slice only when its scoped availability is established; do not generalize a working subset to the whole feature.
- **Work in progress:** require current code, PR, task-state, or dated owner-report evidence that implementation, review, integration, or acceptance work has begun. Name the remaining gap and blocker. Assignment or branch existence alone does not prove work has started. A stale branch is not proof of continuing activity; distinguish recorded work status from a live running process. Explicitly paused/blocked work stays labeled as such.
- **Not started:** include only accepted scope for which the inspected sources show no implementation or active work. Check relevant branches/PRs/tasks as well as the main snapshot. Separate scheduled backlog from target-design requirements that are still untracked. Ideas, rejected work, and out-of-scope features are not commitments.

Do not force every capability into these three views. Report partial but idle work, integrated code awaiting availability, and unknowns in a short **Other gaps / unconfirmed state** note with evidence and what would resolve them. Put a delivery wait in work in progress only when a current workstream supports that classification. Missing access or missing documentation is not evidence of nonexistence or of work not having started.

For every nontrivial classification, cite concise evidence such as commit-pinned paths, tests, release tags, Issue or PR URLs, task records, or validation output. Label code-derived architectural interpretations as inference.

## Reconstruct active work

For each current workstream, record:

- Objective and owning Issue or task
- Status: `planned` | `in-progress` | `in-review` | `blocked` | `merge-ready` | `landed-unverified`
- Branch, PR, and head SHA when they exist
- Dependencies and relationship to other workstreams
- Latest verified result and remaining acceptance gap
- Owner when recorded and the time of the latest activity/status evidence; use `unknown` rather than inventing ownership or current activity
- OpenCode run/revision, delivery/acknowledgement/execution/collection/independent verification, authorized stop point, and evidence time when available; keep executor claims distinct from verified results
- Next concrete action and who or what can authorize it

Do not treat an open or assigned Issue as active work without evidence that work has started. Do not treat a merged PR as fully complete until its intended integration and acceptance conditions are satisfied.

## Preserve active gates

When an unresolved condition constrains the next action, retain its operational role:

- Target action
- Status: `stop` | `conditional` | `allowed`
- Unresolved prerequisite
- Clearing authority
- Admissible fallback
- Evidence snapshot
- Required revalidation immediately before action

Use `none` or `unknown` explicitly. A deadline, existing plan, apparent consensus, delegated ownership, or prior exception does not clear a gate.

## Locate the project in its design

Map accepted roadmap milestones, in their documented order and dependency structure, to capabilities and workstreams. Show completed, current, next, later, blocked, or unconfirmed stages and the exit conditions still unmet. Parallel tracks may have different current stages; do not manufacture a single linear phase. Explain:

- What foundation is already stable
- Which vertical slice or lifecycle stage is currently being built
- What remains disconnected or unvalidated
- Which later work is genuinely dependency-blocked
- Whether implementation order still matches the accepted design

Separate verified progress from percentage-style estimates. Do not invent a completion percentage unless the repository defines a measurable denominator.

If no accepted roadmap exists, explicitly say that the overall roadmap position is unknown. A component map or suggested sequence can help orient the user, but label it as an inference or proposal; never present it as the agreed roadmap.

## Establish what is planned next

Find the next action in the latest applicable user direction, accepted plan, or revalidated coordinator/task state. Check for superseding decisions and unresolved gates. A stale marker, old priority label, or high-value idea is not enough to establish a current plan. Surface conflicting plans instead of silently choosing one.

For each confirmed next action, state the action, intended result, owner when known, prerequisite or gate, and authorized stop point. Keep this to the immediate checkpoint per active track, not a newly generated implementation plan. If no next action is agreed or verifiable, say **not decided** or **unconfirmed** and why.

Optionally suggest a small number of next candidates, ordered by actual dependencies. Label them **recommendations, not agreed actions**. Never replace the current planned action with a recommendation, treat a status request as execution authority, or turn a reported blocker into an unsolicited approval request. If the user actually requests a decision, use the approval brief above.

## Produce the snapshot

Answer in the user's language. Start with a short orientation paragraph and the repository, ref/SHA, observation time, scope, and material evidence limitations. Then always include the following five views; write **none confirmed** or **unknown**, with a reason, rather than omitting an empty view. The Japanese labels below are the defaults for a Japanese request.

```markdown
## 1. 実装済みで利用可能な機能・内容
| 機能・内容 | いま何ができるか | 利用できる範囲・条件 | 根拠 |
|---|---|---|---|

## 2. 実装中の機能・内容
| 機能・内容 | 現在の作業・状態 | 残りの作業・ブロッカー | 担当・根拠（確認時点） |
|---|---|---|---|

## 3. 未着手の機能・内容
| 機能・内容 | 目指すこと | 予定・依存関係 | 根拠・確認範囲 |
|---|---|---|---|

## 4. 全体ロードマップでの現在地点
<全体のどこまで来ていて、今どこを作っているかを短く説明する。>
| 段階・マイルストーン | 到達目標 | 状態 | 完了条件との差分 | 根拠 |
|---|---|---|---|---|

## 5. 次にやろうとしていること
<確認できた予定を、行動・目的・担当・前提条件・停止点・根拠とともに示す。
未決定・未確認なら明記する。追加の提案は「提案（予定として未合意）」に分ける。>
```

Use compact prose or bullets in a view when a table would be mostly empty. Cover the major accepted capabilities and roadmap areas, explaining any omitted scope; an exhaustive Issue inventory should not obscure the project map. Add an **Other gaps / unconfirmed state** note where necessary so idle partial work and availability gaps do not disappear.

Keep supporting detail after the five views only when relevant:

- Gates/blockers: retain all seven fields from **Preserve active gates**; a concise reference from the next action can point here.
- Durable continuation: carrier, state status, update time, drift, and recovery implication; disclose `bootstrap` or a failed checkpoint rather than claiming it was saved.
- Evidence: use inline source links; add an index only if it improves navigation. Keep run IDs and recovery metadata in the supporting detail or owned durable fields.

## Preserve boundaries

- Do not modify code, Issue/PR content, branches, labels, projects, or releases. The only exception is the automatic update of the marked `codex-repo-state:v1` record on an already selected Issue/PR carrier; it must be read back and must never be treated as an approval.
- Do not perform a general defect hunt; use `@repo-review` when the goal is finding Bugs or Feature Requests.
- Do not generate an implementation plan; use `@patch-plan` or `@blueprint` after the user selects work.
- Use `@repo-handoff` for automatic persistence of the owned snapshot fields without overwriting coordinator runs or next actions. Do not replace `@handover` or preserve private conversation context in a public record.
- Ask monitoring/notification belongs to SwitchBoard, not this status snapshot. Do not infer a run failed because the connection is unavailable, or claim monitoring is configured without evidence.
- Route security-sensitive details to `@security-audit`; summarize only the existence and handling status of restricted work.

## Quality gate

Verify that:

- The snapshot is pinned to a branch, commit, and observation time.
- All five views are answered, including an explicit unknown or none-confirmed result where appropriate.
- Usable claims trace through the intended path and name their release/environment or supported checkout and prerequisites; code existence is not mistaken for user availability.
- Planned, partial, absent, and unknown states are not collapsed together.
- Active work is supported by current artifacts rather than open-Issue count alone; stale or idle partial work is not presented as ongoing activity.
- Not-started claims are limited to accepted scope and the inspected branches, PRs, and tasks; inaccessible sources are disclosed.
- Durable continuation records are located, pinned to a carrier, checked for drift, and automatically refreshed with the latest snapshot; missing carriers are reported as `bootstrap` rather than invented.
- Roadmap position is tied to documented milestones and their exit criteria; missing roadmaps and parallel tracks are represented honestly.
- The agreed next action, an unconfirmed plan, and assistant recommendations are distinguished; coordinator checkpoints and prior denials remain intact.
- Every active gate preserves its prerequisite, authority, fallback, evidence, and revalidation.
- Completed work is not presented as pending, and merged-but-unverified work is not overstated.
- A reader can identify the current architectural position and next decision without reading the entire repository history.
