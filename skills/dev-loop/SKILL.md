---
name: dev-loop
description: Coordinate Arca planning, authorized OpenCode delegation, independent change review and human-executed merge through one verified checkpoint at a time. Use to start, resume or advance parallel Issue workstreams with next, collect a run, or generate only guarded Ready/Merge commands. Ask monitoring belongs to SwitchBoard, not this skill.
---

# Coordinate the Development Loop

Orchestrate approved Issue work through OpenCode; Arca does not implement or silently dispatch. Use `@opencode-bridge` for authorized transport; if unavailable before a send, give a complete manual packet, never duplicate an uncertain delivery. Keep **one substantive stage per response** until an explicitly approved broader workflow exists. Never create unapproved external effects, commit/push, Merge or release; preserve exact grant and the next human-owned boundary. SwitchBoard/MUSUBI handles ongoing Ask monitoring.

## Fast path — choose one stage

- **Status, repeated Next, or observation:** read only the current Issue/PR/run delta; do not load a full Skill chain or record an unchanged checkpoint. For delivery/collection, load [collection](references/collection.md).
- **New work or planning:** load [governance](references/governance.md) and [planning and dispatch](references/planning-and-dispatch.md). For executable packets, also read the relevant `@patch-plan` and `@repo-handoff` reference.
- **Independent review, PR, Merge or release:** load [review and release](references/review-and-release.md) and the relevant review/merge contract. Review readiness never grants Merge.
- **Detailed recording/cleanup:** load [ledger and quality](references/ledger-and-quality.md). A newly created persistent resource needs a documented owner and cleanup trigger.

## Non-negotiable working rules

Reuse previously loaded Skill instructions and verified state. Limit each tool response to pertinent fields, bounded log tails or relevant file ranges. Model, effort and variant follow OpenCode configuration: never override them on dispatch.

**Always save/read back dispatch intent before sending**, correlate the actual session/receipt and reconcile uncertain sends without duplicate dispatch. Preserve the human-owned choices for material goals, risk, architecture and resource allocations. Do not demand another Ask for routine work inside an existing grant.

For isolated MOCK-only MVI, apply the approved threat model and minimum scope; defer production-only hardening. Never disclose secrets, bypass execution grants, execute destructive or external effects without authority, silently merge or release, or treat unknown risk as proven safe. A material change to the accepted threat model remains human-owned.

Full stage-specific behavior and exceptions are preserved in the linked references.
