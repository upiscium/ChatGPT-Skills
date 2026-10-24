---
name: repo-status
description: Explain a project's current position through five evidence-backed views — implemented and usable capabilities, work in progress, work not started, position on the overall roadmap, and the currently planned next action — while checkpointing verified repository state. Use when the user asks where a project stands, what they can use now, what is being built, what is still untouched, how far the roadmap has progressed, or what comes next. Distinguish implemented code from actual availability and agreed next steps from recommendations. Do not use as a defect-finding review or a conversation handover.
---

# Summarize Repository Status

Answer in **five views**: usable capabilities, work in progress, not started, roadmap position, and the verified next action. Separate implemented code from current availability. A read-only status query does not dispatch work.

## Load only the relevant detail

1. Pin the requested feature and current commit. Read [sources and scope](references/sources-and-scope.md) only for needed provenance, assumptions or human decisions.
2. Use [classification and roadmap](references/classification-and-roadmap.md) for implemented/partial/planned/unknown classifications and active work.
3. Read [five-view format](references/five-view-format.md) for a complete status response; answer narrower questions without an exhaustive Issue inventory.
4. Read [quality and gates](references/quality-and-gates.md) for material changed decisions, high-stakes handoffs or acceptance claims.

## Essential invariants

Passing tests or a closed Issue does not prove usability, deployment or scientific success. Identify unavailable evidence and preserve approved next actions. **Repeated read-only status with no new state** creates no new marker; only newly verified actionable changes may update `codex-repo-state:v1`.

Do not run implementation, Merge, release or project-content mutations from a status request. Protect existing authority, denials and active workstreams. Keep user-facing results feature-centered and machine details in the durable record.
