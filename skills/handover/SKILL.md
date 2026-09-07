---
name: handover
description: Create a self-contained handover for continuing the current conversation in a new chat or with another agent. Use when the user asks to hand over, transfer, continue elsewhere, preserve context, or prepare a continuation prompt; also use or recommend it proactively at a safe checkpoint when a long technical/development session is approaching context degradation.
---

# Create a Handover

Produce a copy-ready handover that lets a new chat continue safely without access to the original conversation.

## Trigger policy

Use this skill when the user explicitly asks for a handover. In long development, review, investigation, or infrastructure sessions, also recommend `@handover` + New Chat before context quality becomes unsafe.

Proactive trigger signals include:

- many consecutive `next` / review / correction / merge cycles;
- several active Issues, Tasks, PRs, worktrees, branches, or immutable SHAs that are becoming hard to distinguish;
- repeated compaction or loss of older exact details;
- a natural post-merge, post-finalization, post-release, or other terminal checkpoint before another substantial stage;
- evidence that the next action could be misrouted if historical context is lost.

Warn early enough that a complete handover can still be produced. Do not wait for the next action to fail from context loss.

Do not interrupt an in-flight write-producing lifecycle transition when the current chat can safely finish, verify, and record its terminal evidence first. Prefer the nearest safe checkpoint.

## Build the handover

1. Infer the user's actual objective and only the scope that still matters.
2. Preserve decisions, constraints, terminology, user preferences, completed work, current state, failures, unresolved questions, and the exact next action.
3. Distinguish confirmed facts from hypotheses, recommendations, and unknowns.
4. For repository/development work, preserve live identifiers needed for continuation:
   - repository;
   - default/integration branch;
   - current main/base SHA;
   - Issue/Task/PR numbers and URLs;
   - branch/worktree ownership;
   - exact reviewed/published/merge SHAs;
   - lifecycle state and terminal evidence;
   - CI/review/security results;
   - destructive operations still requiring explicit approval.
5. Record exact commands only when the next chat truly needs them; otherwise describe the canonical API/surface.
6. Preserve the reason behind unusual constraints so the next chat does not repeat a rejected workaround.
7. Remove abandoned discussion branches and repetition that do not affect continuation.
8. Never invent missing context; label uncertainty explicitly.
9. Exclude secrets and authentication material. Replace necessary references with `[credential omitted]`.
10. Write in the language primarily used by the user unless requested otherwise.

## Development-loop handover

When handing over an active `@dev-loop`, include a compact loop ledger:

```markdown
- Repository:
- Stage:
- Base/merged commit:
- Execution backend/version:
- Active wave:
- Workstreams:
- Issue/Task/PR mapping:
- Exact PR head(s):
- Review verdict(s):
- Base sensitivity:
- Merge/finalization state:
- Human decisions/approvals still required:
- Next action on `next`:
- Reverify before action:
```

For multiple workstreams, preserve independent status rather than collapsing the batch into one state.

If a previous PR/Task was intentionally frozen, superseded, blocked, or awaiting a dedicated safe cleanup path, say so explicitly and state what must not be done.

## Output requirements

Return only the handover in Markdown. Make it self-contained and ready to paste into a new chat.

Begin with:

```markdown
# 引き継ぎ

## 新しいチャットへの依頼
```

State the concrete action the next chat should perform as a direct request.

Then include only relevant sections from:

```markdown
## 目的
## 背景
## 現在の状況
## 確定事項・決定
## 制約・要件
## これまでに試したこと
## 未解決事項
## 次に行うこと
## 参照情報
```

For development/project work, use relevant subsections under `## 参照情報`:

```markdown
### リポジトリ・ブランチ・コミット
### Issue・Task・PR
### Worktree・実行権限
### ファイル・成果物
### 環境・依存関係
### 実行・検証結果
### エラー・ログ
```

Omit empty sections. Prefer concise bullets while retaining enough causal context to explain important decisions.

End with `## 注意事項` only when there are stale facts, uncertainty, security omissions, destructive actions requiring approval, blocked/superseded state, or actions the next chat must not repeat.

## Quality gate

Before responding, verify that:

- the next chat can identify the goal and immediate next action without the old conversation;
- completed work is not presented as pending;
- rejected approaches are not presented as recommendations;
- exact SHAs/Issue/Task/PR identities are preserved where they control the next action;
- frozen or superseded work is clearly marked and cannot be accidentally reused;
- destructive operations retain their explicit approval requirement;
- facts, inferences, and unknowns are distinguishable;
- references are precise enough to locate;
- no secret or irrelevant conversational detail is included.
