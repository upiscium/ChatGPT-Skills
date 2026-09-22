---
name: repo-status
description: Produce an evidence-backed snapshot of a software repository's current product and development state, including implemented, partial, planned, and absent capabilities; active Issues and pull requests; blockers; and the repository's position within its documented architecture or roadmap. Use when the user asks what exists now, what remains, what is being worked on, where the project currently stands, or requests a comprehensive repository status summary. Do not use as a defect-finding review or a conversation handover.
---

# Summarize Repository Status

Build a current, read-only map of the repository. Explain what the product can do now, what work is active, and how that work fits the intended system.

## Pin the snapshot

1. Identify the repository, default or requested branch, and review scope.
2. Resolve the inspected state to an immutable commit SHA and record the observation time.
3. Read repository instructions, architecture and design documents, roadmaps, manifests, entrypoints, public interfaces, tests, releases, and deployment configuration.
4. Inspect relevant open and recently closed Issues, open and recently merged pull requests, and repository-native task state when available.
5. State inaccessible sources and freshness limitations. Do not fill gaps from memory or infer live status from stale conversation text.
6. Search the canonical Issue/PR carriers for the latest `codex-repo-state:v1` record. Revalidate it against the inspected commit and mark it `fresh`, `stale`, `conflicted`, `incomplete`, or `reconstructed`; never treat the record alone as live authority.

## Reconstruct intended architecture

Derive the system's documented goals, major components, responsibility boundaries, primary end-to-end flows, and milestones. Prefer accepted design records and current code over old plans. When sources disagree, report the conflict and identify which source appears authoritative; do not silently choose a convenient narrative.

If no authoritative overall design exists, say so and provide only a code-derived component map labeled as an inference.

## Classify capability state

Group behavior by user-visible capability or architectural responsibility rather than listing files. Assign exactly one state:

- `implemented`: reachable through the intended production path and supported by code plus meaningful validation or observed integration evidence
- `partial`: substantial implementation exists, but integration, required behavior, validation, migration, or acceptance work remains
- `planned`: explicitly required by an accepted Issue, roadmap, or design, but not implemented in the inspected snapshot
- `absent`: required for the stated target design but no active implementation or accepted plan was found
- `unknown`: evidence is insufficient or contradictory
- `out-of-scope`: intentionally excluded from the current target

Documentation, a closed Issue, an isolated helper, or a merged PR is not by itself proof that a capability is operational. Trace the production entrypoint and current integrated code. Conversely, do not call an undocumented but working capability absent when code and tests establish it.

For every nontrivial classification, cite concise evidence such as commit-pinned paths, tests, release tags, Issue or PR URLs, task records, or validation output. Label code-derived architectural interpretations as inference.

## Reconstruct active work

For each current workstream, record:

- Objective and owning Issue or task
- Status: `planned` | `in-progress` | `in-review` | `blocked` | `merge-ready` | `landed-unverified`
- Branch, PR, and head SHA when they exist
- Dependencies and relationship to other workstreams
- Latest verified result and remaining acceptance gap
- Next concrete action and who or what can authorize it

Do not treat an open Issue as active work without branch, PR, task-state, or explicit ownership evidence. Do not treat a merged PR as fully complete until its intended integration and acceptance conditions are satisfied.

## Preserve active gates

When an unresolved condition constrains the next action, retain its operational role:

- Target action
- Status: `stop` | `conditional` | `allowed`
- Unresolved prerequisite
- Clearing authority
- Admissible fallback
- Evidence snapshot
- Required revalidation immediately before action

Use `none` or `unknown` explicitly. A deadline, existing plan, apparent consensus, delegated ownership, or prior exception does not clear a gate.

## Locate the project in its design

Map each major architectural area or milestone to its capability state and active workstreams. Explain:

- What foundation is already stable
- Which vertical slice or lifecycle stage is currently being built
- What remains disconnected or unvalidated
- Which later work is genuinely dependency-blocked
- Whether implementation order still matches the accepted design

Separate verified progress from percentage-style estimates. Do not invent a completion percentage unless the repository defines a measurable denominator.

## Produce the snapshot

Use this structure, omitting empty sections:

```markdown
# Repository Status

## Snapshot
- Repository:
- Branch and commit:
- Observed at:
- Scope:
- Evidence limitations:

## Executive status
<A concise account of what works, what is active, the current architectural position, and the most important blocker or decision.>

## Product capability matrix
| Capability | State | Current behavior | Remaining gap | Evidence |
|---|---|---|---|---|

## Active workstreams
| Workstream | Issue / Task | Status | PR / Head | Dependency | Remaining work | Next action |
|---|---|---|---|---|---|---|

## Durable continuation state
- Canonical carrier(s):
- State status: `fresh` | `stale` | `conflicted` | `incomplete` | `reconstructed` | `none-found`
- Last durable update:
- Drift or missing fields:
- Recovery implication:

## Architecture position
| Area or milestone | Intended responsibility | Current state | Active work | What unlocks next |
|---|---|---|---|---|

## Active gates and blockers
### <gate>
- Target action:
- Status:
- Unresolved prerequisite:
- Clearing authority:
- Admissible fallback:
- Evidence snapshot:
- Reverify before action:

## Human decisions needed

## Recommended next checkpoints

## Evidence index
```

Keep the executive status short; put detail in the matrices. Rank next checkpoints by dependency and leverage, but do not turn recommendations into authorization.

## Preserve boundaries

- Do not modify code, Issues, pull requests, branches, labels, projects, or releases.
- Do not perform a general defect hunt; use `@repo-review` when the goal is finding Bugs or Feature Requests.
- Do not generate an implementation plan; use `@patch-plan` or `@blueprint` after the user selects work.
- Do not replace `@handover` or `@repo-handoff`: this skill reports state and consumes durable records; it does not write a handoff or preserve private conversation context.
- Do not replace `@handover`: this skill summarizes repository state, not conversation decisions or personal context unless they are represented in repository evidence.
- Route security-sensitive details to `@security-audit`; summarize only the existence and handling status of restricted work.

## Quality gate

Verify that:

- The snapshot is pinned to a branch, commit, and observation time.
- Implemented claims trace through the intended production path.
- Planned, partial, absent, and unknown states are not collapsed together.
- Active work is supported by live artifacts rather than open-Issue count alone.
- The architecture map distinguishes documented intent from inference.
- Durable continuation records are located, pinned to a carrier, and checked for drift; missing records are reported rather than invented.
- Every active gate preserves its prerequisite, authority, fallback, evidence, and revalidation.
- Completed work is not presented as pending, and merged-but-unverified work is not overstated.
- A reader can identify the current architectural position and next decision without reading the entire repository history.
