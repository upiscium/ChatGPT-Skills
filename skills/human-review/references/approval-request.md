# Explain a human approval request

Read before requesting a human decision, consequential permission, or execution of a user-run action. Use this as `@human-review approval-brief` from another workflow without invoking a full review queue. Apply the same content to ordinary chat and any permitted approval UI; a button or tool dialog does not replace the explanation.

## Before asking

1. Check the current request, prior decisions and applicable authority. Continue already authorized work without asking again. This reference changes how a necessary request is explained, not which operations need approval.
2. Complete authorized investigation, preparation and validation so the proposal is concrete and reviewable. Do not perform the gated action in order to prepare its explanation.
3. Establish the exact target, actor, operation, artifact revision and evidence. Read available evidence to resolve material uncertainty; do not ask for blanket approval of an unknown scope.
4. Identify why this decision needs the human. When a skill, AGENTS.md, repository policy or automatic approval review caused the stop, name the source and summarize the applicable requirement. For an automatic rejection, identify the rejected action and stated reason; do not recast it as an unexplained request to retry.

## Four required fields

Put these fields in the same user-facing request, before the question or action command. For chat, make the final message self-contained; for a permitted approval UI, include the brief in its accompanying explanation. Do not rely on an earlier progress update. Use the user's language; use these labels for Japanese. One or two concrete sentences per field usually suffice.

```markdown
- **今回やった内容**: <実際に調査・作成・変更・検証した内容と結果。未実施や未確認の重要部分を区別する。>
- **今回承認してほしい内容**: <誰が、どの対象・版に、何を行い、どこで止まるか。判断が必要な理由と根拠。承認後にこちらが実行するのか、ユーザー自身が実行するのかも明示する。>
- **承認によって影響がある範囲**: <変わる機能、対象リポジトリ・環境・利用者・データ・公開先など。関連する停止、費用、削除、互換性や復旧の制約を具体的に記載する。>
- **否認した場合の対応**: <実行しない対象、保持する成果物や状態、次に可能な修正・代替・終了。代替にも承認が必要なら、その旨を区別する。>

<この対象と範囲に限定した、一つの答えられる承認・判断の質問。>
```

Explain effects in plain language before identifiers. A PR number, SHA, path, raw diff, gate label or command alone does not explain what changes. Keep relevant immutable references/links available as evidence, without forcing the user to open them to understand the four fields. Distinguish implemented, inspected, executor-reported and independently verified work; never turn a prepared plan into a completed implementation claim.

Name only material impacts supported by evidence. State an unresolved impact as unknown with its consequence; do not invent downtime, costs, risks or rollback guarantees. Explain recovery limits for a consequential change when known. Avoid unrelated disclaimers and long lists of unaffected systems.

Scope approval to the stated action and revision. Design acceptance, dispatch, implementation, publication, risk acceptance, merge and cleanup can authorize different effects; do not bundle them behind “approve” or “next”. An explicitly requested combined grant may cover multiple named actions when their effects and stop point are clear. Independently decidable requests need separate IDs and briefs; shared background may be stated once in the same message without losing each decision's four fields.

## Denial, deferral and later continuation

- Treat denial as a valid scoped decision. Do not perform the denied action, route it through another tool, discard completed work or roll back unrelated work by implication. Continue only separable work that is still authorized.
- State the concrete next handling: retain the prepared artifact, revise a named part within the grant, propose a different bounded option, or end that action. Do not automatically execute an unapproved alternative or promise later background work.
- Distinguish denial from deferral/no response. Without a response, leave the affected action paused and preserve results; silence and elapsed time are never approval.
- Record the request ID, target/revision, four-field explanation and human decision through the caller's existing authorized state mechanism. Keep security-sensitive details in the approved private surface. A public marker may carry only a safe summary and resolvable private reference.
- At resume, honor a recorded denial; `next` alone does not reopen it. Preserve previously granted authority too. A material change to the request, target or effects requires revalidation and a newly explained decision for the changed scope, not blanket reapproval of unaffected work.
- An old “please approve” request without a recoverable action/scope cannot give an ambiguous “yes” or “next” a new scope. Reconstruct evidence, present the missing explanation and ask only for the unresolved decision. Do not invalidate a prior explicit, concrete grant merely because its formatting differed.

## Compact example

For a prepared publication request, adapt only verified facts:

- **今回やった内容**: Issue #42の修正案と検証結果をまとめ、固定した差分の独立レビューを完了しました。公開作業は未実施です。
- **今回承認してほしい内容**: レビュー済みの差分について、OpenCodeが対象リポジトリでcommit・pushし、Draft PR作成まで進める許可です。現在の実行範囲は修正と検証までのため、公開操作の判断が必要です。
- **承認によって影響がある範囲**: 修正内容と検証結果が対象ブランチとDraft PRに掲載され、そのリポジトリの閲覧者が読める状態になります。
- **否認した場合の対応**: 公開せず、差分と検証結果を保持します。必要な修正があれば、その範囲を確認して案を更新します。

「このレビュー済み差分のDraft PR作成までを承認しますか？」のように、対象の実際の参照を添えて尋ねる。Example IDs are illustrative, never live targets or evidence.
