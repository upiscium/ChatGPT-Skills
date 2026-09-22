---
name: human-review
description: Inspect the current state of a software repository or development workflow and list only unresolved decisions, approvals, risk acceptances, or focused inspections that require human authority. Use when the user asks what they need to review, whether any human review remains, what is waiting for their judgment, or wants a Japanese human-review queue across Issues, Tasks, pull requests, plans, and blockers. Return an explicit no-review result when nothing qualifies. Do not perform a general code review or invent human gates for routine engineering work.
---

# Identify Human Review

Produce a concise, evidence-backed decision queue in Japanese. Surface only work that an agent cannot legitimately settle from authoritative repository contracts and current evidence.

## Establish the current snapshot

1. Identify the repository or explicitly bounded workflow. Ask only when the target cannot be inferred safely.
2. Resolve the inspected branch to an immutable commit SHA and record the observation time.
3. Inspect current repository instructions, accepted product and architecture contracts, Issues, Tasks, open pull requests, review reports, CI, development-loop ledgers, and blockers that are relevant to the target.
4. Prefer live repository state over conversation summaries. Mark inaccessible or stale evidence.
5. Restore and validate any `codex-repo-state:v1` marker on the relevant Issue/PR. Treat stale, conflicted, incomplete, and reconstructed records as evidence limitations, not as approvals.
5. Preserve separate review items when they have different authorities or can be decided independently. Combine repeated symptoms that require one underlying decision.

## Decide what requires a human

Include an item only when at least one of these conditions is supported by evidence:

- Product direction, priority, scope, non-goals, or user-facing behavior is materially ambiguous or conflicting.
- Competing architecture, public API, data model, migration, compatibility, dependency, or integration choices have materially different consequences and no accepted contract resolves them.
- Security posture, privacy, destructive action, irreversible migration, disclosure, licensing, cost, release, or operational risk requires explicit human acceptance.
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

When no qualifying item exists, return exactly:

```markdown
# Human Review

レビュー対象はありません。
```

Do not add optional suggestions, completed reviews, low-risk summaries, or an empty template after this result.

## Output the review queue

When at least one item exists, use:

```markdown
# Human Review

## HR-001: <レビュー対象の題名>

### 要約

- 人間の判断が必要な理由:
- Blockしているもの:
- 現行実装・判断の問題:
- 判断期限・発火条件: なし | 不明 | <具体的条件>

### レビュー対象

<人間が答えられる一つの具体的な質問。必要なら確認すべきファイル、PR箇所、契約を併記する。>

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

### 根拠

- Snapshot:
- Evidence:
```

Omit the options table only when the task is a focused inspection with a binary pass/fail contract rather than a design choice. Keep each item compact enough that the user can decide without reading the entire repository history.

Order items by blocking dependency, then risk and leverage. Do not use urgency alone to inflate importance.

## Integrate with related skills

- Consume `Human decisions required`, `Human review mode`, risk tier, gate contracts, and focused review locations from `@branch-review` and `@dev-loop` when available, but verify them against the current PR head and repository state.
- Consume the durable decisions and gate fields from `@repo-handoff`; do not invent a review item merely because a record is missing.
- Use `@repo-status` evidence to locate active work, but re-evaluate whether each blocker truly requires human authority.
- Direct code-quality investigation to `@branch-review` or `@repo-review`; include only their unresolved human-owned decisions here.
- After the user decides, report the decision and its exact scope. Do not modify code, Issues, PRs, or gates unless the user separately asks for that action.

## Quality gate

Verify that:

- Every listed item requires human authority rather than more agent work.
- Every item is current for the recorded commit or PR head.
- The question is concrete and answerable.
- The blocked action and consequence of delay are explicit without invented urgency.
- Options are materially distinct and recommendations are clearly advisory.
- The safe fallback does not bypass the unresolved decision.
- Duplicate manifestations of one decision are consolidated.
- If no item qualifies, the response contains only the required no-review result.
