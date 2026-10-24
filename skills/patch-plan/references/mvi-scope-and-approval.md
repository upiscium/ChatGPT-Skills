## Minimum viable implementation planning

Size the packet to the approved target and current execution stage. For an isolated MOCK-only MVI, prioritize end-to-end minimum acceptance criteria, contained effects, deterministic regression checks and measured evidence. Do not add production identity, attack resistance against excluded privileged actors, extra encryption/signature layers, high availability or migration infrastructure unless the approved contract specifically requires them.

Mark each proposed extra safeguard `in-scope-required`, `production-deferred`, or `out-of-scope` with its threat assumption and impact. Only in-scope failures block the MVI. A newly proposed real external effect, destructive operation, sensitive-data exposure or material change to the accepted threat model requires the applicable original human authority. Keep compact packets self-contained, including exact allowed operations, stop point, ACs, real resource identities if any, and evidence; omit inapplicable boilerplate rather than inventing fields.

Use the relevant sections of [references/patch-plan-template.md](patch-plan-template.md) and `@repo-handoff`'s `references/execution-contract.md` only when producing an execution-ready plan. Reuse previously loaded text, and include only applicable resolved contract fields in the packet; an executor must not need these installed skills.

Read `@change-review`'s `references/verification.md` when specifying tests or completion evidence. Copy the applicable rules into the packet. See [references/superpowers-notice.md](superpowers-notice.md) for the adapted planning source.

## Explain any human approval request

When actually requesting a human decision or handing off a user-run action, use `@human-review approval-brief`. Include **今回やった内容**, **今回承認してほしい内容**, **承認によって影響がある範囲**, and **否認した場合の対応** in the same message. Name the action/actor, target/revision and reason for the gate; distinguish completed work from proposals. Use the brief only to explain a needed decision, without an additional queue scan/write or confirmation for already authorized work. Preserve the stated denial response at continuation.
