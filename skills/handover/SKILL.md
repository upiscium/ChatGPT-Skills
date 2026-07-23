---
name: handover
description: Create a self-contained handover for continuing the current conversation in a new chat or with another agent. Use when the user asks to hand over, transfer, continue elsewhere, preserve context, prepare a continuation prompt, or summarize the current state for another chat. Adapt automatically to general conversations, technical work, investigations, and development projects.
---

# Create a Handover

Produce a copy-ready handover that lets a new chat continue the work without access to the original conversation.

## Build the handover

1. Infer the user's real objective and the scope that still matters.
2. Select the appropriate detail level:
   - Use the general format for advice, planning, research, troubleshooting, and ordinary conversations.
   - Add the project section for software development, infrastructure, repository work, document creation, or other artifact-based work.
   - Combine both when the conversation spans them.
3. Preserve decisions, constraints, terminology, user preferences, completed work, current state, failures, and unresolved questions.
4. Distinguish confirmed facts from hypotheses, recommendations, and unknowns.
5. Record exact identifiers only when useful: filenames, paths, branches, commits, commands, errors, versions, URLs, issue numbers, and configuration values.
6. Remove repetition, abandoned branches of discussion, and details that do not affect continuation.
7. Never invent missing context. Label material uncertainty explicitly.
8. Exclude secrets and authentication material. Replace any necessary mention with a description such as `[credential omitted]`.
9. Write in the language primarily used by the user unless they request another language.

## Output requirements

Return only the handover in Markdown. Make it self-contained and ready to paste into a new chat. Do not add commentary before or after it.

Begin with:

```markdown
# 引き継ぎ

## 新しいチャットへの依頼
```

In that section, state the concrete task the next chat should perform. Write it as a direct request, not as a description of the old conversation.

Then include only the relevant sections from this list:

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

For development or project work, add relevant subsections under `## 参照情報`:

```markdown
### リポジトリ・ブランチ・コミット
### ファイル・成果物
### 環境・依存関係
### 実行・検証結果
### エラー・ログ
```

Omit empty sections. Prefer concise bullets, but retain enough causal context to explain why important decisions were made. Include code or logs only when their exact text is necessary; otherwise summarize them.

End with:

```markdown
## 注意事項
```

Use this section only for uncertainty, stale information, security omissions, assumptions that need verification, or actions the next chat must not repeat. Omit it when none apply.

## Quality check

Before responding, verify that:

- The next chat can identify the goal and immediate next action.
- Completed work is not presented as pending.
- Rejected approaches are not presented as recommendations.
- Facts, inferences, and unknowns are distinguishable.
- References are precise enough to locate.
- No secret or irrelevant conversational detail is included.
