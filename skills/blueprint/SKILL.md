---
name: blueprint
description: Turn a vague idea, desired capability or workflow pain into a human-approved design brief, stable acceptance criteria and bounded Issue candidates through an adaptive interview. Use to discover requirements, challenge a proposed solution, define an MVP or decide technical design before issue-filer and patch-plan prepare execution.
---

# Build a Blueprint

Guide the user from an incomplete signal to a decision-ready design. Own what and why; leave filed-Issue execution instructions to `@patch-plan`. Do not assume that the user's first proposed feature is the correct solution to the underlying problem.

Read [references/design-brief-template.md](references/design-brief-template.md) before producing the final design brief.

## Identify the starting signal

Classify the input as one or more of:

- An idea or possible solution
- A desired outcome or capability
- A recurring task or unmet need
- A complaint about an existing product or workflow
- A partially designed feature
- A requested change to an existing repository

Restate the underlying problem separately from the proposed solution. Ask the user to correct the restatement before locking major design decisions.

## Run an adaptive interview

Ask only questions whose answers can materially change scope, architecture, risk, or acceptance criteria.

- Ask one focused group of at most three questions per turn.
- Prioritize blocking questions over exhaustive questionnaires.
- Offer concrete options with tradeoffs when the user may not know the design space.
- Explain assumptions in plain language.
- Challenge contradictory requirements, solution anchoring, hidden operational cost, and unjustified scope.
- Reuse information already established in the conversation. Never ask the user to repeat it.

Cover the relevant dimensions:

- Target users, actors, and permissions
- Current workflow and the specific pain or failure
- Desired outcome and measurable success
- Core scenarios, edge cases, and failure behavior
- MVP scope, later extensions, and explicit non-goals
- Platform, environment, integrations, data, and compatibility
- Security, privacy, reliability, performance, and accessibility
- Deployment, migration, observability, maintenance, and rollback
- Time, hardware, dependency, licensing, and organizational constraints

Skip dimensions that cannot affect the requested work.

## Maintain a decision ledger

Continuously distinguish:

- `Confirmed`: explicitly decided or evidenced
- `Assumed`: provisionally chosen to keep progress moving
- `Open`: blocks or materially changes the plan
- `Rejected`: considered and intentionally excluded, with the reason

Periodically summarize new decisions and correct misunderstandings before continuing.

## Inspect implementation context

For an existing product or repository:

1. Resolve the repository, target branch, and commit.
2. Read applicable instructions, architecture, manifests, public interfaces, tests, CI, and the code around the requested change.
3. Identify reusable components, integration points, conventions, and constraints.
4. Do not prescribe files, APIs, or commands that were not verified. Mark unavoidable guesses.

For greenfield work, specify a minimal proposed structure and explain why it is appropriate.

## Apply the readiness gate

Do not finalize the plan until:

- The problem and target outcome are clear.
- MVP boundaries and non-goals are explicit.
- Material actors, data, integrations, and failure modes are understood.
- Acceptance criteria can be tested.
- Material architectural decisions are confirmed by their proper authority or retained as explicit blocking questions; assumptions do not authorize implementation.
- Remaining unknowns do not prevent safe implementation.

If the user asks to proceed despite open questions, retain material human-owned gates and propose only bounded discovery or another admissible fallback. Do not convert an unresolved approval into an executable assumption.

## Produce the design contract and Issue candidates

Use `references/design-brief-template.md`. Give the brief a stable ID and revision, approval status and source. Distinguish design approval from authorization to file Issues, dispatch, implement or publish.

Make the approved design traceable:

- Identify coherent capability/change units and their dependencies, not a second executable task plan.
- Name components and interfaces when verified; leave exact execution steps/commands to `@patch-plan` after Issue selection.
- Separate discovery questions from approved implementation scope.
- Include tests alongside the behavior they validate.
- Include security, failure handling, observability, compatibility, rollout, and rollback where relevant.
- Assign stable `AC-*` criteria and `DES-*` candidate IDs with desired outcome, scope, non-goals, dependencies and evidence.
- State invariants and what later implementers must not change.
- Preserve every action-binding decision or unresolved dependency as an execution contract: target action, status, prerequisite, clearing authority, admissible fallback, evidence snapshot, and execution-time revalidation. Use `none` or `unknown` explicitly when needed.

Do not let an existing implementation plan, deadline, apparent agreement, delegated ownership, or precedent turn an unresolved prerequisite into optional guidance.

Do not write implementation code or modify the repository unless the user separately asks.

Offer `@issue-filer` for explicitly selected approved candidates, then `@patch-plan` for the resulting filed Issues. Do not create Issues or an OpenCode execution packet inside this skill. For an existing canonical carrier, automatically persist the brief revision, decision provenance and next gate through `@repo-handoff`; if no carrier exists, return a bootstrap reference without creating one.

## Quality gate

Before delivering the final plan, verify that:

- The plan solves the underlying problem, not merely the initial phrasing.
- Requirements and design choices are distinguishable.
- The MVP is smaller than the unrestricted vision but still useful.
- Every task traces to a requirement or risk.
- Acceptance criteria are externally observable or mechanically testable.
- Dependencies, migrations, and failure paths are covered.
- Assumptions and unresolved risks are visible to Codex.
- Action-binding decisions retain their operational force and cannot be bypassed by the first implementation task.
- A new agent can reconstruct the design and approval boundaries without the interview transcript, then route through Issue filing and execution planning.
