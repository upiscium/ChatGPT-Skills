---
name: blueprint
description: Turn a vague idea, desired capability, unmet need, workflow pain point, or dissatisfaction with an existing product into a validated design brief and a Codex-ready implementation plan through an adaptive interview. Use when the user wants help discovering requirements, challenging a proposed solution, defining an MVP, writing a technical design, or preparing an actionable implementation specification before coding.
---

# Build a Blueprint

Guide the user from an incomplete signal to an implementation-ready plan. Do not assume that the user's first proposed feature is the correct solution to the underlying problem.

Read [references/implementation-plan-template.md](references/implementation-plan-template.md) before producing the final document.

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
- Architectural decisions are either confirmed or clearly labeled assumptions.
- Remaining unknowns do not prevent safe implementation.

If the user asks to proceed despite open questions, convert each one into an explicit assumption, risk, or discovery task. Never hide uncertainty with false precision.

## Produce the design and plan

Use the structure in `references/implementation-plan-template.md`. Adapt it to the project and omit irrelevant sections.

Make the Codex plan executable:

- Order tasks by dependency.
- Name concrete files, modules, symbols, interfaces, migrations, and commands when verified.
- Separate discovery tasks from implementation tasks.
- Include tests alongside the behavior they validate.
- Include security, failure handling, observability, compatibility, rollout, and rollback where relevant.
- Give each phase verifiable completion criteria.
- State what Codex must not change.

Do not write implementation code or modify the repository unless the user separately asks.

## Quality gate

Before delivering the final plan, verify that:

- The plan solves the underlying problem, not merely the initial phrasing.
- Requirements and design choices are distinguishable.
- The MVP is smaller than the unrestricted vision but still useful.
- Every task traces to a requirement or risk.
- Acceptance criteria are externally observable or mechanically testable.
- Dependencies, migrations, and failure paths are covered.
- Assumptions and unresolved risks are visible to Codex.
- A new agent could begin work without access to the interview transcript.
