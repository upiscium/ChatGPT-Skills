## Define authority and stop point

Apply `@human-review`'s `references/goal-alignment.md` before planning a new workstream or materially revised scope. Copy the approved objective/revision, outcome criteria, non-goals, known resource envelope and unresolved material deltas into the packet. Before returning, apply its `references/decision-sweep.md` to the actual planned architecture/responsibilities, grants and next action; a complete task list or Green CI cannot settle an unapproved human-owned choice.

Every packet must include workflow/workstream/run ID, approved instruction revision, immutable packet reference/digest, exact target/session role, operation allowlist and approval source. Use OpenCode only; never instruct it to launch standalone Codex CLI.

Include the OpenCode model policy from `@opencode-bridge`'s `references/model-selection.md`: `model_policy: opencode-config`. Use the model, reasoning effort and variant already configured by OpenCode; omit model/effort overrides from CLI arguments, API fields and instructions. Record actual metadata when exposed, otherwise `unknown`. Copy this policy into every independent and manual packet; do not propagate an older pinned-model requirement.

Choose the requested delivery scope, never a blanket default:
- Investigation only: bounded questions/evidence; no code or publication.
- Implementation and tests: deliver a frozen manifest/diff and evidence, stop before unapproved commit/push/Draft PR.
- Publication: only specifically authorized operations and reviewed snapshot, through repository guards; stop at the named Draft PR or earlier artifact.

Planning approval is not dispatch authority. Goal approval is not architecture/risk or publication permission. Unknown operations remain not-authorized. Ready/Merge stays user-executed outside the packet. Include the seven-field execution gate even for an allowed stream, and retain the exact unresolved human decisions. Copy the human-question contract into every packet: report work completed, exact requested action/actor and target/revision, affected scope, denial handling and why human authority is needed. Do not send a bare approval prompt or assume OpenCode can load Arca's skills.

Require run-correlated receipt and result formats. Arca coordinates and independently verifies; OpenCode implements; SwitchBoard owns Ask monitoring/notifications. Do not add monitoring loops to Arca or OpenCode or require a new monitoring service before otherwise authorized work. Connection configuration is separate from this generic skill.

Copy `@workspace-cleanup`'s resource lifecycle into every packet: register newly created persistent processes/tmux resources/worktrees with real IDs, ownership, consumers, cleanup owner, recovery destination and release trigger. Grant the coordinator routine cleanup of eligible owned resources after collection/completion; preserve explicit keep instructions and repository-owned finalization gates. Reused/shared resources are not disposable. Require cleanup receipts or a retained reason/owner/revisit trigger; do not turn an execution stop point into indefinite resource retention.

## Form implementation units

Group active work by root cause, change boundary, and dependency rather than making one task per issue.

- Combine findings repaired by one invariant or shared component.
- Separate unrelated bugs and capabilities even when they share an issue.
- Separate product decisions from implementation work.
- Preserve every source finding ID and issue link.
- Assign stable implementation IDs such as `IMP-001`.
- Distinguish required work from optional follow-ups.

In `agent-core` mode, map every runnable workstream to exactly one authoritative numeric GitHub Issue-backed Task. The Issue must contain the complete Task intent and acceptance contract required by the repository; an external implementation packet may clarify execution but must not become a second authority. If inseparable Issues lack one canonical Issue that defines their combined scope, block execution until the Issue contract is consolidated or serialize them instead of inventing a multi-Issue Task.

For feature requests, verify the user outcome, proposed scope, non-goals, and compatibility expectations. For bugs, verify the incorrect behavior, expected behavior, triggering path, and regression boundary.

## Build the workstream graph

Map implementation units into workstreams before writing tasks.

For each pair of candidate workstreams, inspect:

- Direct Issue or architectural dependencies
- Expected files, modules, symbols, generated artifacts, and tests
- Shared APIs, schemas, migrations, configuration, lockfiles, and build files
- Ordering requirements and whether one workstream changes the assumptions of another
- Active branches or PRs touching the same boundaries
- In `agent-core` mode, declared Task dependencies, scopes, coordination surfaces, and external resources

Classify the relationship as:

- `parallel`: No material dependency or likely conflicting write boundary
- `ordered`: One workstream must be merged before the other is replanned or implemented
- `combined`: Changes share one root cause or cannot be reviewed and validated independently
- `blocked`: A product decision or external dependency prevents scheduling

Assign stable workstream IDs such as `WS-001` and dependency waves starting at `Wave 1`.

Do not claim exact file-level independence when the files have not been verified. Put uncertain overlap into a discovery task or serialize it.

## Design executable work

For each implementation unit:

1. State the intended behavior or invariant.
2. Identify the narrowest complete change that addresses the root cause.
3. Specify files, modules, symbols, APIs, configuration, and commands only when verified against the implementation base.
4. Describe data, schema, API, compatibility, migration, deployment, and documentation effects when applicable.
5. Define tests that fail before the change and pass after it when practical.
6. Define observable completion criteria and trace them to source acceptance criteria.
7. Record dependencies, blockers, risks, and explicit non-goals.

When evidence is insufficient for exact instructions, add a bounded Phase 0 discovery task with a decision output. Do not invent paths, APIs, commands, or architecture.

### Make each unit executable without overprescribing

- Size tasks by independently verifiable outcomes and review boundaries, not a fixed number of minutes, lines or agent calls. Keep setup and documentation with the behavior they support.
- Identify each changed component's responsibility and the interfaces it consumes and produces. Pin names, types and values only when the approved contract or inspected code pins them. Preserve ordinary implementation latitude.
- Give each step an observable result. Verification steps name a verified command, expected result and evidence to retain. Avoid vague instructions such as “test thoroughly”; do not transcribe the complete implementation into the plan.
- Inspect the relevant baseline before attributing failures to the change. Preserve existing failures and environment blockers separately. An unrelated baseline failure need not block independent authorized work; a failure that prevents validating the changed behavior leaves that criterion unverified.
- For an unexplained bug, use `@debug-investigate` or include its bounded method in Phase 0: reproduce, trace the first incorrect boundary, compare a working case, test one discriminating hypothesis, and record the result before selecting a repair. Investigation does not grant host changes or instrumentation edits.
- Prefer a failing behavioral regression before a bug fix when practical. Record why it fails; a broken fixture or missing dependency is not the intended regression. Preserve existing work when adding tests later; never delete code to satisfy test-first ceremony.
- Require tests to detect named behavioral defects using independently derived expectations. Avoid assertions that merely pin editable budgets, warning margins, prose or implementation text. Test the behavior across the chosen boundary instead. Low-impact prose or value changes may need no new automated test.
- Choose focused checks plus required repository gates. Add broader integration checks for a concrete interaction risk; do not multiply full-suite runs or reviewers per small task without a reason.

Before handing off, check AC coverage, consistent interfaces across tasks, unresolved assumptions, failure cases and proportionality. Copy the necessary design constraints into every independent packet without turning each packet into a second design authority.

## Order the plan

Within each workstream, sequence work by dependency and risk:

1. Discovery or decisions that block design
2. Shared contracts, types, or migrations
3. Core implementation
4. Integrations and callers
5. Tests and documentation
6. Rollout, monitoring, cleanup, and rollback
7. Delivery at the authorized stop point: frozen prepublication evidence or separately authorized Draft PR

Run workstreams in the same wave concurrently. Start a later wave only after its prerequisite PRs are merged and its base SHA is refreshed.

Prefer one primary Issue or one inseparable Issue group per workstream and PR. Do not combine unrelated Issues to reduce PR count.
