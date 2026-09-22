# Codex Implementation Plan

Use this structure and omit sections that are genuinely irrelevant. Preserve source traceability and verified facts.

## Objective

- Desired outcome:
- Repository:
- Source repository review:
- Related merged PRs:
- Implementation branch or base:
- Base commit SHA:
- Follow-up PR target branch:
- Repository-local worktree root: `<repository-root>/.worktrees/`
- `.gitignore` prerequisite: verified | setup PR required
- Selected scope:
- Non-goals:
- Durable state carrier(s): existing Issue/PR URL(s) | bootstrap required
- Workflow ID:
- State status at planning: fresh | stale | conflicted | incomplete | reconstructed | none-found

## Source map

| Workstream | Wave | Implementation unit | Finding | Issue | Type | Status |
|---|---:|---|---|---|---|---|
| WS-001 | 1 | IMP-001 | F-001 | #123 | bug | active |

## Workstream execution contracts

Repeat for every workstream whose execution is blocked or conditional. Omit this section only when no action-binding state exists.

### WS-001
- Target action:
- Status: stop | conditional | allowed
- Unresolved prerequisite:
- Clearing authority:
- Admissible fallback:
- Evidence snapshot:
- Reverify before action:

Use `none` or `unknown` explicitly. Deadlines, prior plans, agreement among agents, delegated ownership, or precedent do not clear a prerequisite. Only the named authority or evidence may change the status.

List excluded, stale, duplicate, closed, already-fixed, blocked, and security-routed inputs after the table.

## Dependency and conflict matrix

| Workstream | Depends on | Expected write boundaries | Relationship | Rationale |
|---|---|---|---|---|
| WS-001 | none | verified paths/modules | parallel | |

Use `parallel`, `ordered`, `combined`, or `blocked`. Mark unverified boundaries explicitly.

## Verified current state

- Relevant behavior:
- Code and contracts inspected:
- Validation performed:
- Constraints:
- Assumptions and evidence gaps:

## Durable continuation state

- Carrier for each workstream:
- Aggregate carrier, if any:
- Latest `codex-repo-state:v1` sequence and update time:
- State write authorization: explicit | announced checkpoint | not granted
- Restore/revalidation required before implementation:

At every substantive checkpoint, update the workstream's canonical Issue or PR with the state marker through `@repo-handoff`, or return the exact marker block as `not-saved` when write authorization is absent. Never use this plan or the chat ledger as the only recovery source.

## Design decisions

Record each decision, its rationale, alternatives rejected, and compatibility consequences. If a decision cannot yet be made, convert it into a Phase 0 task with a concrete output.

## Workstream execution

Before Wave 1, resolve the repository root, verify that its committed `.gitignore` contains the exact entry `/.worktrees/`, and confirm it with `git check-ignore .worktrees/`. If missing, create and merge a minimal setup PR first, refresh the common base SHA, and stop until that prerequisite is complete.

### Wave 1

Run independent workstreams in this wave concurrently, bounded by available SubAgent slots.

### WS-001: <Issue outcome>

- Issues:
- Base SHA:
- Dedicated branch:
- Isolated worktree: `<repository-root>/.worktrees/WS-001`
- Expected files/modules:
- Must not touch:
- Dependencies:
- Assigned SubAgent:

#### Phase 0: Discovery and blocking decisions

Omit when unnecessary.

##### Task WS1-P0-T1: <decision or investigation>

- Purpose:
- Inspect:
- Questions to resolve:
- Required output:
- Completion criteria:

#### Phase 1: <cohesive change boundary>

##### Task WS1-P1-T1: <imperative task title>

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

Repeat phases and tasks in dependency order. Repeat the workstream section for every Issue or inseparable Issue group. Put dependent work in later waves and require a refreshed base SHA.

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

## Delivery plan by workstream

### WS-001

- Implementation branch and repository-local worktree:
- Commit boundaries:
- Follow-up PR target:
- Issues and source review to link:
- Required PR body:
  - Change summary
  - Validation evidence
  - Compatibility or migration notes
  - Known limitations
  - Rollback guidance
- Workstream report must include:
  - Workstream ID
  - Created PR number
  - Canonical PR URL
  - Head branch and resulting commit SHA
  - Durable state carrier URL, marker sequence, and read-back result (or `not-saved`)

Each workstream executor must create its own follow-up PR after validation. If creation is blocked, it must report the workstream ID, exact blocker, and pushed branch instead of inventing a PR number.

## Wave integration

- Concurrent PRs:
- Cross-workstream checks:
- Merge order:
- Later waves requiring replanning:

## Definition of done

- All active source findings and issue acceptance criteria map to completed tasks and tests.
- Required checks pass.
- Compatibility, migration, documentation, rollout, and rollback work is complete or explicitly not applicable.
- No excluded or security-routed work was implemented accidentally.
- Every completed workstream created its own PR against the planned target branch.
- Every workstream report names the actual PR number and canonical URL.
- Concurrent work used isolated branches and repository-local `.worktrees/<workstream-id>` worktrees and did not modify another workstream.
- The committed root `.gitignore` contains `/.worktrees/`, verified before the first worktree was created.
- Cross-workstream checks and merge ordering are recorded.
- The final implementation summary can cite the base and resulting commit SHAs.
- Each workstream's durable carrier can reconstruct its stage, dependencies, gates, decisions, and next action without the planning conversation.
