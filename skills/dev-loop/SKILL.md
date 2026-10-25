---
name: dev-loop
description: Align user requirements, prepare approved Issue specifications, and evaluate KAGARI delivery against original user goals. Legacy OpenCode orchestration remains explicit-only.
---

# Coordinate the Development Loop

Arca defaults to human-aligned requirements, Issue specifications and user-goal acceptance. KAGARI owns authorized Task execution. For an explicitly selected legacy run, use `@opencode-bridge` for authorized OpenCode transport; if unavailable before a send, give a complete manual packet, never duplicate an uncertain delivery. For the new requirements/acceptance lane, combine authorized read-only and specification steps without an arbitrary one-stage limit; existing legacy OpenCode runs retain their exact stage boundaries. Never create unapproved external effects, commit/push, Merge or release; preserve exact grant and the next human-owned boundary. KAGARI owns native Task/Ask; MUSUBI is its mobile-first UI. Legacy SwitchBoard is not a new-MVI prerequisite.

## Default — user requirements to accepted results

Use [requirements and acceptance](references/requirements-and-acceptance.md) for new requests. Arca aligns original user intent through blueprint, produces human-approved Issue-level specifications through issue-filer, and evaluates delivered user-visible behavior against original goals through repo-review. KAGARI owns Issue execution, tests, technical review and correction.

Require first human alignment on user-visible behavior and in/out scope, then a focused second alignment on the exact selected Issue set before implementation authorization. Do not invent a KAGARI adapter or dispatch if the supported CLI/API is unverified; report not-dispatched.

Stop at human-owned material requirements, selected Issue execution, next phase, Merge or Plugin release. Routine bounded specification steps may proceed together. Do not run Arca's own Task Ask watcher or duplicate technical reviewer.

## Legacy explicit-only path — choose the required stage

- **Status, repeated Next, or observation:** read only the current Issue/PR/run delta; do not load a full Skill chain or record an unchanged checkpoint. For delivery/collection, load [collection](references/collection.md).
- **New work or planning:** load [governance](references/governance.md) and [planning and dispatch](references/planning-and-dispatch.md). For executable packets, also read the relevant `@patch-plan` and `@repo-handoff` reference.
- **Independent review, PR, Merge or release:** load [review and release](references/review-and-release.md) and the relevant review/merge contract. Review readiness never grants Merge.
- **Detailed recording/cleanup:** load [ledger and quality](references/ledger-and-quality.md). A newly created persistent resource needs a documented owner and cleanup trigger.

## Non-negotiable working rules

Reuse previously loaded Skill instructions and verified state. Limit each tool response to pertinent fields, bounded log tails or relevant file ranges. Model, effort and variant follow OpenCode configuration: never override them on dispatch.

**Always save/read back dispatch intent before sending**, correlate the actual session/receipt and reconcile uncertain sends without duplicate dispatch. Preserve the human-owned choices for material goals, risk, architecture and resource allocations. Do not demand another Ask for routine work inside an existing grant.

For isolated MOCK-only MVI, apply the approved threat model and minimum scope; defer production-only hardening. Never disclose secrets, bypass execution grants, execute destructive or external effects without authority, silently merge or release, or treat unknown risk as proven safe. A material change to the accepted threat model remains human-owned.

Old OpenCode stage-specific behavior is preserved only for explicitly requested legacy continuation. New default work never interprets generic Next as authorization for KAGARI execution.
