---
name: human-review
description: Explain concrete approvals, identify unresolved human decisions, and independently audit missed decisions in bounded repository history. Use approval-brief for an approval or user-run action handoff, review-queue for current human judgment across Issues/PRs/plans, and missed-decision-audit for retrospective scope/architecture milestones or historical samples. Supply goal-alignment and per-turn decision-sweep guidance to repository workflows. Do not invent gates for routine or already authorized work.
---

# Identify Human Review

Produce a concise, evidence-backed approval brief, decision queue or independent retrospective audit in the user's language. Surface only work that an agent cannot legitimately settle from authoritative contracts and current evidence.

For an accepted isolated MVI, judge security and assurance choices against its **documented threat model and actual effect scope**. Record production-only hardening as deferred rather than blocking the MVI, unless the user changes the agreed boundary. Do not treat a reviewer severity label as automatic permission to expand the MVI or demand new approval. Preserve explicit material risk, irreversible/external action and release gates.

## Optional feature contracts — no extra gates

When a feature spans several Issues or has a material user-visible scope/acceptance change, use [Feature Contract](references/feature-contract.md) to bind the original approved goal, only the necessary [Scope Change](references/scope-change-gate.md) to route material deviations, and [Feature Acceptance](references/feature-acceptance-gate.md) to distinguish KAGARI technical completion from original user-goal success. For a bounded already-approved Issue, reuse its existing goal/ACs rather than creating a new Epic, contract database, interview or repeated approval. These references do **not** authorize KAGARI dispatch, Merge, release or Plugin update. KAGARI owns Task technical repair and runtime Ask; MUSUBI is its UI.

## Select the operation

- `approval-brief`: explain a concrete decision or action already identified by the calling workflow. Read [references/approval-request.md](references/approval-request.md) and return its four-field brief in the user's language. Use the supplied current evidence and resolve only material gaps. Do not start a repository-wide review, create a queue, write a checkpoint or perform the proposed action merely to format the request; the caller keeps its existing authority and recording rules.
- `review-queue`: inspect the selected repository/workflow using the steps below. For every qualifying item, read the same reference and include all four fields before asking for judgment. Automatically checkpoint only under the existing queue workflow's recording policy.
- `missed-decision-audit`: read [references/missed-decision-audit.md](references/missed-decision-audit.md) and perform its bounded independent retrospective review. Do not substitute the current queue or rely only on executor flags. Return a pinned delta to the existing writer; keep substantive actions read-only.

This format explains a necessary decision; it never creates an additional approval requirement. Reuse applicable prior authorization. Finish already authorized preparation and verification before asking so the user decides on a concrete result.

## Shared checks for calling workflows

Read [references/goal-alignment.md](references/goal-alignment.md) at new workstreams, material scope/design/resource changes, important PR/release milestones and repository status. Read [references/decision-sweep.md](references/decision-sweep.md) before final responses of substantive repository turns, including a review-queue result. These checks inspect actual deltas even without `NEEDS_DECISION`; exempt `@btw`, unrelated conversation and unchanged pure observations. They are declarative guidance, not a guaranteed runtime hook or background Ask monitor. Resolve references by installed skill name; opaque installation directory IDs and sibling paths are not portable.

For `approval-brief`, use supplied evidence only and preserve formatter-only behavior; the calling workflow owns any sweep, gate and recording. For `missed-decision-audit`, follow the audit reference rather than the queue procedure below. The remaining snapshot/queue steps apply to `review-queue`.

## Establish the current snapshot

1. Identify the repository or explicitly bounded workflow. Ask only when the target cannot be inferred safely.
2. Resolve the inspected branch to an immutable commit SHA and record the observation time.
3. Inspect current repository instructions, accepted product and architecture contracts, Issues, Tasks, open pull requests, review reports, CI, development-loop ledgers, and blockers that are relevant to the target.
4. Prefer live repository state over conversation summaries. Mark inaccessible or stale evidence.
5. Restore and validate any `codex-repo-state:v1` marker on the relevant Issue/PR. Treat stale, conflicted, incomplete, and reconstructed records as evidence limitations, not as approvals.
6. Preserve separate review items when they have different authorities or can be decided independently. Combine repeated symptoms that require one underlying decision.
7. Persist changed human-gate fields through `@repo-handoff` when the queue introduces or resolves a material decision; unchanged queue observations reuse the previous marker. Preserve unrelated runs and pending actions; batch workers return deltas to the coordinator. Read back any performed write. Recording never approves or changes the underlying work.

## Decide what requires a human

Include an item only when at least one of these conditions is supported by evidence:

- Product direction, priority, scope, non-goals, or user-facing behavior is materially ambiguous or conflicting.
- Competing architecture, public API, data model, migration, compatibility, dependency, or integration choices have materially different consequences and no accepted contract resolves them.
- A material change to the **accepted, in-scope** security/privacy posture; destructive action, irreversible migration, disclosure, licensing, cost, release, or a genuinely new critical operational risk requires explicit human acceptance.
- A medium- or high-risk PR review identifies a specific contract, location, or trade-off that needs focused human confirmation.
- An existing gate explicitly names the user or another human authority as the only entity that may clear it.
- The user explicitly requested a human review of a named artifact or decision.

Do not include:

- Routine implementation, refactoring, test writing, linting, CI repair, or defect correction when the accepted contract already determines the answer.
- A PR merely because it exists, is Draft, or has not received a human comment.
- Missing permissions, unavailable tools, authentication, or environment failures unless the user must choose among meaningful alternatives or authorize a consequential action.
- Questions that further repository inspection can answer mechanically.
- Decisions already resolved by an authoritative source for the current artifact revision.
- Speculative future choices that do not block or materially affect current work.
- Production-only security hardening or out-of-threat-model findings for a MOCK-only MVI, unless they expose an in-scope effect, agreed invariant, or material change requiring user risk acceptance.
- Low-risk `summary-only` review when there is no unresolved judgment; report it only if the user explicitly asks to inspect that PR.

Durable-state drift alone is not a human decision. List it only when the user must choose a carrier, resolve conflicting records, accept a risk, or decide whether to proceed despite the drift.

The purpose is to reduce human review load. Do not manufacture a review queue to appear thorough.

## Define each review item

For every qualifying item, determine:

- A stable ID `HR-001`, `HR-002`, and so on
- The exact decision or inspection the human must perform
- Why human authority is required
- What action, workstream, release, or merge is blocked
- The problematic or ambiguous part of the current implementation or decision
- Decision deadline or trigger, if one actually exists
- Available options and their material trade-offs
- A recommended decision, rationale, and confidence
- A safe default or fallback if the review is deferred
- Work actually completed, the exact approval and actor, affected scope, and the response to denial, following the shared approval brief
- Evidence pinned to current Issues, PR heads, commits, files, checks, or review findings

Phrase the review target as an answerable question. Avoid vague requests such as “please review the architecture” or “check whether this looks good.” Name the smallest contract, behavior, diff location, or trade-off that enables a decision.

## Preserve the gate

When the item blocks an action, retain:

- Target action
- Status: `stop` | `conditional`
- Unresolved prerequisite
- Clearing authority
- Admissible fallback
- Evidence snapshot
- Revalidation required before the blocked action

Do not weaken a gate because of a deadline, existing plan, apparent consensus, delegated ownership, or precedent. A recommendation is not approval.

## Output no-review state

In `review-queue` mode, when no qualifying item exists, return exactly:

```markdown
# Human Review

レビュー対象はありません。
```

Do not add optional suggestions, completed reviews, low-risk summaries, or an empty template after this result.

## Output the review queue

In `review-queue` mode, when at least one item exists, use:

```markdown
# Human Review

## HR-001: <レビュー対象の題名>

<references/approval-request.md の4項目を、この判断対象について具体的に記載する。>

### 選択肢

| 選択肢 | 得られるもの | コスト・リスク | 後続への影響 |
|---|---|---|---|
| A | | | |
| B | | | |

### 推奨

- 推奨判断:
- 理由:
- 確信度: high | medium | low

### 保留時の扱い

- 安全な既定動作:
- 再開条件:
- 判断期限・発火条件: なし | 不明 | <根拠のある具体的条件>

### 根拠

- Snapshot:
- Evidence:
```

Omit the options table for a simple approval or focused binary inspection. Keep recommendations advisory and each item compact enough to decide without the repository history. Never replace the four-field brief with a link, gate ID, command, prior commentary or a bare request to approve.

Order items by blocking dependency, then risk and leverage. Do not use urgency alone to inflate importance.

## Integrate with related skills

- Consume decisions, risk, gate contracts and focused locations from `@change-review` and `@dev-loop`; bind each item to the current frozen snapshot or PR head and instruction revision.
- Consume the durable decisions and gate fields from `@repo-handoff`; do not invent a review item merely because a record is missing.
- Use `@repo-status` evidence to locate active work, but re-evaluate whether each blocker truly requires human authority.
- In the default Arca → KAGARI workflow, route implementation defects, code-quality investigation, technical review, and ordinary corrective work to the owning KAGARI Task Orchestrator. Arca retains original-user-goal acceptance and only unresolved Human-owned decisions; it does not run a duplicate technical review loop. `@change-review` and the legacy technical-audit mode of `@repo-review` are available only when explicitly requested.
- KAGARI owns native Task/Ask monitoring, current pending state and answer delivery; MUSUBI presents the same Task/Ask interface. SwitchBoard observation applies only to an explicitly selected legacy OpenCode workflow, not the default vNext path. A notification alone is not a new Human gate or approval.
- After the user decides, report the decision and its exact scope. Do not modify code, Issue/PR content, or gates unless the user separately asks for that action. The automatic `codex-repo-state:v1` marker update on an existing carrier is the sole recording exception; if unavailable, mark it `pending-write`.
- Preserve `denied` and `deferred` separately from `open` and `approved`, with the request/snapshot and decision source. Follow the stated denial response within existing authority; do not silently substitute another action or reopen the same denied request on `next`. A changed proposal needs a new scope/revision and explanation of the change.
- Preserve an exact no-review final response. If recording is unavailable, disclose `bootstrap`/`pending-write` and its consequence in commentary before that final response; do not invent a review item to carry the storage failure.

## Quality gate

Verify that:

- Every listed item requires human authority rather than more agent work.
- Every item is current for the recorded commit or PR head.
- The question is concrete and answerable.
- Every actual approval request includes completed work, requested action, affected scope and denial response in the same user-facing message; proposed work and verification limits are explicit.
- The blocked action and consequence of delay are explicit without invented urgency.
- Options are materially distinct and recommendations are clearly advisory.
- The safe fallback does not bypass the unresolved decision.
- Duplicate manifestations of one decision are consolidated.
- In `review-queue` mode, if no item qualifies, the response contains only the required no-review result.
- The latest review-queue snapshot is automatically saved and read back, or is explicitly marked `bootstrap`/`pending-write` with the recovery consequence.
- `approval-brief` alone performed no queue scan, checkpoint write or proposed action, and added no redundant confirmation.
