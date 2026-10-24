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
