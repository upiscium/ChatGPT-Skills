# Design and Codex Implementation Plan Template

Adapt this template to the task. Omit sections that do not apply.

```markdown
# <Project or Change Name>

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
- Technical acceptance criteria:
- Operational signals:

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
### Rejected

## 10. Codex implementation plan

### Phase 0: Discovery or prerequisite work
#### Task 0.1: <task>
- Objective:
- Inspect:
- Deliverable:
- Completion criteria:

### Phase 1: <coherent implementation milestone>
#### Task 1.1: <task>
- Objective:
- Files and symbols:
- Changes:
- Dependencies:
- Failure handling:
- Tests:
- Validation commands:
- Completion criteria:
- Do not change:

## 11. Test strategy
### Unit
### Integration
### End-to-end or system
### Security and abuse cases
### Performance and reliability

## 12. Deployment, migration, and rollback

## 13. Observability and operations

## 14. Risks and mitigations
| Risk | Likelihood | Impact | Mitigation | Validation |
|---|---|---|---|---|

## 15. Future extensions

## 16. Definition of done
```

## Task-writing rules

- Make each task independently understandable and bounded.
- Describe behavior and responsibility before implementation mechanics.
- Use exact paths and symbols only after inspecting them.
- Pair schema or API changes with compatibility and migration tasks.
- Pair background or distributed work with retries, idempotency, and observability.
- Pair privileged operations with authorization and audit requirements.
- Put tests in the same phase as the behavior they verify.
- End every phase with a runnable or inspectable validation checkpoint.
