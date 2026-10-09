# OpenCode Execution Packet

Use this structure and omit sections that are genuinely irrelevant. Preserve source traceability and verified facts.

## Objective

- Desired outcome:
- Repository:
- Source repository review:
- Related merged PRs:
- Implementation branch or base:
- Base commit SHA:
- Follow-up PR target branch:
- Execution backend: agent-core | generic-worktree
- Backend evidence and version:
- Repository-local worktree contract: guarded Agent Core assignment | `<repository-root>/.worktrees/`
- Generic `.gitignore` prerequisite: not-applicable | verified | setup PR required
- Selected scope:
- Non-goals:
- Durable state carrier(s): existing Issue/PR URL(s) | bootstrap required
- Workflow ID:
- Run ID / instruction revision:
- Immutable packet reference / actual digest:
- Design source / approved revision / approval scope:
- Operation allowlist: investigate / edit / test / commit / push / Draft PR / executor report
- Approval source and prerequisites per operation:
- Exact stop point:
- Connection/session reference and Main/Task/generic role:
- Requested OpenCode model / effort: GPT-6.1 Sol / high, unless explicitly overridden by the user
- Resolved provider/model ID / variant: openai/gpt-6.1-sol / high, subject to verification on the selected target
- Model-selection evidence / observed values / verified at: unknown until inspected; verify both before dispatch
- Ask monitoring owner: SwitchBoard
- State status at planning: fresh | stale | conflicted | incomplete | reconstructed | none-found

## Source map

| Workstream | Wave | Implementation unit | Finding | Issue | Agent Core Task | Type | Status |
|---|---:|---|---|---|---|---|---|
| WS-001 | 1 | IMP-001 | F-001 | #123 | #123 or not-applicable | bug | active |

## Workstream execution contracts

Repeat for every workstream, including allowed ones. Unknown authority never means permission.

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
- Coordinator writer / ownership:
- Recording: automatic / saved | pending-write | bootstrap
- Restore/revalidation required before implementation:

At every substantive checkpoint, the coordinator updates the existing carrier through `@repo-handoff`, preserving unrelated fields and reading back its event. A missing marker is created automatically on an existing carrier. Executors append only authorized run-scoped reports, not coordinator markers. Never claim durable recovery from a chat-only packet. Save dispatch intent before sending; reconcile uncertain delivery instead of retrying.

## Design decisions

Record each decision, its rationale, alternatives rejected, and compatibility consequences. If a decision cannot yet be made, convert it into a Phase 0 task with a concrete output.

## Workstream execution

Before Wave 1, follow only the selected backend:

- `agent-core`: initialize Main, create or resume explicitly selected Issue-backed Tasks only through guarded lifecycle APIs, retain exact readiness evidence, and run the repository batch safety check before concurrent Task launch. Do not create branches or worktrees manually.
- `generic-worktree`: verify the committed root `.gitignore` entry `/.worktrees/` and `git check-ignore .worktrees/`. If absent, stop for separately authorized setup-PR work; the human executes Ready/Merge. Verify the merge and refresh the base before creating worktrees.

### Agent Core batch launch

Omit for `generic-worktree` mode.

| Workstream | Issue | Task | New or resume | Readiness mode | Worktree | Contract checksum | Batch-plan result |
|---|---|---|---|---|---|---|---|
| WS-001 | #123 | #123 | new | initial | guarded assignment | | parallel-safe |

- Main initialization evidence:
- Explicit Task set passed to batch planning:
- Conflicting pairs to serialize:
- Available Task Orchestrator slots:
- Partial-progress policy:

### Wave 1

Run independent workstreams in this wave concurrently, bounded by available SubAgent slots.

### WS-001: <Issue outcome>

- Issues:
- Agent Core Task and lifecycle status:
- Base SHA:
- Run / approved instruction revision / packet digest:
- Allowed operations and their authority:
- Exact stop point and fallback:
- Requested OpenCode model / effort, resolved ID / variant and pre-dispatch selection check:
- Dedicated branch:
- Isolated worktree: guarded Agent Core assignment | `<repository-root>/.worktrees/WS-001`
- Expected files/modules:
- Must not touch:
- Dependencies:
- Assigned SubAgent:
- Assigned Task Orchestrator:

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

For each task, include only applicable details:
- Interfaces consumed / produced and their authoritative constraints:
- Named defect each new test detects; independently derived expected behavior:
- Relevant baseline / intended pre-fix failure / post-fix evidence:
- Verified command, expected outcome, result scope and retained log reference:
- Safe execution surface and any environment or operation prerequisite:
- Optional broader checks and the concrete risk that requires them:

Use independently testable change units, not arbitrary time slices. Keep code bodies out of the plan unless an approved algorithm is otherwise ambiguous. No new automated test is required merely to pin prose, editable configuration values or implementation structure.

Repeat phases and tasks in dependency order. Repeat the workstream section for every Issue or inseparable Issue group. Put dependent work in later waves and require a refreshed base SHA.

## Test strategy

- Unit:
- Integration:
- End-to-end:
- Regression and failure paths:
- Compatibility or migration:
- Validation commands:

For each claimed result record the exact snapshot, command, environment, exit status, outcome (`pass|fail|blocked|not-run|timed-out`), scope, counts/skips and a readable evidence reference. Keep executor claims separate from inspected evidence. A timeout, incomplete shard set or dependency failure never proves the full suite passed. Reuse evidence only after checking snapshot, environment and scope applicability; rerun affected checks when those change.

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
- Agent Core Task ID, readiness evidence, and lifecycle status:
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
  - Agent Core Task ID and lifecycle status when applicable
  - Actual PR number and URL if authorized/created; otherwise not-created and reason
  - Frozen manifest/digest and exact validation snapshot
  - Requested and observed OpenCode model/effort, evidence reference and any mismatch
  - Head branch and resulting commit SHA
  - Executor report reference; coordinator carrier/read-back status or pending-write

Each executor stops at its granted boundary. Implementation-only delivery ends with frozen evidence for independent change-review, not publication. Commit/push/Draft PR require individual authority and repository gates. If authorized publication is blocked, report the exact blocker and preserved snapshot/branch; never invent a PR. Never invoke standalone Codex CLI or install Ask monitoring.

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
- Every workstream reached its authorized stop point and reports run/revision, actual scope and immutable evidence.
- Every authorized completed PR delivery names its actual number/URL; prepublication-only delivery explicitly has no PR.
- Concurrent work used backend-owned isolated branches and worktrees and did not modify another workstream.
- Agent Core mode used guarded Task lifecycle plus batch planning; generic mode verified the committed root `.gitignore` contains `/.worktrees/` before the first worktree was created.
- Cross-workstream checks and merge ordering are recorded.
- The final implementation summary can cite the base and resulting commit SHAs.
- Each workstream's durable carrier can reconstruct its stage, dependencies, gates, decisions, and next action without the planning conversation.
