# Codex Implementation Plan

Use this structure and omit sections that are genuinely irrelevant. Preserve source traceability and verified facts.

## Objective

- Desired outcome:
- Repository:
- Implementation branch or base:
- Base commit SHA:
- Selected scope:
- Non-goals:

## Source map

| Implementation unit | Finding | Issue | Type | Status | Reason |
|---|---|---|---|---|---|
| IMP-001 | F-001 | #123 or not-filed | bug or feature-request | active | |

List excluded, stale, duplicate, closed, already-fixed, blocked, and security-routed inputs after the table.

## Verified current state

- Relevant behavior:
- Code and contracts inspected:
- Validation performed:
- Constraints:
- Assumptions and evidence gaps:

## Design decisions

Record each decision, its rationale, alternatives rejected, and compatibility consequences. If a decision cannot yet be made, convert it into a Phase 0 task with a concrete output.

## Implementation phases

### Phase 0: Discovery and blocking decisions

Omit when unnecessary.

#### Task P0-T1: <decision or investigation>

- Purpose:
- Inspect:
- Questions to resolve:
- Required output:
- Completion criteria:

### Phase 1: <cohesive change boundary>

#### Task P1-T1: <imperative task title>

- Implementation unit:
- Source findings and issues:
- Files, modules, and symbols:
- Required behavior or invariant:
- Changes:
- API, data, configuration, or compatibility effects:
- Must not change:
- Dependencies:
- Tests:
- Validation:
- Completion criteria:

Repeat phases and tasks in dependency order. Keep optional follow-ups clearly separate from required work.

## Test strategy

- Unit:
- Integration:
- End-to-end:
- Regression and failure paths:
- Compatibility or migration:
- Validation commands:

Use only commands verified in the repository. Otherwise describe the check and mark command discovery as required.

## Documentation and operations

- Documentation:
- Rollout:
- Monitoring and success signals:
- Rollback:
- Cleanup:

## Risks and blockers

| Risk or blocker | Impact | Mitigation or owner decision |
|---|---|---|

## Suggested delivery boundaries

Describe safe incremental implementation, commit, or pull-request boundaries when useful. Do not create them.

## Definition of done

- All active source findings and issue acceptance criteria map to completed tasks and tests.
- Required checks pass.
- Compatibility, migration, documentation, rollout, and rollback work is complete or explicitly not applicable.
- No excluded or security-routed work was implemented accidentally.
- The final implementation summary can cite the base and resulting commit SHAs.
