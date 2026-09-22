---
name: btw
description: Answer a one-off side question about the current session without advancing, mutating, or contaminating the main task. Use for `/btw`, `@btw`, “by the way”, quick context checks, terminology questions, or a small tangent during an active implementation, review, or development loop.
---

# Answer a Side Question

Treat this as a single-turn, non-interrupting side channel. Answer from the context already available in the current session and then return control to the main task. Do not change the main task's stage, ledger, plan, files, branches, Issues, pull requests, Tasks, or approvals.

The behavior mirrors Claude Code's `/btw`: the question is a disposable side lookup, not a second conversation. The result must not become an implicit instruction for the main task. In this environment a response is visible in the chat, so preserve the same semantic boundary by explicitly declaring that the main state is unchanged.

## Scope and tools

- Prefer the supplied conversation context, visible files, and already collected evidence.
- Do not call tools, browse, inspect a repository, or query GitHub for a pure `btw` question. This keeps it fast and prevents a side question from changing the evidence basis of the main task.
- If the answer requires live state, a new file read, a web lookup, or a mutation, say that it cannot be verified in the side channel and offer the exact main-task request that would be needed. Do not guess.
- Never edit code, create or update Issues/PRs, run commands, send messages, merge, or dispatch an agent from `btw`.

## Answer procedure

1. Capture the main-task snapshot mentally: repository/branch or project, current stage, active workstream, unresolved gate, and next announced action. If any are unknown, preserve `unknown`.
2. Read only the side question. Answer it directly and briefly; distinguish fact, inference, recommendation, and unknown.
3. State the impact on the main task as exactly one of:
   - `なし`: the answer does not change scope or decisions;
   - `参考`: useful context, but no action is authorized;
   - `判断候補`: it may affect a decision, but the user must explicitly promote it to the main task;
   - `要確認`: live evidence or a human decision is required outside `btw`.
4. End with the unchanged main-task stage and next action. Do not add a new plan or a follow-up question unless the side question itself is incomplete.

## Explicit promotion

If the user asks to save, implement, file, review, or otherwise promote the tangent, do not do it inside `btw`. Return a short promotion proposal and wait for a separate explicit request. For GitHub-backed work, suggest `@repo-handoff` with `record` for a note on an existing canonical Issue/PR, or the appropriate workflow such as `@issue-filer`, `@patch-plan`, or `@dev-loop`. Creating a new Issue or comment needs its own authorization.

If the user invokes `btw` with no question, report the usage and, when available in the visible session, the most recent side question and its answer. Do not reconstruct hidden history or add the empty invocation to the main ledger.

## Output format

Return only:

```markdown
# BTW

## 回答
<direct answer; concise, with uncertainty labeled>

## 本線への影響
- 判定: `なし` | `参考` | `判断候補` | `要確認`
- 記録・変更: `なし` (default)

## 本線の状態
- Stage: <unchanged stage or unknown>
- Next action: <unchanged announced action or unknown>
```

If live evidence is required, replace the answer with the smallest safe explanation and the exact next main-task request, while keeping `記録・変更: なし`.

## Quality gate

Verify that:

- the answer uses only already available context unless the user explicitly exits `btw`;
- no tool, write, approval, or workflow transition occurred;
- the main stage and next action are unchanged and clearly shown;
- speculation is labeled and no side comment is silently promoted to a requirement;
- a user can continue the main task immediately after reading the side answer.
