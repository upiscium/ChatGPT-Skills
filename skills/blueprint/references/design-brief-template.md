# Design brief and Issue candidate template

Adapt this template to the task. Omit sections that do not apply.

```markdown
# <Project or Change Name>

- Brief ID / revision:
- Design status: draft | decision-required | human-approved
- Approval source and exact scope:
- Repository snapshot / evidence date:
- Execution or publication permission: not implied

## 1. Executive summary
- Problem:
- Target outcome:
- Proposed solution:
- MVP boundary:

## 2. Background and current workflow

## 3. Users and use cases
### Actors and permissions
### Primary scenarios
### Edge and failure scenarios

## 4. Requirements
### Functional requirements
### Non-functional requirements
### Constraints
### Non-goals

## 5. Success criteria
- User or product outcomes:
- Research outcome/evidence standard, if applicable (technical execution is separate):
- Technical acceptance criteria:
- Operational signals:
- Resource envelope and authority: time / cost / compute / maintenance / allocation; unknown limits remain unknown
- Goal-alignment snapshot: approved objective/source/revision, actual scope delta, aligned | off-goal | unknown, next action

## 6. Existing-system assessment
- Repository:
- Branch and commit:
- Relevant components:
- Reusable behavior:
- Current limitations:

## 7. Proposed design
### Architecture and responsibility boundaries
### Data model and state transitions
### Interfaces, APIs, and events
### User experience or operator workflow
### Error handling and recovery
### Security and privacy
### Performance and reliability
### Compatibility and migration

## 8. Alternatives considered
| Alternative | Benefits | Costs and risks | Decision |
|---|---|---|---|

## 9. Decision ledger
### Confirmed
### Assumed
### Open
For each requested human decision, include work completed, exact requested approval and scope, affected behavior/users, and handling if denied. Use the four-field approval brief; design acceptance grants only the stated scope. For critical choices add why-now, credible alternatives including retaining the current state, recommendation, losses/tradeoffs, facts versus inference/confidence, unverified impact, acceptance/recovery/revalidation. Do not reopen resolved choices.
### Rejected

## 10. Execution contracts

Repeat for each decision, approval, dependency, or safety condition that constrains implementation.

### <contract ID>
- Target action:
- Status: stop | conditional | allowed
- Unresolved prerequisite:
- Clearing authority:
- Admissible fallback:
- Evidence snapshot:
- Reverify before action:

Use `none` or `unknown` explicitly. Omit this section only when no action-binding state exists.

## 11. Issue candidates, not execution instructions

### DES-001: <coherent outcome>
- Source requirement / design revision:
- Type: bug | feature-request
- Desired outcome and evidence:
- Scope / non-goals / invariants:
- Stable AC IDs and observable acceptance:
- Dependencies:
- Material decisions still open:
- Design approval status:
- Issue filing authorization: granted for this unit | not granted

Use bounded discovery candidates when an unknown blocks design. Never hide an unresolved human choice in an implementation task. Hand selected authorized candidates to issue-filer; execution steps belong to patch-plan after Issues exist.

## 12. Test strategy
### Unit
### Integration
### End-to-end or system
### Security and abuse cases
### Performance and reliability

## 13. Deployment, migration, and rollback

## 14. Observability and operations

## 15. Risks and mitigations
| Risk | Likelihood | Impact | Mitigation | Validation |
|---|---|---|---|---|

## 16. Future extensions

## 17. Definition of done
```

## Candidate-writing rules

- Make each candidate independently understandable and bounded.
- Describe behavior and responsibility before implementation mechanics.
- Use exact paths and symbols only after inspecting them.
- Pair schema or API changes with compatibility and migration tasks.
- Pair background or distributed work with retries, idempotency, and observability.
- Pair privileged operations with authorization and audit requirements.
- Pair acceptance criteria with testable behavior, without inventing exact commands.
- End with the design decision and next authorized handoff, not automatic dispatch.
