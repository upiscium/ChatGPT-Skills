## Separate implementation, availability, and activity

Group behavior by user-visible capability or architectural responsibility rather than listing files. Scope rows to a specific feature slice or version: a usable feature can coexist with an enhancement in progress. For each slice and inspected ref, assign one implementation state:

- `implemented`: reachable through the intended production path and supported by code plus meaningful validation or observed integration evidence
- `partial`: substantial implementation exists, but integration, required behavior, validation, migration, or acceptance work remains
- `planned`: accepted work item or roadmap scope, with no substantial implementation found in the inspected refs
- `absent`: required by the accepted target design, but no implementation or tracked delivery plan was found
- `unknown`: evidence is insufficient or contradictory
- `out-of-scope`: intentionally excluded from the current target

Documentation, a closed Issue, an isolated helper, or a merged PR is not by itself proof that a capability is operational. Trace the production entrypoint and current integrated code. Conversely, do not call an undocumented but working capability absent when code and tests establish it.

Assess availability separately: usable in a named release/environment or supported source checkout, usable with stated prerequisites, not yet available, or unknown. Cite the entrypoint and validation or release/deployment evidence appropriate to the product. A library or CLI need not be deployed to a server, but passing source tests do not establish availability in a hosted production service. Do not run a deployment or change an environment to prove availability.

Map the evidence to the user's three capability views:

- **Implemented and usable:** name what the user can do, where/how it is available, and any setup, access, feature-flag, or environment conditions. Include an `implemented` slice only when its scoped availability is established; do not generalize a working subset to the whole feature.
- **Work in progress:** require current code, PR, task-state, or dated owner-report evidence that implementation, review, integration, or acceptance work has begun. Name the remaining gap and blocker. Assignment or branch existence alone does not prove work has started. A stale branch is not proof of continuing activity; distinguish recorded work status from a live running process. Explicitly paused/blocked work stays labeled as such.
- **Not started:** include only accepted scope for which the inspected sources show no implementation or active work. Check relevant branches/PRs/tasks as well as the main snapshot. Separate scheduled backlog from target-design requirements that are still untracked. Ideas, rejected work, and out-of-scope features are not commitments.

Do not force every capability into these three views. Report partial but idle work, integrated code awaiting availability, and unknowns in a short **Other gaps / unconfirmed state** note with evidence and what would resolve them. Put a delivery wait in work in progress only when a current workstream supports that classification. Missing access or missing documentation is not evidence of nonexistence or of work not having started.

For every nontrivial classification, cite concise evidence such as commit-pinned paths, tests, release tags, Issue or PR URLs, task records, or validation output. Label code-derived architectural interpretations as inference.

## Reconstruct active work

For each current workstream, record:

- Objective and owning Issue or task
- Status: `planned` | `in-progress` | `in-review` | `blocked` | `merge-ready` | `landed-unverified`
- Branch, PR, and head SHA when they exist
- Dependencies and relationship to other workstreams
- Latest verified result and remaining acceptance gap
- Owner when recorded and the time of the latest activity/status evidence; use `unknown` rather than inventing ownership or current activity
- OpenCode run/revision, delivery/acknowledgement/execution/collection/independent verification, authorized stop point, and evidence time when available; keep executor claims distinct from verified results
- Next concrete action and who or what can authorize it

Do not treat an open or assigned Issue as active work without evidence that work has started. Do not treat a merged PR as fully complete until its intended integration and acceptance conditions are satisfied.

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

Map accepted roadmap milestones, in their documented order and dependency structure, to capabilities and workstreams. Show completed, current, next, later, blocked, or unconfirmed stages and the exit conditions still unmet. Parallel tracks may have different current stages; do not manufacture a single linear phase. Explain:

- What foundation is already stable
- Which vertical slice or lifecycle stage is currently being built
- What remains disconnected or unvalidated
- Which later work is genuinely dependency-blocked
- Whether implementation order still matches the accepted design

Separate verified progress from percentage-style estimates. Do not invent a completion percentage unless the repository defines a measurable denominator.

If no accepted roadmap exists, explicitly say that the overall roadmap position is unknown. A component map or suggested sequence can help orient the user, but label it as an inference or proposal; never present it as the agreed roadmap.

## Establish what is planned next

Find the next action in the latest applicable user direction, accepted plan, or revalidated coordinator/task state. Check for superseding decisions and unresolved gates. A stale marker, old priority label, or high-value idea is not enough to establish a current plan. Surface conflicting plans instead of silently choosing one.

For each confirmed next action, state the action, intended result, owner when known, prerequisite or gate, and authorized stop point. Keep this to the immediate checkpoint per active track, not a newly generated implementation plan. If no next action is agreed or verifiable, say **not decided** or **unconfirmed** and why.

Optionally suggest a small number of next candidates, ordered by actual dependencies. Label them **recommendations, not agreed actions**. Never replace the current planned action with a recommendation, treat a status request as execution authority, or turn a reported blocker into an unsolicited approval request. If the user actually requests a decision, use the approval brief above.
