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
