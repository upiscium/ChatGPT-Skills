---
name: patch-plan
description: Convert selected filed GitHub Issues into dependency-aware OpenCode execution packets with explicit operation grants and stop points. Use to plan parallel implementation through the live repository Agent Core lifecycle or isolated generic worktrees, including prepublication delivery without assuming commit, push or PR authorization.
---

# Plan Review Patches

Convert only selected, filed Issues and approved Feature Contracts into bounded, self-contained OpenCode execution plans. Arca plans; OpenCode implements inside its grant. Publication, Merge, real external effects and material human-owned changes remain separate decisions.

## Fast path — load references on demand

1. For a new plan or scope change, read [MVI scope and human decisions](references/mvi-scope-and-approval.md), then [target and backend selection](references/target-and-backend.md).
2. For runnable work units, read [workstream planning](references/workstream-planning.md). Choose **one** backend: [Agent Core](references/agent-core.md) **or** [generic worktree](references/generic-worktree.md), not both.
3. For output, evidence and stop points, read [delivery and quality](references/delivery-and-quality.md). Include exact authority/ACs/resource ownership in each executable packet; do not require the executor to read Arca Skills.

## MVI-first and authority

For isolated MOCK-only MVI, prove the accepted functional minimum with effect isolation and meaningful tests. Classify hardening `in-scope-required`, `production-deferred`, or `out-of-scope`; **Only in-scope failures block the MVI**. Real effects or materially changed accepted risks still require the responsible human authority.

Use the relevant sections of reference files only when producing an execution-ready plan; omit inapplicable boilerplate, never omit a required execution grant or stop point. Restore the existing carrier, record changed planning state (reuse the existing marker without writing for an identical plan), and do not automatically commit/push/create PR.
