# Security Remediation Implementation Plan Template

Adapt this template to the repository and selected findings. Keep restricted details out of broadly visible tracking systems.

```markdown
# Security Remediation Plan: <scope>

## 1. Confidentiality and handling
- Intended audience:
- Safe for normal engineering tracking:
- Restricted details:

## 2. Patch target
- Repository:
- Patch base branch:
- Patch base commit:
- Audit target commit:
- Selected findings:

## 3. Executive summary
- Exposure:
- Desired security state:
- Remediation units:
- Highest-priority action:

## 4. Assumptions and validation status
### Confirmed
### Assumed
### Needs validation
### Stale or excluded findings

## 5. Security invariants
| ID | Source findings | Violated invariant | Required invariant |
|---|---|---|---|

## 6. Immediate containment
### CON-001: <action>
- Findings:
- Exposure reduced:
- Operational impact:
- Preconditions and approvals:
- Validation:
- Reversal:

## 7. Permanent remediation design

### REM-001: <root-cause remediation>
- Source findings:
- Root cause:
- Design:
- Files and symbols:
- Interface or data changes:
- Compatibility and migration:
- Failure behavior:
- Non-goals:
- Defense-in-depth follow-up:

## 8. Codex patch implementation plan

### Phase 0: Revalidate and preserve evidence
#### Task 0.1: <task>
- Objective:
- Inspect:
- Deliverable:
- Completion criteria:

### Phase 1: Encode safe regression coverage
#### Task 1.1: <test task>
- Findings:
- Files and symbols:
- Test behavior:
- Safe fixtures:
- Validation commands:
- Completion criteria:

### Phase 2: Implement root-cause fixes
#### Task 2.1: <patch task>
- Remediation unit:
- Objective:
- Files and symbols:
- Changes:
- Security invariant:
- Error and fallback behavior:
- Compatibility:
- Tests:
- Validation commands:
- Completion criteria:
- Do not change:

### Phase 3: Recovery and defense in depth

### Phase 4: Full verification and release preparation

## 9. Test matrix
| Scenario | Actor or input | Expected result | Test level | Finding |
|---|---|---|---|---|

Include legitimate behavior, unauthorized behavior, malformed input, boundary values, failure paths, concurrency where relevant, and regression of adjacent functionality.

## 10. Rollout and monitoring
- Deployment order:
- Feature flags or staged rollout:
- Security signals:
- Reliability signals:
- Alert thresholds:
- Success criteria:

## 11. Rollback and recovery
- Rollback trigger:
- Reversible components:
- Irreversible changes:
- Data or credential recovery:
- Post-rollback security posture:

## 12. Risks and mitigations
| Risk | Likelihood | Impact | Mitigation | Validation |
|---|---|---|---|---|

## 13. Restricted follow-up
- Credential or key rotation:
- Session invalidation:
- Data exposure assessment:
- Incident-response coordination:

## 14. Definition of done
```

## Planning rules

- Use one remediation unit per root cause or inseparable change boundary.
- Put regression coverage before the root fix when safe and feasible.
- Require tests for both permitted and denied behavior at authorization boundaries.
- Pair schema and API changes with migration and compatibility work.
- Pair containment actions with reversal procedures.
- Pair deployment changes with observable rollout and rollback criteria.
- Do not place active secrets, exploit-ready payloads, or sensitive production evidence in the plan.
